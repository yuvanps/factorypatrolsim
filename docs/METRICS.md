# Benchmark metrics: definitions and how they are calculated

Every algorithm is measured by the same code from the same data: the drones' telemetry and the
events the controllers and the coordinator publish. No metric is computed by, or depends on, the
algorithm under test.

- Implementation: `factory_patrol_ws/src/patrol_coordinator/patrol_coordinator/metrics_summary.py`
  (class `RunMetrics`, no ROS dependency, unit-tested in `test/test_metrics_summary.py`), fed by the
  `metrics_collector` node.
- Output per run: `experiment_results/summaries/<run_id>_<algorithm>_<scenario>_<N>drones.csv` (one
  row, the columns below) and `experiment_results/<run_id>/metrics_detail.json` (per drone / per
  task breakdowns, every fault event).
- Comparison over many runs: `scripts/run_suite.sh` then `scripts/aggregate_suite.py` (mean and 95 %
  confidence interval per algorithm and scenario).

## Data sources

| Source | Topic | Rate | Used for |
|---|---|---|---|
| Ground-truth drone state | `/experiment/ground_truth_state` | 10 Hz per drone | position, battery, state: every position-based metric |
| Drone state (radio) | `/ground_station/drone_state` | 10 Hz per drone | fallback only, if a controller does not publish ground truth |
| Task completions | `/experiment/events` `task_completed` | per event | completion, workload, idleness, fault recovery |
| Task assignments | `/swarm/task_assignment` | per event | fault metrics (reassignment) |
| Fault and failure events | `/experiment/events` | per event | fault metrics |
| Compute statistics | `/experiment/events` `compute_stats` | every 5 s | compute time |
| Obstacle model | `config/environment/factory_obstacles.yaml` | once | obstacle clearance |

**Why a separate ground-truth topic:** `/ground_station/drone_state` is also the drones' radio:
it carries their heartbeats and positions to each other and to the coordinator. When a drone's radio
is lost (fault injection, below), it must disappear from that topic, but the measurement must not go
blind. So each controller also publishes its true state on an instrumentation topic that no
algorithm reads.

Positions are in the factory frame: x east, y north, z = −height (negative above the floor).
Timestamps are the collector's receive times.

## Windows

- **Mission window**: from the coordinator's `mission_started` event until every mission task has
  been completed at least once (one full patrol cycle), or until the run ends. Metrics 1–6 use it.
- **Evaluation window**: the mission window, or, when the scenario sets
  `metrics.observation_window_s`, the fixed window [start, start + that many seconds], so a run can be
  observed after its first patrol cycle (needed to see recovery from a fault). Metrics 7–11 use it.

## Sample validity (all position metrics)

From `metrics_summary.py`:
- The pre-odometry placeholder (0, 0, 0) is not a position.
- A jump implying more than 15 m/s is rejected, and integration restarts.
- A drone is permanently excluded from its first invalid sample, and the run notes say why:
  - state FAILED;
  - non-finite values;
  - outside the walls, below the floor or above the ceiling;
  - on the ground for 5 s while in a flying state.

**A crash shows up as an exclusion note.** `scripts/aggregate_suite.py` counts these as "runs with a
crashed drone".

## The metrics

### 1–6: mission metrics (mission window)

| # | Column | Definition |
|---|---|---|
| 1 | `mission_completion_time_s` | time from mission start to the completion that makes every task completed at least once; empty if the mission did not complete |
| 2 | `completed_tasks`, `task_completion_rate_percent` | distinct tasks completed at least once / total |
| 3 | `total_flight_distance_m` | sum over drones of the 3-D path length of consecutive valid samples |
| 4 | `drone_<i>_tasks`, `workload_min/max` | tasks whose first completion was by drone i |
| 5 | `minimum_inter_drone_distance_m` | minimum 3-D distance between any two drones, on a 20 Hz timeline with linear interpolation (no interpolation across gaps > 0.5 s) |
| 6 | `total_battery_consumed_percent` | sum over drones of first − last valid battery value |

### 7: obstacle safety (evaluation window)

On the same 20 Hz timeline, for every airborne drone (height > 0.5 m, so take-off pads on the floor
do not count), the clearance is the distance from the drone's centre to the nearest point of any
obstacle box: 0 inside a box. The boxes come from the scenario's `obstacles_file`, the same geometry
the algorithms use: racks, partition, machines, walls and ceiling. The floor is excluded.

| Column | Definition |
|---|---|
| `min_obstacle_clearance_m` | minimum clearance |
| `obstacle_near_miss_s` | drone-seconds with clearance < 0.6 m (twice the drone's half-size) |
| `obstacle_contacts` | number of episodes with clearance < 0.3 m: the airframe (x500, about 0.3 m half-size) touches an obstacle. Each continuous episode counts once |

### 8: drone-to-drone safety (evaluation window)

| Column | Definition |
|---|---|
| `separation_near_miss_s` | seconds during which any pair of drones is closer than 1.0 m |
| `separation_contacts` | episodes of a pair closer than 0.6 m (2 × 0.3 m: the airframes touch) |

### 9: patrol idleness (evaluation window)

Idleness of a task at time t is the time since its last visit, where a visit is a `task_completed`
by any drone. Before the first visit, it is t − start. This is the standard measure of
multi-robot patrolling (Machado et al., 2002).

| Column | Definition |
|---|---|
| `mean_task_idleness_s` | time average of the idleness over the window and all tasks: for each task, the sum of gap²/2 over the gaps between consecutive visits (including start → first visit and last visit → window end), divided by window length × number of tasks |
| `max_task_idleness_s` | the longest gap of any task: the worst coverage hole |
| `task_visits` | total completions in the window |

### 10: compute time (evaluation window)

| Column | Source | What is timed |
|---|---|---|
| `decision_time_mean/p95/max_ms` | coordinator, every `compute()` call | one coordination step of APF or RL: wall time of the algorithm's `compute()` (RL includes path planning when it plans) |
| `allocation_time_mean/max_ms` | drone 0's controller, every 100 ms | the on-board auction step: heartbeat check, task recycling, allocation (`CLOCK_MONOTONIC`) |

- **Reporting:** each source reports `compute_stats` every 5 s (count, mean, p95, max). The mean is
  weighted by count. The p95 is the largest per-report p95, a conservative upper bound.
- **What auction measures:** auction has no coordinator decision step: its navigation is the C state
  machine in each controller. So for auction only the allocation time exists. APF and RL also use
  this on-board allocation, so the allocation times are comparable across all three.
- **A blocking step stalls every drone.** The coordinator runs at 10 Hz on a single thread, so a step
  that takes longer than 100 ms delays the commands to every drone. The max column shows this.

### 11: communication loss (evaluation window; only in fault scenarios)

**Fault injection**: `faults.comm_loss: "drone:start_s:duration_s"` in the scenario, or
`--comm-loss` on the launcher, implemented in `patrol_controller.c` (`PATROL_COMM_LOSS`).

During the window, measured from the moment the drone receives the mission, the drone's radio is dead:
- **Outgoing:** it publishes nothing on the swarm and ground-station topics: no heartbeat or
  state, no bids, assignments or swarm status.
- **Incoming:** it ignores everything it would receive on them: peer states, bids, assignments,
  movement commands.
- **What still works:** it keeps flying on its own state machine. Instrumentation (events and
  ground-truth state) is not radio traffic and is unaffected.

How the system reacts:
- **Detection:** drone 0's controller runs the swarm heartbeat monitor and declares a silent drone
  FAILED after 5 s. Its tasks then go back to the auction. This is identical for every algorithm,
  since all use the on-board auction for allocation.
- **Drone behaviour during the loss:**
  - An auction drone keeps flying its own task loop.
  - An APF or RL drone receives no movement commands and holds its last setpoint.

Events:
- `comm_loss_started` / `comm_loss_ended`: from the affected drone;
- `peer_declared_failed` / `peer_recovered`: from drone 0's heartbeat monitor, when the heartbeat
  times out and when it comes back.

| Column | Definition |
|---|---|
| `comm_loss_drone`, `comm_loss_start_s`, `comm_loss_duration_s` | which drone, when, how long |
| `detection_s` | loss start → the drone is declared FAILED |
| `reassignment_s` | loss start → the first task the lost drone held (its last assignment before the loss) is assigned to another drone |
| `coverage_restored_s` | loss start → every task the lost drone held has been visited again by any drone. This includes the lost drone itself, if it kept flying its loop without radio |
| `rejoin_s` | link restored → its heartbeat is accepted again |
| `resume_s` | link restored → the lost drone completes a task again (back in coordinated service) |
| `min_separation_during_loss_m` | minimum distance between the lost drone and any other drone, from loss start to 10 s after the link returns: the collision risk while positions are not shared |

A column is empty when the event did not happen in the window. Two examples:
- `detection_s` is empty when the orchestrator (drone 0) itself loses its radio: nobody else
  monitors heartbeats.
- `resume_s` is empty if the drone did not complete another task before the window ended.

### 12–15: review-framework metrics (evaluation window)

These follow the ten core metrics of *A Comprehensive Performance Analysis Framework for Swarm
Coordination Algorithms in Industrial Drone Networks* (the review in the project root, §1). The
mapping of every framework metric to a column is in the table at the end of this section.

**12. Workload imbalance.** Two workloads per drone `w_i`, as the framework recommends: task
completions (every visit in the window) and flight distance.

| Column | Definition |
|---|---|
| `workload_imbalance_tasks`, `workload_imbalance_distance` | 1 − Jain index = 1 − (Σw)² / (N Σw²). 0 = equal; at most 1 − 1/N (0.67 for 3 drones) when one drone does everything |
| `workload_gini_tasks`, `workload_gini_distance` | Gini coefficient Σᵢ Σⱼ \|wᵢ − wⱼ\| / (2 N² w̄) |

Empty when no drone did any work. The auction caps every drone at ⌈M / N_healthy⌉ tasks, so the
*assignment* is balanced in every algorithm; imbalance comes from loop speed and from faults.

**13. Task reallocations.** `task_reallocations` = assignments that give a task to a different drone
than its previous assignee (giving it to the same drone again is not counted); `reallocations_per_min`
over the window.

**14. Allocation latency.** `alloc_first_assignment_s` = mission start → first `task_assigned`;
`alloc_all_assigned_s` = mission start → every task assigned at least once;
`allocation_to_mct_ratio` = `alloc_all_assigned_s` / MCT (completed runs). The framework flags a
ratio above 0.3 as coordination-bound. All three algorithms share the auction, whose 5 s wait for peer
states dominates the latency.

**15. Separation profile.** On the 20 Hz timeline, s(t) = minimum distance over all drone pairs.

| Column | Definition |
|---|---|
| `separation_p1_m`, `separation_p5_m` | 1st / 5th percentile of s(t) over the window |
| `separation_violations` | episodes with s(t) < d_safe = 1.0 m (the framework's safety radius) |

`metrics_detail.json` also holds `separation_histogram_m` (0.25 m bins, samples at 20 Hz).

**Communication-loss additions (metric 11).**

| Column | Definition |
|---|---|
| `reassign_after_detection_s` | detection → first reassignment (the framework's t_propagate + t_reassign) |
| `loss_safety_depth_m` | transient safety degradation depth: max(0, 1.0 m − min s(t)) over [loss start, loss end + 10 s], all pairs |
| `loss_safety_time_s` | time with s(t) < 1.0 m in the same window |

In the framework's terms: t_detect = `detection_s`, T_recovery = `coverage_restored_s`.

| Framework metric | Columns | Status |
|---|---|---|
| Mission completion time | `mission_completion_time_s` | measured |
| Task completion rate | `task_completion_rate_percent` | measured |
| Total flight distance | `total_flight_distance_m` | measured |
| Total energy consumed | `total_battery_consumed_percent` | modelled: the battery is a time counter (0.01 % per 100 ms) |
| Workload imbalance | `workload_imbalance_*`, `workload_gini_*` | measured |
| Allocation time | `alloc_*`, `allocation_to_mct_ratio`, `allocation_time_*_ms` | measured |
| Task reallocations | `task_reallocations`, `reallocations_per_min` | measured |
| Messages / bytes exchanged | – | not instrumented |
| Minimum inter-drone distance | `minimum_inter_drone_distance_m`, `separation_p1/p5_m`, `separation_violations` | measured |
| Failure recovery time | `detection_s`, `reassignment_s`, `reassign_after_detection_s`, `coverage_restored_s`, `rejoin_s`, `resume_s`, `loss_safety_*` | measured |

## Scenarios

| Scenario | Tasks | Purpose |
|---|---|---|
| `benchmark` | 6 tasks over racks and machines, no crossing routes | nominal patrol: efficiency |
| `safety_stress` | 8 tasks: collinear tasks under transit routes, a task beside the shared centre corridor, a low task inside a rack aisle | spatial conflicts: safety |
| `comm_loss` | benchmark tasks; drone 1's radio lost at t + 20 s for 15 s; observed for 150 s | fault detection and recovery |
| `comm_loss_orchestrator` | as above, but drone 0, the auction orchestrator, loses its radio | single point of failure |

## Known limitations

- **One model per algorithm.** The obstacle boxes are the same for every metric and for APF. RL plans
  on its own model of the same Gazebo world (cylinder chains for the NMOPSO cost), and auction does
  not use an obstacle model at all (fixed transit layers and a centre corridor). The clearance metric
  always uses the boxes.
- **Collector receive times.** Timestamps are the collector's receive times, so durations carry
  roughly 10–100 ms of message latency.
- **`drone_states.csv` is a periodic snapshot** (`metrics.state_snapshot_interval`, 1 s in
  `benchmark`) for plots. The metrics themselves use every 10 Hz sample.
- **Fault timing is relative to each drone receiving the mission,** which can differ from the
  collector's mission start by up to about 0.1 s.
