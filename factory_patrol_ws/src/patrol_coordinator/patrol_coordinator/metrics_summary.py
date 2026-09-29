"""Preliminary per-run benchmark metrics (algorithm-independent, no ROS dependency).

The metrics collector feeds this class with the same inputs for every algorithm:

    start(...)              mission_started event (coordinator) + Mission task list
    on_state(...)           every /ground_station/drone_state message (10 Hz per drone)
    on_task_completed(...)  'task_completed' events published by the patrol controllers at the
                            exact moment their mission logic sets task->completed
    finalize(...)           -> one summary row (dict)

Metrics (window = [mission start, mission end]):
    1. mission_completion_time_s     end - start, where end = the task_completed event that
                                     completes the LAST not-yet-completed mission task
                                     (every task completed at least once = one patrol cycle).
                                     Empty if the mission did not complete.
    2. task completion               completed_tasks = distinct mission tasks completed >= once;
                                     rate = completed / total * 100.
    3. total_flight_distance_m       sum over drones of sum |p_k - p_(k-1)| (3D) over consecutive
                                     VALID samples inside the window.
    4. per-drone workload            drone_<i>_tasks = number of mission tasks whose FIRST
                                     completion was performed by drone i (sums to completed_tasks).
    5. minimum_inter_drone_distance  min over time of the 3D distance between every pair of
                                     valid drones, evaluated on a common 20 Hz timeline with
                                     linear interpolation of each drone's samples.
    6. battery consumption           per drone: first valid battery sample in the window minus
                                     the last valid one; total = sum over drones that have both.

Sample validity.
  Pre-odometry placeholder: a patrol controller publishes DroneState with its initial position
  (0.0, 0.0, 0.0) until its first PX4 odometry arrives (patrol_controller.c: current_x/y/z are
  initialised to 0 and published while position_received is false). A sample at EXACTLY the
  origin is therefore "no position yet": it is not used for distance or separation (the first
  real sample becomes the reference), but its battery value is real and is used.
  Isolated impossible transitions (rejected, NOT a failure): if the implied speed between the
  previous accepted sample and a new one exceeds max_speed_mps, that TRANSITION is rejected:
  no distance is counted across it, the new sample becomes the reference of a new track
  segment, and collection continues. Separation is never interpolated across a segment
  boundary. Every rejected transition is kept (raw values) in the run detail.
  Observed cause: a controller publishes DroneState with its initial placeholder position
  (0, 0, 0) until its first PX4 odometry arrives; when odometry starts after the mission start,
  the placeholder -> real-position step looks like a multi-metre jump in 0.1 s.
  Speed uses dt >= min_dt_s because timestamps are collector receipt times (10 Hz telemetry
  delivered back-to-back would otherwise give dt ~ 0).

  Permanent exclusion (post-failure garbage). A drone's samples are used until the FIRST of the
  following; from then on it contributes no distance, separation or battery samples (its
  completed tasks still count, its pre-failure distance / last valid battery value are kept):
    - state == FAILED (4)
    - non-finite position/battery
    - position outside the factory walls / below the floor / above the ceiling
    - after having been airborne, below grounded_height_m for >= grounded_timeout_s while its
      state still says PATROLLING or INSPECTING (crashed but still publishing)
Phantom drones (drone_id >= num_drones) are ignored entirely.
"""

import math
from dataclasses import dataclass, field

STATE_PATROLLING = 1
STATE_INSPECTING = 2
STATE_FAILED = 4


@dataclass
class ValidityLimits:
    x_limit: float = 15.0          # factory walls at |x| = 15 m
    y_limit: float = 10.0          # factory walls at |y| = 10 m
    floor_z: float = 0.5           # z > +0.5 (NED-like) = below the floor
    ceiling_z: float = -12.5       # z < -12.5 = above the 12 m ceiling barrier
    max_speed_mps: float = 15.0    # x500 cannot exceed this; faster transition = rejected
    min_dt_s: float = 0.05         # floor on dt for the speed test (receipt-time jitter)
    airborne_height_m: float = 1.0
    grounded_height_m: float = 0.3
    grounded_timeout_s: float = 5.0


@dataclass
class _DroneTrack:
    samples: list = field(default_factory=list)   # (t_ns, x, y, z, battery, segment) accepted samples
    segment: int = 0
    placeholder_samples: int = 0
    battery_first: float | None = None   # from every non-excluded sample, incl. placeholders
    battery_last: float | None = None
    rejected: list = field(default_factory=list)  # raw details of rejected transitions
    invalid_since_ns: int | None = None
    invalid_reason: str = ''
    airborne: bool = False
    grounded_since_ns: int | None = None


class RunMetrics:
    SEPARATION_STEP_NS = 50_000_000     # 20 Hz evaluation timeline
    SEPARATION_MAX_GAP_NS = 500_000_000  # do not interpolate across telemetry gaps > 0.5 s

    def __init__(self, limits: ValidityLimits | None = None):
        self.limits = limits or ValidityLimits()
        self.started = False
        self.start_ns = None
        self.end_ns = None
        self.algorithm = ''
        self.scenario = ''
        self.num_drones = 0
        self.task_ids: list[int] = []
        self.first_completion: dict[int, tuple[int, int]] = {}  # task_id -> (t_ns, drone_id)
        self.tracks: dict[int, _DroneTrack] = {}

    # ------------------------------------------------------------------ inputs

    def start(self, t_ns: int, algorithm: str, scenario: str, num_drones: int, task_ids):
        self.started = True
        self.start_ns = int(t_ns)
        self.algorithm, self.scenario = str(algorithm), str(scenario)
        self.num_drones = int(num_drones)
        self.task_ids = sorted({int(t) for t in task_ids})
        self.tracks = {d: _DroneTrack() for d in range(self.num_drones)}

    @property
    def mission_complete(self) -> bool:
        return self.started and bool(self.task_ids) and len(self.first_completion) == len(self.task_ids)

    def on_task_completed(self, t_ns: int, drone_id: int, task_id: int):
        if not self.started or self.mission_complete or t_ns < self.start_ns:
            return
        if not 0 <= drone_id < self.num_drones or task_id not in self.task_ids:
            return
        if task_id not in self.first_completion:
            self.first_completion[task_id] = (int(t_ns), int(drone_id))
            if self.mission_complete:
                self.end_ns = int(t_ns)

    def on_state(self, t_ns: int, drone_id: int, x, y, z, battery, state: int):
        if not self.started or t_ns < self.start_ns or self.end_ns is not None:
            return
        tr = self.tracks.get(drone_id)
        if tr is None or tr.invalid_since_ns is not None:
            return  # phantom drone, or drone already excluded after failure
        reason = self._invalid_reason(tr, t_ns, x, y, z, battery, state)
        if reason:
            tr.invalid_since_ns, tr.invalid_reason = int(t_ns), reason
            return
        if tr.battery_first is None:
            tr.battery_first = float(battery)
        tr.battery_last = float(battery)
        if x == 0.0 and y == 0.0 and z == 0.0:
            tr.placeholder_samples += 1   # controller has no odometry yet: no position information
            return
        if tr.samples and t_ns <= tr.samples[-1][0]:
            return  # out-of-order / duplicate timestamp: cannot be used for integration
        if tr.samples:
            t0, x0, y0, z0 = tr.samples[-1][:4]
            dt = (t_ns - t0) / 1e9
            jump = math.dist((x, y, z), (x0, y0, z0))
            speed = jump / max(dt, self.limits.min_dt_s)
            if dt < 1.0 and speed > self.limits.max_speed_mps:
                # Isolated impossible transition: do not integrate it; start a new segment
                # with this sample as the new reference and keep collecting.
                tr.segment += 1
                tr.rejected.append({
                    't_s': round((t_ns - self.start_ns) / 1e9, 3), 'dt_s': round(dt, 4),
                    'jump_m': round(jump, 3), 'implied_speed_mps': round(speed, 1),
                    'from': [round(v, 3) for v in (x0, y0, z0)],
                    'to': [round(float(v), 3) for v in (x, y, z)],
                })
        tr.samples.append((int(t_ns), float(x), float(y), float(z), float(battery), tr.segment))

    def _invalid_reason(self, tr, t_ns, x, y, z, battery, state) -> str:
        L = self.limits
        if state == STATE_FAILED:
            return 'state FAILED'
        if not all(math.isfinite(v) for v in (x, y, z, battery)):
            return 'non-finite telemetry'
        if abs(x) > L.x_limit or abs(y) > L.y_limit or z > L.floor_z or z < L.ceiling_z:
            return f'position outside factory ({x:.1f},{y:.1f},{z:.1f})'
        height = -z
        if height > L.airborne_height_m:
            tr.airborne = True
        if tr.airborne and height < L.grounded_height_m and state in (STATE_PATROLLING, STATE_INSPECTING):
            if tr.grounded_since_ns is None:
                tr.grounded_since_ns = int(t_ns)
            elif (t_ns - tr.grounded_since_ns) / 1e9 >= L.grounded_timeout_s:
                return 'on the ground while in a flying state (crashed)'
        else:
            tr.grounded_since_ns = None
        return ''

    # ----------------------------------------------------------------- metrics

    def _window_end(self, now_ns: int) -> int:
        return self.end_ns if self.end_ns is not None else int(now_ns)

    def per_drone_distance(self, end_ns: int) -> dict[int, float]:
        out = {}
        for d, tr in self.tracks.items():
            s = [p for p in tr.samples if p[0] <= end_ns]
            out[d] = sum(math.dist(a[1:4], b[1:4]) for a, b in zip(s, s[1:]) if a[5] == b[5])
        return out

    def per_drone_battery(self, end_ns: int) -> dict[int, float | None]:
        # Samples are only accepted up to end_ns (on_state ignores later ones), so first/last
        # battery values already lie inside the metric window.
        return {d: (tr.battery_first - tr.battery_last) if tr.battery_first is not None else None
                for d, tr in self.tracks.items()}

    @staticmethod
    def _interp(samples, t):
        """Linear interpolation of (x,y,z) at t; None outside the samples or across a gap."""
        lo, hi = 0, len(samples) - 1
        if hi < 0 or t < samples[0][0] or t > samples[-1][0]:
            return None
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if samples[mid][0] <= t:
                lo = mid
            else:
                hi = mid
        a, b = samples[lo], samples[hi]
        if a[0] == t or hi == lo:
            return a[1:4]
        if b[0] - a[0] > RunMetrics.SEPARATION_MAX_GAP_NS or a[5] != b[5]:
            return None  # telemetry gap or rejected (impossible) transition
        f = (t - a[0]) / (b[0] - a[0])
        return tuple(a[i] + f * (b[i] - a[i]) for i in (1, 2, 3))

    def minimum_separation(self, end_ns: int) -> float | None:
        tracks = {d: [p for p in tr.samples if p[0] <= end_ns] for d, tr in self.tracks.items()}
        tracks = {d: s for d, s in tracks.items() if len(s) >= 2}
        if len(tracks) < 2:
            return None
        best = None
        t = self.start_ns
        while t <= end_ns:
            pos = [p for p in (self._interp(s, t) for s in tracks.values()) if p is not None]
            for i in range(len(pos)):
                for j in range(i + 1, len(pos)):
                    dd = math.dist(pos[i], pos[j])
                    if best is None or dd < best:
                        best = dd
            t += self.SEPARATION_STEP_NS
        return best

    def finalize(self, now_ns: int, run_id: str, timestamp_iso: str, status: str | None = None) -> tuple[dict, dict]:
        """Return (summary_row, detail). status defaults to 'completed' or 'incomplete'."""
        end = self._window_end(now_ns)
        if status is None:
            status = 'completed' if self.mission_complete else 'incomplete'
        dist = self.per_drone_distance(end)
        batt = self.per_drone_battery(end)
        workload = {d: 0 for d in range(self.num_drones)}
        for _, (_, d) in self.first_completion.items():
            workload[d] += 1
        total = len(self.task_ids)
        completed = len(self.first_completion)
        min_sep = self.minimum_separation(end)
        batt_known = [v for v in batt.values() if v is not None]
        notes = []
        for d, tr in sorted(self.tracks.items()):
            if tr.invalid_since_ns is not None and tr.invalid_since_ns <= end:
                notes.append(f'drone {d} excluded from t+{(tr.invalid_since_ns - self.start_ns) / 1e9:.1f}s '
                             f'({tr.invalid_reason})')
            if batt[d] is None:
                notes.append(f'drone {d} no valid battery samples')
            if tr.rejected:
                notes.append(f'drone {d}: {len(tr.rejected)} impossible transition(s) rejected '
                             f'(first at t+{tr.rejected[0]["t_s"]:.1f}s, {tr.rejected[0]["jump_m"]:.1f} m)')
        if self.num_drones < 2:
            notes.append('min separation N/A (single drone)')

        row = {
            'run_id': run_id,
            'timestamp': timestamp_iso,
            'algorithm': self.algorithm,
            'scenario': self.scenario,
            'num_drones': self.num_drones,
            'status': status,
            'total_tasks': total,
            'completed_tasks': completed,
            'task_completion_rate_percent': round(100.0 * completed / total, 2) if total else '',
            'mission_completion_time_s': round((self.end_ns - self.start_ns) / 1e9, 3) if self.mission_complete else '',
            'total_flight_distance_m': round(sum(dist.values()), 3),
            'minimum_inter_drone_distance_m': round(min_sep, 3) if min_sep is not None else 'N/A',
            'total_battery_consumed_percent': round(sum(batt_known), 2) if batt_known else '',
            'workload_min': min(workload.values()) if workload else '',
            'workload_max': max(workload.values()) if workload else '',
        }
        for d in range(self.num_drones):
            row[f'drone_{d}_tasks'] = workload[d]
        row['notes'] = '; '.join(notes)

        detail = {
            'run_id': run_id, 'status': status,
            'window_s': round((end - self.start_ns) / 1e9, 3),
            'per_drone_distance_m': {d: round(v, 3) for d, v in dist.items()},
            'per_drone_battery_consumed_percent': {d: (round(v, 2) if v is not None else None) for d, v in batt.items()},
            'per_drone_valid_samples': {d: len(tr.samples) for d, tr in self.tracks.items()},
            'per_drone_placeholder_samples': {d: tr.placeholder_samples for d, tr in self.tracks.items()},
            'rejected_transitions': {d: tr.rejected for d, tr in self.tracks.items() if tr.rejected},
            'first_completion': {t: {'drone_id': d, 't_s': round((ts - self.start_ns) / 1e9, 3)}
                                 for t, (ts, d) in sorted(self.first_completion.items())},
            'excluded': {d: {'from_s': round((tr.invalid_since_ns - self.start_ns) / 1e9, 3), 'reason': tr.invalid_reason}
                         for d, tr in self.tracks.items() if tr.invalid_since_ns is not None},
        }
        return row, detail
