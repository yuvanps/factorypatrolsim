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

Extended metrics (EVALUATION window = the mission window above, or [start, start +
observation_window_s] when an observation window is set, so a run can be observed past its first
patrol cycle, e.g. to measure recovery from a fault; metrics 1-6 keep the mission window):
    7. obstacle safety               on the common 20 Hz timeline, per airborne drone (height > 0.5 m),
                                     distance from its centre to the nearest obstacle box of the
                                     scenario's obstacles_file (0 inside a box; the floor is excluded):
                                     min_obstacle_clearance_m; obstacle_near_miss_s = drone-seconds
                                     below NEAR_MISS_CLEARANCE_M; obstacle_contacts = episodes below
                                     DRONE_RADIUS_M (a contact: the airframe touches the box).
    8. drone-drone safety            separation_near_miss_s = seconds with any pair closer than
                                     NEAR_MISS_SEPARATION_M; separation_contacts = episodes of a pair
                                     closer than 2 * DRONE_RADIUS_M.
    9. patrol idleness               idleness of a task at time t = t - its last visit (task_completed,
                                     by any drone; t - start before the first visit).
                                     mean_task_idleness_s = its time average over the window and the
                                     tasks (the standard average idleness of multi-robot patrolling);
                                     max_task_idleness_s = its maximum (the worst coverage gap).
   10. compute time                  compute_stats events: source "coordinator" = wall time of the
                                     algorithm's compute() in the coordinator (APF, RL: one decision
                                     step), source "allocation" = the controllers' on-board auction
                                     allocation step (every algorithm uses it). Mean (weighted), p95
                                     (max of the per-report p95) and max, in ms.
   11. communication loss            from the fault-injection events (comm_loss_started / _ended of the
                                     affected drone, peer_declared_failed / peer_recovered of drone 0's
                                     heartbeat monitor) and the task assignments, for the first loss:
                                     detection_s  = loss start -> drone declared FAILED,
                                     reassignment_s = loss start -> first task the lost drone held is
                                                    assigned to another drone,
                                     coverage_restored_s = loss start -> every task the lost drone held
                                                    has been visited again (by any drone),
                                     rejoin_s     = loss end -> heartbeat accepted again,
                                     resume_s     = loss end -> the lost drone's next task completion,
                                     min_separation_during_loss_m = minimum separation between the lost
                                                    drone and any other from loss start to 10 s after
                                                    its end (flying without shared positions).
                                     Empty when the event did not happen in the window.
                                     In the terms of the review framework (docs/METRICS.md):
                                     t_detect = detection_s, t_propagate + t_reassign =
                                     reassign_after_detection_s, T_recovery = coverage_restored_s.
                                     Transient safety degradation, over [loss start, loss end + 10 s],
                                     all pairs: loss_safety_depth_m = max(0, D_SAFE_M - min swarm
                                     separation), loss_safety_time_s = time any pair is below D_SAFE_M.
   12. workload imbalance            per-drone workload over the evaluation window, two definitions:
                                     w = task completions (every visit) and w = flight distance.
                                     workload_imbalance_* = 1 - Jain index = 1 - (sum w)^2 / (N sum w^2)
                                     (0 = equal; at most 1 - 1/N, one drone does everything);
                                     workload_gini_* = sum_i sum_j |w_i - w_j| / (2 N^2 mean w).
   13. task reallocations            number of assignments that give a task to a different drone than
                                     its previous assignee (re-assignments to the same drone are not
                                     reallocations); task_reallocations and per minute of the window.
   14. allocation latency            alloc_first_assignment_s = mission start -> first task assignment,
                                     alloc_all_assigned_s = mission start -> every task assigned at
                                     least once; allocation_to_mct_ratio = alloc_all_assigned_s / MCT.
   15. separation profile            the swarm separation s(t) = min over pairs at each 20 Hz step:
                                     separation_p1_m / separation_p5_m = its 1st / 5th percentile
                                     over the window; separation_violations = episodes of s(t) < D_SAFE_M.

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

DRONE_RADIUS_M = 0.3            # x500 half-size; contact = centre closer than this to a box
NEAR_MISS_CLEARANCE_M = 0.6     # 2 x radius
NEAR_MISS_SEPARATION_M = 1.0
CLEARANCE_AIRBORNE_M = 0.5      # clearance only counts above this height (take-off pads are on the floor)
CLEARANCE_IGNORED = {'floor'}   # obstacle ids that are not obstacles for clearance
LOSS_AFTER_S = 10.0             # min_separation_during_loss_m: window extends this long after the loss
D_SAFE_M = 1.0                  # safety radius of the review framework (separation violations)


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
        self.observe_until_ns = None                 # evaluation window end (observation window)
        self.obstacles: list = []                    # boxes with .obstacle_id and .closest_point(p)
        self.visits: dict[int, list] = {}            # task_id -> [(t_ns, drone_id)] every completion
        self.assignments: list = []                  # (t_ns, task_id, drone_id)
        self.fault_events: list = []                 # (t_ns, event_type, data)
        self.compute: dict[str, list] = {}           # source -> [compute_stats data]

    # ------------------------------------------------------------------ inputs

    def start(self, t_ns: int, algorithm: str, scenario: str, num_drones: int, task_ids,
              observation_window_s: float = 0.0, obstacles=None):
        self.started = True
        self.start_ns = int(t_ns)
        self.algorithm, self.scenario = str(algorithm), str(scenario)
        self.num_drones = int(num_drones)
        self.task_ids = sorted({int(t) for t in task_ids})
        self.tracks = {d: _DroneTrack() for d in range(self.num_drones)}
        self.visits = {t: [] for t in self.task_ids}
        self.observe_until_ns = (self.start_ns + int(observation_window_s * 1e9)
                                 if observation_window_s and observation_window_s > 0 else None)
        self.obstacles = [o for o in (obstacles or []) if o.obstacle_id not in CLEARANCE_IGNORED]

    def _accepting(self, t_ns: int) -> bool:
        """inside the evaluation window (the observation window if set, else the mission window)"""
        if self.observe_until_ns is not None:
            return t_ns <= self.observe_until_ns
        return self.end_ns is None or t_ns <= self.end_ns

    @property
    def mission_complete(self) -> bool:
        return self.started and bool(self.task_ids) and len(self.first_completion) == len(self.task_ids)

    def on_task_completed(self, t_ns: int, drone_id: int, task_id: int):
        if not self.started or t_ns < self.start_ns:
            return
        if not 0 <= drone_id < self.num_drones or task_id not in self.task_ids:
            return
        if self._accepting(t_ns):
            self.visits[task_id].append((int(t_ns), int(drone_id)))
        if self.mission_complete:
            return
        if task_id not in self.first_completion:
            self.first_completion[task_id] = (int(t_ns), int(drone_id))
            if self.mission_complete:
                self.end_ns = int(t_ns)

    def on_assignment(self, t_ns: int, task_id: int, drone_id: int):
        if self.started and t_ns >= self.start_ns and self._accepting(t_ns):
            self.assignments.append((int(t_ns), int(task_id), int(drone_id)))

    def on_event(self, t_ns: int, event_type: str, data: dict):
        """fault-injection, failure-detection and compute_stats events (others are ignored)."""
        if not self.started or not isinstance(data, dict):
            return
        if event_type == 'compute_stats':
            if self._accepting(t_ns) and t_ns >= self.start_ns:
                self.compute.setdefault(str(data.get('source', 'unknown')), []).append(data)
        elif event_type in ('comm_loss_started', 'comm_loss_ended', 'peer_declared_failed', 'peer_recovered'):
            if t_ns >= self.start_ns and self._accepting(t_ns):
                self.fault_events.append((int(t_ns), event_type, data))

    def on_state(self, t_ns: int, drone_id: int, x, y, z, battery, state: int):
        if not self.started or t_ns < self.start_ns or not self._accepting(t_ns):
            return
        tr = self.tracks.get(drone_id)
        if tr is None or tr.invalid_since_ns is not None:
            return  # phantom drone, or drone already excluded after failure
        reason = self._invalid_reason(tr, t_ns, x, y, z, battery, state)
        if reason:
            tr.invalid_since_ns, tr.invalid_reason = int(t_ns), reason
            return
        in_mission = self.end_ns is None or t_ns <= self.end_ns   # battery: mission window only
        if tr.battery_first is None and in_mission:
            tr.battery_first = float(battery)
        if in_mission:
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

    # ------------------------------------------------------- extended metrics (7-11)

    def _eval_end(self, now_ns: int) -> int:
        if self.observe_until_ns is not None:
            return min(int(now_ns), self.observe_until_ns)
        return self._window_end(now_ns)

    def _positions(self, end_ns: int):
        """[(t, {drone: (x, y, z)})] on the 20 Hz timeline up to end_ns."""
        tracks = {d: [p for p in tr.samples if p[0] <= end_ns] for d, tr in self.tracks.items()}
        tracks = {d: s for d, s in tracks.items() if s}
        out, t = [], self.start_ns
        while t <= end_ns:
            pos = {d: self._interp(s, t) for d, s in tracks.items()}
            out.append((t, {d: p for d, p in pos.items() if p is not None}))
            t += self.SEPARATION_STEP_NS
        return out

    def safety(self, end_ns: int) -> dict:
        dt = self.SEPARATION_STEP_NS / 1e9
        best_clear, clear_by = None, {}
        near_obst = 0.0
        obst_contacts, in_contact = 0, set()
        near_sep = 0.0
        sep_contacts, pair_contact = 0, set()
        sep_series, violations, violating = [], 0, False    # swarm separation s(t), D_SAFE_M episodes
        for t, pos in self._positions(end_ns):
            for d, p in pos.items():
                if not self.obstacles or -p[2] <= CLEARANCE_AIRBORNE_M:
                    in_contact.discard(d)
                    continue
                c = min(math.dist(p, o.closest_point(p)) for o in self.obstacles)
                clear_by[d] = c if d not in clear_by else min(clear_by[d], c)
                if best_clear is None or c < best_clear:
                    best_clear = c
                if c < NEAR_MISS_CLEARANCE_M:
                    near_obst += dt
                if c < DRONE_RADIUS_M:
                    if d not in in_contact:
                        obst_contacts += 1
                        in_contact.add(d)
                else:
                    in_contact.discard(d)
            ids = sorted(pos)
            any_near = False
            for i in range(len(ids)):
                for j in range(i + 1, len(ids)):
                    dd = math.dist(pos[ids[i]], pos[ids[j]])
                    any_near |= dd < NEAR_MISS_SEPARATION_M
                    key = (ids[i], ids[j])
                    if dd < 2 * DRONE_RADIUS_M:
                        if key not in pair_contact:
                            sep_contacts += 1
                            pair_contact.add(key)
                    else:
                        pair_contact.discard(key)
            if any_near:
                near_sep += dt
            if len(ids) >= 2:
                swarm = min(math.dist(pos[ids[i]], pos[ids[j]])
                            for i in range(len(ids)) for j in range(i + 1, len(ids)))
                sep_series.append((t, swarm))
                if swarm < D_SAFE_M:
                    if not violating:
                        violations += 1
                    violating = True
                else:
                    violating = False
        return {'min_obstacle_clearance_m': best_clear, 'per_drone_min_clearance_m': clear_by,
                'obstacle_near_miss_s': near_obst, 'obstacle_contacts': obst_contacts,
                'separation_near_miss_s': near_sep, 'separation_contacts': sep_contacts,
                'separation_series': sep_series, 'separation_violations': violations}

    def idleness(self, end_ns: int) -> dict:
        """time-average and maximum task idleness over [start, end] (visits = every completion)."""
        T = (end_ns - self.start_ns) / 1e9
        if T <= 0 or not self.task_ids:
            return {'mean_task_idleness_s': None, 'max_task_idleness_s': None, 'per_task_max_idleness_s': {}}
        total, worst, per = 0.0, 0.0, {}
        for task in self.task_ids:
            times = [self.start_ns] + sorted(t for t, _ in self.visits.get(task, []) if t <= end_ns) + [end_ns]
            gaps = [(b - a) / 1e9 for a, b in zip(times, times[1:])]
            total += sum(g * g / 2 for g in gaps)
            per[task] = max(gaps)
            worst = max(worst, per[task])
        return {'mean_task_idleness_s': total / (T * len(self.task_ids)), 'max_task_idleness_s': worst,
                'per_task_max_idleness_s': per}

    def compute_time(self) -> dict:
        out = {}
        for src, reports in self.compute.items():
            n = sum(int(r.get('n', 0)) for r in reports)
            if not n:
                continue
            out[src] = {'mean_ms': sum(float(r['mean_ms']) * int(r['n']) for r in reports) / n,
                        'p95_ms': max(float(r.get('p95_ms', r['max_ms'])) for r in reports),
                        'max_ms': max(float(r['max_ms']) for r in reports), 'n': n}
        return out

    def _min_separation_of(self, drone: int, t_a: int, t_b: int):
        tr = self.tracks.get(drone)
        if tr is None:
            return None
        best, t = None, t_a
        while t <= t_b:
            p = self._interp(tr.samples, t)
            if p is not None:
                for d, other in self.tracks.items():
                    if d == drone:
                        continue
                    q = self._interp(other.samples, t)
                    if q is not None:
                        dd = math.dist(p, q)
                        best = dd if best is None or dd < best else best
            t += self.SEPARATION_STEP_NS
        return best

    def comm_loss(self, end_ns: int) -> dict:
        """metric 11 for the first communication loss in the window ({} if none)."""
        starts = [(t, int(d.get('drone_id', -1))) for t, e, d in self.fault_events if e == 'comm_loss_started']
        if not starts:
            return {}
        t0, lost = starts[0]
        t1 = next((t for t, e, d in self.fault_events if e == 'comm_loss_ended' and int(d.get('drone_id', -1)) == lost
                   and t >= t0), None)
        sec = lambda a, b: round((b - a) / 1e9, 3) if a is not None and b is not None else None
        detected = next((t for t, e, d in self.fault_events if e == 'peer_declared_failed'
                         and int(d.get('drone_id', -1)) == lost and t >= t0), None)
        held = {}                                         # task -> drone, last assignment before the loss
        for t, task, d in sorted(self.assignments):
            if t <= t0:
                held[task] = d
        if not held:                                      # no assignment seen: the lost drone's first completions
            held = {task: d for task, (_, d) in self.first_completion.items()}
        lost_tasks = sorted(task for task, d in held.items() if d == lost)
        reassigned = next((t for t, task, d in sorted(self.assignments)
                           if t > t0 and task in lost_tasks and d != lost), None)
        restored = None
        if lost_tasks:
            firsts = [min((t for t, _ in self.visits.get(task, []) if t > t0), default=None) for task in lost_tasks]
            restored = max(firsts) if all(f is not None for f in firsts) else None
        rejoined = (next((t for t, e, d in self.fault_events if e == 'peer_recovered'
                          and int(d.get('drone_id', -1)) == lost and t >= t1), None) if t1 is not None else None)
        resumed = (min((t for task in self.task_ids for t, d in self.visits.get(task, []) if d == lost and t > t1),
                       default=None) if t1 is not None else None)
        sep_end = min(end_ns, (t1 if t1 is not None else end_ns) + int(LOSS_AFTER_S * 1e9))
        min_sep = self._min_separation_of(lost, t0, sep_end)
        return {'comm_loss_drone': lost, 'comm_loss_start_s': sec(self.start_ns, t0),
                'comm_loss_duration_s': sec(t0, t1), 'detection_s': sec(t0, detected),
                'reassignment_s': sec(t0, reassigned), 'coverage_restored_s': sec(t0, restored),
                'reassign_after_detection_s': sec(detected, reassigned) if reassigned and detected else None,
                'rejoin_s': sec(t1, rejoined), 'resume_s': sec(t1, resumed),
                'min_separation_during_loss_m': round(min_sep, 3) if min_sep is not None else None,
                'lost_drone_tasks': lost_tasks}

    @staticmethod
    def _imbalance(w: list) -> tuple:
        """(1 - Jain index, Gini coefficient) of the workloads w; (None, None) if all are zero."""
        n, total = len(w), sum(w)
        if n == 0 or total <= 0:
            return None, None
        jain = total * total / (n * sum(x * x for x in w))
        gini = sum(abs(a - b) for a in w for b in w) / (2 * n * total)
        return 1.0 - jain, gini

    def workload(self, end_ns: int) -> dict:
        """metric 12: imbalance of task completions and of flight distance over [start, end_ns]."""
        tasks = {d: 0 for d in range(self.num_drones)}
        for v in self.visits.values():
            for t, d in v:
                if t <= end_ns:
                    tasks[d] += 1
        dist = self.per_drone_distance(end_ns)
        wi_t, gini_t = self._imbalance([tasks[d] for d in sorted(tasks)])
        wi_d, gini_d = self._imbalance([dist.get(d, 0.0) for d in sorted(tasks)])
        return {'per_drone_task_completions': tasks, 'workload_imbalance_tasks': wi_t,
                'workload_gini_tasks': gini_t, 'workload_imbalance_distance': wi_d, 'workload_gini_distance': gini_d}

    def reallocations(self, end_ns: int) -> dict:
        """metric 13: assignments that move a task to a different drone."""
        owner, count = {}, 0
        for t, task, d in sorted(self.assignments):
            if t > end_ns:
                break
            if task in owner and owner[task] != d:
                count += 1
            owner[task] = d
        minutes = (end_ns - self.start_ns) / 60e9
        return {'task_reallocations': count, 'reallocations_per_min': count / minutes if minutes > 0 else None}

    def allocation_latency(self) -> dict:
        """metric 14: mission start -> first assignment / every task assigned once."""
        seen, first, all_t = set(), None, None
        for t, task, _ in sorted(self.assignments):
            first = t if first is None else first
            seen.add(task)
            if all_t is None and seen >= set(self.task_ids):
                all_t = t
        sec = lambda t: (t - self.start_ns) / 1e9 if t is not None else None
        mct = (self.end_ns - self.start_ns) / 1e9 if self.mission_complete else None
        a = sec(all_t)
        return {'alloc_first_assignment_s': sec(first), 'alloc_all_assigned_s': a,
                'allocation_to_mct_ratio': a / mct if a is not None and mct else None}

    @staticmethod
    def _histogram(xs: list, width: float = 0.25, top: float = 10.0) -> dict:
        """seconds-weighted histogram of s(t): bin lower edge (m) -> samples (20 Hz), last bin open"""
        out = {}
        for x in xs:
            b = round(min(math.floor(x / width) * width, top), 2)
            out[b] = out.get(b, 0) + 1
        return dict(sorted(out.items()))

    @staticmethod
    def _percentile(xs: list, q: float):
        """q-th percentile (0-100) with linear interpolation; None for no data."""
        if not xs:
            return None
        xs = sorted(xs)
        k = (len(xs) - 1) * q / 100.0
        lo = int(math.floor(k))
        hi = min(lo + 1, len(xs) - 1)
        return xs[lo] + (xs[hi] - xs[lo]) * (k - lo)

    def loss_safety(self, series: list, loss: dict) -> dict:
        """transient safety degradation (all pairs) over [loss start, loss end + LOSS_AFTER_S]."""
        if not loss or loss.get('comm_loss_start_s') is None:
            return {}
        t0 = self.start_ns + int(loss['comm_loss_start_s'] * 1e9)
        dur = loss.get('comm_loss_duration_s')
        t1 = t0 + int((dur + LOSS_AFTER_S) * 1e9) if dur is not None else math.inf   # link never back: to the end
        win = [s for t, s in series if t0 <= t <= t1]
        if not win:
            return {}
        dt = self.SEPARATION_STEP_NS / 1e9
        return {'loss_safety_depth_m': max(0.0, D_SAFE_M - min(win)),
                'loss_safety_time_s': dt * sum(1 for s in win if s < D_SAFE_M)}

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

        ev_end = self._eval_end(now_ns)
        r3 = lambda v: round(v, 3) if v is not None else ''
        safe = self.safety(ev_end)
        idle = self.idleness(ev_end)
        comp = self.compute_time()
        loss = self.comm_loss(ev_end)
        row.update({
            'evaluation_window_s': round((ev_end - self.start_ns) / 1e9, 3),
            'min_obstacle_clearance_m': r3(safe['min_obstacle_clearance_m']),
            'obstacle_near_miss_s': round(safe['obstacle_near_miss_s'], 2),
            'obstacle_contacts': safe['obstacle_contacts'],
            'separation_near_miss_s': round(safe['separation_near_miss_s'], 2),
            'separation_contacts': safe['separation_contacts'],
            'mean_task_idleness_s': r3(idle['mean_task_idleness_s']),
            'max_task_idleness_s': r3(idle['max_task_idleness_s']),
            'task_visits': sum(len(v) for v in self.visits.values()),
            'decision_time_mean_ms': r3(comp.get('coordinator', {}).get('mean_ms')),
            'decision_time_p95_ms': r3(comp.get('coordinator', {}).get('p95_ms')),
            'decision_time_max_ms': r3(comp.get('coordinator', {}).get('max_ms')),
            'allocation_time_mean_ms': r3(comp.get('allocation', {}).get('mean_ms')),
            'allocation_time_max_ms': r3(comp.get('allocation', {}).get('max_ms')),
        })
        for k in ('comm_loss_drone', 'comm_loss_start_s', 'comm_loss_duration_s', 'detection_s', 'reassignment_s',
                  'reassign_after_detection_s', 'coverage_restored_s', 'rejoin_s', 'resume_s',
                  'min_separation_during_loss_m'):
            v = loss.get(k)
            row[k] = '' if v is None else v
        work = self.workload(ev_end)
        realloc = self.reallocations(ev_end)
        alloc = self.allocation_latency()
        seps = [v for _, v in safe['separation_series']]
        lsafe = self.loss_safety(safe['separation_series'], loss)
        row.update({
            'workload_imbalance_tasks': r3(work['workload_imbalance_tasks']),
            'workload_imbalance_distance': r3(work['workload_imbalance_distance']),
            'workload_gini_tasks': r3(work['workload_gini_tasks']),
            'workload_gini_distance': r3(work['workload_gini_distance']),
            'task_reallocations': realloc['task_reallocations'],
            'reallocations_per_min': r3(realloc['reallocations_per_min']),
            'alloc_first_assignment_s': r3(alloc['alloc_first_assignment_s']),
            'alloc_all_assigned_s': r3(alloc['alloc_all_assigned_s']),
            'allocation_to_mct_ratio': r3(alloc['allocation_to_mct_ratio']),
            'separation_p1_m': r3(self._percentile(seps, 1)),
            'separation_p5_m': r3(self._percentile(seps, 5)),
            'separation_violations': safe['separation_violations'],
            'loss_safety_depth_m': r3(lsafe.get('loss_safety_depth_m')),
            'loss_safety_time_s': r3(lsafe.get('loss_safety_time_s')),
        })
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
            'per_drone_min_obstacle_clearance_m': {d: round(v, 3) for d, v in safe['per_drone_min_clearance_m'].items()},
            'per_task_max_idleness_s': {t: round(v, 3) for t, v in idle['per_task_max_idleness_s'].items()},
            'task_visits': {t: [{'t_s': round((ts - self.start_ns) / 1e9, 3), 'drone_id': d} for ts, d in v]
                            for t, v in self.visits.items()},
            'compute_time_ms': {k: {kk: round(vv, 4) for kk, vv in v.items()} for k, v in comp.items()},
            'comm_loss': loss,
            'per_drone_task_completions': work['per_drone_task_completions'],
            'separation_histogram_m': self._histogram(seps),
            'fault_events': [{'t_s': round((t - self.start_ns) / 1e9, 3), 'event': e, **d} for t, e, d in self.fault_events],
        }
        return row, detail
