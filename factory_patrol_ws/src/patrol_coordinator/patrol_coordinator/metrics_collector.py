"""Metrics collector node.

Subscribes to all relevant topics, records raw experiment data, and computes the
preliminary per-run summary metrics (see metrics_summary.py). The metrics are
algorithm-independent: every algorithm is measured from the same telemetry and events.

Output files (run_id = run_YYYYMMDD_HHMMSS, also the name of the run directory):
    - <output_dir>/<run_id>/experiment_events.jsonl  — one JSON object per line per event
    - <output_dir>/<run_id>/drone_states.csv         — periodic drone state snapshots
    - <output_dir>/<run_id>/metrics_detail.json      — per-drone distance/battery, exclusions
    - <output_dir>/summaries/<run_id>_<algorithm>_<scenario>_<N>drones.csv
                                                     — ONE summary row for the run, written
                                                       automatically when the mission completes,
                                                       times out (mission_timeout_s) or the
                                                       collector is shut down before completion.

Usage:
    ros2 run patrol_coordinator metrics_collector \
        --ros-args -p output_dir:=/path/to/results
"""

import os
import json
import csv
from datetime import datetime

import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

from patrol_msgs.msg import (
    DroneState, TaskAssignment, TaskBid,
    SwarmStatus, ExperimentEvent, Mission,
)
from patrol_coordinator.metrics_summary import RunMetrics


class MetricsCollector(Node):
    def __init__(self):
        super().__init__('metrics_collector')

        self.declare_parameter('output_dir', 'experiment_results')
        self.declare_parameter('state_snapshot_interval', 1.0)  # seconds
        self.declare_parameter('mission_timeout_s', 600.0)  # summary written as 'timeout' after this

        output_dir = self.get_parameter('output_dir').value
        snapshot_interval = self.get_parameter('state_snapshot_interval').value

        # Create output directory with timestamp
        timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        self._run_id = f'run_{timestamp_str}'
        self._output_dir = os.path.join(output_dir, self._run_id)
        self._summary_dir = os.path.join(output_dir, 'summaries')
        os.makedirs(self._output_dir, exist_ok=True)
        self._mission_timeout_s = float(self.get_parameter('mission_timeout_s').value)

        # Summary metrics state
        self._metrics = RunMetrics()
        self._mission_info = None       # from the coordinator's mission_started event
        self._mission_task_ids = None   # from /ground_station/mission
        self._summary_written = False

        # Open output files
        self._events_file = open(
            os.path.join(self._output_dir, 'experiment_events.jsonl'), 'w'
        )
        self._states_file = open(
            os.path.join(self._output_dir, 'drone_states.csv'), 'w', newline=''
        )
        self._states_writer = csv.writer(self._states_file)
        self._states_writer.writerow([
            'timestamp_ns', 'wall_time', 'drone_id',
            'x', 'y', 'z', 'battery_level', 'state', 'current_task_id',
        ])

        self.get_logger().info(f'Writing results to: {self._output_dir}')

        # QoS
        reliable_qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
        )

        # Drone state tracking
        self._latest_states: dict[int, DroneState] = {}

        # Subscribers
        self.create_subscription(
            DroneState, '/ground_station/drone_state',
            self._drone_state_cb, reliable_qos)
        self.create_subscription(
            TaskAssignment, '/swarm/task_assignment',
            self._task_assignment_cb, reliable_qos)
        self.create_subscription(
            TaskBid, '/swarm/task_bid',
            self._task_bid_cb, reliable_qos)
        self.create_subscription(
            SwarmStatus, '/ground_station/swarm_status',
            self._swarm_status_cb, reliable_qos)
        self.create_subscription(
            ExperimentEvent, '/experiment/events',
            self._experiment_event_cb, reliable_qos)
        self.create_subscription(
            Mission, '/ground_station/mission',
            self._mission_cb, reliable_qos)

        # Periodic state snapshot timer
        self._snapshot_timer = self.create_timer(
            snapshot_interval, self._write_state_snapshot)
        self._summary_timer = self.create_timer(1.0, self._check_mission_timeout)

        self._record_event('metrics_collector_started', {})
        self.get_logger().info('Metrics collector ready.')

    def _record_event(self, event_type: str, data: dict):
        """Write an event to the JSONL file."""
        record = {
            'timestamp_ns': self.get_clock().now().nanoseconds,
            'wall_time': datetime.now().isoformat(),
            'event_type': event_type,
            **data,
        }
        self._events_file.write(json.dumps(record) + '\n')
        self._events_file.flush()

    def _drone_state_cb(self, msg: DroneState):
        self._latest_states[msg.drone_id] = msg
        self._metrics.on_state(self.get_clock().now().nanoseconds, msg.drone_id,
                               msg.x, msg.y, msg.z, msg.battery_level, msg.state)

    def _task_assignment_cb(self, msg: TaskAssignment):
        self._record_event('task_assigned', {
            'task_id': msg.task_id,
            'drone_id': msg.drone_id,
        })

    def _task_bid_cb(self, msg: TaskBid):
        self._record_event('bid_received', {
            'task_id': msg.task_id,
            'drone_id': msg.drone_id,
            'cost': float(msg.cost),
        })

    def _swarm_status_cb(self, msg: SwarmStatus):
        self._record_event('swarm_status', {
            'status': msg.status,
            'reason': msg.reason,
        })

    def _experiment_event_cb(self, msg: ExperimentEvent):
        """Forward events from the coordinator."""
        try:
            data = json.loads(msg.data)
        except json.JSONDecodeError:
            data = {'raw': msg.data}
        self._record_event(msg.event_type, data)
        if msg.event_type == 'mission_started' and self._mission_info is None:
            self._mission_info = (int(msg.timestamp), data)
            self._maybe_start_metrics()
        elif msg.event_type == 'task_completed' and isinstance(data, dict):
            try:
                self._metrics.on_task_completed(int(msg.timestamp), int(data['drone_id']), int(data['task_id']))
            except (KeyError, TypeError, ValueError):
                return
            if self._metrics.mission_complete and not self._summary_written:
                self._write_summary()

    def _mission_cb(self, msg: Mission):
        if self._mission_task_ids is None:
            self._mission_task_ids = [t.task_id for t in msg.tasks]
            self._maybe_start_metrics()

    def _maybe_start_metrics(self):
        """Start the metric window once both the mission_started event and the task list are known."""
        if self._metrics.started or self._mission_info is None or self._mission_task_ids is None:
            return
        t_ns, info = self._mission_info
        self._metrics.start(t_ns, info.get('algorithm', 'unknown'), info.get('scenario', 'unspecified'),
                            int(info.get('num_drones', 0)), self._mission_task_ids)
        self.get_logger().info(
            f'Metrics window started: {self._metrics.algorithm} / {self._metrics.scenario} / '
            f'{self._metrics.num_drones} drones / {len(self._metrics.task_ids)} tasks')

    def _check_mission_timeout(self):
        if self._metrics.started and not self._summary_written:
            elapsed = (self.get_clock().now().nanoseconds - self._metrics.start_ns) / 1e9
            if elapsed >= self._mission_timeout_s:
                self._write_summary(status='timeout')

    def _write_summary(self, status=None):
        """Compute the summary metrics and write the run's single summary CSV row."""
        if self._summary_written or not self._metrics.started:
            return
        self._summary_written = True
        m = self._metrics
        start_iso = datetime.fromtimestamp(m.start_ns / 1e9).isoformat(timespec='seconds')
        row, detail = m.finalize(self.get_clock().now().nanoseconds, self._run_id, start_iso, status)
        os.makedirs(self._summary_dir, exist_ok=True)
        path = os.path.join(self._summary_dir,
                            f'{self._run_id}_{row["algorithm"]}_{row["scenario"]}_{row["num_drones"]}drones.csv')
        with open(path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=list(row.keys()))
            writer.writeheader()
            writer.writerow(row)
        with open(os.path.join(self._output_dir, 'metrics_detail.json'), 'w') as f:
            json.dump(detail, f, indent=2)
        self._record_event('run_summary_written', {'path': path, **{k: row[k] for k in (
            'status', 'completed_tasks', 'total_tasks', 'mission_completion_time_s')}})
        self.get_logger().info(f'Run summary ({row["status"]}) written to: {path}')

    def _write_state_snapshot(self):
        """Write current drone states to CSV."""
        now_ns = self.get_clock().now().nanoseconds
        wall_time = datetime.now().isoformat()
        for drone_id, state in sorted(self._latest_states.items()):
            self._states_writer.writerow([
                now_ns, wall_time, state.drone_id,
                f'{state.x:.3f}', f'{state.y:.3f}', f'{state.z:.3f}',
                f'{state.battery_level:.2f}', state.state, state.current_task_id,
            ])
        self._states_file.flush()

    def destroy_node(self):
        """Clean up files on shutdown."""
        if self._metrics.started and not self._summary_written:
            self._write_summary(status='aborted')  # stopped before the mission completed
        elif not self._metrics.started:
            self.get_logger().warn('No mission was started; no run summary written.')
        self._record_event('metrics_collector_stopped', {})
        self._events_file.close()
        self._states_file.close()
        self.get_logger().info(f'Results saved to: {self._output_dir}')
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = MetricsCollector()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
