"""NMOPSO navigation: legs planned by NMOPSO (Duong, Bui & Phung 2025), flown like the RL planner's.

NMOPSO is the multi-objective particle swarm path planner whose problem the RL policy was trained on
(same path encoding and MyCost objectives). This algorithm is the RL navigation algorithm with the
policy replaced by NMOPSO (rlpatrol.nmopso.NMOPSOPlanner, a vectorised port of the authors' NMOPSO.m
with their parameters): allocation (native auction), the flown path geometry (per-drone layers),
path following, the yield rule and the hold-on-failure behaviour are identical, so NMOPSO and RL
differ only in how a leg's path is found. See rl_nav.py for all of those.

Planning time is NMOPSO's defining cost (several seconds per leg at 500 iterations even vectorised,
against 0.1 s for the policy), so it is never done inside the 10 Hz coordinator tick:
  plan cache   legs between the scenario's fixed points (drone spawn points and tasks) are planned
               before the run by scripts/precompute_nmopso_cache.py with the same planner and loaded
               at start-up; a leg whose start is within cache_start_tolerance of a cached start and
               whose goal is the same task uses the cached path (the drone first flies straight to the
               cached start at its current altitude, as for a moved start in rl_nav.py);
  worker       any other leg (e.g. from wherever a drone was holding after a radio blackout) is
               planned online in a background thread; the drone holds its position until the plan
               arrives. Online plans are added to the cache.
The coordinator's decision time therefore measures the tick only; the planning time of every leg is
reported in the nmopso_plan events (plan_time_s, source cache | online).

Events: nmopso_planner_loaded, nmopso_plan, nmopso_plan_started, nmopso_plan_failed, plus every
rl_* event of rl_nav.py except rl_plan / rl_plan_failed / rl_policy_loaded.
"""
import json
import math
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from patrol_coordinator.algorithms.rl_nav import RLNavigationAlgorithm, RLParams, _norm, _sub, find_project_path


@dataclass
class NMOPSOParams(RLParams):
    """RL navigation parameters plus NMOPSO's; defaults mirror config/algorithms/nmopso.yaml."""
    max_iterations: int = 500
    population: int = 100
    repository: int = 50
    cache_file: str = 'config/algorithms/nmopso_cache.json'
    cache_start_tolerance: float = 1.0
    max_plans_per_tick: int = 3


def plan_to_dict(plan):
    return {'feasible': bool(plan.feasible), 'path': [[float(c) for c in q] for q in plan.path],
            'F': [float(f) if math.isfinite(f) else None for f in plan.F], 'method': plan.method,
            'start_free': [float(c) for c in plan.start_free], 'goal_free': [float(c) for c in plan.goal_free],
            'n_candidates': int(plan.n_candidates), 'n_feasible': int(plan.n_feasible),
            'plan_time_s': float(plan.plan_time_s), 'reason': plan.reason,
            'legs': len(plan.extra.get('legs', [])) or 1, 'decomposed': bool(plan.extra.get('decomposed', False))}


class _CachedPlan:
    """the fields of rlpatrol.planner.LegPlan that rl_nav.py reads, rebuilt from the cache file."""

    def __init__(self, d):
        import numpy as np
        self.feasible = d['feasible']
        self.path = np.array(d['path'], float)
        self.F = [math.inf if f is None else f for f in d['F']]
        self.method = d['method']
        self.start_free = np.array(d['start_free'], float)
        self.goal_free = np.array(d['goal_free'], float)
        self.n_candidates, self.n_feasible = d['n_candidates'], d['n_feasible']
        self.plan_time_s, self.reason = d['plan_time_s'], d.get('reason', '')
        self.extra = {'legs': [None] * d.get('legs', 1), 'decomposed': d.get('decomposed', False)}


class NMOPSONavigationAlgorithm(RLNavigationAlgorithm):
    """NMOPSO leg planner (cached + background thread) + the RL algorithm's path following."""

    def __init__(self, config: dict):
        super().__init__({**config, 'algorithm_params': {}})
        self.params = NMOPSOParams.from_dict(config.get('algorithm_params', {}) or {})
        self._cache = []                   # [(start (x, y), goal (x, y), plan)]
        self._pending = {}                 # drone -> (future, track, task_id, reason, submitted wall time)
        self._worker = ThreadPoolExecutor(max_workers=1, thread_name_prefix='nmopso')

    def get_name(self) -> str:
        return 'NMOPSO (multi-objective PSO leg planner, cached + background planning)'

    def _load_planner(self):
        p = self.params
        repo = find_project_path(p.repo_path)
        if repo not in sys.path:
            sys.path.insert(0, repo)
        try:
            from rlpatrol.nmopso import NMOPSOPlanner
        except ImportError as e:
            raise ImportError(f'cannot import rlpatrol.nmopso from {repo} ({e}); run the coordinator with the '
                              f'RL virtual environment (scripts/start_experiment.sh does this for --algorithm nmopso)')
        keep_in = ((-p.keep_in_x, p.keep_in_x, -p.keep_in_y, p.keep_in_y)
                   if p.keep_in_x > 0 and p.keep_in_y > 0 else None)
        return NMOPSOPlanner(max_it=p.max_iterations, n_pop=p.population, n_rep=p.repository, device=p.device,
                             threads=p.torch_threads, seed=p.seed, keep_in=keep_in)

    def initialize(self, num_drones, tasks, planner=None) -> None:
        super().initialize(num_drones, tasks, planner)
        self._pending_events = [e for e in self._pending_events if e[0] != 'rl_policy_loaded']
        path = find_project_path(self.params.cache_file)
        n = 0
        if os.path.isfile(path):
            data = json.load(open(path))
            if data.get('planner') == json.loads(json.dumps(self._planner.ckpt_info)):   # tuples -> lists
                for e in data['legs']:
                    self._cache.append((tuple(e['start']), tuple(e['goal']), _CachedPlan(e['plan'])))
                n = len(self._cache)
        self._pending_events.append(('nmopso_planner_loaded', {
            **self._planner.ckpt_info, 'cache_file': path, 'cached_legs': n,
            'cache_matches_planner': n > 0,
            'cruise_heights_m': [round(self.cruise_height(d), 3) for d in range(num_drones)]}))

    def reset(self) -> None:
        super().reset()
        self._pending.clear()

    def on_drone_failed(self, drone_id: int) -> None:
        super().on_drone_failed(drone_id)
        self._pending.pop(drone_id, None)

    # --- planning ---------------------------------------------------------------------------------------
    def _lookup(self, p, task):
        tol = self.params.cache_start_tolerance
        best = None
        for start, goal, plan in self._cache:
            if math.hypot(goal[0] - task.x, goal[1] - task.y) > 0.05:
                continue
            d = math.hypot(start[0] - p[0], start[1] - p[1])
            if d <= tol and (best is None or d < best[0]):
                best = (d, plan)
        return best[1] if best else None

    def _plan(self, drone_id, p, task, track, timestamp_ns, events, reason):
        if drone_id in self._pending:
            return
        plan = self._lookup(p, task)
        if plan is not None:
            self._apply(drone_id, p, task, track, plan, timestamp_ns, events, reason, 'cache', 0.0)
            return
        self._plan_count += 1
        seed = self.params.seed + self._plan_count
        fut = self._worker.submit(self._planner.plan_route, (p[0], p[1]), (task.x, task.y), seed)
        self._pending[drone_id] = (fut, track, task.task_id, reason, time.perf_counter(), (p[0], p[1]))
        events.append(('nmopso_plan_started', {'drone_id': drone_id, 'task_id': task.task_id, 'reason': reason,
                                               'start': [round(p[0], 3), round(p[1], 3)]}))

    def _collect(self, timestamp_ns, events):
        """apply finished background plans to the drones that still fly the same leg."""
        for drone_id, (fut, track, task_id, reason, t0, start) in list(self._pending.items()):
            if not fut.done():
                continue
            del self._pending[drone_id]
            try:
                plan = fut.result()
            except Exception as e:                                   # noqa: BLE001 (reported, drone holds)
                events.append(('nmopso_plan_failed', {'drone_id': drone_id, 'task_id': task_id,
                                                      'detail': f'{type(e).__name__}: {e}'}))
                track.failed_at_ns, track.attempts = timestamp_ns, track.attempts + 1
                continue
            if plan.feasible:
                goal = self._tasks_by_id[task_id]
                self._cache.append((start, (goal.x, goal.y), plan))
            if self._tracks.get(drone_id) is not track or track.task_id != task_id:
                continue                                             # the drone moved on meanwhile
            s = self._drone_states.get(drone_id)
            p = (s.x, s.y, s.z) if s else (start[0], start[1], 0.0)
            task = self._tasks_by_id[task_id]
            self._apply(drone_id, p, task, track, plan, timestamp_ns, events, reason, 'online',
                        time.perf_counter() - t0)

    def _apply(self, drone_id, p, task, track, plan, timestamp_ns, events, reason, source, wait_s):
        base = {'drone_id': drone_id, 'task_id': task.task_id, 'reason': reason, 'source': source,
                'plan_time_s': round(plan.plan_time_s, 4), 'wait_s': round(wait_s, 3), 'method': plan.method,
                'candidates': plan.n_candidates, 'feasible_candidates': plan.n_feasible,
                'start': [round(p[0], 3), round(p[1], 3)], 'goal': [round(task.x, 3), round(task.y, 3)]}
        track.attempts += 1
        if not plan.feasible:
            track.path, track.failed_at_ns = None, timestamp_ns
            track.hold = track.hold or tuple(p)
            events.append(('nmopso_plan_failed', {**base, 'attempt': track.attempts, 'detail': plan.reason}))
            return
        track.path, track.s, track.hold, track.failed_at_ns = self.flight_path(drone_id, p, task, plan), 0.0, None, 0
        events.append(('nmopso_plan', {
            **base, 'F': [round(float(f), 6) if math.isfinite(f) else None for f in plan.F],
            'decomposed': bool(plan.extra.get('decomposed', False)),
            'sub_legs': len(plan.extra.get('legs', [])) or 1,
            'path_length_m': round(track.path.length, 3),
            'straight_distance_m': round(_norm(_sub(track.path.points[-1], p)), 3),
            'cruise_height_m': round(self.cruise_height(drone_id), 3),
        }))

    def compute(self, timestamp_ns: int):
        events = []
        self._collect(timestamp_ns, events)
        result = super().compute(timestamp_ns)
        result.metadata['events'] = events + result.metadata['events']
        return result

    def get_metrics(self) -> dict:
        return {**super().get_metrics(), 'cached_legs': len(self._cache), 'pending_plans': len(self._pending)}
