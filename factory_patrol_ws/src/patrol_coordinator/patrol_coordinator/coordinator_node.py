"""Experiment coordinator node.

This ROS 2 node orchestrates experiments:
1. Loads experiment config from YAML
2. Loads tasks from YAML
3. Selects coordination algorithm
4. Publishes mission to /ground_station/mission
5. For non-auction algorithms: subscribes to drone state and publishes assignments
   (/swarm/task_assignment) and/or movement commands (/swarm/movement_command)
6. Emits experiment events for metrics collection

Algorithm parameters are read from config/algorithms/<algorithm>.yaml (section
<algorithm>:), each overridable as a ROS parameter "<algorithm>.<name>". The static
factory geometry is read from the scenario's simulation.obstacles_file.

Usage:
    ros2 run patrol_coordinator coordinator_node \
        --ros-args -p algorithm:=auction -p config_file:=config/experiments/benchmark.yaml

The config file defines the SCENARIO (task set, metrics sampling); the algorithm is
selected independently. tasks_file overrides the scenario's mission.tasks_file.
"""

import os
import json
import yaml
import time

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

from patrol_msgs.msg import (
    Mission, Task, DroneState as DroneStateMsg,
    TaskAssignment as TaskAssignmentMsg, TaskBid,
    SwarmStatus, ExperimentEvent, MovementCommand as MovementCommandMsg,
)
from patrol_coordinator.algorithm_base import DroneState, TaskInfo
from patrol_coordinator.algorithms import get_algorithm_class
from patrol_coordinator.obstacles import load_obstacles


def _find_config_file(config_path: str) -> str:
    """Resolve config file path relative to workspace root."""
    if os.path.isabs(config_path) and os.path.exists(config_path):
        return config_path
    # Try relative to factory_patrol_sim root
    root = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
    candidates = [
        os.path.join(root, config_path),
        os.path.join('/home/mrweirdo/factory_patrol_sim', config_path),
        config_path,
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return config_path  # Return as-is, will fail later with a clear error


class CoordinatorNode(Node):
    def __init__(self):
        super().__init__('patrol_coordinator')

        # --- Parameters ---
        self.declare_parameter('algorithm', 'auction')
        self.declare_parameter('num_drones', 0)  # 0 = not given on command line -> use config (default 3)
        self.declare_parameter('config_file', 'config/experiments/benchmark.yaml')
        self.declare_parameter('tasks_file', '')  # '' = use the scenario's mission.tasks_file
        self.declare_parameter('mission_delay', 3.0)  # seconds to wait before publishing mission
        self.declare_parameter('hover_time', 4.0)
        self.declare_parameter('initial_battery', 100.0)
        self.declare_parameter('algorithm_config', '')  # '' = config/algorithms/<algorithm>.yaml if present

        self._algorithm_name = self.get_parameter('algorithm').value
        self._num_drones = self.get_parameter('num_drones').value
        config_file = self.get_parameter('config_file').value
        tasks_file = self.get_parameter('tasks_file').value
        self._mission_delay = self.get_parameter('mission_delay').value

        # --- Load config (override params if present) ---
        self._config = {}
        config_path = _find_config_file(config_file)
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self._config = yaml.safe_load(f) or {}
            self.get_logger().info(f'Loaded config from {config_path}')
            # Config values override default params
            exp = self._config.get('experiment', {})
            if 'algorithm' in exp and self._algorithm_name == 'auction':  # only override if param wasn't explicitly set
                self._algorithm_name = exp['algorithm']
            # An explicit num_drones parameter (set by the launcher that spawns the drones) wins
            if 'num_drones' in exp and self._num_drones <= 0:
                self._num_drones = exp['num_drones']
        else:
            self.get_logger().warn(f'Config file not found: {config_path} — using parameters')

        if self._num_drones <= 0:
            self._num_drones = 3

        self._scenario = self._config.get('scenario', {}).get('name', 'unspecified')
        if not tasks_file:
            tasks_file = self._config.get('mission', {}).get('tasks_file', '')
        if not tasks_file:
            self.get_logger().error('No tasks_file parameter and no mission.tasks_file in config')

        # --- Load tasks ---
        self._tasks: list[TaskInfo] = []
        tasks_path = _find_config_file(tasks_file)
        self._tasks_path = tasks_path
        if os.path.exists(tasks_path):
            with open(tasks_path, 'r') as f:
                tasks_data = yaml.safe_load(f) or {}
            for t in tasks_data.get('tasks', []):
                pos = t.get('position', [0, 0, -3])
                self._tasks.append(TaskInfo(
                    task_id=t['id'],
                    x=float(pos[0]),
                    y=float(pos[1]),
                    z=float(pos[2]),
                    priority=t.get('priority', 1),
                    inspection_type=t.get('inspection_type', 0),
                    hover_duration=t.get('hover_duration',
                                        self.get_parameter('hover_time').value),
                    label=t.get('label', ''),
                ))
            self.get_logger().info(f'Loaded {len(self._tasks)} tasks from {tasks_path}')
        else:
            self.get_logger().warn(f'Tasks file not found: {tasks_path}')

        # --- Algorithm parameters (config/algorithms/<algorithm>.yaml + ROS overrides) ---
        self._config['algorithm_params'] = self._load_algorithm_params()

        # --- Static factory geometry (shared by all algorithms) ---
        obstacles_file = self._config.get('simulation', {}).get('obstacles_file', '')
        self._obstacles_path = _find_config_file(obstacles_file) if obstacles_file else ''
        self._config['obstacles'] = []
        if self._obstacles_path and os.path.exists(self._obstacles_path):
            self._config['obstacles'] = load_obstacles(self._obstacles_path)
            self.get_logger().info(
                f'Loaded {len(self._config["obstacles"])} obstacles from {self._obstacles_path}')
        elif obstacles_file:
            self.get_logger().warn(f'Obstacles file not found: {self._obstacles_path}')

        # --- Initialize algorithm ---
        self.get_logger().info(f'Scenario: {self._scenario}')
        self.get_logger().info(f'Algorithm: {self._algorithm_name}')
        self.get_logger().info(f'Num drones: {self._num_drones}')

        # Fail closed: if the selected algorithm cannot be initialised, NO mission is published.
        # (Publishing it anyway would let the controllers' native auction fly the run while the
        # metrics label it with the selected algorithm.)
        self._init_error = None
        try:
            algo_class = get_algorithm_class(self._algorithm_name)
            self._algorithm = algo_class(self._config)
            self._algorithm.initialize(self._num_drones, self._tasks)
            self._algorithm_active = True
            self.get_logger().info(f'Algorithm initialized: {self._algorithm.get_name()}')
        except NotImplementedError as e:
            self._algorithm = None
            self._algorithm_active = False
            self._init_error = f'Algorithm not available: {e}'
        except Exception as e:
            self._algorithm = None
            self._algorithm_active = False
            self._init_error = f'Failed to initialize algorithm {self._algorithm_name!r}: {type(e).__name__}: {e}'
        if self._init_error:
            self.get_logger().error(self._init_error)
            self.get_logger().error('No mission will be published (no silent fallback to another algorithm).')

        # --- QoS ---
        reliable_qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
        )

        # --- Publishers ---
        self._mission_pub = self.create_publisher(Mission, '/ground_station/mission', reliable_qos)
        self._assignment_pub = self.create_publisher(TaskAssignmentMsg, '/swarm/task_assignment', reliable_qos)
        self._movement_pub = self.create_publisher(MovementCommandMsg, '/swarm/movement_command', reliable_qos)
        self._event_pub = self.create_publisher(ExperimentEvent, '/experiment/events', reliable_qos)

        # --- Subscribers ---
        self._drone_state_sub = self.create_subscription(
            DroneStateMsg, '/ground_station/drone_state',
            self._drone_state_cb, reliable_qos)
        self._bid_sub = self.create_subscription(
            TaskBid, '/swarm/task_bid',
            self._bid_cb, reliable_qos)
        self._assignment_sub = self.create_subscription(
            TaskAssignmentMsg, '/swarm/task_assignment',
            self._assignment_cb, reliable_qos)

        # --- State ---
        self._compute_ms: list[float] = []      # compute() durations since the last compute_stats event
        self._compute_report_t = time.monotonic()
        self._mission_published = False
        self._shutdown_requested = False
        self._drone_states: dict[int, DroneState] = {}

        # --- Timer: publish mission after delay ---
        self._startup_timer = self.create_timer(self._mission_delay, self._publish_mission_once)

        # --- Timer: periodic coordination (for non-auction algorithms) ---
        if self._algorithm_active and self._algorithm_name != 'auction':
            self._coord_timer = self.create_timer(
                self._algorithm.get_update_period(), self._coordination_tick)
        else:
            self._coord_timer = None

        self._emit_event('coordinator_started', {
            'scenario': self._scenario,
            'algorithm': self._algorithm_name,
            'num_drones': self._num_drones,
            'num_tasks': len(self._tasks),
        })

        self.get_logger().info('Coordinator node ready.')

    def _publish_mission_once(self):
        """Publish the mission to /ground_station/mission (once)."""
        if self._mission_published:
            return
        self._mission_published = True
        self._startup_timer.cancel()

        if self._init_error:
            self._emit_event('algorithm_init_failed', {
                'algorithm': self._algorithm_name, 'scenario': self._scenario, 'error': self._init_error})
            self.get_logger().error(f'Mission NOT published: {self._init_error}')
            self._shutdown_requested = True
            return

        if not self._tasks:
            self.get_logger().error('No tasks loaded — cannot publish mission!')
            return

        mission = Mission()
        mission.mission_id = 1
        for ti in self._tasks:
            t = Task()
            t.task_id = ti.task_id
            t.x = ti.x
            t.y = ti.y
            t.z = ti.z
            t.priority = ti.priority
            t.inspection_type = ti.inspection_type
            t.hover_duration = ti.hover_duration
            mission.tasks.append(t)

        self._mission_pub.publish(mission)
        self.get_logger().info(
            f'Published Mission 1 with {len(mission.tasks)} tasks'
        )
        # Carries the run identity too: coordinator_started is emitted during __init__,
        # usually before the metrics collector has matched the publisher, so it can be lost.
        self._emit_event('mission_started', {
            'mission_id': 1,
            'num_tasks': len(mission.tasks),
            'scenario': self._scenario,
            'algorithm': self._algorithm_name,
            'num_drones': self._num_drones,
            'tasks_file': self._tasks_path,
            'obstacles_file': self._obstacles_path,
            'num_obstacles': len(self._config['obstacles']),
            'algorithm_params': self._config['algorithm_params'],
        })

    def _drone_state_cb(self, msg: DroneStateMsg):
        """Handle incoming drone state."""
        state = DroneState(
            drone_id=msg.drone_id,
            x=msg.x, y=msg.y, z=msg.z,
            battery_level=msg.battery_level,
            state=msg.state,
            timestamp_ns=self.get_clock().now().nanoseconds,
            current_task_id=msg.current_task_id,
        )
        self._drone_states[msg.drone_id] = state
        if self._algorithm_active:
            self._algorithm.update_drone_state(state)

    def _bid_cb(self, msg: TaskBid):
        """Log bid events."""
        self._emit_event('bid_received', {
            'task_id': msg.task_id,
            'drone_id': msg.drone_id,
            'cost': float(msg.cost),
        })

    def _assignment_cb(self, msg: TaskAssignmentMsg):
        """Log assignment events."""
        self._emit_event('task_assigned', {
            'task_id': msg.task_id,
            'drone_id': msg.drone_id,
        })

    def _coordination_tick(self):
        """Periodic coordination step for non-auction algorithms."""
        if not self._algorithm_active or not self._mission_published:
            return

        t0 = time.perf_counter()
        try:
            result = self._algorithm.compute(self.get_clock().now().nanoseconds)
        except NotImplementedError as e:
            self.get_logger().error(f'Algorithm error: {e}', throttle_duration_sec=10.0)
            return
        self._record_compute_time((time.perf_counter() - t0) * 1e3)

        # Publish task assignments
        for assignment in result.assignments:
            msg = TaskAssignmentMsg()
            msg.task_id = assignment.task_id
            msg.drone_id = assignment.drone_id
            self._assignment_pub.publish(msg)
            self.get_logger().info(
                f'Assignment: Task {assignment.task_id} -> Drone {assignment.drone_id}'
            )

        # Publish movement commands (reactive algorithms, e.g. APF)
        for cmd in result.movement_commands:
            msg = MovementCommandMsg()
            msg.drone_id = cmd.drone_id
            msg.task_id = cmd.task_id
            msg.target_x = float(cmd.target_x)
            msg.target_y = float(cmd.target_y)
            msg.target_z = float(cmd.target_z)
            msg.velocity_x = float(cmd.velocity_x)
            msg.velocity_y = float(cmd.velocity_y)
            msg.velocity_z = float(cmd.velocity_z)
            self._movement_pub.publish(msg)

        for event_type, data in result.metadata.get('events', []):
            self._emit_event(event_type, data)

    def _record_compute_time(self, ms: float):
        """Decision time of the algorithm (wall time of compute()), reported every 5 s as a
        compute_stats event (source "coordinator"); the metrics collector aggregates them."""
        self._compute_ms.append(ms)
        if time.monotonic() - self._compute_report_t < 5.0:
            return
        v = sorted(self._compute_ms)
        self._emit_event('compute_stats', {
            'source': 'coordinator', 'algorithm': self._algorithm_name, 'n': len(v),
            'mean_ms': round(sum(v) / len(v), 4), 'max_ms': round(v[-1], 4),
            'p95_ms': round(v[min(len(v) - 1, int(0.95 * len(v)))], 4),
        })
        self._compute_ms.clear()
        self._compute_report_t = time.monotonic()

    def _load_algorithm_params(self) -> dict:
        """Read the '<algorithm>:' section of the algorithm config file.

        Every key is declared as a ROS parameter '<algorithm>.<key>' with the file value as
        default, so single values can be overridden with  -p <algorithm>.<key>:=<value>.
        """
        path_param = self.get_parameter('algorithm_config').value
        path = _find_config_file(path_param or f'config/algorithms/{self._algorithm_name}.yaml')
        if not os.path.exists(path):
            if path_param:
                self.get_logger().error(f'Algorithm config not found: {path}')
            return {}
        with open(path, 'r') as f:
            section = (yaml.safe_load(f) or {}).get(self._algorithm_name, {}) or {}
        params = {}
        for key, value in section.items():
            name = f'{self._algorithm_name}.{key}'
            self.declare_parameter(name, value)
            params[key] = self.get_parameter(name).value
        self.get_logger().info(f'Loaded {len(params)} {self._algorithm_name} parameters from {path}')
        return params

    def _emit_event(self, event_type: str, data: dict):
        """Publish an experiment event."""
        msg = ExperimentEvent()
        msg.timestamp = self.get_clock().now().nanoseconds
        msg.event_type = event_type
        msg.data = json.dumps(data)
        self._event_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = CoordinatorNode()
    exit_code = 0
    try:
        while rclpy.ok() and not node._shutdown_requested:
            rclpy.spin_once(node, timeout_sec=0.1)
        if node._shutdown_requested:
            # let the algorithm_init_failed event reach the metrics collector, then exit non-zero
            end = time.time() + 1.0
            while time.time() < end:
                rclpy.spin_once(node, timeout_sec=0.1)
            exit_code = 1
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
    return exit_code


if __name__ == '__main__':
    raise SystemExit(main())
