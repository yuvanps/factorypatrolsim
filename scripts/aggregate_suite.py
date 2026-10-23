#!/usr/bin/env python3
"""Aggregate a benchmark suite (scripts/run_suite.sh) into per-scenario comparison tables.

    python3 scripts/aggregate_suite.py experiment_results/suites/<suite_name>

Reads <suite>/manifest.csv and every run's summary CSV (experiment_results/summaries/), and writes
    <suite>/runs.csv        one row per run (manifest + summary columns)
    <suite>/aggregate.csv   one row per (scenario, algorithm, metric): n, mean, std, 95 % CI
    <suite>/aggregate.md    the same as tables, with the best algorithm per metric

Statistics: mean over the runs that have the metric; 95 % confidence interval of the mean with the
t distribution (n - 1 degrees of freedom). The best algorithm of a metric is the best mean in the
metric's direction; it is reported as a clear winner only if its interval does not overlap the
runner-up's, otherwise as a tie. Mission metrics (time, distance, ...) are only averaged over runs
that completed the mission; safety and fault metrics over every run that has them. Runs the watchdog
stopped for an infrastructure reason (disk low, PX4 log too big; see scripts/run_guarded.sh) say
nothing about the algorithm: they are kept in runs.csv but left out of every statistic.
"""
import csv
import math
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INFRA_STOPS = ('disk below', 'log too big')
T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
       15: 2.131, 20: 2.086, 30: 2.042}

# metric -> (label, unit, better: "low" | "high", completed runs only)
METRICS = {
    'task_completion_rate_percent': ('Task completion', '%', 'high', False),
    'mission_completion_time_s': ('Mission completion time', 's', 'low', True),
    'total_flight_distance_m': ('Total flight distance', 'm', 'low', True),
    'total_battery_consumed_percent': ('Battery consumed (sum of drones)', '%', 'low', True),
    'minimum_inter_drone_distance_m': ('Minimum drone separation', 'm', 'high', False),
    'min_obstacle_clearance_m': ('Minimum obstacle clearance', 'm', 'high', False),
    'obstacle_near_miss_s': ('Obstacle near-miss time (< 0.6 m)', 'drone-s', 'low', False),
    'obstacle_contacts': ('Obstacle contacts (< 0.3 m)', 'episodes', 'low', False),
    'separation_near_miss_s': ('Drone near-miss time (< 1.0 m)', 's', 'low', False),
    'separation_contacts': ('Drone contacts (< 0.6 m)', 'episodes', 'low', False),
    'mean_task_idleness_s': ('Average task idleness', 's', 'low', False),
    'max_task_idleness_s': ('Worst task idleness', 's', 'low', False),
    'decision_time_mean_ms': ('Decision time, mean (coordinator)', 'ms', 'low', False),
    'decision_time_max_ms': ('Decision time, max (coordinator)', 'ms', 'low', False),
    'allocation_time_mean_ms': ('Allocation time, mean (on board)', 'ms', 'low', False),
    'alloc_first_assignment_s': ('Allocation latency: first assignment', 's', 'low', False),
    'alloc_all_assigned_s': ('Allocation latency: all tasks assigned', 's', 'low', False),
    'allocation_to_mct_ratio': ('Allocation time / MCT', '-', 'low', True),
    'workload_imbalance_tasks': ('Workload imbalance, tasks (1 - Jain)', '-', 'low', False),
    'workload_imbalance_distance': ('Workload imbalance, distance (1 - Jain)', '-', 'low', False),
    'workload_gini_tasks': ('Workload Gini, tasks', '-', 'low', False),
    'workload_gini_distance': ('Workload Gini, distance', '-', 'low', False),
    'task_reallocations': ('Task reallocations', 'count', 'low', False),
    'reallocations_per_min': ('Task reallocations per minute', '1/min', 'low', False),
    'separation_p1_m': ('Swarm separation, 1st percentile', 'm', 'high', False),
    'separation_p5_m': ('Swarm separation, 5th percentile', 'm', 'high', False),
    'separation_violations': ('Separation violations (< 1.0 m)', 'episodes', 'low', False),
    'detection_s': ('Comm loss: detection', 's', 'low', False),
    'reassignment_s': ('Comm loss: task reassignment', 's', 'low', False),
    'reassign_after_detection_s': ('Comm loss: reassignment after detection', 's', 'low', False),
    'coverage_restored_s': ('Comm loss: coverage restored', 's', 'low', False),
    'rejoin_s': ('Comm loss: rejoin after link back', 's', 'low', False),
    'resume_s': ('Comm loss: back in service', 's', 'low', False),
    'min_separation_during_loss_m': ('Comm loss: min separation of the lost drone', 'm', 'high', False),
    'loss_safety_depth_m': ('Comm loss: safety degradation depth (1.0 m - min)', 'm', 'low', False),
    'loss_safety_time_s': ('Comm loss: time below 1.0 m', 's', 'low', False),
}
ORDER = ['auction', 'apf', 'rl', 'nmopso']


def num(v):
    try:
        x = float(v)
        return x if math.isfinite(x) else None
    except (TypeError, ValueError):
        return None


def stats(xs):
    n = len(xs)
    if not n:
        return None
    m = sum(xs) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1)) if n > 1 else 0.0
    t = None
    if n > 1:
        dof = n - 1
        t = T95.get(dof) or (T95[min(k for k in T95 if k >= dof)] if dof <= max(T95) else 1.96)
    hw = t * sd / math.sqrt(n) if t else None
    return {'n': n, 'mean': m, 'std': sd, 'ci_lo': m - hw if hw is not None else None,
            'ci_hi': m + hw if hw is not None else None}


def main():
    suite = Path(sys.argv[1]).resolve()
    rows = []
    for r in csv.DictReader(open(suite / 'manifest.csv')):
        if not r['run_id']:
            rows.append({**r, 'status': 'no summary'})
            continue
        f = next((ROOT / 'experiment_results' / 'summaries').glob(f"{r['run_id']}_*.csv"), None)
        s = next(csv.DictReader(open(f))) if f else {}
        rows.append({**s, **r, 'status': s.get('status', 'no summary')})
    keys = sorted({k for r in rows for k in r}, key=lambda k: (k not in ('run_id', 'algorithm', 'scenario', 'repeat'), k))
    with open(suite / 'runs.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)

    groups = defaultdict(list)
    infra = [r for r in rows if r.get('stop_reason', '').startswith(INFRA_STOPS)]
    for r in rows:
        if r not in infra:
            groups[(r['scenario'], r['algorithm'])].append(r)
    scenarios = list(dict.fromkeys(r['scenario'] for r in rows))
    agg, md = [], [f'# Benchmark suite `{suite.name}`', '',
                   'Mean ± 95 % confidence interval over the runs (n in brackets). **Bold**: best mean; '
                   '"tie" when its interval overlaps the runner-up\'s. Generated by `scripts/aggregate_suite.py`; '
                   'metric definitions in `docs/METRICS.md`.', '']
    if infra:
        md += ['Left out (stopped for an infrastructure reason, not an algorithm outcome): ' +
               ', '.join(f"{r['run_id'] or '?'} ({r['algorithm']}, {r['scenario']}: {r['stop_reason']})" for r in infra), '']
    for scen in scenarios:
        algos = sorted({a for s, a in groups if s == scen}, key=lambda a: ORDER.index(a) if a in ORDER else 99)
        md += [f'## {scen}', '']
        crash = {a: sum('excluded' in (r.get('notes') or '') for r in groups[(scen, a)]) for a in algos}
        done = {a: sum(r['status'] == 'completed' for r in groups[(scen, a)]) for a in algos}
        md += ['| Metric | ' + ' | '.join(algos) + ' | Best |', '|---|' + '---|' * (len(algos) + 1)]
        md.append('| Runs completed / total | ' + ' | '.join(f'{done[a]} / {len(groups[(scen, a)])}' for a in algos) + ' | |')
        md.append('| Runs with a crashed drone | ' + ' | '.join(str(crash[a]) for a in algos) + ' | |')
        for key, (label, unit, better, completed_only) in METRICS.items():
            st = {}
            for a in algos:
                runs = [r for r in groups[(scen, a)] if not completed_only or r['status'] == 'completed']
                st[a] = stats([x for x in (num(r.get(key)) for r in runs) if x is not None])
                if st[a]:
                    agg.append({'scenario': scen, 'algorithm': a, 'metric': key, **{k: (round(v, 4) if isinstance(v, float) else v)
                                                                                   for k, v in st[a].items()}})
            have = [a for a in algos if st[a]]
            if not have:
                continue
            ranked = sorted(have, key=lambda a: st[a]['mean'], reverse=(better == 'high'))
            best = ranked[0]
            verdict = ''
            if len(ranked) > 1 and len({round(st[a]['mean'], 9) for a in ranked}) > 1:
                b, r2 = st[best], st[ranked[1]]
                overlap = (b['ci_lo'] is None or r2['ci_lo'] is None or
                           (b['ci_lo'] <= r2['ci_hi'] and r2['ci_lo'] <= b['ci_hi']))
                verdict = f'{best} (tie with {ranked[1]})' if overlap else f'**{best}**'
            cells = []
            for a in algos:
                s = st[a]
                if not s:
                    cells.append('–')
                    continue
                hw = f' ± {(s["ci_hi"] - s["mean"]):.2f}' if s['ci_hi'] is not None else ''
                prec = 3 if 0 < abs(s['mean']) < 0.1 else 2
                hw = f' ± {(s["ci_hi"] - s["mean"]):.{prec}f}' if s['ci_hi'] is not None else ''
                txt = f'{s["mean"]:.{prec}f}{hw} ({s["n"]})'
                cells.append(f'**{txt}**' if a == best and verdict.startswith('**') else txt)
            md.append(f'| {label} ({unit}, {"lower" if better == "low" else "higher"} is better) | ' + ' | '.join(cells) + f' | {verdict} |')
        md.append('')
    with open(suite / 'aggregate.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['scenario', 'algorithm', 'metric', 'n', 'mean', 'std', 'ci_lo', 'ci_hi'])
        w.writeheader()
        w.writerows(agg)
    (suite / 'aggregate.md').write_text('\n'.join(md) + '\n')
    print('\n'.join(md))


if __name__ == '__main__':
    main()
