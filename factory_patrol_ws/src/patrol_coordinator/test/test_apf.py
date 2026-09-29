"""Unit tests for the APF algorithm, the obstacle model and algorithm registration.

Run:  cd factory_patrol_ws/src/patrol_coordinator && python3 -m pytest test -q
"""

import math
import os

import pytest
import yaml

from patrol_coordinator.algorithm_base import DroneState, TaskInfo
from patrol_coordinator.algorithms import get_algorithm_class
from patrol_coordinator.algorithms.apf import (
    APFAlgorithm, APFParams, attractive_force, drone_force, khatib_magnitude, obstacle_force,
)
from patrol_coordinator.obstacles import BoxObstacle, load_obstacles

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
SEC = 1_000_000_000
PATROLLING, INSPECTING, FAILED = 1, 2, 4


def _norm(v):
    return math.sqrt(sum(c * c for c in v))


def _params():
    with open(os.path.join(ROOT, 'config/algorithms/apf.yaml')) as f:
        return yaml.safe_load(f)['apf']


def _algo(num_drones=3, tasks=None, obstacles=None):
    algo = APFAlgorithm({'algorithm_params': _params(), 'obstacles': obstacles or []})
    algo.initialize(num_drones, tasks or [TaskInfo(101, 10.0, 0.0, -4.0)])
    return algo


def _state(d, x, y, z, t_ns, state=PATROLLING, task=101):
    return DroneState(d, x, y, z, 90.0, state, timestamp_ns=t_ns, current_task_id=task)


# --- registry ---------------------------------------------------------------

def test_registry_selects_expected_classes():
    assert get_algorithm_class('auction').__name__ == 'AuctionAlgorithm'
    assert get_algorithm_class('apf') is APFAlgorithm
    with pytest.raises(ValueError):
        get_algorithm_class('nope')


def test_apf_loads_with_repo_config_and_obstacles():
    obstacles = load_obstacles(os.path.join(ROOT, 'config/environment/factory_obstacles.yaml'))
    algo = _algo(obstacles=obstacles)
    assert algo.params == APFParams.from_dict(_params())
    assert algo.get_update_period() == pytest.approx(0.1)
    assert algo.uses_external_navigation()
    assert len(obstacles) == 18


def test_unknown_parameter_rejected():
    with pytest.raises(ValueError):
        APFParams.from_dict({'goal_gian': 1.0})


# --- force terms --------------------------------------------------------------

def test_attraction_linear_near_goal_and_saturated_far():
    p = APFParams()
    near = attractive_force((0, 0, -4), (1, 0, -4), p)
    assert near == pytest.approx((0.5, 0.0, 0.0))
    far = attractive_force((0, 0, -4), (20, 0, -4), p)
    assert _norm(far) == pytest.approx(p.max_velocity)
    assert far[0] > 0 and far[1] == 0 and far[2] == 0


def test_khatib_zero_outside_radius_and_finite_at_zero():
    assert khatib_magnitude(3.0, 10.0, 3.0, 0.1) == 0.0
    assert khatib_magnitude(0.0, 10.0, 3.0, 0.1) == khatib_magnitude(0.1, 10.0, 3.0, 0.1)
    assert math.isfinite(khatib_magnitude(0.0, 10.0, 3.0, 0.1))
    assert khatib_magnitude(1.0, 10.0, 3.0, 0.1) > khatib_magnitude(2.0, 10.0, 3.0, 0.1) > 0


def test_obstacle_repulsion_points_away_from_box():
    p = APFParams()
    wall = BoxObstacle.from_center_size('wall', (0, 0, -2), (0.2, 10, 4))  # x in [-0.1, 0.1]
    f, d = obstacle_force((0.6, 0, -2), [wall], p)
    assert d == pytest.approx(0.5)
    assert f[0] > 0 and f[1] == pytest.approx(0) and f[2] == pytest.approx(0)
    f_far, _ = obstacle_force((2.0, 0, -2), [wall], p)
    assert f_far == (0.0, 0.0, 0.0)


def test_obstacle_repulsion_over_rack_top_pushes_up():
    # Rack occupies heights 0..3.5 m -> factory z in [-3.5, 0]; drone 0.5 m above it.
    rack = BoxObstacle.from_center_size('rack', (0, 0, -1.75), (0.4, 8, 3.5))
    f, _ = obstacle_force((0, 0, -4.0), [rack], APFParams())
    assert f[2] < 0 and f[0] == pytest.approx(0) and f[1] == pytest.approx(0)  # z negative = up


def test_point_inside_box_is_pushed_out_through_nearest_face():
    box = BoxObstacle.from_center_size('b', (0, 0, -1), (2, 2, 2))
    f, d = obstacle_force((0.9, 0, -1), [box], APFParams())
    assert d == 0.0
    assert all(math.isfinite(c) for c in f)
    assert f[0] > 0 and f[1] == 0 and f[2] == 0


def test_drone_repulsion_symmetric_and_coincident_safe():
    p = APFParams()
    f0, d = drone_force(0, (0, 0, -4), {0: (0, 0, -4), 1: (1, 0, -4)}, p)
    f1, _ = drone_force(1, (1, 0, -4), {0: (0, 0, -4), 1: (1, 0, -4)}, p)
    assert d == pytest.approx(1.0)
    assert f0[0] < 0 and f1[0] > 0 and f0[0] == pytest.approx(-f1[0])
    c0, _ = drone_force(0, (0, 0, -4), {1: (0, 0, -4)}, p)
    c1, _ = drone_force(1, (0, 0, -4), {0: (0, 0, -4)}, p)
    assert all(math.isfinite(c) for c in c0 + c1)
    assert c0[0] < 0 < c1[0]
    far, _ = drone_force(0, (0, 0, -4), {1: (3.5, 0, -4)}, p)
    assert far == (0.0, 0.0, 0.0)


# --- algorithm step -----------------------------------------------------------

def test_single_drone_command_toward_goal_bounded():
    algo = _algo(num_drones=1)
    algo.update_drone_state(_state(0, 0.0, 0.0, -4.0, 1 * SEC))
    res = algo.compute(1 * SEC)
    (cmd,) = res.movement_commands
    assert cmd.drone_id == 0 and cmd.task_id == 101
    v = (cmd.velocity_x, cmd.velocity_y, cmd.velocity_z)
    assert _norm(v) <= algo.params.max_velocity + 1e-9
    assert cmd.velocity_x > 0
    assert cmd.target_x == pytest.approx(0.0 + cmd.velocity_x * algo.params.command_horizon)


def test_goal_capture_commands_exact_goal():
    algo = _algo(num_drones=2)
    algo.update_drone_state(_state(0, 9.5, 0.0, -4.0, SEC))
    algo.update_drone_state(_state(1, 9.5, 1.0, -4.0, SEC, state=INSPECTING))  # close neighbour
    (cmd,) = algo.compute(SEC).movement_commands
    assert (cmd.target_x, cmd.target_y, cmd.target_z) == (10.0, 0.0, -4.0)
    assert (cmd.velocity_x, cmd.velocity_y, cmd.velocity_z) == (0.0, 0.0, 0.0)


def test_phantom_failed_and_silent_drones_are_not_neighbours():
    algo = _algo(num_drones=2)
    now = 20 * SEC
    algo.update_drone_state(_state(0, 0.0, 0.0, -4.0, now))
    algo.update_drone_state(_state(5, 0.5, 0.0, -4.0, now))                    # phantom id >= num_drones
    active = algo.active_drones(now)
    assert set(active) == {0}
    algo.update_drone_state(_state(1, 0.5, 0.0, -4.0, now, state=FAILED))      # failed
    assert set(algo.active_drones(now)) == {0}
    algo.update_drone_state(_state(1, 0.5, 0.0, -4.0, now - 6 * SEC))          # silent > 5 s
    assert set(algo.active_drones(now)) == {0}
    (cmd,) = algo.compute(now).movement_commands
    assert cmd.velocity_x > 0  # no repulsion from any excluded drone
    algo.update_drone_state(_state(1, 0.5, 0.0, -4.0, now, state=INSPECTING))  # healthy again
    assert set(algo.active_drones(now)) == {0, 1}


def test_two_drones_close_repel_and_only_patrolling_drones_commanded():
    tasks = [TaskInfo(101, 10.0, 0.0, -4.0), TaskInfo(102, -10.0, 0.0, -4.0)]
    algo = _algo(num_drones=2, tasks=tasks)
    algo.update_drone_state(_state(0, 0.0, 0.0, -4.0, SEC, task=101))
    algo.update_drone_state(_state(1, 1.0, 0.0, -4.0, SEC, task=102))  # head-on, 1 m apart
    res = algo.compute(SEC)
    cmds = {c.drone_id: c for c in res.movement_commands}
    assert set(cmds) == {0, 1}
    for c in cmds.values():
        assert all(math.isfinite(v) for v in (c.target_x, c.target_y, c.target_z,
                                              c.velocity_x, c.velocity_y, c.velocity_z))
    # Repulsion dominates attraction at 1 m: drones are pushed apart.
    assert cmds[0].velocity_x < 0 and cmds[1].velocity_x > 0
    diag = [d for e, d in res.metadata['events'] if e == 'apf_diagnostics']
    assert all(d['f_drone'] > 0 for d in diag)
    sep = [d for e, d in res.metadata['events'] if e == 'apf_clearance'][0]
    assert sep['min_separation'] == pytest.approx(1.0)
    # Inspecting drones receive no commands (controller holds the task point).
    algo.update_drone_state(_state(1, 1.0, 0.0, -4.0, 2 * SEC, state=INSPECTING, task=102))
    algo.update_drone_state(_state(0, 0.0, 0.0, -4.0, 2 * SEC, task=101))
    assert [c.drone_id for c in algo.compute(2 * SEC).movement_commands] == [0]


def test_task_with_default_altitude_uses_controller_patrol_altitude():
    algo = _algo(num_drones=3, tasks=[TaskInfo(101, 1.0, 0.0, 0.0)])
    assert algo.goal_for(2, algo._tasks_by_id[101]) == (1.0, 0.0, -4.5)


def test_stall_reported_once_per_goal():
    # stall_speed above max_velocity: every step counts as "slow", isolating the timer logic.
    params = dict(_params(), stall_speed=10.0, stall_time=5.0)
    algo = APFAlgorithm({'algorithm_params': params, 'obstacles': []})
    algo.initialize(1, [TaskInfo(101, 10.0, 0.0, -4.0)])
    stalls = []
    for k in range(80):  # 7.9 s at 10 Hz
        t = SEC + k * SEC // 10
        algo.update_drone_state(_state(0, 0.0, 0.0, -4.0, t))
        stalls += [d for e, d in algo.compute(t).metadata['events'] if e == 'apf_stall']
    assert len(stalls) == 1 and stalls[0]['task_id'] == 101


def test_repo_obstacles_match_world_heights():
    obstacles = {o.obstacle_id: o for o in load_obstacles(
        os.path.join(ROOT, 'config/environment/factory_obstacles.yaml'))}
    rack = obstacles['rack_row_1']
    assert rack.min_corner[2] == pytest.approx(-3.5) and rack.max_corner[2] == pytest.approx(0.0)
    # Every benchmark task is outside every obstacle.
    with open(os.path.join(ROOT, 'config/tasks/benchmark.yaml')) as f:
        tasks = yaml.safe_load(f)['tasks']
    for t in tasks:
        for o in obstacles.values():
            assert o.closest_point(t['position']) != tuple(t['position'])
