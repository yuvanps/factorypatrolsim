"""Deterministic tests for the preliminary run metrics (no ROS needed)."""

import pytest

from patrol_coordinator.metrics_summary import RunMetrics

S = 1_000_000_000  # 1 s in ns
T0 = 100 * S


def started(num_drones=2, tasks=(101, 102, 103)):
    m = RunMetrics()
    m.start(T0, 'auction', 'benchmark', num_drones, tasks)
    return m


def test_distance_accumulation_3_4_5():
    m = started(1, (101,))
    # (0,0,0) itself is the controller's pre-odometry placeholder, so start from (1,1,-2):
    # (1,1,-2) -> (4,5,-2) is the same 3-4-5 step.
    m.on_state(T0 + 1 * S, 0, 1.0, 1.0, -2.0, 100.0, 1)
    m.on_state(T0 + 2 * S, 0, 4.0, 5.0, -2.0, 99.0, 1)
    row, detail = m.finalize(T0 + 3 * S, 'run_x', 'ts')
    assert detail['per_drone_distance_m'][0] == pytest.approx(5.0)
    assert row['total_flight_distance_m'] == pytest.approx(5.0)


def test_completion_rate_mission_time_and_workload():
    m = started(2, (101, 102, 103))
    m.on_task_completed(T0 + 10 * S, 0, 101)
    m.on_task_completed(T0 + 12 * S, 1, 102)
    m.on_task_completed(T0 + 15 * S, 0, 101)   # repeat visit: not a new completion
    m.on_task_completed(T0 + 16 * S, 5, 103)   # phantom drone: ignored
    m.on_task_completed(T0 + 17 * S, 1, 999)   # not a mission task: ignored
    row, _ = m.finalize(T0 + 20 * S, 'run_x', 'ts')
    assert (row['total_tasks'], row['completed_tasks']) == (3, 2)
    assert row['task_completion_rate_percent'] == pytest.approx(66.67)
    assert row['status'] == 'incomplete' and row['mission_completion_time_s'] == ''
    m.on_task_completed(T0 + 30 * S, 1, 103)
    row, _ = m.finalize(T0 + 40 * S, 'run_x', 'ts')
    assert row['status'] == 'completed'
    assert row['task_completion_rate_percent'] == 100.0
    assert row['mission_completion_time_s'] == pytest.approx(30.0)
    assert (row['drone_0_tasks'], row['drone_1_tasks']) == (1, 2)
    assert (row['workload_min'], row['workload_max']) == (1, 2)
    assert 'drone_2_tasks' not in row


def test_minimum_pairwise_distance_with_interpolation():
    m = started(2, (101,))
    # drone 0 static at origin; drone 1 moves from x=4 to x=0.5 then away (sampled at 1 Hz).
    for k, x1 in enumerate([4.0, 2.0, 0.5, 3.0]):
        t = T0 + k * S // 4
        m.on_state(t, 0, 0.0, 0.0, -5.0, 100.0, 1)
        m.on_state(t + 1, 1, x1, 0.0, -5.0, 100.0, 1)
    row, _ = m.finalize(T0 + 2 * S, 'run_x', 'ts')
    assert row['minimum_inter_drone_distance_m'] == pytest.approx(0.5, abs=1e-3)


def test_minimum_distance_na_for_single_drone():
    m = started(1, (101,))
    m.on_state(T0 + S, 0, 0.0, 0.0, -5.0, 100.0, 1)
    m.on_state(T0 + 2 * S, 0, 1.0, 0.0, -5.0, 100.0, 1)
    row, _ = m.finalize(T0 + 3 * S, 'run_x', 'ts')
    assert row['minimum_inter_drone_distance_m'] == 'N/A'


def test_battery_consumption_per_drone_and_total():
    m = started(2, (101,))
    m.on_state(T0 + 1 * S, 0, 0, 0, -1, 100.0, 1)
    m.on_state(T0 + 2 * S, 0, 0, 0, -1, 97.5, 1)
    m.on_state(T0 + 1 * S, 1, 5, 0, -1, 99.0, 1)
    m.on_state(T0 + 2 * S, 1, 5, 0, -1, 98.0, 1)
    row, detail = m.finalize(T0 + 3 * S, 'run_x', 'ts')
    assert detail['per_drone_battery_consumed_percent'] == {0: 2.5, 1: 1.0}
    assert row['total_battery_consumed_percent'] == pytest.approx(3.5)


def test_missing_battery_is_not_fabricated():
    m = started(2, (101,))
    m.on_state(T0 + 1 * S, 0, 0, 0, -1, 100.0, 1)
    m.on_state(T0 + 2 * S, 0, 0, 0, -1, 99.0, 1)
    row, detail = m.finalize(T0 + 3 * S, 'run_x', 'ts')
    assert detail['per_drone_battery_consumed_percent'][1] is None
    assert row['total_battery_consumed_percent'] == pytest.approx(1.0)
    assert 'drone 1 no valid battery samples' in row['notes']


def test_diverged_drone_excluded_after_failure_but_keeps_tasks():
    m = started(2, (101, 102))
    m.on_state(T0 + 1 * S, 0, 0.0, 0.0, -4.0, 100.0, 1)
    m.on_state(T0 + 2 * S, 0, 1.0, 0.0, -4.0, 99.9, 1)        # +1 m valid
    m.on_task_completed(T0 + 2 * S, 0, 101)
    m.on_state(T0 + 3 * S, 0, 150.0, -80.0, -2.0, 99.8, 1)   # EKF divergence after a crash
    m.on_state(T0 + 4 * S, 0, 2.0, 0.0, -4.0, 99.7, 1)       # ignored: drone already excluded
    m.on_state(T0 + 1 * S, 1, 5.0, 0.0, -4.0, 100.0, 1)
    m.on_state(T0 + 4 * S, 1, 5.0, 3.0, -4.0, 99.0, 1)
    row, detail = m.finalize(T0 + 5 * S, 'run_x', 'ts')
    assert detail['per_drone_distance_m'][0] == pytest.approx(1.0)
    assert detail['per_drone_battery_consumed_percent'][0] == pytest.approx(0.1)
    assert row['drone_0_tasks'] == 1
    assert 'drone 0 excluded' in row['notes']


def test_placeholder_before_first_odometry_is_rejected_transition_not_failure():
    """Observed in run_20260929_212256: a controller publishes its (0,0,0) placeholder until its
    first odometry arrives ~0.5 s after mission start, then its real spawn position (0, 7, 0)."""
    m = started(2, (101,))
    D = S // 10
    for k in range(5):                                        # placeholder, 10 Hz
        m.on_state(T0 + k * D, 1, 0.0, 0.0, 0.0, 100.0, 0)
        m.on_state(T0 + k * D + 1, 0, -8.0, 7.0, 0.0, 100.0, 0)
    for k in range(5, 40):                                    # real telemetry: climbs 0.1 m per sample
        z = -0.1 * (k - 5)
        m.on_state(T0 + k * D, 1, 0.0, 7.0, z, 100.0 - 0.01 * k, 1)
        m.on_state(T0 + k * D + 1, 0, -8.0, 7.0, 0.0, 100.0, 0)
    tr = m.tracks[1]
    assert tr.invalid_since_ns is None                        # drone NOT excluded
    assert tr.placeholder_samples == 5 and len(tr.samples) == 35 and tr.rejected == []
    row, detail = m.finalize(T0 + 4 * S, 'run_x', 'ts')
    assert detail['per_drone_distance_m'][1] == pytest.approx(3.4)   # only the real climb, no 7 m jump
    assert detail['per_drone_battery_consumed_percent'][1] == pytest.approx(0.39)  # from the placeholder's battery
    assert row['minimum_inter_drone_distance_m'] == pytest.approx(8.0, abs=1e-3)   # origin never used as a position
    assert row['notes'] == ''


def test_isolated_spike_rejected_and_collection_continues():
    m = started(1, (101,))
    D = S // 10
    pts = [(0.0, 0.0), (0.1, 0.0), (9.0, 9.0), (0.2, 0.0), (0.3, 0.0)]   # one bad sample
    for k, (x, y) in enumerate(pts):
        m.on_state(T0 + k * D, 0, x, y, -4.0, 100.0, 1)
    tr = m.tracks[0]
    assert tr.invalid_since_ns is None and len(tr.rejected) == 2 and len(tr.samples) == 5
    _, detail = m.finalize(T0 + S, 'run_x', 'ts')
    assert detail['per_drone_distance_m'][0] == pytest.approx(0.2)    # 0->0.1 and 0.2->0.3


def test_crashed_on_ground_rule():
    m = started(2, (101,))
    for k in range(0, 100):                                  # airborne, ~1 s fall, then ~8 s on the floor while PATROLLING
        z = -3.0 if k < 10 else min(-0.1, -3.0 + 0.3 * (k - 10))
        m.on_state(T0 + k * S // 10, 1, 5.0, 0.0, z, 100.0, 1)
    assert 'crashed' in m.tracks[1].invalid_reason


def test_phantom_and_pre_start_samples_ignored():
    m = RunMetrics()
    m.on_state(T0, 0, 0, 0, 0, 100, 1)              # before start
    m.start(T0, 'apf', 'benchmark', 2, (101,))
    m.on_state(T0 + S, 7, 0, 0, -3, 100, 1)          # phantom drone id
    assert 7 not in m.tracks and m.tracks[0].samples == []


# --------------------------------------------------------------------------- extended metrics (7-11)

from patrol_coordinator.obstacles import BoxObstacle  # noqa: E402

BOX = BoxObstacle.from_center_size('rack', (0.0, 0.0, -1.75), (1.0, 1.0, 3.5))      # x, y in [-0.5, 0.5]
FLOOR = BoxObstacle.from_center_size('floor', (0.0, 0.0, 0.05), (30.0, 20.0, 0.1))


def started_ext(num_drones=2, tasks=(101, 102), window=0.0, obstacles=(BOX, FLOOR)):
    m = RunMetrics()
    m.start(T0, 'rl', 'benchmark', num_drones, tasks, observation_window_s=window, obstacles=list(obstacles))
    return m


def fly(m, drone, points, t_start=0.0, dt=0.1):
    """10 Hz samples along the given (x, y, z) points."""
    for k, (x, y, z) in enumerate(points):
        m.on_state(T0 + int((t_start + k * dt) * S), drone, x, y, z, 100.0, 1)


def test_obstacle_clearance_contacts_and_floor_ignored():
    m = started_ext(1, (101,))
    # 2 s at 2.0 m from the box face (x = 2.5), then 1 s at 0.2 m (x = 0.7): one contact episode
    fly(m, 0, [(2.5, 0.0, -2.0)] * 20 + [(0.7, 0.0, -2.0)] * 10)
    row, detail = m.finalize(T0 + int(2.9 * S), 'run_x', 'ts')
    assert row['min_obstacle_clearance_m'] == pytest.approx(0.2, abs=1e-6)   # floor (1.95 m below) ignored
    assert row['obstacle_contacts'] == 1
    assert row['obstacle_near_miss_s'] == pytest.approx(0.9, abs=0.11)       # 20 Hz timeline over the last second


def test_low_samples_do_not_count_for_clearance():
    m = started_ext(1, (101,))
    fly(m, 0, [(0.7, 0.0, -0.2)] * 10)                                       # 0.2 m high: on the pad
    row, _ = m.finalize(T0 + 1 * S, 'run_x', 'ts')
    assert row['min_obstacle_clearance_m'] == '' and row['obstacle_contacts'] == 0


def test_separation_near_miss_and_contact_episodes():
    m = started_ext(2, (101,), obstacles=())
    fly(m, 0, [(5.0, 5.0, -3.0)] * 30)
    fly(m, 1, [(5.0, 8.0, -3.0)] * 10 + [(5.0, 5.8, -3.0)] * 10 + [(5.0, 5.5, -3.0)] * 10)
    row, _ = m.finalize(T0 + int(2.9 * S), 'run_x', 'ts')
    assert row['separation_near_miss_s'] == pytest.approx(1.9, abs=0.11)    # 0.8 m and 0.5 m phases
    assert row['separation_contacts'] == 1                                  # 0.5 m < 2 x 0.3 m, one episode


def test_idleness_average_and_worst():
    m = started_ext(1, (101, 102), obstacles=())
    m.on_task_completed(T0 + 4 * S, 0, 101)          # 101: gaps 4 s, 6 s; 102: never visited, 10 s
    m.on_task_completed(T0 + 7 * S, 0, 102)          # 102 visited at 7: gaps 7 s, 3 s
    row, _ = m.finalize(T0 + 10 * S, 'run_x', 'ts', status='incomplete')
    # mission completes at t+7 (both tasks visited): the evaluation window is the mission window
    assert row['evaluation_window_s'] == pytest.approx(7.0)
    # 101: gaps 4, 3 -> 8 + 4.5 = 12.5 ; 102: gap 7 -> 24.5 ; mean = 37 / (7 * 2)
    assert row['mean_task_idleness_s'] == pytest.approx(37 / 14, abs=1e-3)
    assert row['max_task_idleness_s'] == pytest.approx(7.0)


def test_observation_window_keeps_mission_metrics_and_extends_the_rest():
    m = started_ext(1, (101,), window=20.0, obstacles=())
    fly(m, 0, [(float(k), 0.0, -2.0) for k in range(20)], dt=1.0)           # 1 m/s for 19 s
    m.on_task_completed(T0 + 5 * S, 0, 101)                                 # mission done at t+5
    m.on_task_completed(T0 + 15 * S, 0, 101)                                # a later visit (observation only)
    row, detail = m.finalize(T0 + 30 * S, 'run_x', 'ts')
    assert row['mission_completion_time_s'] == pytest.approx(5.0)
    assert row['total_flight_distance_m'] == pytest.approx(5.0)            # mission window only
    assert row['evaluation_window_s'] == pytest.approx(20.0)
    assert row['task_visits'] == 2
    assert row['max_task_idleness_s'] == pytest.approx(10.0)               # 5 -> 15


def test_compute_time_aggregation_per_source():
    m = started_ext(1, (101,), obstacles=())
    m.on_event(T0 + 5 * S, 'compute_stats', {'source': 'coordinator', 'n': 10, 'mean_ms': 1.0, 'max_ms': 3.0, 'p95_ms': 2.0})
    m.on_event(T0 + 10 * S, 'compute_stats', {'source': 'coordinator', 'n': 30, 'mean_ms': 2.0, 'max_ms': 9.0, 'p95_ms': 4.0})
    m.on_event(T0 + 5 * S, 'compute_stats', {'source': 'allocation', 'n': 50, 'mean_ms': 0.01, 'max_ms': 0.05})
    row, _ = m.finalize(T0 + 11 * S, 'run_x', 'ts')
    assert row['decision_time_mean_ms'] == pytest.approx(1.75)                # (10 * 1 + 30 * 2) / 40
    assert row['decision_time_p95_ms'] == pytest.approx(4.0) and row['decision_time_max_ms'] == pytest.approx(9.0)
    assert row['allocation_time_mean_ms'] == pytest.approx(0.01)


def test_comm_loss_detection_reassignment_restoration_rejoin_resume():
    m = started_ext(2, (101, 102, 103), window=100.0, obstacles=())
    m.on_assignment(T0 + 1 * S, 101, 0)
    m.on_assignment(T0 + 1 * S, 102, 1)
    m.on_assignment(T0 + 1 * S, 103, 1)
    fly(m, 0, [(0.0, 0.0, -3.0)] * 600)                                     # 60 s
    fly(m, 1, [(4.0, 0.0, -3.0)] * 200 + [(1.5, 0.0, -3.0)] * 400)         # 2.5 m apart from t+20
    m.on_event(T0 + 20 * S, 'comm_loss_started', {'drone_id': 1})
    m.on_event(T0 + 25 * S, 'peer_declared_failed', {'drone_id': 1, 'by': 0})
    m.on_assignment(T0 + 26 * S, 102, 0)
    m.on_task_completed(T0 + 30 * S, 0, 102)
    m.on_task_completed(T0 + 33 * S, 0, 103)
    m.on_event(T0 + 35 * S, 'comm_loss_ended', {'drone_id': 1})
    m.on_event(T0 + 35 * S + S // 2, 'peer_recovered', {'drone_id': 1, 'by': 0})
    m.on_task_completed(T0 + 41 * S, 1, 102)
    row, detail = m.finalize(T0 + 100 * S, 'run_x', 'ts')
    assert row['comm_loss_drone'] == 1 and row['comm_loss_start_s'] == pytest.approx(20.0)
    assert row['comm_loss_duration_s'] == pytest.approx(15.0)
    assert row['detection_s'] == pytest.approx(5.0)
    assert row['reassignment_s'] == pytest.approx(6.0)
    assert row['coverage_restored_s'] == pytest.approx(13.0)                # 102 at +30, 103 at +33
    assert row['rejoin_s'] == pytest.approx(0.5)
    assert row['resume_s'] == pytest.approx(6.0)
    assert row['min_separation_during_loss_m'] == pytest.approx(1.5)
    assert detail['comm_loss']['lost_drone_tasks'] == [102, 103]


def test_no_comm_loss_leaves_columns_empty():
    m = started_ext(1, (101,), obstacles=())
    row, _ = m.finalize(T0 + 5 * S, 'run_x', 'ts')
    assert all(row[k] == '' for k in ('comm_loss_drone', 'detection_s', 'rejoin_s', 'resume_s'))


def test_workload_imbalance_jain_and_gini_on_tasks_and_distance():
    m = started_ext(2, (101, 102), window=10.0, obstacles=())
    fly(m, 0, [(float(k) * 0.1, 0.0, -3.0) for k in range(31)])          # 3 m
    fly(m, 1, [(5.0 + k * 0.1, 0.0, -3.0) for k in range(11)])           # 1 m
    for t, d, task in ((1, 0, 101), (2, 0, 102), (3, 0, 101), (4, 1, 102)):
        m.on_task_completed(T0 + t * S, d, task)
    row, detail = m.finalize(T0 + 10 * S, 'run_x', 'ts')
    # tasks (3, 1): Jain = 16 / (2 * 10) = 0.8; Gini = 2 * 2 / (2 * 2 * 4) = 0.25
    assert row['workload_imbalance_tasks'] == pytest.approx(0.2)
    assert row['workload_gini_tasks'] == pytest.approx(0.25)
    # distance (3, 1) m: the same ratios
    assert row['workload_imbalance_distance'] == pytest.approx(0.2, abs=1e-3)
    assert row['workload_gini_distance'] == pytest.approx(0.25, abs=1e-3)
    assert detail['per_drone_task_completions'] == {0: 3, 1: 1}


def test_workload_imbalance_empty_without_work():
    m = started_ext(2, (101,), obstacles=())
    row, _ = m.finalize(T0 + 5 * S, 'run_x', 'ts')
    assert row['workload_imbalance_tasks'] == '' and row['workload_gini_tasks'] == ''


def test_reallocations_count_only_changes_of_drone_and_allocation_latency():
    m = started_ext(2, (101, 102), window=120.0, obstacles=())
    m.on_assignment(T0 + 2 * S, 101, 0)
    m.on_assignment(T0 + 3 * S, 102, 1)          # every task assigned at +3 s
    m.on_assignment(T0 + 20 * S, 101, 0)         # same drone again: not a reallocation
    m.on_assignment(T0 + 30 * S, 102, 0)         # 1 -> 0
    m.on_assignment(T0 + 40 * S, 102, 1)         # 0 -> 1
    m.on_task_completed(T0 + 5 * S, 0, 101)
    m.on_task_completed(T0 + 12 * S, 1, 102)     # MCT = 12 s
    row, _ = m.finalize(T0 + 120 * S, 'run_x', 'ts')
    assert row['task_reallocations'] == 2
    assert row['reallocations_per_min'] == pytest.approx(1.0)       # 2 in a 2 min window
    assert row['alloc_first_assignment_s'] == pytest.approx(2.0)
    assert row['alloc_all_assigned_s'] == pytest.approx(3.0)
    assert row['allocation_to_mct_ratio'] == pytest.approx(0.25)


def test_separation_percentiles_and_violation_episodes():
    m = started_ext(2, (101,), window=10.0, obstacles=())
    # pair 3 m apart, then 0.8 m for 1 s twice (two episodes below D_SAFE = 1 m)
    xs = [3.0] * 30 + [0.8] * 10 + [3.0] * 20 + [0.8] * 10 + [3.0] * 31
    fly(m, 0, [(0.0, 0.0, -3.0)] * len(xs))
    fly(m, 1, [(x, 0.0, -3.0) for x in xs])
    row, detail = m.finalize(T0 + 10 * S, 'run_x', 'ts')
    assert row['separation_violations'] == 2
    assert row['separation_p1_m'] == pytest.approx(0.8, abs=0.05)
    assert row['separation_p5_m'] == pytest.approx(0.8, abs=0.05)   # ~20 % of the time at 0.8 m
    assert sum(detail['separation_histogram_m'].values()) > 0


def test_loss_safety_depth_and_time_and_reassign_after_detection():
    m = started_ext(2, (101, 102), window=60.0, obstacles=())
    m.on_assignment(T0 + 1 * S, 101, 0)
    m.on_assignment(T0 + 1 * S, 102, 1)
    fly(m, 0, [(0.0, 0.0, -3.0)] * 600)
    # drone 1: 3 m away, 0.6 m away for 2 s during the loss (t+20..t+35), then 3 m
    fly(m, 1, [(3.0, 0.0, -3.0)] * 240 + [(0.6, 0.0, -3.0)] * 20 + [(3.0, 0.0, -3.0)] * 340)
    m.on_event(T0 + 20 * S, 'comm_loss_started', {'drone_id': 1})
    m.on_event(T0 + 25 * S, 'peer_declared_failed', {'drone_id': 1, 'by': 0})
    m.on_assignment(T0 + 27 * S, 102, 0)
    m.on_event(T0 + 35 * S, 'comm_loss_ended', {'drone_id': 1})
    row, _ = m.finalize(T0 + 60 * S, 'run_x', 'ts')
    assert row['reassign_after_detection_s'] == pytest.approx(2.0)
    assert row['loss_safety_depth_m'] == pytest.approx(0.4, abs=0.01)
    assert row['loss_safety_time_s'] == pytest.approx(2.0, abs=0.15)


def test_no_loss_leaves_transient_safety_empty():
    m = started_ext(2, (101,), obstacles=())
    row, _ = m.finalize(T0 + 5 * S, 'run_x', 'ts')
    assert row['loss_safety_depth_m'] == '' and row['loss_safety_time_s'] == ''
