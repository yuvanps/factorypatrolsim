#!/usr/bin/env python3
"""Comparison figures of a benchmark suite (scripts/run_suite.sh + scripts/aggregate_suite.py).

    python3 presentation/scripts/suite_figures.py experiment_results/suites/<suite_name>

One figure per scenario (<suite>/figures/<scenario>.png): small multiples, one panel per metric,
each algorithm one row: the dot is the mean over the runs, the line its 95 % confidence interval,
the light dots the individual runs. Every number is read from <suite>/aggregate.csv and runs.csv;
the table version of the same data is <suite>/aggregate.md.
"""
import csv
import math
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402

ALGOS = ['auction', 'apf', 'rl', 'nmopso']
NAMES = {'auction': 'Auction', 'apf': 'APF', 'rl': 'RL (vB)', 'nmopso': 'NMOPSO'}
COLORS = {'auction': '#2a78d6', 'apf': '#eb6834', 'rl': '#1baf7a', 'nmopso': '#c2185b'}   # categorical slots 1-4 (validated)
INK, INK2, GRID, SURFACE = '#0b0b0b', '#52514e', '#e6e5e0', '#fcfcfb'
PANELS = {
    'default': [('mission_completion_time_s', 'Mission completion time (s)', 'low'),
                ('total_flight_distance_m', 'Total flight distance (m)', 'low'),
                ('min_obstacle_clearance_m', 'Min obstacle clearance (m)', 'high'),
                ('minimum_inter_drone_distance_m', 'Min drone separation (m)', 'high'),
                ('mean_task_idleness_s', 'Average task idleness (s)', 'low'),
                ('decision_time_max_ms', 'Worst decision time (ms)', 'low')],
    'comm_loss': [('detection_s', 'Detection (s)', 'low'),
                  ('coverage_restored_s', 'Coverage restored (s)', 'low'),
                  ('resume_s', 'Back in service after link (s)', 'low'),
                  ('min_separation_during_loss_m', 'Min separation of lost drone (m)', 'high'),
                  ('max_task_idleness_s', 'Worst task idleness (s)', 'low'),
                  ('obstacle_contacts', 'Obstacle contacts (episodes)', 'low')],
}
COMPLETED_ONLY = {'mission_completion_time_s', 'total_flight_distance_m'}

plt.rcParams.update({
    'font.family': 'DejaVu Sans', 'font.size': 10, 'axes.edgecolor': GRID, 'axes.labelcolor': INK2,
    'xtick.color': INK2, 'ytick.color': INK, 'axes.titlesize': 10.5, 'axes.titleweight': 'bold',
    'axes.titlecolor': INK, 'figure.facecolor': SURFACE, 'axes.facecolor': SURFACE, 'savefig.facecolor': SURFACE,
})


def num(v):
    try:
        x = float(v)
        return x if math.isfinite(x) else None
    except (TypeError, ValueError):
        return None


def main():
    suite = Path(sys.argv[1]).resolve()
    agg = {(r['scenario'], r['algorithm'], r['metric']): r for r in csv.DictReader(open(suite / 'aggregate.csv'))}
    runs = defaultdict(list)
    for r in csv.DictReader(open(suite / 'runs.csv')):
        if r.get('stop_reason', '').startswith(('disk below', 'log too big')):
            continue                                 # infrastructure stop, left out like in aggregate.md
        runs[(r['scenario'], r['algorithm'])].append(r)
    out = suite / 'figures'
    out.mkdir(exist_ok=True)
    for scen in sorted({s for s, _ in runs}):
        panels = PANELS['comm_loss' if scen.startswith('comm_loss') else 'default']
        if not any(num(r.get('detection_s')) is not None for k, rs in runs.items() if k[0] == scen for r in rs):
            # nobody detects a loss of the orchestrator (drone 0 runs the detector): show the time instead
            panels = [('mission_completion_time_s', 'Mission completion time (s)', 'low') if p[0] == 'detection_s'
                      else p for p in panels]
        algos = [a for a in ALGOS if (scen, a) in runs]
        fig, axes = plt.subplots(2, 3, figsize=(12, 5.6))
        for ax, (key, title, better) in zip(axes.flat, panels):
            for i, a in enumerate(reversed(algos)):
                vals = [num(r.get(key)) for r in runs[(scen, a)]
                        if key not in COMPLETED_ONLY or r.get('status') == 'completed']
                vals = [v for v in vals if v is not None]
                ax.scatter(vals, [i] * len(vals), s=18, color=COLORS[a], alpha=0.35, linewidths=0, zorder=2)
                s = agg.get((scen, a, key))
                if s and s['mean']:
                    m = float(s['mean'])
                    if s['ci_lo'] and s['ci_hi']:
                        ax.plot([float(s['ci_lo']), float(s['ci_hi'])], [i, i], color=COLORS[a], lw=2,
                                solid_capstyle='round', zorder=3)
                    ax.scatter([m], [i], s=64, color=COLORS[a], edgecolors=SURFACE, linewidths=2, zorder=4)
                elif not vals:
                    ax.text(0.02, i, 'n/a', transform=ax.get_yaxis_transform(), va='center', color=INK2, fontsize=9)
            ax.set_yticks(range(len(algos)))
            ax.set_yticklabels([NAMES[a] for a in reversed(algos)])
            ax.set_ylim(-0.6, len(algos) - 0.4)
            ax.set_title(title, loc='left')
            ax.set_xlabel('lower is better' if better == 'low' else 'higher is better', fontsize=8.5)
            ax.grid(axis='x', color=GRID, lw=1)
            ax.set_axisbelow(True)
            for side in ('top', 'right', 'left'):
                ax.spines[side].set_visible(False)
            ax.tick_params(axis='y', length=0)
        n = {a: len(runs[(scen, a)]) for a in algos}
        done = {a: sum(r.get('status') == 'completed' for r in runs[(scen, a)]) for a in algos}
        crash = {a: sum('excluded' in (r.get('notes') or '') for r in runs[(scen, a)]) for a in algos}
        fig.suptitle(f'{scen}: 3 drones', x=0.01, y=0.985, ha='left', fontsize=12.5, fontweight='bold', color=INK)
        fig.text(0.01, 0.925, ';   '.join(f'{NAMES[a]}: {done[a]}/{n[a]} runs completed, {crash[a]} with a crashed drone'
                                          for a in algos), fontsize=9.5, color=INK2)
        fig.text(0.01, 0.005, 'Dot: mean over runs; line: 95 % confidence interval; light dots: individual runs. '
                 'Time and distance: completed runs only. Definitions: docs/METRICS.md.', fontsize=8.5, color=INK2)
        fig.tight_layout(rect=(0, 0.03, 1, 0.91))
        fig.savefig(out / f'{scen}.png', dpi=150)
        plt.close(fig)
        print('wrote', out / f'{scen}.png')


if __name__ == '__main__':
    main()
