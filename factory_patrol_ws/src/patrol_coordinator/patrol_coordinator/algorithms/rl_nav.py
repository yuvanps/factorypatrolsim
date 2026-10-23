"""RL navigation: legs planned by the trained PPO policy of rl-nmopso-factory-patrol.

The policy (rlpatrol, PPO trained on NMOPSO's own leg-planning problem: same path encoding, bounds
and MyCost objectives) is a LEG PLANNER. It does not allocate tasks. This algorithm therefore
plugs in exactly where APF does:

  allocation   unchanged: the native auction in the patrol controllers assigns zones, and each
               controller reports the task it is flying to in DroneState.current_task_id;
  navigation   this algorithm (controllers in 'external' navigation mode): when a drone starts a
               leg to a task, the policy plans the leg (rlpatrol.planner.LegPlanner.plan_route),
               and the drone follows the planned path through MovementCommands;
  everything   arrival (WAYPOINT_RADIUS), inspection hover, zone looping, low-battery return and
  else         failure handling stay in the patrol controller, as for APF.

Flown path for drone d to task T (factory frame: x = east, y = north, z = -height):
  current position -> (planned start, current altitude)      only if the start had to be moved to
                                                             free space (e.g. leaving a task above a machine)
  -> (planned start, cruise altitude of d)                   vertical
  -> the policy's path at the cruise altitude of d           the planned nodes, horizontally exact
  -> (planned goal, cruise altitude) -> (planned goal, task altitude)    vertical
  -> (task x, y, task altitude)                              only if the goal had to be moved
The policy plans in its trained patrol band (world z_patrol = 1.8 m). MyCost.m models every obstacle
as an infinitely tall cylinder, so the planned horizontal path is obstacle-free at any height; each
drone flies it on its own layer: cruise_height + drone_id * layer_separation (capped at
max_cruise_height), which separates crossing drones vertically. The task altitude uses the
controller's rule (task z, or the drone's patrol altitude if z >= -1).

Following: a carrot at lookahead = max_velocity * command_horizon ahead of the drone's progress
along the path; the command is p + clamp(carrot - p, max_velocity * command_horizon), i.e. the same
speed cap and setpoint look-ahead as APF. A drone further than replan_deviation from its path is
replanned. Yield rule (same as the RL repository's Gazebo flights, patrol_follower.py yield_radius):
a drone holds while a lower-ID active drone is within yield_radius and its next step would close
the distance, for at most max_yield_time per episode.

Failures are explicit. A checkpoint that cannot be loaded raises in initialize() (the coordinator
then publishes no mission). A leg with no feasible plan emits 'rl_plan_failed', the drone holds its
position and planning is retried every retry_period with a new seed; there is NO fallback to a
straight line, APF or the auction's transit.

Events (experiment_events.jsonl): rl_policy_loaded, rl_plan, rl_plan_failed, rl_replan, rl_yield,
rl_stall, rl_diagnostics (1 Hz per commanded drone), rl_clearance (1 Hz; same fields and definition
as apf_clearance).
"""

import math
import os
import sys
from dataclasses import dataclass, fields

from patrol_coordinator.algorithm_base import (
    CoordinationAlgorithm, AlgorithmResult, MovementCommand, TaskInfo,
)
from patrol_coordinator.obstacles import BoxObstacle

DRONE_STATE_PATROLLING = 1
DRONE_STATE_FAILED = 4


@dataclass
class RLParams:
    """RL navigation parameters; defaults mirror config/algorithms/rl.yaml."""
    repo_path: str = 'rl-nmopso-factory-patrol'
    checkpoint: str = 'rl-nmopso-factory-patrol/results/ckpt/vB_seed2.pt'
    device: str = 'cpu'
    torch_threads: int = 2
    num_preferences: int = 50
    samples_per_preference: int = 3
    refine_on_failure: bool = True
    seed: int = 0
    keep_in_x: float = 12.0
    keep_in_y: float = 7.0
    cruise_height: float = 1.8
    layer_separation: float = 1.0
    max_cruise_height: float = 10.0
    max_velocity: float = 1.5
    command_horizon: float = 1.0
    goal_tolerance: float = 1.2
    replan_deviation: float = 2.5
    retry_period: float = 2.0
    max_plans_per_tick: int = 1
    yield_radius: float = 2.5
    max_yield_time: float = 30.0
    update_rate_hz: float = 10.0
    heartbeat_timeout: float = 5.0
    diagnostics_interval: float = 1.0
    stall_speed: float = 0.1
    stall_time: float = 5.0

    @classmethod
    def from_dict(cls, values: dict) -> 'RLParams':
        types = {f.name: type(f.default) for f in fields(cls)}
        unknown = set(values) - set(types)
        if unknown:
            raise ValueError(f"Unknown RL parameter(s): {', '.join(sorted(unknown))}")

        def conv(k, v):
            t = types[k]
            if t is bool and not isinstance(v, bool):
                if str(v).lower() not in ('true', 'false', '1', '0'):
                    raise ValueError(f'RL parameter {k} must be a boolean, got {v!r}')
                return str(v).lower() in ('true', '1')
            if t is int and isinstance(v, float) and not v.is_integer():
                raise ValueError(f'RL parameter {k} must be an integer, got {v!r}')
            return t(v)
        params = cls(**{k: conv(k, v) for k, v in values.items()})
        for name in ('max_velocity', 'command_horizon', 'update_rate_hz', 'heartbeat_timeout',
                     'goal_tolerance', 'replan_deviation', 'retry_period', 'cruise_height',
                     'max_cruise_height', 'max_plans_per_tick', 'num_preferences'):
            if getattr(params, name) <= 0:
                raise ValueError(f'RL parameter {name} must be > 0')
        if params.keep_in_x < 0 or params.keep_in_y < 0:
            raise ValueError('RL parameters keep_in_x and keep_in_y must be >= 0 (0 disables the keep-in box)')
        if params.cruise_height > params.max_cruise_height:
            raise ValueError('RL parameter cruise_height must be <= max_cruise_height')
        return params


def _norm(a):
    return math.sqrt(sum(c * c for c in a))


def _sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def _round_or_none(x):
    return round(x, 3) if math.isfinite(x) else None


def patrol_altitude(drone_id: int) -> float:
    """Mirror of get_patrol_altitude() in patrol_controller.c (used for tasks with z >= -1)."""
    return -2.5 - drone_id * 1.0


def find_project_path(path: str) -> str:
    """Absolute paths as given; relative ones against $FACTORY_PATROL_ROOT, then the first parent of this
    file that contains config/algorithms (the factory_patrol_sim root), then the working directory."""
    if os.path.isabs(path):
        return path
    roots = []
    if os.environ.get('FACTORY_PATROL_ROOT'):
        roots.append(os.environ['FACTORY_PATROL_ROOT'])
    d = os.path.dirname(os.path.abspath(__file__))
    while d != os.path.dirname(d):
        if os.path.isdir(os.path.join(d, 'config', 'algorithms')):
            roots.append(d)
            break
        d = os.path.dirname(d)
    roots.append(os.getcwd())
    for r in roots:
        if os.path.exists(os.path.join(r, path)):
            return os.path.join(r, path)
    return os.path.join(roots[0], path)


class Polyline:
    """3D path with arc-length parametrisation (factory frame)."""

    def __init__(self, points):
        pts = [tuple(float(c) for c in points[0])]
        for p in points[1:]:
            p = tuple(float(c) for c in p)
            if _norm(_sub(p, pts[-1])) > 1e-6:
                pts.append(p)
        self.points = pts
        self.cum = [0.0]
        for a, b in zip(pts[:-1], pts[1:]):
            self.cum.append(self.cum[-1] + _norm(_sub(b, a)))
        self.length = self.cum[-1]

    def at(self, s):
        s = min(max(s, 0.0), self.length)
        for i in range(len(self.points) - 1):
            if s <= self.cum[i + 1] or i == len(self.points) - 2:
                seg = self.cum[i + 1] - self.cum[i]
                t = 0.0 if seg <= 0 else (s - self.cum[i]) / seg
                a, b = self.points[i], self.points[i + 1]
                return tuple(a[k] + t * (b[k] - a[k]) for k in range(3))
        return self.points[-1]

    def project(self, p, s_min=0.0, s_max=math.inf):
        """(arc length, distance) of the point of the path nearest to p with s in [s_min, s_max]."""
        best = (s_min, math.inf)
        for i in range(len(self.points) - 1):
            lo, hi = self.cum[i], self.cum[i + 1]
            if hi < s_min or lo > s_max or hi <= lo:
                continue
            a, b = self.points[i], self.points[i + 1]
            ab = _sub(b, a)
            t_lo, t_hi = max(0.0, (s_min - lo) / (hi - lo)), min(1.0, (s_max - lo) / (hi - lo))
            t = sum(x * y for x, y in zip(_sub(p, a), ab)) / ((hi - lo) ** 2)
            t = min(max(t, t_lo), t_hi)
            q = tuple(a[k] + t * ab[k] for k in range(3))
            d = _norm(_sub(p, q))
            if d < best[1]:
                best = (lo + t * (hi - lo), d)
        return best


@dataclass
class _Track:
    task_id: int
    path: Polyline = None
    s: float = 0.0
    failed_at_ns: int = 0
    attempts: int = 0
    hold: tuple = None              # hold point while the plan failed or while yielding
    yield_since_ns: int = 0
    yield_used_s: float = 0.0
    yielding_to: int = -1


class RLNavigationAlgorithm(CoordinationAlgorithm):
    """Trained PPO leg planner (rlpatrol) + path following through MovementCommands."""

    def __init__(self, config: dict):
        super().__init__(config)
        self.params = RLParams.from_dict(config.get('algorithm_params', {}) or {})
        self._obstacles: list[BoxObstacle] = list(config.get('obstacles', []) or [])
        self._num_drones = 0
        self._tasks_by_id: dict[int, TaskInfo] = {}
        self._drone_states = {}
        self._tracks: dict[int, _Track] = {}
        self._planner = None
        self._pending_events = []
        self._last_diag_ns = 0
        self._diag: dict[int, dict] = {}
        self._min_separation = math.inf
        self._min_obstacle_distance = math.inf
        self._motion_ref: dict[int, tuple] = {}     # drone -> (t_ns, position) for stall detection
        self._stall_reported: set = set()
        self._plan_count = 0

    def get_name(self) -> str:
        return 'RL (PPO leg planner, rl-nmopso-factory-patrol)'

    def get_update_period(self) -> float:
        return 1.0 / self.params.update_rate_hz

    def uses_external_navigation(self) -> bool:
        return True

    # --- set-up ---------------------------------------------------------------------------------------
    def _load_planner(self):
        p = self.params
        repo = find_project_path(p.repo_path)
        ckpt = find_project_path(p.checkpoint)
        if not os.path.isdir(os.path.join(repo, 'rlpatrol')):
            raise FileNotFoundError(f'RL repository not found (no rlpatrol/ in {repo}); set rl.repo_path')
        if not os.path.isfile(ckpt):
            raise FileNotFoundError(f'RL checkpoint not found: {ckpt}; set rl.checkpoint')
        if repo not in sys.path:
            sys.path.insert(0, repo)
        try:
            from rlpatrol.planner import LegPlanner
        except ImportError as e:
            raise ImportError(f'cannot import rlpatrol from {repo} ({e}); run the coordinator with the RL '
                              f'virtual environment (scripts/start_experiment.sh does this for --algorithm rl)')
        keep_in = ((-p.keep_in_x, p.keep_in_x, -p.keep_in_y, p.keep_in_y)
                   if p.keep_in_x > 0 and p.keep_in_y > 0 else None)
        return LegPlanner(ckpt, n_prefs=p.num_preferences, n_samples=p.samples_per_preference,
                          refine=p.refine_on_failure, device=p.device, threads=p.torch_threads, seed=p.seed,
                          keep_in=keep_in)

    def initialize(self, num_drones: int, tasks: list[TaskInfo], planner=None) -> None:
        self._num_drones = num_drones
        self.update_tasks(tasks)
        self._planner = planner if planner is not None else self._load_planner()
        unreachable = [t.task_id for t in tasks if self._planner.nearest_free((t.x, t.y)) is None]
        if unreachable:
            raise ValueError(f'tasks {unreachable} have no free point within '
                             f'{self._planner.free_r} m in the RL world model')
        self._pending_events.append(('rl_policy_loaded', {
            **self._planner.ckpt_info, 'device': str(self._planner.dev),
            'num_preferences': self.params.num_preferences,
            'samples_per_preference': self.params.samples_per_preference,
            'cruise_heights_m': [round(self.cruise_height(d), 3) for d in range(num_drones)],
            'tasks_projected': [t.task_id for t in tasks if not self._planner.is_free((t.x, t.y))],
        }))

    def update_tasks(self, tasks: list[TaskInfo]) -> None:
        super().update_tasks(tasks)
        self._tasks_by_id = {t.task_id: t for t in tasks}

    def reset(self) -> None:
        super().reset()
        self._tracks.clear()
        self._diag.clear()
        self._motion_ref.clear()
        self._stall_reported.clear()
        self._min_separation = math.inf
        self._min_obstacle_distance = math.inf

    def on_drone_failed(self, drone_id: int) -> None:
        self._drone_states.pop(drone_id, None)
        self._tracks.pop(drone_id, None)

    # --- geometry -------------------------------------------------------------------------------------
    def cruise_height(self, drone_id: int) -> float:
        p = self.params
        return min(p.cruise_height + drone_id * p.layer_separation, p.max_cruise_height)

    def task_z(self, drone_id: int, task: TaskInfo) -> float:
        return task.z if task.z < -1.0 else patrol_altitude(drone_id)

    def active_drones(self, timestamp_ns: int) -> dict:
        """Spawned (id < num_drones), heard within heartbeat_timeout, and not FAILED (as APF)."""
        timeout_ns = int(self.params.heartbeat_timeout * 1e9)
        return {d: s for d, s in self._drone_states.items()
                if 0 <= d < self._num_drones and s.state != DRONE_STATE_FAILED
                and timestamp_ns - s.timestamp_ns <= timeout_ns}

    def flight_path(self, drone_id, p, task, plan):
        """the 3D path flown (factory frame) from the planner's band path; see the module docstring."""
        cz = -self.cruise_height(drone_id)
        tz = self.task_z(drone_id, task)
        sx, sy = (float(c) for c in plan.start_free)
        gx, gy = (float(c) for c in plan.goal_free)
        pts = [tuple(p)]
        if math.hypot(sx - p[0], sy - p[1]) > 0.05:
            pts.append((sx, sy, p[2]))
        pts.append((sx, sy, cz))
        pts += [(float(x), float(y), cz) for x, y, _ in plan.path[1:-1]]
        pts += [(gx, gy, cz), (gx, gy, tz)]
        if math.hypot(gx - task.x, gy - task.y) > 0.05:
            pts.append((task.x, task.y, tz))
        return Polyline(pts)

    # --- core step ------------------------------------------------------------------------------------
    def _plan(self, drone_id, p, task, track, timestamp_ns, events, reason):
        self._plan_count += 1
        plan = self._planner.plan_route((p[0], p[1]), (task.x, task.y), seed=self.params.seed + self._plan_count)
        base = {'drone_id': drone_id, 'task_id': task.task_id, 'reason': reason,
                'plan_time_s': round(plan.plan_time_s, 4), 'method': plan.method,
                'candidates': plan.n_candidates, 'feasible_candidates': plan.n_feasible,
                'start': [round(p[0], 3), round(p[1], 3)], 'goal': [round(task.x, 3), round(task.y, 3)]}
        track.attempts += 1
        if not plan.feasible:
            track.path, track.failed_at_ns = None, timestamp_ns
            track.hold = track.hold or tuple(p)
            events.append(('rl_plan_failed', {**base, 'attempt': track.attempts, 'detail': plan.reason,
                                              'legs': plan.extra.get('legs', [])}))
            return
        track.path, track.s, track.hold, track.failed_at_ns = self.flight_path(drone_id, p, task, plan), 0.0, None, 0
        events.append(('rl_plan', {
            **base, 'F': [round(float(f), 6) if math.isfinite(f) else None for f in plan.F],
            'decomposed': bool(plan.extra.get('decomposed', False)),
            'sub_legs': len(plan.extra.get('legs', [])) or 1,
            'path_length_m': round(track.path.length, 3),
            'straight_distance_m': round(_norm(_sub(track.path.points[-1], p)), 3),
            'cruise_height_m': round(self.cruise_height(drone_id), 3),
            'waypoints': [[round(c, 3) for c in q] for q in track.path.points],
        }))

    def _yield(self, drone_id, p, target, positions, track, timestamp_ns, events):
        """True if the drone must hold for a lower-ID drone (see module docstring)."""
        prm = self.params
        used = track.yield_used_s + ((timestamp_ns - track.yield_since_ns) / 1e9 if track.yielding_to >= 0 else 0.0)
        if prm.yield_radius <= 0 or used >= prm.max_yield_time:
            if track.yielding_to >= 0:
                track.yield_used_s, track.yielding_to = used, -1
            return False
        step = _sub(target, p)
        for other, q in positions.items():
            if other >= drone_id:
                continue
            d = _sub(q, p)
            if _norm(d) < prm.yield_radius and sum(a * b for a, b in zip(step, d)) > 0:
                if track.yielding_to != other:
                    track.yielding_to, track.yield_since_ns = other, timestamp_ns
                    events.append(('rl_yield', {'drone_id': drone_id, 'to_drone': other, 'task_id': track.task_id,
                                                'distance': round(_norm(d), 3)}))
                return True
        if track.yielding_to >= 0:
            track.yield_used_s += (timestamp_ns - track.yield_since_ns) / 1e9
            track.yielding_to = -1
        return False

    def compute(self, timestamp_ns: int) -> AlgorithmResult:
        prm = self.params
        events, self._pending_events = self._pending_events, []
        active = self.active_drones(timestamp_ns)
        positions = {d: (s.x, s.y, s.z) for d, s in active.items()}
        ids = sorted(positions)
        for i, a in enumerate(ids):
            for b in ids[i + 1:]:
                self._min_separation = min(self._min_separation, _norm(_sub(positions[a], positions[b])))

        commands, plans_left = [], prm.max_plans_per_tick
        reach = prm.max_velocity * prm.command_horizon
        for drone_id, s in sorted(active.items()):
            task = self._tasks_by_id.get(s.current_task_id)
            p = positions[drone_id]
            if s.state != DRONE_STATE_PATROLLING or task is None:
                self._tracks.pop(drone_id, None)
                self._motion_ref.pop(drone_id, None)
                continue
            track = self._tracks.get(drone_id)
            if track is None or track.task_id != task.task_id:
                track = self._tracks[drone_id] = _Track(task_id=task.task_id)
                self._stall_reported.discard(drone_id)
                self._motion_ref[drone_id] = (timestamp_ns, p)

            if track.path is None:                               # (re)plan, rate-limited per tick
                due = track.failed_at_ns == 0 or timestamp_ns - track.failed_at_ns >= prm.retry_period * 1e9
                # first leg: wait until the controller's vertical takeoff is (nearly) done
                airborne = -p[2] >= min(-self.task_z(drone_id, task), self.cruise_height(drone_id)) - 0.3
                if due and plans_left > 0 and (airborne or track.attempts > 0):
                    plans_left -= 1
                    self._plan(drone_id, p, task, track, timestamp_ns, events,
                               'new_task' if track.attempts == 0 else 'retry')
            else:
                s_new, dev = track.path.project(p, track.s, track.s + 3.0)
                if dev > prm.replan_deviation and plans_left > 0:
                    plans_left -= 1
                    events.append(('rl_replan', {'drone_id': drone_id, 'task_id': task.task_id,
                                                 'deviation': round(dev, 3), 'progress_m': round(track.s, 3)}))
                    self._plan(drone_id, p, task, track, timestamp_ns, events, 'deviation')
                else:
                    track.s = max(track.s, s_new)

            if track.path is None:                               # no plan: hold, never fly unplanned
                if track.attempts:                               # failed plan: hold where it failed
                    track.hold = track.hold or p
                    target = track.hold
                else:                                            # still taking off (controller-driven)
                    target = p
                velocity = (0.0, 0.0, 0.0)
                cross = math.nan
            else:
                _, cross = track.path.project(p, track.s, track.s + 3.0)
                carrot = track.path.at(track.s + reach)
                step = _sub(carrot, p)
                n = _norm(step)
                if n > reach:
                    step = tuple(c * reach / n for c in step)
                target = tuple(p[k] + step[k] for k in range(3))
                if self._yield(drone_id, p, target, positions, track, timestamp_ns, events):
                    track.hold = track.hold or p
                    target = track.hold
                else:
                    track.hold = None
                velocity = tuple(c / prm.command_horizon for c in _sub(target, p))
            if not all(math.isfinite(c) for c in target):
                target, velocity = p, (0.0, 0.0, 0.0)            # never forward NaN/Inf

            commands.append(MovementCommand(
                drone_id=drone_id, task_id=task.task_id,
                target_x=target[0], target_y=target[1], target_z=target[2],
                velocity_x=velocity[0], velocity_y=velocity[1], velocity_z=velocity[2]))

            goal = (task.x, task.y, self.task_z(drone_id, task))
            goal_dist = _norm(_sub(goal, p))
            d_obs = min((_norm(_sub(p, b.closest_point(p))) for b in self._obstacles), default=math.inf)
            self._min_obstacle_distance = min(self._min_obstacle_distance, d_obs)
            others = [_norm(_sub(p, q)) for o, q in positions.items() if o != drone_id]
            stall = self._check_stall(drone_id, task.task_id, goal_dist, p, timestamp_ns)
            if stall:
                events.append(('rl_stall', stall))
            self._diag[drone_id] = {
                'drone_id': drone_id, 'task_id': task.task_id, 'goal_distance': round(goal_dist, 3),
                'has_plan': track.path is not None,
                'progress_m': round(track.s, 3) if track.path else None,
                'path_length_m': round(track.path.length, 3) if track.path else None,
                'cross_track_m': _round_or_none(cross),
                'command_speed': round(_norm(velocity), 3), 'yielding_to': track.yielding_to,
                'nearest_obstacle': _round_or_none(d_obs),
                'nearest_drone': _round_or_none(min(others, default=math.inf)),
            }

        if timestamp_ns - self._last_diag_ns >= int(prm.diagnostics_interval * 1e9):
            self._last_diag_ns = timestamp_ns
            for diag in self._diag.values():
                events.append(('rl_diagnostics', diag))
            events.append(('rl_clearance', {
                'active_drones': ids,
                'min_separation': _round_or_none(self._min_separation),
                'min_obstacle_distance': _round_or_none(self._min_obstacle_distance),
            }))
            self._diag = {}
            self._min_separation = math.inf
            self._min_obstacle_distance = math.inf
        return AlgorithmResult(movement_commands=commands, metadata={'events': events})

    def _check_stall(self, drone_id, task_id, goal_dist, p, timestamp_ns):
        """Once per goal: the drone moved less than stall_speed * stall_time during stall_time outside
        goal_tolerance (holding for a failed plan or yielding counts: the event says which)."""
        prm = self.params
        t0, p0 = self._motion_ref.get(drone_id, (timestamp_ns, p))
        if goal_dist <= prm.goal_tolerance or _norm(_sub(p, p0)) >= prm.stall_speed * prm.stall_time:
            self._motion_ref[drone_id] = (timestamp_ns, p)
            return None
        if drone_id in self._stall_reported or timestamp_ns - t0 < prm.stall_time * 1e9:
            return None
        self._stall_reported.add(drone_id)
        tr = self._tracks.get(drone_id)
        return {'drone_id': drone_id, 'task_id': task_id, 'goal_distance': round(goal_dist, 3),
                'x': round(p[0], 3), 'y': round(p[1], 3), 'z': round(p[2], 3),
                'has_plan': bool(tr and tr.path), 'yielding_to': tr.yielding_to if tr else -1}

    def get_metrics(self) -> dict:
        return {'num_obstacles': len(self._obstacles), 'plans': self._plan_count}
