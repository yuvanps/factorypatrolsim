"""Tests for the NMOPSO navigation algorithm (patrol_coordinator.algorithms.nmopso_nav): plan cache,
background planning and the hand-over of finished plans. Planning itself is faked (no torch)."""

import json
import os
import threading
import time

import yaml

from patrol_coordinator.algorithm_base import TaskInfo
from patrol_coordinator.algorithms import get_algorithm_class
from patrol_coordinator.algorithms.nmopso_nav import NMOPSONavigationAlgorithm, NMOPSOParams, plan_to_dict
from test_rl_nav import ROOT, SEC, FakePlanner, _state


def _params(**over):
    with open(os.path.join(ROOT, 'config/algorithms/nmopso.yaml')) as f:
        p = yaml.safe_load(f)['nmopso']
    p.update(over)
    return p


class SlowPlanner(FakePlanner):
    """plan_route blocks until released, so a test can observe the drone while a plan is pending."""

    def __init__(self):
        super().__init__()
        self.release = threading.Event()

    def plan_route(self, start, goal, seed=None):
        self.release.wait(5)
        return super().plan_route(start, goal, seed)


def _algo(tmp_path, planner, cache_legs=(), **over):
    cache = tmp_path / 'cache.json'
    json.dump({'planner': planner.ckpt_info, 'legs': [
        {'start': list(s), 'goal': list(g), 'plan': plan_to_dict(FakePlanner().plan_route(s, g))}
        for s, g in cache_legs]}, open(cache, 'w'))
    algo = NMOPSONavigationAlgorithm({'algorithm_params': _params(cache_file=str(cache), **over), 'obstacles': []})
    algo.initialize(3, [TaskInfo(101, 6.0, 0.0, -4.0)], planner=planner)
    return algo


def _wait_events(algo, t, n=50):
    """run compute until a plan is applied (or n ticks); returns all events"""
    out = []
    for k in range(n):
        algo.update_drone_state(_state(0, 0.0, 0.0, -1.8, t + k * SEC // 10))
        out += algo.compute(t + k * SEC // 10).metadata['events']
        if any(e[0] == 'nmopso_plan' for e in out):
            break
        time.sleep(0.02)
    return out


def test_registry_and_config():
    assert get_algorithm_class('nmopso') is NMOPSONavigationAlgorithm
    p = NMOPSOParams.from_dict(_params())
    assert (p.max_iterations, p.population, p.repository) == (500, 100, 50)


def test_cached_leg_is_used_without_planning(tmp_path):
    planner = FakePlanner()
    algo = _algo(tmp_path, planner, cache_legs=[((0.3, 0.2), (6.0, 0.0))])
    ev = _wait_events(algo, 1 * SEC, n=1)
    plan = [e[1] for e in ev if e[0] == 'nmopso_plan']
    assert plan and plan[0]['source'] == 'cache' and planner.calls == []
    loaded = [e[1] for e in algo.compute(2 * SEC).metadata['events'] if e[0] == 'nmopso_planner_loaded']
    assert loaded == [] or loaded[0]['cached_legs'] == 1


def test_uncached_leg_is_planned_in_background_and_drone_holds(tmp_path):
    planner = SlowPlanner()
    algo = _algo(tmp_path, planner)
    algo.update_drone_state(_state(0, 0.0, 0.0, -1.8, SEC))
    r = algo.compute(SEC)
    started = [e for e in r.metadata['events'] if e[0] == 'nmopso_plan_started']
    assert started and r.movement_commands[0].target_x == 0.0       # holds while the plan is pending
    planner.release.set()
    ev = _wait_events(algo, 2 * SEC)
    plan = [e[1] for e in ev if e[0] == 'nmopso_plan']
    assert plan and plan[0]['source'] == 'online' and len(planner.calls) == 1
    # the online plan is now cached: a second drone starting nearby uses it
    assert algo._lookup((0.2, 0.1), algo._tasks_by_id[101]) is not None


def test_stale_background_plan_is_not_applied(tmp_path):
    planner = SlowPlanner()
    algo = _algo(tmp_path, planner)
    algo.update_drone_state(_state(0, 0.0, 0.0, -1.8, SEC))
    algo.compute(SEC)
    algo.on_drone_failed(0)                                          # the drone is gone meanwhile
    planner.release.set()
    time.sleep(0.2)
    algo.update_drone_state(_state(1, 4.0, 7.0, -2.8, 2 * SEC, task=0))
    ev = algo.compute(2 * SEC).metadata['events']
    assert not any(e[0] == 'nmopso_plan' for e in ev)
