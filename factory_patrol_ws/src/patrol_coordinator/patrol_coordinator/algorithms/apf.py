"""Artificial Potential Field (APF) coordination algorithm.

Behaviour-based, reactive movement coordination. For every active drone that is
flying to a task, APF sums three velocity-space forces in the common factory frame
(x = east, y = north, z = -height):

    F_total = F_att + F_obs + F_drone

    F_att   = k_att (g - p), with |F_att| <= v_max
              (quadratic potential near the goal, conic far from it)
    F_obs   = sum over boxes with d < rho_obs:    k_obs   (1/d - 1/rho_obs)   (1/d^2) n
    F_drone = sum over drones with d < rho_drone: k_drone (1/d - 1/rho_drone) (1/d^2) n

d is the distance to the closest point of the obstacle box (or to the other drone),
n the unit vector pointing away from it, and d is floored at min_distance. The
result is smoothed with the previous command, clamped to v_max and turned into a
position setpoint p + v * command_horizon (MovementCommand).

Goal/task selection is NOT done here. Tasks are allocated by the framework's existing
mechanism (the native auction in the patrol controllers); each controller reports the
task it is currently flying to in DroneState.current_task_id, and APF steers toward it.
Arrival, inspection hover, zone looping, low-battery return and failure handling stay
in the patrol controller (external navigation mode).

The algorithm never publishes ROS messages or talks to PX4; the coordinator node
publishes the returned MovementCommands on /swarm/movement_command.
"""

import math
from dataclasses import dataclass, fields

from patrol_coordinator.algorithm_base import (
    CoordinationAlgorithm, AlgorithmResult, MovementCommand, TaskInfo,
)
from patrol_coordinator.obstacles import BoxObstacle

DRONE_STATE_PATROLLING = 1
DRONE_STATE_FAILED = 4


@dataclass
class APFParams:
    """APF parameters; defaults mirror config/algorithms/apf.yaml."""
    goal_gain: float = 0.5
    max_velocity: float = 1.5
    obstacle_repulsion_gain: float = 0.5
    obstacle_influence_radius: float = 1.5
    drone_repulsion_gain: float = 10.0
    drone_influence_radius: float = 3.0
    goal_tolerance: float = 1.2
    min_distance: float = 0.1
    velocity_smoothing: float = 0.2
    command_horizon: float = 1.0
    update_rate_hz: float = 10.0
    heartbeat_timeout: float = 5.0
    diagnostics_interval: float = 1.0
    stall_speed: float = 0.1
    stall_time: float = 5.0

    @classmethod
    def from_dict(cls, values: dict) -> 'APFParams':
        known = {f.name for f in fields(cls)}
        unknown = set(values) - known
        if unknown:
            raise ValueError(f"Unknown APF parameter(s): {', '.join(sorted(unknown))}")
        params = cls(**{k: float(v) for k, v in values.items()})
        for name in ('goal_gain', 'max_velocity', 'obstacle_influence_radius',
                     'drone_influence_radius', 'min_distance', 'command_horizon',
                     'update_rate_hz', 'heartbeat_timeout'):
            if getattr(params, name) <= 0.0:
                raise ValueError(f'APF parameter {name} must be > 0')
        if not 0.0 <= params.velocity_smoothing < 1.0:
            raise ValueError('APF parameter velocity_smoothing must be in [0, 1)')
        return params


# ---------------------------------------------------------------------------
# Vector helpers (plain tuples; 3 components)
# ---------------------------------------------------------------------------

def _add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _scale(a, s):
    return (a[0] * s, a[1] * s, a[2] * s)


def _norm(a):
    return math.sqrt(a[0] * a[0] + a[1] * a[1] + a[2] * a[2])


def _clamp_norm(a, limit):
    n = _norm(a)
    return _scale(a, limit / n) if n > limit else a


ZERO = (0.0, 0.0, 0.0)


# ---------------------------------------------------------------------------
# Force terms
# ---------------------------------------------------------------------------

def attractive_force(p, goal, params: APFParams):
    """F_att = k_att (g - p), magnitude saturated at max_velocity."""
    return _clamp_norm(_scale(_sub(goal, p), params.goal_gain), params.max_velocity)


def khatib_magnitude(d, gain, influence_radius, min_distance):
    """Magnitude of the Khatib repulsive gradient  k (1/d - 1/rho) / d^2  (0 outside rho)."""
    d = max(d, min_distance)
    if d >= influence_radius:
        return 0.0
    return gain * (1.0 / d - 1.0 / influence_radius) / (d * d)


def obstacle_force(p, obstacles: list[BoxObstacle], params: APFParams):
    """Sum of box repulsions. Returns (force, distance to the nearest obstacle surface)."""
    force, nearest = ZERO, math.inf
    for box in obstacles:
        diff = _sub(p, box.closest_point(p))
        d = _norm(diff)
        nearest = min(nearest, d)
        if d >= params.obstacle_influence_radius:
            continue
        # Inside the box (d == 0): push out through the nearest face.
        n = _scale(diff, 1.0 / d) if d > 1e-9 else box.outward_normal_inside(p)
        mag = khatib_magnitude(d, params.obstacle_repulsion_gain,
                               params.obstacle_influence_radius, params.min_distance)
        force = _add(force, _scale(n, mag))
    return force, nearest


def drone_force(drone_id, p, neighbours: dict, params: APFParams):
    """Sum of repulsions from other active drones. neighbours: {id: (x, y, z)}.

    Returns (force, distance to the nearest neighbour).
    """
    force, nearest = ZERO, math.inf
    for other_id, q in neighbours.items():
        if other_id == drone_id:
            continue
        diff = _sub(p, q)
        d = _norm(diff)
        nearest = min(nearest, d)
        if d >= params.drone_influence_radius:
            continue
        if d > 1e-9:
            n = _scale(diff, 1.0 / d)
        else:
            # Coincident positions: separate deterministically along x (opposite for the pair).
            n = (1.0 if drone_id > other_id else -1.0, 0.0, 0.0)
        mag = khatib_magnitude(d, params.drone_repulsion_gain,
                               params.drone_influence_radius, params.min_distance)
        force = _add(force, _scale(n, mag))
    return force, nearest


def _finite(v):
    return all(math.isfinite(c) for c in v)


def _round_or_none(x):
    return round(x, 3) if math.isfinite(x) else None


# ---------------------------------------------------------------------------
# Algorithm
# ---------------------------------------------------------------------------

def patrol_altitude(drone_id: int) -> float:
    """Mirror of get_patrol_altitude() in patrol_controller.c (used for tasks with z >= -1)."""
    return -2.5 - drone_id * 1.0


class APFAlgorithm(CoordinationAlgorithm):
    """Artificial Potential Field reactive movement coordination."""

    def __init__(self, config: dict):
        super().__init__(config)
        self.params = APFParams.from_dict(config.get('algorithm_params', {}) or {})
        self._obstacles: list[BoxObstacle] = list(config.get('obstacles', []) or [])
        self._num_drones = 0
        self._tasks_by_id: dict[int, TaskInfo] = {}
        self._drone_states = {}
        self._prev_velocity: dict[int, tuple] = {}
        self._prev_goal: dict[int, int] = {}
        self._stall_since_ns: dict[int, int] = {}
        self._stall_reported: set[int] = set()
        self._last_diag_ns = 0
        self._min_separation = math.inf  # since the last diagnostics event
        self._min_obstacle_distance = math.inf  # commanded drones, since the last diagnostics event
        self._diag: dict[int, dict] = {}

    def get_name(self) -> str:
        return 'APF (artificial potential field)'

    def get_update_period(self) -> float:
        return 1.0 / self.params.update_rate_hz

    def uses_external_navigation(self) -> bool:
        return True

    def initialize(self, num_drones: int, tasks: list[TaskInfo]) -> None:
        self._num_drones = num_drones
        self.update_tasks(tasks)

    def update_tasks(self, tasks: list[TaskInfo]) -> None:
        super().update_tasks(tasks)
        self._tasks_by_id = {t.task_id: t for t in tasks}

    def reset(self) -> None:
        super().reset()
        self._prev_velocity.clear()
        self._prev_goal.clear()
        self._stall_since_ns.clear()
        self._stall_reported.clear()
        self._diag.clear()
        self._min_separation = math.inf
        self._min_obstacle_distance = math.inf

    def on_drone_failed(self, drone_id: int) -> None:
        self._drone_states.pop(drone_id, None)

    # --- neighbour set ------------------------------------------------------

    def active_drones(self, timestamp_ns: int) -> dict:
        """Spawned (id < num_drones), heard within heartbeat_timeout, and not FAILED."""
        timeout_ns = int(self.params.heartbeat_timeout * 1e9)
        return {
            d: s for d, s in self._drone_states.items()
            if 0 <= d < self._num_drones
            and s.state != DRONE_STATE_FAILED
            and timestamp_ns - s.timestamp_ns <= timeout_ns
        }

    def goal_for(self, drone_id: int, task: TaskInfo):
        # Same altitude rule as the controller: z >= -1 means "use the drone's patrol altitude".
        z = task.z if task.z < -1.0 else patrol_altitude(drone_id)
        return (task.x, task.y, z)

    # --- core step ----------------------------------------------------------

    def compute(self, timestamp_ns: int) -> AlgorithmResult:
        p_ = self.params
        active = self.active_drones(timestamp_ns)
        positions = {d: (s.x, s.y, s.z) for d, s in active.items()}

        ids = sorted(positions)
        for i, a in enumerate(ids):
            for b in ids[i + 1:]:
                self._min_separation = min(self._min_separation, _norm(_sub(positions[a], positions[b])))

        commands, events = [], []
        for drone_id, s in sorted(active.items()):
            task = self._tasks_by_id.get(s.current_task_id)
            if s.state != DRONE_STATE_PATROLLING or task is None:
                self._prev_velocity.pop(drone_id, None)
                self._stall_since_ns.pop(drone_id, None)
                continue
            if self._prev_goal.get(drone_id) != task.task_id:
                self._prev_goal[drone_id] = task.task_id
                self._prev_velocity.pop(drone_id, None)
                self._stall_since_ns.pop(drone_id, None)
                self._stall_reported.discard(drone_id)

            p = positions[drone_id]
            goal = self.goal_for(drone_id, task)
            goal_dist = _norm(_sub(goal, p))

            if goal_dist <= p_.goal_tolerance:
                # Capture: command the exact goal, ignore repulsion -> no oscillation at the goal.
                f_att = f_obs = f_drone = velocity = ZERO
                target = goal
                d_obs = d_drone = math.nan
                self._prev_velocity.pop(drone_id, None)
            else:
                f_att = attractive_force(p, goal, p_)
                f_obs, d_obs = obstacle_force(p, self._obstacles, p_)
                f_drone, d_drone = drone_force(drone_id, p, positions, p_)
                self._min_obstacle_distance = min(self._min_obstacle_distance, d_obs)
                total = _add(_add(f_att, f_obs), f_drone)
                prev = self._prev_velocity.get(drone_id, total)
                velocity = _add(_scale(total, 1.0 - p_.velocity_smoothing),
                                _scale(prev, p_.velocity_smoothing))
                velocity = _clamp_norm(velocity, p_.max_velocity)
                if not _finite(velocity):
                    velocity = ZERO  # never forward NaN/Inf; hold position this step
                self._prev_velocity[drone_id] = velocity
                target = _add(p, _scale(velocity, p_.command_horizon))

            commands.append(MovementCommand(
                drone_id=drone_id, task_id=task.task_id,
                target_x=target[0], target_y=target[1], target_z=target[2],
                velocity_x=velocity[0], velocity_y=velocity[1], velocity_z=velocity[2],
            ))

            stall = self._check_stall(drone_id, task.task_id, goal_dist, velocity, p, timestamp_ns)
            if stall:
                events.append(('apf_stall', stall))

            self._diag[drone_id] = {
                'drone_id': drone_id, 'task_id': task.task_id,
                'goal_distance': round(goal_dist, 3),
                'f_att': round(_norm(f_att), 3), 'f_obs': round(_norm(f_obs), 3),
                'f_drone': round(_norm(f_drone), 3), 'f_total': round(_norm(velocity), 3),
                'nearest_obstacle': _round_or_none(d_obs),
                'nearest_drone': _round_or_none(d_drone),
            }

        if timestamp_ns - self._last_diag_ns >= int(p_.diagnostics_interval * 1e9):
            self._last_diag_ns = timestamp_ns
            for diag in self._diag.values():
                events.append(('apf_diagnostics', diag))
            events.append(('apf_clearance', {
                'active_drones': ids,
                'min_separation': _round_or_none(self._min_separation),
                'min_obstacle_distance': _round_or_none(self._min_obstacle_distance),
            }))
            self._diag = {}
            self._min_separation = math.inf
            self._min_obstacle_distance = math.inf

        return AlgorithmResult(movement_commands=commands, metadata={'events': events})

    def _check_stall(self, drone_id, task_id, goal_dist, velocity, p, timestamp_ns):
        """Report once per goal when a drone stays slow outside the goal (APF local minimum)."""
        if goal_dist <= self.params.goal_tolerance or _norm(velocity) >= self.params.stall_speed:
            self._stall_since_ns.pop(drone_id, None)
            return None
        since = self._stall_since_ns.setdefault(drone_id, timestamp_ns)
        if drone_id in self._stall_reported or timestamp_ns - since < self.params.stall_time * 1e9:
            return None
        self._stall_reported.add(drone_id)
        return {'drone_id': drone_id, 'task_id': task_id, 'goal_distance': round(goal_dist, 3),
                'x': round(p[0], 3), 'y': round(p[1], 3), 'z': round(p[2], 3)}

    def get_metrics(self) -> dict:
        return {'num_obstacles': len(self._obstacles)}
