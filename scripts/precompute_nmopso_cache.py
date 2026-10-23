#!/usr/bin/env python3
"""Precompute the NMOPSO plan cache used by the 'nmopso' algorithm (nmopso_nav.py).

    rl-nmopso-factory-patrol/.venv/bin/python scripts/precompute_nmopso_cache.py [--workers 12]

Plans every leg between the fixed points of the experiment scenarios: each drone's spawn point
(start_experiment.sh: x = 4 i - 8, y = 7) to each task, and each task to each other task, for the task
files of every config/experiments/*.yaml. The planner and its parameters are read from
config/algorithms/nmopso.yaml (section nmopso), exactly as the coordinator builds it; the cache records
them and the coordinator ignores a cache made with different ones. Legs are planned in parallel
processes (one torch thread each); a leg's seed is fixed by its index, so the cache is reproducible.
"""
import os
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):   # one thread per worker process:
    os.environ.setdefault(_v, '1')                                          # 13 x 16 BLAS threads thrash
import argparse
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CFG = yaml.safe_load(open(ROOT / 'config/algorithms/nmopso.yaml'))['nmopso']
sys.path.insert(0, str(ROOT / CFG['repo_path']))
sys.path.insert(0, str(ROOT / 'factory_patrol_ws/src/patrol_coordinator'))


def make_planner(threads):
    from rlpatrol.nmopso import NMOPSOPlanner
    kx, ky = CFG['keep_in_x'], CFG['keep_in_y']
    return NMOPSOPlanner(max_it=CFG['max_iterations'], n_pop=CFG['population'], n_rep=CFG['repository'],
                         device=CFG['device'], threads=threads, seed=CFG['seed'],
                         keep_in=(-kx, kx, -ky, ky) if kx > 0 and ky > 0 else None)


_planner = None


def plan_leg(job):
    global _planner
    if _planner is None:
        _planner = make_planner(1)
    i, start, goal = job
    from patrol_coordinator.algorithms.nmopso_nav import plan_to_dict
    plan = _planner.plan_route(start, goal, seed=CFG['seed'] + 100000 + i)
    return {'start': list(start), 'goal': list(goal), 'plan': plan_to_dict(plan)}


def fixed_points(num_drones):
    spawns = [(4.0 * i - 8.0, 7.0) for i in range(num_drones)]
    tasks = set()
    for f in sorted((ROOT / 'config/experiments').glob('*.yaml')):
        exp = (yaml.safe_load(open(f)) or {}).get('mission', {})
        tf = exp.get('tasks_file')
        if tf:
            for t in (yaml.safe_load(open(ROOT / tf)) or {}).get('tasks', []):
                tasks.add((float(t['position'][0]), float(t['position'][1])))
    return spawns, sorted(tasks)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--workers', type=int, default=12)
    ap.add_argument('--drones', type=int, default=3)
    ap.add_argument('--out', default=str(ROOT / CFG['cache_file']))
    a = ap.parse_args()
    spawns, tasks = fixed_points(a.drones)
    legs = [(s, t) for s in spawns for t in tasks] + [(s, t) for s in tasks for t in tasks if s != t]
    jobs = [(i, s, t) for i, (s, t) in enumerate(legs)]
    print(f'{len(spawns)} spawn points, {len(tasks)} tasks -> {len(jobs)} legs on {a.workers} workers')
    t0 = time.time()
    out = []
    with Pool(a.workers) as pool:
        for k, r in enumerate(pool.imap_unordered(plan_leg, jobs), 1):
            out.append(r)
            if k % 10 == 0 or k == len(jobs):
                print(f'  {k}/{len(jobs)} legs, {time.time() - t0:.0f} s')
    info = make_planner(1).ckpt_info
    bad = [r for r in out if not r['plan']['feasible']]
    json.dump({'planner': json.loads(json.dumps(info)), 'created': time.strftime('%Y-%m-%dT%H:%M:%S'),
               'wall_time_s': round(time.time() - t0, 1),
               'plan_time_s_median': sorted(r['plan']['plan_time_s'] for r in out)[len(out) // 2],
               'legs': out}, open(a.out, 'w'))
    print(f'wrote {a.out}: {len(out)} legs ({len(bad)} infeasible) in {time.time() - t0:.0f} s')


if __name__ == '__main__':
    main()
