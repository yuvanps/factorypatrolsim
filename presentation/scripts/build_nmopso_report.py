#!/usr/bin/env python3
"""NMOPSO preliminary report (PDF): external NMOPSO run(s) placed against a benchmark suite.

    presentation/.venv/bin/python presentation/scripts/build_nmopso_report.py \
        experiment_results/suites/<suite> experiment_results/external/nmopso [docs/nmopso_report.pdf]

The NMOPSO folder holds summary CSVs (<run_id>_nmopso_<scenario>_3drones.csv) and, per run,
<run_id>/metrics_detail.json, produced by the same metric code (metrics_summary.py). With fewer than
two NMOPSO runs per scenario no statistics are possible: each NMOPSO value is placed against the
distribution of the suite's runs (range and rank), and the report says so.
"""
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
from reportlab.lib.units import cm  # noqa: E402
from reportlab.platypus import Paragraph  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_report as br   # noqa: E402
import report_figures as rf  # noqa: E402

sys.path.insert(0, str(rf.ROOT / 'scripts'))
from aggregate_suite import METRICS  # noqa: E402

NM, NM_NAME, NM_COLOR = 'nmopso', 'NMOPSO', '#7a52c7'
TITLE = 'NMOPSO in the factory patrol benchmark: preliminary results'

# (metric, short title) shown in the comparison figure / table, in this order
FIG_METRICS = [
    ('mission_completion_time_s', 'Mission time (s)'),
    ('total_flight_distance_m', 'Total flight distance (m)'),
    ('mean_task_idleness_s', 'Average task idleness (s)'),
    ('minimum_inter_drone_distance_m', 'Min. drone separation (m)'),
    ('separation_p5_m', 'Separation, 5th pct. (m)'),
    ('min_obstacle_clearance_m', 'Min. obstacle clearance (m)'),
    ('obstacle_near_miss_s', 'Obstacle near-miss (drone-s)'),
    ('workload_imbalance_distance', 'Imbalance, distance'),
]
NOT_COMPARABLE = {'alloc_first_assignment_s', 'alloc_all_assigned_s'}   # see the differences table
TABLE_METRICS = [
    'task_completion_rate_percent', 'mission_completion_time_s', 'total_flight_distance_m',
    'total_battery_consumed_percent', 'mean_task_idleness_s', 'max_task_idleness_s',
    'minimum_inter_drone_distance_m', 'separation_p1_m', 'separation_p5_m', 'separation_violations',
    'separation_near_miss_s', 'separation_contacts', 'min_obstacle_clearance_m', 'obstacle_near_miss_s',
    'obstacle_contacts', 'workload_imbalance_tasks', 'workload_imbalance_distance', 'workload_gini_distance',
    'task_reallocations', 'alloc_first_assignment_s', 'alloc_all_assigned_s', 'decision_time_mean_ms',
]


class External:
    """NMOPSO runs: summary rows + details, by scenario."""

    def __init__(self, path):
        self.path = Path(path).resolve()
        self.runs = defaultdict(list)
        for f in sorted(self.path.glob(f'*_{NM}_*.csv')):
            for r in csv.DictReader(open(f)):
                self.runs[r['scenario']].append(r)

    def detail(self, run):
        try:
            return json.load(open(self.path / run['run_id'] / 'metrics_detail.json'))
        except (OSError, ValueError):
            return {}

    def values(self, scen, metric):
        rows = self.runs.get(scen, [])
        return [v for v in (rf.num(r.get(metric)) for r in rows
                            if metric not in rf.COMPLETED_ONLY or r.get('status') == 'completed') if v is not None]


def fmt(x, d=None):
    if x is None:
        return '–'
    if d is None:
        d = 3 if abs(x) < 0.1 and x != 0 else (2 if abs(x) < 10 else 1)
    return f'{x:.{d}f}'


def placement(x, vals, better):
    """where a single NMOPSO value x falls among the n runs of one algorithm"""
    if x is None or not vals:
        return '–'
    n = len(vals)
    good = (lambda v: v < x) if better == 'low' else (lambda v: v > x)   # runs better than NMOPSO
    k = sum(good(v) for v in vals)
    ties = sum(v == x for v in vals)
    if k == 0 and ties == 0:
        return f'better than all {n}'
    if k + ties == n and k == n:
        return f'worse than all {n}'
    if ties == n:
        return f'equal to all {n}'
    return f'within range ({k} of {n} better)'


# ------------------------------------------------------------------------------------------- figures
def dot_figure(suite, ext, scen, out):
    algos = rf.ALGOS + [NM]
    fig, axes = plt.subplots(len(FIG_METRICS) // 2, 2, figsize=(7.2, 1.25 * len(FIG_METRICS) // 2 + 0.3))
    for ax, (key, title) in zip(axes.flat, FIG_METRICS):
        for k, a in enumerate(reversed(algos)):
            if a == NM:
                vals = ext.values(scen, key)
                ax.scatter(vals, [k] * len(vals), s=55, marker='D', color=NM_COLOR, edgecolors=rf.SURFACE,
                           linewidths=1.2, zorder=4)
                if not vals:
                    ax.text(0.02, k, 'n/a', transform=ax.get_yaxis_transform(), va='center', color=rf.INK2,
                            fontsize=7)
                continue
            vals = suite.values(scen, a, key)
            ax.scatter(vals, [k] * len(vals), s=12, color=rf.COLORS[a], alpha=0.4, linewidths=0, zorder=2)
            st = suite.stat(scen, a, key)
            if st:
                m, hw, _ = st
                ax.plot([m - hw, m + hw], [k, k], color=rf.COLORS[a], lw=2, solid_capstyle='round', zorder=3)
                ax.scatter([m], [k], s=36, color=rf.COLORS[a], edgecolors=rf.SURFACE, linewidths=1.3, zorder=4)
        ax.set_yticks(range(len(algos)))
        ax.set_yticklabels([NM_NAME if a == NM else rf.NAMES[a] for a in reversed(algos)], fontsize=7.5)
        ax.set_ylim(-0.6, len(algos) - 0.4)
        better = METRICS[key][2]
        ax.set_title(f'{title}, {"lower" if better == "low" else "higher"} better', fontsize=7.3, loc='left')
        ax.tick_params(axis='x', labelsize=7)
        ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(4))
        ax.margins(x=0.12)
        rf._style(ax)
    fig.tight_layout(h_pad=1.2, w_pad=1.5)
    fig.savefig(out, dpi=200)
    plt.close(fig)
    return out


def _cdf(hist):
    xs = sorted(hist)
    tot = sum(hist.values())
    cum, ys = 0, []
    for x in xs:
        cum += hist[x]
        ys.append(cum / tot)
    return [x + 0.25 for x in xs], ys


def separation_figure(suite, ext, scen, out, xmax=6.0):
    fig, ax = plt.subplots(figsize=(5.2, 2.6))
    for a in rf.ALGOS:
        hist = defaultdict(int)
        for r in suite.runs.get((scen, a), []):
            for b, c in (suite.detail(r).get('separation_histogram_m') or {}).items():
                hist[float(b)] += c
        if hist:
            ax.step(*_cdf(hist), where='post', color=rf.COLORS[a], lw=2, label=rf.NAMES[a])
    hist = defaultdict(int)
    for r in ext.runs.get(scen, []):
        for b, c in (ext.detail(r).get('separation_histogram_m') or {}).items():
            hist[float(b)] += c
    if hist:
        ax.step(*_cdf(hist), where='post', color=NM_COLOR, lw=2, ls=(0, (4, 2)), label=NM_NAME)
    ax.axvline(1.0, color=rf.INK2, lw=1, ls=(0, (3, 3)))
    ax.text(1.08, 0.92, '$d_{safe}$ = 1 m', fontsize=7.5, color=rf.INK2)
    ax.set_xlim(0, xmax)
    ax.set_ylim(0, 1.02)
    ax.set_xlabel('swarm separation s(t) (m)', fontsize=8)
    ax.set_ylabel('fraction of time\nwith s(t) <= x', fontsize=8)
    ax.grid(color=rf.GRID, lw=1)
    ax.set_axisbelow(True)
    for side in ('top', 'right'):
        ax.spines[side].set_visible(False)
    ax.tick_params(labelsize=7.5)
    ax.legend(frameon=False, fontsize=7.5, loc='lower right')
    fig.tight_layout()
    fig.savefig(out, dpi=200)
    plt.close(fig)
    return out


def coverage_figure(suite, ext, scen, out):
    """fraction of mission tasks visited at least once vs time since mission start"""
    fig, ax = plt.subplots(figsize=(5.2, 2.6))

    def curve(detail):
        ts = sorted(v['t_s'] for v in (detail.get('first_completion') or {}).values())
        return ts

    for a in rf.ALGOS:
        first = True
        for r in suite.runs.get((scen, a), []):
            d = suite.detail(r)
            ts = curve(d)
            total = int(r.get('total_tasks') or 0) or len(ts)
            if not ts or not total:
                continue
            ax.step([0] + ts, [0] + [(i + 1) / total for i in range(len(ts))], where='post', color=rf.COLORS[a],
                    lw=1.1, alpha=0.55, label=rf.NAMES[a] if first else None)
            first = False
    for r in ext.runs.get(scen, []):
        ts = curve(ext.detail(r))
        total = int(r.get('total_tasks') or 0) or len(ts)
        if ts and total:
            ax.step([0] + ts, [0] + [(i + 1) / total for i in range(len(ts))], where='post', color=NM_COLOR, lw=2.2,
                    label=NM_NAME)
    ax.set_xlabel('time since mission start (s)', fontsize=8)
    ax.set_ylabel('tasks visited\nat least once', fontsize=8)
    ax.set_ylim(0, 1.05)
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    ax.grid(color=rf.GRID, lw=1)
    ax.set_axisbelow(True)
    for side in ('top', 'right'):
        ax.spines[side].set_visible(False)
    ax.tick_params(labelsize=7.5)
    ax.legend(frameon=False, fontsize=7.5, loc='lower right')
    fig.tight_layout()
    fig.savefig(out, dpi=200)
    plt.close(fig)
    return out


# ---------------------------------------------------------------------------------------------- text
def write(B, suite, ext):
    scens = [s for s in rf.SCENARIOS if ext.runs.get(s)]
    n_runs = sum(len(v) for v in ext.runs.values())
    S = B.story

    S.append(Paragraph(TITLE, br.ST['title']))
    S.append(Paragraph(f'{n_runs} NMOPSO run{"s" if n_runs != 1 else ""} ({", ".join(scens)}) placed against '
                       f'suite <font face="Mono">{suite.path.name}</font> (auction, APF, RL; '
                       f'{sum(len(v) for v in suite.runs.values())} runs)', br.ST['subtitle']))
    first = {s: ext.runs[s][0] for s in scens}

    # ------------------------------------------------------------------ summary
    B.h1('Summary')
    b = first.get('benchmark')
    if b:
        mct, dist = rf.num(b['mission_completion_time_s']), rf.num(b['total_flight_distance_m'])
        msep, clr = rf.num(b['minimum_inter_drone_distance_m']), rf.num(b['min_obstacle_clearance_m'])
        ranges = {a: suite.values('benchmark', a, 'mission_completion_time_s') for a in rf.ALGOS}
        B.p(f'The NMOPSO run on the <i>benchmark</i> scenario completed the mission: all '
            f'{b["completed_tasks"]} of {b["total_tasks"]} tasks visited, with no drone excluded '
            f'(no crash). It took {fmt(mct)} s and {fmt(dist)} m of flight. Its closest approach between drones '
            f'was {fmt(msep)} m, and its closest approach to an obstacle was {fmt(clr)} m.')
        speed = {a: (B.m('benchmark', a, 'total_flight_distance_m') or 0) / 3 /
                 (B.m('benchmark', a, 'mission_completion_time_s') or 1) for a in rf.ALGOS}
        nm_speed = dist / int(b['num_drones']) / mct
        B.p(f'<b>The clearest difference is speed.</b> NMOPSO took {mct / max(v for v in ranges.values() for v in v):.1f} '
            f'times as long as the slowest suite run to complete the patrol cycle. Its drones covered '
            f'{fmt(nm_speed)} m/s on average (flight distance per drone over the mission time), against ' +
            ', '.join(f'{fmt(v)} m/s for {rf.NAMES[a]}' for a, v in speed.items()) + '. '
            'Its first task was completed after '
            f'{fmt(min(v["t_s"] for v in ext.detail(b).get("first_completion", {}).values()))} s. '
            'The data do not show whether the time went into planning, waiting or slow flight. The planner\'s '
            'decision time was not recorded (Section 2.3), and it is the first thing to check.')
        B.p('<b>This is one run, so it supports no statistical claim.</b> On <i>benchmark</i> the suite '
            'algorithms are very repeatable (their 95 % intervals are a few tenths of a second wide), so a gap this '
            'large is unlikely to be noise in the suite. NMOPSO\'s own run-to-run spread, however, is '
            'unknown, and this run could be unrepresentative. Section 4 places each NMOPSO value inside or '
            'outside the range of the other algorithms\' runs. Section 5 lists what is needed for a real '
            'comparison.')
        B.bullets([
            f'<b>Mission completion time:</b> NMOPSO {fmt(mct)} s. Range of the other algorithms\' completed runs: ' +
            '; '.join(f'{rf.NAMES[a]} {fmt(min(v))}–{fmt(max(v))} s' for a, v in ranges.items() if v) + '.',
            f'<b>Safety:</b> {b["separation_contacts"]} drone contacts and {b["obstacle_contacts"]} obstacle '
            f'contacts. Separation never fell below the 1 m safety radius '
            f'({b["separation_violations"]} violations). Time within 0.6 m of an obstacle: '
            f'{fmt(rf.num(b["obstacle_near_miss_s"]))} drone-s.',
            f'<b>Workload:</b> two tasks per drone, so task imbalance is {fmt(rf.num(b["workload_imbalance_tasks"]))}. '
            f'Distance imbalance is {fmt(rf.num(b["workload_imbalance_distance"]))}: '
            f'per-drone distances of ' + ', '.join(f'{fmt(v)} m' for v in
                                                    ext.detail(b).get('per_drone_distance_m', {}).values()) + '.',
        ])

    # ------------------------------------------------------------------ method
    B.h1('What was run and how it was measured')
    B.h2('NMOPSO')
    B.p('NMOPSO (navigation-variable multi-objective particle swarm optimisation) plans a path as n nodes. '
        'Each node is encoded in spherical coordinates relative to the previous one, so a particle is a '
        'vector of navigation variables, not of absolute waypoints:')
    B.eq(r'\mathbf{T}_k = \mathbf{T}_{k-1}\,R_z(\phi_k)\,R_y(-\psi_k)\,T_x(r_k),\qquad '
         r'\mathbf{x} = (r_1,\psi_1,\phi_1,\;\ldots,\;r_n,\psi_n,\phi_n)', size=10.5)
    B.p('A swarm of such particles is moved with the PSO velocity update:')
    B.eq(r'\mathbf{v}_i \leftarrow w\,\mathbf{v}_i + c_1\,\mathbf{r}_1\odot(\mathbf{p}_i-\mathbf{x}_i)'
         r' + c_2\,\mathbf{r}_2\odot(\mathbf{g}-\mathbf{x}_i),\qquad \mathbf{x}_i \leftarrow \mathbf{x}_i+\mathbf{v}_i',
         size=10.5)
    B.p('Here p<sub>i</sub> is the particle\'s own best position and g is a leader taken from the archive of '
        'non-dominated paths. The particles minimise four objectives together (the NMOPSO MyCost function):')
    B.eq(r'J_1 = \left|1-\frac{\|\mathbf{g}-\mathbf{s}\|}{L(P)}\right|,\quad '
         r'J_2 = \frac{1}{S\,M}\sum_{s,m}\mathrm{clip}_{[0,1]}\!\left(1-\frac{d_{sm}-\delta-R_m}{10\,\delta}\right),'
         r'\quad J_3 = \frac{1}{n}\sum_{k}\frac{|z_k-\bar z|}{\Delta z/2},\quad '
         r'J_4 = \frac{1}{n}\sum_{k}\frac{\angle(\mathbf{e}_k,\mathbf{e}_{k+1})}{\pi}', size=9.5)
    B.p('The four objectives measure:')
    B.bullets([
        '<b>J<sub>1</sub></b>: length overhead against the straight line.',
        '<b>J<sub>2</sub></b>: threat, i.e. proximity to obstacles modelled as cylinders of radius '
        'R<sub>m</sub>.',
        '<b>J<sub>3</sub></b>: altitude deviation.',
        '<b>J<sub>4</sub></b>: turning.',
    ])
    B.p('The result is a Pareto front of paths. One path is then chosen from the front.')
    B.p('<i>Not covered here.</i> This describes the reference NMOPSO formulation, which is also the path '
        'model the RL planner was trained on. The parameters of the NMOPSO implementation that produced this '
        'run were not supplied with the result files, so this report does not describe them: swarm size, '
        'iterations, the archive and leader rules, how a path is picked from the front, and how the planner '
        'is called during the mission. They belong in the final report.')
    B.h2('Measurement')
    B.p('The NMOPSO result files have exactly the columns of the current benchmark, including the new '
        'workload, reallocation, allocation-latency and separation-profile metrics, and the same per-run '
        'detail file. They were therefore produced by the same metric code (<font face="Mono">metrics_summary.py'
        '</font>) as the suite. The battery model and the 10 Hz telemetry are also the same:')
    B.bullets([
        'The battery fell by 12.28 % per drone in 122.9 s. That is the platform\'s battery model, '
        '0.01 % per 100 ms.',
        'There were 1229 valid state samples per drone, i.e. 10 Hz telemetry.',
    ])
    B.p('Every metric is therefore defined identically. The definitions are in '
        '<font face="Mono">docs/METRICS.md</font>.')
    B.h2('Differences in this run that affect comparability')
    rows = [['Observation', 'NMOPSO run', 'Suite runs', 'Consequence']]
    if b:
        visits = rf.num(b['task_visits'])
        rows += [
            ['Task visits in the mission window', f'{int(visits)} (each task once)',
             '9 (APF, RL) or 10 (auction): every drone visits its first task twice',
             'NMOPSO\'s controller follows a different task sequence, so visit counts and idleness are not '
             'measured under identical task logic'],
            ['Allocation latency', f'{fmt(rf.num(b["alloc_first_assignment_s"]))} s first, '
             f'{fmt(rf.num(b["alloc_all_assigned_s"]))} s all',
             'about 5 s (the shared auction waits for peer states)',
             'tasks were assigned at mission start, not by the shared auction, so latency and the AT/MCT ratio '
             'are not comparable'],
            ['Decision time', 'not recorded', 'APF and RL report compute() time every 5 s',
             'the planner\'s compute time is unknown. It is needed to check that planning fits the 100 ms '
             'coordination period'],
            ['Date and version', b['timestamp'][:10], f'{suite.path.name} (2026-10-23)',
             'the run may come from an older controller or launcher version. Re-run it with the current one '
             'for the final comparison'],
        ]
    B.table(rows, 'Differences between the NMOPSO run and the suite runs.',
            widths=[3.3 * cm, 3.3 * cm, 4.3 * cm, br.WIDTH - 10.9 * cm])

    # ------------------------------------------------------------------ results
    for scen in scens:
        B.h1(f'Results: {scen}')
        f1 = dot_figure(suite, ext, scen, B.d / f'nm_dots_{scen}.png')
        B.fig(f1, f'NMOPSO (diamond, one run) against the suite\'s five runs per algorithm on <i>{scen}</i>. '
                  'Small dots are individual runs, and the large dot with a bar is the mean with its 95 % '
                  'confidence interval. Time and distance use completed runs only.')
        f2 = coverage_figure(suite, ext, scen, B.d / f'nm_cov_{scen}.png')
        B.fig(f2, 'Coverage over time: the share of tasks visited at least once. Thin lines are individual '
                  'suite runs, and the thick line is NMOPSO. The curve reaches 100 % at the mission completion '
                  'time.', width=12.5 * cm)
        f3 = separation_figure(suite, ext, scen, B.d / f'nm_sep_{scen}.png')
        B.fig(f3, 'Distribution of the swarm separation s(t), the distance between the closest pair of drones, '
                  'sampled at 20 Hz. All runs of an algorithm are pooled. A curve further right means the '
                  'drones keep further apart. The dashed line is the 1 m safety radius.', width=12.5 * cm)

        B.h1(f'Metric-by-metric placement: {scen}')
        B.p('The table shows each metric for the suite algorithms (mean ± 95 % CI over n runs) and for the '
            'single NMOPSO run. The last three columns place the NMOPSO value against each algorithm\'s individual '
            'runs. "better than all 5" means that no run of that algorithm did as well. With one NMOPSO run, '
            '"within range" is the expected result for any algorithm of similar performance, so it does '
            'not mean "equal".')
        rows = [['Metric', 'Auction', 'APF', 'RL', 'NMOPSO', 'vs Auction', 'vs APF', 'vs RL']]
        for key in TABLE_METRICS:
            label, unit, better, _ = METRICS[key]
            x = (ext.values(scen, key) or [None])[0]
            row = [f'{label} ({unit})']
            for a in rf.ALGOS:
                st = suite.stat(scen, a, key)
                row.append(f'{fmt(st[0])} ± {fmt(st[1])}' if st else '–')
            row.append(f'<b>{fmt(x)}</b>')
            for a in rf.ALGOS:
                row.append('not comparable' if key in NOT_COMPARABLE else placement(x, suite.values(scen, a, key), better))
            rows.append(row)
        B.table(rows, f'<i>{scen}</i>: suite means ± 95 % CI, the NMOPSO value and its placement among each '
                      'algorithm\'s runs.',
                widths=[3.9 * cm, 1.65 * cm, 1.65 * cm, 1.65 * cm, 1.3 * cm] + [(br.WIDTH - 10.15 * cm) / 3] * 3)

        B.h2('Reading the placement')
        notes = []
        for key, why in [
            ('mission_completion_time_s', 'Speed of one patrol cycle.'),
            ('total_flight_distance_m', 'Path efficiency. NMOPSO optimises path length (J<sub>1</sub>) directly.'),
            ('min_obstacle_clearance_m', 'Closest approach to any obstacle box. Below 0.3 m the airframe touches.'),
            ('minimum_inter_drone_distance_m', 'Closest approach between two drones.'),
            ('mean_task_idleness_s', 'How long a task waits, on average, between visits.'),
        ]:
            x = (ext.values(scen, key) or [None])[0]
            better = METRICS[key][2]
            parts = '; '.join(f'{rf.NAMES[a]}: {placement(x, suite.values(scen, a, key), better)}'
                              for a in rf.ALGOS)
            notes.append(f'<b>{METRICS[key][0]}</b> ({fmt(x)} {METRICS[key][1]}). {why} Placement: {parts}.')
        B.bullets(notes)

    # ------------------------------------------------------------------ conclusion
    B.h1('Conclusion and next steps')
    B.p('On the benchmark scenario, NMOPSO completed a full patrol cycle without a crash, a contact or a '
        'separation violation, so it works in nominal conditions. It was, however, much slower than all three '
        'suite algorithms. It also kept smaller margins than auction and RL: a smaller minimum drone separation, '
        'a smaller obstacle clearance and more time near obstacles. It still had more clearance than APF. '
        'As a patrol algorithm, this run would place it last on mission time and idleness. One run cannot '
        'rank it, though:')
    B.bullets([
        'NMOPSO\'s variance is unknown. Five runs per scenario are the minimum at which the report\'s '
        'Mann–Whitney tests can reach significance after Holm correction.',
        'The scenarios that separate the algorithms most were not run: <i>safety_stress</i> (crowded '
        'airspace, where auction and APF crash) and the two communication-loss scenarios (recovery). A '
        'factory recommendation rests mostly on these.',
    ])
    B.p('Needed for NMOPSO to enter the benchmark report as a fourth algorithm:')
    B.bullets([
        'Run 5 repeats × 4 scenarios = 20 runs with the current launcher: '
        '<font face="Mono">./scripts/run_suite.sh suite_nmopso 5 "nmopso"</font>. That is about one hour.',
        'Report <font face="Mono">compute_stats</font> from the NMOPSO planner (source '
        '<font face="Mono">coordinator</font>), so its decision time is measured. Particle-swarm planning is '
        'the most expensive step of any of the four planners.',
        'Use the shared auction for allocation, as the other three algorithms do, or document why NMOPSO '
        'assigns at mission start. Otherwise allocation latency and comm-loss reassignment are not comparable.',
        'Append the NMOPSO rows to a copy of the suite manifest, then re-run '
        '<font face="Mono">aggregate_suite.py</font> and <font face="Mono">build_report.py</font>.',
    ])


def build(suite_dir, ext_dir, out_pdf):
    suite = rf.Suite(suite_dir)
    ext = External(ext_dir)
    if not ext.runs:
        sys.exit(f'no *_{NM}_*.csv in {ext_dir}')
    B = br.Builder(suite, rf.ROOT / 'presentation' / 'report_build' / 'nmopso')
    write(B, suite, ext)

    class Doc(br.Doc):
        @staticmethod
        def _decor(canv, doc):
            if doc.page == 1:
                return
            canv.saveState()
            canv.setFont('Sans', 7.5)
            canv.setFillColor(br.INK2)
            canv.drawString(2.1 * cm, 1.2 * cm, TITLE)
            canv.drawRightString(br.A4[0] - 2.1 * cm, 1.2 * cm, str(doc.page))
            canv.restoreState()

    doc = Doc(out_pdf)
    doc.title = TITLE
    doc.multiBuild(B.story)
    print('wrote', out_pdf)


if __name__ == '__main__':
    out = Path(sys.argv[3]) if len(sys.argv) > 3 else rf.ROOT / 'docs' / 'nmopso_report.pdf'
    build(sys.argv[1], sys.argv[2], out.resolve())
