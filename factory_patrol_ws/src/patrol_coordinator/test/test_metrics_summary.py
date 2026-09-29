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
