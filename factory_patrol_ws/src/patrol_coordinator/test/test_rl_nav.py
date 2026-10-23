"""Unit and closed-loop tests for the RL navigation algorithm (patrol_coordinator.algorithms.rl_nav).

Run:  cd factory_patrol_ws/src/patrol_coordinator && python3 -m pytest test -q
The tests marked 'policy' load the real checkpoint and need torch: run them with the RL venv,
  ../../../rl-nmopso-factory-patrol/.venv/bin/python -m pytest test -q
(with plain python3 they are skipped).
"""

import math
import os
from dataclasses import dataclass, field

import numpy as np
import pytest
import yaml

from patrol_coordinator.algorithm_base import DroneState, TaskInfo
from patrol_coordinator.algorithms import get_algorithm_class
from patrol_coordinator.algorithms.rl_nav import Polyline, RLNavigationAlgorithm, RLParams
from patrol_coordinator.obstacles import load_obstacles

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
SEC = 1_000_000_000
PATROLLING, INSPECTING, FAILED = 1, 2, 4


def _params(**over):
    with open(os.path.join(ROOT, 'config/algorithms/rl.yaml')) as f:
        p = yaml.safe_load(f)['rl']
    p.update(over)
    return p


def _state(d, x, y, z, t_ns, state=PATROLLING, task=101):
    return DroneState(d, x, y, z, 90.0, state, timestamp_ns=t_ns, current_task_id=task)


@dataclass
class _Plan:
    feasible: bool
    path: np.ndarray
    start_free: np.ndarray
    goal_free: np.ndarray
    F: list = field(default_factory=lambda: [0.1, 0.0, 0.0, 0.0])
    method: str = 'rl'
    n_candidates: int = 201
    n_feasible: int = 150
    plan_time_s: float = 0.01
    reason: str = ''
    extra: dict = field(default_factory=dict)


class FakePlanner:
    """Stands in for rlpatrol.planner.LegPlanner (no torch): straight band path, or failure."""
    free_r = 3.0
    ckpt_info = {'path': 'fake.pt', 'iteration': 0}
    dev = 'cpu'

    def __init__(self, feasible=True, blocked=()):
        self.feasible, self.blocked, self.calls = feasible, blocked, []

    def is_free(self, xy):
        return tuple(xy) not in self.blocked

    def nearest_free(self, xy):
        return np.array([xy[0], xy[1] - 1.0]) if tuple(xy) in self.blocked else np.asarray(xy, float)

    def plan_route(self, start, goal, seed=None):
        self.calls.append((tuple(start), tuple(goal), seed))
        s, g = self.nearest_free(start), self.nearest_free(goal)
        if not self.feasible:
            return _Plan(False, np.zeros((0, 3)), s, g, F=[math.inf] * 4, method='none', reason='blocked')
        mid = (s + g) / 2
        return _Plan(True, np.array([[*s, 1.8], [*mid, 1.8], [*g, 1.8]]), s, g)


def _algo(num_drones=3, tasks=None, planner=None, obstacles=None, **over):
    algo = RLNavigationAlgorithm({'algorithm_params': _params(**over), 'obstacles': obstacles or []})
    algo.initialize(num_drones, tasks or [TaskInfo(101, 6.0, 0.0, -4.0)], planner=planner or FakePlanner())
    return algo


# --- configuration / registry ----------------------------------------------------------------------

def test_registry_selects_rl():
    assert get_algorithm_class('rl') is RLNavigationAlgorithm


def test_repo_config_loads_and_validates():
    p = RLParams.from_dict(_params())
    assert p.max_velocity == 1.5 and p.command_horizon == 1.0       # same speed cap / look-ahead as APF
    assert p.refine_on_failure is True and isinstance(p.torch_threads, int)
    with pytest.raises(ValueError):
        RLParams.from_dict(_params(nope=1))
    with pytest.raises(ValueError):
        RLParams.from_dict(_params(max_velocity=0.0))
    with pytest.raises(ValueError):
        RLParams.from_dict(_params(refine_on_failure='maybe'))
    assert RLParams.from_dict(_params(refine_on_failure='false')).refine_on_failure is False


def test_algorithm_is_external_navigation_at_rate():
    algo = _algo()
    assert algo.uses_external_navigation()
    assert algo.get_update_period() == pytest.approx(0.1)


def test_missing_checkpoint_raises_at_initialize(tmp_path):
    algo = RLNavigationAlgorithm({'algorithm_params': _params(checkpoint=str(tmp_path / 'none.pt'))})
    with pytest.raises((FileNotFoundError, ImportError)):
        algo.initialize(3, [TaskInfo(101, 0.0, 0.0, -4.0)])


# --- geometry --------------------------------------------------------------------------------------

def test_polyline_arc_length_and_projection():
    pl = Polyline([(0, 0, 0), (3, 0, 0), (3, 4, 0), (3, 4, 0)])   # duplicate point dropped
    assert pl.length == pytest.approx(7.0) and len(pl.points) == 3
    assert pl.at(4.0) == pytest.approx((3.0, 1.0, 0.0))
    s, d = pl.project((1.0, 0.5, 0.0))
    assert s == pytest.approx(1.0) and d == pytest.approx(0.5)
    s, d = pl.project((3.0, 3.0, 0.0), 0.0, 2.0)                   # window excludes the 2nd segment
    assert s == pytest.approx(2.0)


def test_cruise_layers_and_task_altitude_rule():
    algo = _algo(num_drones=12)
    assert [algo.cruise_height(d) for d in range(3)] == pytest.approx([1.8, 2.8, 3.8])
    assert algo.cruise_height(11) == pytest.approx(10.0)            # capped at max_cruise_height
    assert algo.task_z(1, TaskInfo(1, 0, 0, -0.5)) == pytest.approx(-3.5)   # controller patrol altitude
    assert algo.task_z(1, TaskInfo(1, 0, 0, -4.0)) == pytest.approx(-4.0)


def test_flight_path_descends_to_layer_flies_band_path_and_climbs_to_task():
    task = TaskInfo(104, 4.0, 5.0, -3.5)
    planner = FakePlanner(blocked=[(4.0, 5.0)])                       # task above a machine
    algo = _algo(tasks=[task], planner=planner)
    plan = planner.plan_route((-8.0, 7.0), (4.0, 5.0))
    pl = algo.flight_path(1, (-8.0, 7.0, -4.0), task, plan)
    P = np.array(pl.points)
    assert P[0] == pytest.approx([-8.0, 7.0, -4.0])
    assert P[1] == pytest.approx([-8.0, 7.0, -2.8])                   # vertical to drone 1's layer
    assert np.all(P[1:-2, 2] == pytest.approx(-2.8))
    assert P[-2] == pytest.approx([4.0, 4.0, -3.5])                   # climb at the free goal point
    assert P[-1] == pytest.approx([4.0, 5.0, -3.5])                   # then to the task itself


# --- control loop ----------------------------------------------------------------------------------

def test_plans_once_per_task_and_commands_bounded_along_path():
    algo = _algo()
    algo.update_drone_state(_state(0, 0.0, 0.0, -1.8, 1 * SEC))
    r = algo.compute(1 * SEC)
    assert [e for e, _ in r.metadata['events']].count('rl_plan') == 1
    assert 'rl_policy_loaded' in [e for e, _ in r.metadata['events']]
    (cmd,) = r.movement_commands
    assert cmd.task_id == 101
    step = math.dist((cmd.target_x, cmd.target_y, cmd.target_z), (0.0, 0.0, -1.8))
    assert step <= 1.5 + 1e-9 and cmd.target_x > 0                    # toward the goal, speed cap
    algo.update_drone_state(_state(0, 1.0, 0.0, -1.8, 2 * SEC))
    r = algo.compute(2 * SEC)
    assert 'rl_plan' not in [e for e, _ in r.metadata['events']]       # no replanning on the same leg
    assert len(algo._planner.calls) == 1


def test_waits_for_takeoff_before_first_plan():
    algo = _algo()
    algo.update_drone_state(_state(0, -8.0, 7.0, -0.3, 1 * SEC))       # still climbing off the pad
    r = algo.compute(1 * SEC)
    assert not algo._planner.calls
    (cmd,) = r.movement_commands                                     # holds where it is (ignored by the controller)
    assert (cmd.target_x, cmd.target_y) == pytest.approx((-8.0, 7.0))


def test_plan_failure_holds_and_retries_without_fallback():
    planner = FakePlanner(feasible=False)
    algo = _algo(planner=planner)
    algo.update_drone_state(_state(0, 0.0, 0.0, -1.8, 1 * SEC))
    r = algo.compute(1 * SEC)
    assert 'rl_plan_failed' in [e for e, _ in r.metadata['events']]
    (cmd,) = r.movement_commands
    assert (cmd.target_x, cmd.target_y, cmd.target_z) == pytest.approx((0.0, 0.0, -1.8))  # hold, not fly
    algo.update_drone_state(_state(0, 0.05, 0.0, -1.8, int(1.5 * SEC)))
    algo.compute(int(1.5 * SEC))
    assert len(planner.calls) == 1                                   # retry only after retry_period
    algo.update_drone_state(_state(0, 0.05, 0.0, -1.8, int(3.1 * SEC)))
    r = algo.compute(int(3.1 * SEC))
    assert len(planner.calls) == 2 and planner.calls[0][2] != planner.calls[1][2]   # new seed
    (cmd,) = r.movement_commands
    assert (cmd.target_x, cmd.target_y) == pytest.approx((0.0, 0.0))  # still the original hold point


def test_replans_when_far_off_path():
    algo = _algo()
    algo.update_drone_state(_state(0, 0.0, 0.0, -1.8, 1 * SEC))
    algo.compute(1 * SEC)
    algo.update_drone_state(_state(0, 1.0, 4.0, -1.8, 2 * SEC))       # 4 m off the planned line
    r = algo.compute(2 * SEC)
    names = [e for e, _ in r.metadata['events']]
    assert 'rl_replan' in names and names.count('rl_plan') == 1


def test_higher_id_yields_to_lower_id_ahead_only():
    algo = _algo(tasks=[TaskInfo(101, 6.0, 0.0, -4.0), TaskInfo(102, -6.0, 0.0, -4.0)])
    algo.update_drone_state(_state(0, 2.0, 0.0, -1.8, 1 * SEC, state=INSPECTING, task=101))
    algo.update_drone_state(_state(1, 0.0, 0.0, -2.8, 1 * SEC, task=101))   # on its 2.8 m layer
    r = algo.compute(1 * SEC)
    (cmd,) = r.movement_commands                                      # only drone 1 is PATROLLING
    assert cmd.drone_id == 1
    assert (cmd.target_x, cmd.target_y) == pytest.approx((0.0, 0.0))  # holds: drone 0 is ahead, 2.2 m
    assert 'rl_yield' in [e for e, _ in r.metadata['events']]
    algo.update_drone_state(_state(1, 0.0, 0.0, -2.8, 2 * SEC, task=102))   # new leg away from drone 0
    algo.update_drone_state(_state(0, 2.0, 0.0, -1.8, 2 * SEC, state=INSPECTING, task=101))
    (cmd,) = algo.compute(2 * SEC).movement_commands
    assert cmd.target_x < 0.0                                          # moving away: no yield


def test_failed_silent_and_phantom_drones_get_no_commands():
    algo = _algo(num_drones=2)
    algo.update_drone_state(_state(0, 0.0, 0.0, -1.8, 10 * SEC, state=FAILED))
    algo.update_drone_state(_state(1, 0.0, 0.0, -1.8, 1 * SEC))        # silent for 9 s
    algo.update_drone_state(_state(5, 0.0, 0.0, -1.8, 10 * SEC))       # phantom id
    assert algo.compute(10 * SEC).movement_commands == []


def test_diagnostics_and_clearance_events_once_per_interval():
    obstacles = load_obstacles(os.path.join(ROOT, 'config/environment/factory_obstacles.yaml'))
    algo = _algo(obstacles=obstacles)
    algo.update_drone_state(_state(0, 0.0, -6.0, -1.8, 1 * SEC))
    algo.update_drone_state(_state(1, 3.0, -6.0, -2.8, 1 * SEC))
    ev = dict(algo.compute(1 * SEC).metadata['events'])
    clr = ev['rl_clearance']
    assert clr['active_drones'] == [0, 1]
    assert clr['min_separation'] == pytest.approx(math.dist((0, -6, -1.8), (3, -6, -2.8)), abs=1e-3)
    # nearest box surface over both drones (same definition as apf_clearance): drone 1 is 1.3 m
    # above the 1.5 m packing station (x 2.5..5.5, y -8..-6)
    assert clr['min_obstacle_distance'] == pytest.approx(1.3, abs=1e-3)
    assert 'rl_clearance' not in dict(algo.compute(int(1.5 * SEC)).metadata['events'])


def test_stall_reported_once_while_holding():
    algo = _algo(planner=FakePlanner(feasible=False))
    names = []
    for k in range(80):
        t = SEC + k * SEC // 10
        algo.update_drone_state(_state(0, 0.0, 0.0, -1.8, t))
        names += [e for e, _ in algo.compute(t).metadata['events']]
    assert names.count('rl_stall') == 1


# --- with the real policy (needs torch; run with the RL venv) ---------------------------------------

def _real_planner():
    torch = pytest.importorskip('torch')  # noqa: F841
    import sys
    repo = os.path.join(ROOT, 'rl-nmopso-factory-patrol')
    sys.path.insert(0, repo)
    from rlpatrol.planner import LegPlanner
    return LegPlanner(os.path.join(repo, 'results', 'ckpt', 'v2.pt'), threads=2)


def test_policy_loads_through_initialize_with_repo_config():
    pytest.importorskip('torch')
    tasks = [TaskInfo(t['id'], *t['position'], label=t['label'])
             for t in yaml.safe_load(open(os.path.join(ROOT, 'config/tasks/benchmark.yaml')))['tasks']]
    algo = RLNavigationAlgorithm({'algorithm_params': _params()})
    algo.initialize(3, tasks)                                          # real _load_planner()
    (name, info), = [e for e in algo._pending_events if e[0] == 'rl_policy_loaded']
    assert info['path'].endswith('vB_seed2.pt') and info['tasks_projected'] == [104, 105]
    assert info['budget'] and info['route_obs'] and info['keep_in'] == (-12.0, 12.0, -7.0, 7.0)


@pytest.mark.parametrize('scenario', ['benchmark', 'safety_stress'])
def test_closed_loop_kinematic_patrol_reaches_every_task_without_obstacle_contact(scenario):
    """Drones follow the commands with a first-order kinematic model (no PX4): every task of the
    scenario is reached by its auction-like owner, commands stay finite and bounded, and the flown
    paths keep clear of the factory boxes."""
    planner = _real_planner()
    obstacles = load_obstacles(os.path.join(ROOT, 'config/environment/factory_obstacles.yaml'))
    data = yaml.safe_load(open(os.path.join(ROOT, f'config/tasks/{scenario}.yaml')))['tasks']
    tasks = [TaskInfo(t['id'], *t['position']) for t in data]
    algo = RLNavigationAlgorithm({'algorithm_params': _params(), 'obstacles': obstacles})
    algo.initialize(3, tasks, planner=planner)
    zones = {d: tasks[d::3] for d in range(3)}                          # round-robin stand-in for the auction
    pos = {d: [d * 4.0 - 8.0, 7.0, tasks[d].z] for d in range(3)}       # after the controller's takeoff
    idx = {d: 0 for d in range(3)}
    reached = set()
    walls = [b for b in obstacles if b.obstacle_id not in ('floor', 'ceiling_barrier')]
    min_clear = math.inf
    for k in range(6000):
        t = SEC + k * SEC // 10
        for d in range(3):
            if idx[d] < len(zones[d]):
                algo.update_drone_state(_state(d, *pos[d], t, task=zones[d][idx[d]].task_id))
            else:
                algo.update_drone_state(_state(d, *pos[d], t, state=INSPECTING, task=0))
        r = algo.compute(t)
        assert not [e for e, _ in r.metadata['events'] if e == 'rl_plan_failed']
        for c in r.movement_commands:
            tgt = (c.target_x, c.target_y, c.target_z)
            assert all(math.isfinite(v) for v in tgt)
            step = [tgt[i] - pos[c.drone_id][i] for i in range(3)]
            assert math.sqrt(sum(s * s for s in step)) <= 1.5 + 1e-6
            pos[c.drone_id] = [pos[c.drone_id][i] + 0.1 * step[i] / 1.0 for i in range(3)]  # v = step / horizon
        for d in range(3):
            p = pos[d]
            min_clear = min(min_clear, min(math.dist(p, b.closest_point(p)) for b in walls))
            if idx[d] < len(zones[d]):
                g = zones[d][idx[d]]
                if math.dist(p, (g.x, g.y, g.z)) < 1.2:                    # controller WAYPOINT_RADIUS
                    reached.add(g.task_id)
                    pos[d] = [g.x, g.y, g.z]                              # controller holds the task point
                    idx[d] += 1
        if len(reached) == len(tasks):
            break
    assert reached == {t.task_id for t in tasks}, f'not reached: {set(t.task_id for t in tasks) - reached}'
    assert min_clear > 0.3, f'came within {min_clear:.2f} m of a box'
