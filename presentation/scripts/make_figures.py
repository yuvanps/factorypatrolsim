#!/usr/bin/env python3
"""Generate progress-review figures from the project's own config and run data.

Every number drawn here is read from config/*.yaml or experiment_results/; nothing is typed in
by hand except the spawn formula (x = 4*i - 8, y = 7), which is copied from start_swarm.sh /
patrol_controller.c.

    python3 presentation/scripts/make_figures.py
"""
import csv
import json
import math
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUT = os.path.join(ROOT, 'presentation', 'figures')
os.makedirs(OUT, exist_ok=True)

RUN_AUCTION = 'run_20260929_214901'
RUN_APF = 'run_20260929_215220'

# Categorical slots 1-3 of the validated reference palette (pass all-pairs CVD checks).
DRONE_COLORS = ['#2a78d6', '#eb6834', '#1baf7a']
INK, INK2, MUTED = '#0b0b0b', '#52514e', '#8a8984'
OBST_FILL, OBST_EDGE = '#e6e5e0', '#a9a8a2'
WALL = '#52514e'

plt.rcParams.update({
    'font.family': 'DejaVu Sans', 'font.size': 11, 'axes.edgecolor': MUTED,
    'axes.labelcolor': INK2, 'xtick.color': INK2, 'ytick.color': INK2,
    'axes.titlesize': 13, 'axes.titleweight': 'bold', 'axes.titlecolor': INK,
    'figure.facecolor': 'white', 'axes.facecolor': 'white', 'savefig.facecolor': 'white',
})


def load_yaml(rel):
    with open(os.path.join(ROOT, rel)) as f:
        return yaml.safe_load(f)


OBSTACLES = load_yaml('config/environment/factory_obstacles.yaml')['obstacles']
TASKS = load_yaml('config/tasks/benchmark.yaml')['tasks']
TASK_NAME = {t['id']: f'T{i + 1}' for i, t in enumerate(TASKS)}  # 101 -> T1 ...
N_DRONES = 3
SPAWN = [(4.0 * i - 8.0, 7.0) for i in range(N_DRONES)]


def save(fig, name):
    for ext in ('png', 'svg'):
        fig.savefig(os.path.join(OUT, f'{name}.{ext}'), dpi=200, bbox_inches='tight')
    plt.close(fig)
    print('wrote', name)


# ---------------------------------------------------------------------------
# Run data
# ---------------------------------------------------------------------------

def load_run(run):
    d = os.path.join(ROOT, 'experiment_results', run)
    events = [json.loads(l) for l in open(os.path.join(d, 'experiment_events.jsonl'))]
    t0 = next(e['timestamp_ns'] for e in events if e['event_type'] == 'mission_started')
    detail = json.load(open(os.path.join(d, 'metrics_detail.json')))
    states = []
    with open(os.path.join(d, 'drone_states.csv')) as f:
        for r in csv.DictReader(f):
            states.append({'t': (int(r['timestamp_ns']) - t0) / 1e9, 'id': int(r['drone_id']),
                           'x': float(r['x']), 'y': float(r['y']), 'z': float(r['z']),
                           'state': int(r['state'])})
    completions = [((e['timestamp_ns'] - t0) / 1e9, e['drone_id'], e['task_id'])
                   for e in events if e['event_type'] == 'task_completed']
    assigned, seen = [], set()
    for e in events:  # events are logged twice (direct topic + coordinator relay): dedupe
        if e['event_type'] == 'task_assigned' and e['task_id'] not in seen:
            seen.add(e['task_id'])
            assigned.append((e['task_id'], e['drone_id']))
    return {'events': events, 'detail': detail, 'states': states,
            'completions': completions, 'assigned': dict(assigned)}


AUC = load_run(RUN_AUCTION)
APF = load_run(RUN_APF)
ASSIGN = AUC['assigned']
assert ASSIGN == APF['assigned'], 'both algorithms use the same native auction allocation'


# ---------------------------------------------------------------------------
# Factory map helpers
# ---------------------------------------------------------------------------

LABELS = {
    'central_partition': 'Partition', 'rack_row_1': 'Rack 1', 'rack_row_2': 'Rack 2',
    'rack_row_3': 'Rack 3', 'rack_row_4': 'Rack 4', 'loading_dock': 'Loading dock',
    'cnc_machine': 'CNC', 'lathe_machine': 'Lathe', 'assembly_workbench': 'Workbench',
    'conveyor_belt': 'Conveyor', 'packing_station': 'Packing', 'shipping_crate_stack': 'Crates',
}


def draw_factory(ax, labels=True):
    for o in OBSTACLES:
        if o['id'] in ('floor', 'ceiling_barrier'):
            continue
        cx, cy, cz = o['center']
        sx, sy, sz = o['size']
        wall = o['id'].endswith('_wall')
        ax.add_patch(Rectangle((cx - sx / 2, cy - sy / 2), sx, sy,
                               facecolor=WALL if wall else OBST_FILL,
                               edgecolor=WALL if wall else OBST_EDGE, lw=0.8, zorder=1))
        if labels and o['id'] in LABELS:
            h = sz  # height = size z (box sits on the floor)
            if o['id'].startswith('rack_row'):
                if o['id'] == 'rack_row_1':  # one shared label under the four rack rows
                    ax.text(-8.25, cy - sy / 2 - 0.25, f'Rack rows 1–4 ({h:g} m)', ha='center',
                            va='top', fontsize=7, color=MUTED, zorder=2)
            elif sy > 3 * sx:  # partition: inside, rotated
                ax.text(cx, cy + 3.0, f"{LABELS[o['id']]} {h:g} m", ha='center', va='center',
                        fontsize=7, color=MUTED, rotation=90, zorder=2)
            else:  # machines: just below the box, clear of task markers
                ax.text(cx, cy - sy / 2 - 0.25, f"{LABELS[o['id']]} ({h:g} m)", ha='center',
                        va='top', fontsize=7, color=MUTED, zorder=2)
    ax.set_xlim(-15.6, 15.6)
    ax.set_ylim(-10.6, 10.6)
    ax.set_aspect('equal')
    ax.set_xlabel('x (m, Gazebo east)')
    ax.set_ylabel('y (m, Gazebo north)')
    ax.grid(True, color='#efeee9', lw=0.6, zorder=0)
    ax.set_axisbelow(True)


def draw_spawns(ax):
    for i, (x, y) in enumerate(SPAWN):
        ax.plot(x, y, marker='^', ms=11, color=DRONE_COLORS[i], mec='white', mew=1.5, zorder=6)
        ax.annotate(f'D{i} start', (x, y), xytext=(0, 10), textcoords='offset points',
                    ha='center', fontsize=9, color=INK, zorder=7)


def draw_tasks(ax, color_by_drone=False):
    for t in TASKS:
        x, y, z = t['position']
        c = DRONE_COLORS[ASSIGN[t['id']]] if color_by_drone else INK
        ax.plot(x, y, marker='o', ms=12, color='white', mec=c, mew=2.5, zorder=8)
        ax.plot(x, y, marker='o', ms=4, color=c, zorder=9)
        ax.annotate(f"{TASK_NAME[t['id']]}  h={-z:g} m", (x, y), xytext=(9, -3),
                    textcoords='offset points', fontsize=9, color=INK, weight='bold', zorder=9,
                    bbox=dict(boxstyle='round,pad=0.15', fc='white', ec='none', alpha=0.85))


# ---------------------------------------------------------------------------
# Fig 1: environment + task layout
# ---------------------------------------------------------------------------

def fig_factory_map():
    fig, ax = plt.subplots(figsize=(12.8, 7.2))
    draw_factory(ax)
    draw_spawns(ax)
    draw_tasks(ax)
    ax.plot(0, 0, marker='+', ms=12, color=MUTED, mew=1.5, zorder=5)
    ax.annotate('centre corridor (0,0)\n(auction transit waypoint)', (0, 0), xytext=(8, 22),
                textcoords='offset points', fontsize=8, color=MUTED)
    ax.set_title('Factory world (30 m × 20 m, top-down) — UAV start positions and benchmark patrol tasks',
                 loc='left')
    ax.text(0.0, -0.1, 'Source: worlds/factory.sdf via config/environment/factory_obstacles.yaml; '
            'config/tasks/benchmark.yaml; spawn x = 4i − 8, y = 7 (start_swarm.sh). '
            'h = inspection height above floor.', transform=ax.transAxes, fontsize=8, color=MUTED)
    save(fig, 'fig01_factory_map')


def fig_task_allocation_map():
    fig, ax = plt.subplots(figsize=(12.8, 7.2))
    draw_factory(ax, labels=False)
    # patrol loop of each drone: start -> first task -> second task -> first task ...
    for d in range(N_DRONES):
        zones = [tid for tid, dd in ASSIGN.items() if dd == d]
        pts = {t['id']: t['position'] for t in TASKS}
        a, b = pts[zones[0]], pts[zones[1]]
        s = SPAWN[d]
        for (p, q, style) in ((s, a, (0, (3, 3))), (a, b, '-'), (b, a, '-')):
            ax.add_patch(FancyArrowPatch(p[:2], q[:2], arrowstyle='-|>', mutation_scale=14,
                                         color=DRONE_COLORS[d], lw=2, linestyle=style,
                                         connectionstyle='arc3,rad=0.12', zorder=4, alpha=0.9))
    draw_spawns(ax)
    draw_tasks(ax, color_by_drone=True)
    for d in range(N_DRONES):
        zones = [TASK_NAME[tid] for tid, dd in ASSIGN.items() if dd == d]
        ax.plot([], [], color=DRONE_COLORS[d], lw=3, label=f'D{d}: {zones[0]} ⇄ {zones[1]}')
    ax.legend(loc='lower left', frameon=True, fontsize=10, title='Auction result (both runs)')
    ax.set_title('Task allocation produced by the auction — each UAV then loops its two zones',
                 loc='left')
    ax.text(0.0, -0.1, 'Arrows are logical order only (not flown paths). Dashed = first leg from start. '
            f'Assignments from task_assigned events in {RUN_AUCTION} and {RUN_APF} (identical).',
            transform=ax.transAxes, fontsize=8, color=MUTED)
    save(fig, 'fig02_task_allocation_map')


# ---------------------------------------------------------------------------
# Fig 9a: auction cost matrix (reconstructed from the cost function in auction_logic.c)
# ---------------------------------------------------------------------------

def auction_greedy():
    """Replay auction_run_allocation() from the nominal spawn state (battery 100 %)."""
    n_t = len(TASKS)
    cap = math.ceil(n_t / N_DRONES)
    count = [0] * N_DRONES
    steps = []
    for t in TASKS:
        tx, ty, tz = t['position']
        row = []
        for d in range(N_DRONES):
            sx, sy = SPAWN[d]
            dist = math.dist((sx, sy, 0.0), (tx, ty, tz))
            if count[d] >= cap:
                row.append((dist, None))
            else:
                row.append((dist, dist + 15.0 * count[d] + 0.2 * (100.0 - 100.0)))
        win = min((c, d) for d, (_, c) in enumerate(row) if c is not None)[1]
        steps.append((t['id'], row, win, list(count)))
        count[win] += 1
    return steps, cap


def fig_cost_matrix():
    steps, cap = auction_greedy()
    fig, ax = plt.subplots(figsize=(12.8, 5.4))
    ax.axis('off')
    col_x = [0.02, 0.2, 0.42, 0.64, 0.86]
    heads = ['Step / task', 'D0  start (−8, 7, 0)', 'D1  start (−4, 7, 0)', 'D2  start (0, 7, 0)', 'Winner']
    for x, h in zip(col_x, heads):
        ax.text(x, 0.95, h, fontsize=11, weight='bold', color=INK, transform=ax.transAxes)
    for k, (tid, row, win, cnt) in enumerate(steps):
        y = 0.83 - k * 0.12
        ax.text(col_x[0], y, f'{k + 1}.  {TASK_NAME[tid]} ({tid})', fontsize=11, color=INK,
                transform=ax.transAxes)
        for d, (dist, cost) in enumerate(row):
            if cost is None:
                txt, col, w = f'—  at cap ({cap} tasks)', MUTED, 'normal'
            else:
                pen = cost - dist
                txt = f'{dist:5.2f}' + (f' + {pen:.0f} = {cost:5.2f}' if pen else f' = {cost:5.2f}')
                col, w = (DRONE_COLORS[d], 'bold') if d == win else (INK2, 'normal')
            ax.text(col_x[d + 1], y, txt, fontsize=11, color=col, weight=w, family='DejaVu Sans Mono',
                    transform=ax.transAxes)
        ax.text(col_x[4], y, f'D{win}', fontsize=12, weight='bold', color=DRONE_COLORS[win],
                transform=ax.transAxes)
    ax.set_title('Auction allocation, replayed step by step:  C_ij = d_ij + 15·n_i + 0.2·(100 − b_i)',
                 loc='left')
    ax.text(0.02, 0.02, f'Greedy over tasks in file order; cap = ⌈6/3⌉ = {cap} tasks per UAV. Uses nominal '
            'spawn positions and b_i = 100 %; the controller uses live telemetry at t ≈ 5 s (battery ≈ 99.5 %, '
            '+0.1 cost), which gives the same winners as the logged task_assigned events.',
            fontsize=8, color=MUTED, transform=ax.transAxes, wrap=True)
    save(fig, 'fig09a_auction_cost_matrix')
    return steps


# ---------------------------------------------------------------------------
# Fig 8: trajectories (top-down) + Fig 10: altitude vs time
# ---------------------------------------------------------------------------

def tracks(run, t_end):
    out = {d: [] for d in range(N_DRONES)}
    for s in run['states']:
        if s['id'] < N_DRONES and -0.5 <= s['t'] <= t_end + 0.5:
            if (s['x'], s['y'], s['z']) == (0.0, 0.0, 0.0):
                continue  # pre-odometry placeholder
            out[s['id']].append(s)
    return out


def fig_trajectories():
    fig, axes = plt.subplots(1, 2, figsize=(16, 6.2))
    for ax, run, name in ((axes[0], AUC, 'Auction (internal navigation)'),
                          (axes[1], APF, 'APF (external navigation, same allocation)')):
        t_end = run['detail']['window_s']
        draw_factory(ax, labels=False)
        for d, pts in tracks(run, t_end).items():
            ax.plot([p['x'] for p in pts], [p['y'] for p in pts], color=DRONE_COLORS[d], lw=2,
                    zorder=5, label=f"D{d}  ({run['detail']['per_drone_distance_m'][str(d)]:.1f} m)")
        draw_spawns(ax)
        draw_tasks(ax, color_by_drone=True)
        ax.set_title(f'{name}\nfirst 0–{t_end:.1f} s (one patrol cycle)', loc='left', fontsize=12)
        ax.legend(loc='lower left', fontsize=9, title='3D path length (10 Hz)', title_fontsize=9)
    fig.text(0.01, -0.02, f'Paths drawn from drone_states.csv 1 Hz snapshots ({RUN_AUCTION}, {RUN_APF}); '
             'distances in the legend are computed by the metrics collector from 10 Hz telemetry.',
             fontsize=8, color=MUTED)
    save(fig, 'fig08_trajectories_topdown')


def fig_altitude():
    fig, axes = plt.subplots(2, 1, figsize=(12.8, 7.2), sharex=True, sharey=True)
    for ax, run, name in ((axes[0], AUC, 'Auction'), (axes[1], APF, 'APF')):
        t_end = run['detail']['window_s']
        for d, pts in tracks(run, t_end).items():
            ax.plot([p['t'] for p in pts], [-p['z'] for p in pts], color=DRONE_COLORS[d], lw=2,
                    label=f'D{d}')
        for t, d, tid in run['completions']:
            if t <= t_end + 0.1:
                ax.axvspan(t - 4.0, t, color=DRONE_COLORS[d], alpha=0.10, lw=0)
        ax.set_ylabel('height (m)')
        ax.set_title(name, loc='left', fontsize=12)
        ax.grid(True, color='#efeee9')
        ax.axvline(t_end, color=MUTED, ls='--', lw=1)
        ax.text(t_end, ax.get_ylim()[1] if False else 8.2, ' mission end', fontsize=8, color=MUTED, va='top')
    axes[0].legend(loc='upper left', ncol=3, fontsize=9)
    axes[1].set_xlabel('time since mission published (s)')
    axes[0].set_ylim(-0.3, 8.5)
    fig.suptitle('Height vs time — auction transits on per-UAV layers via (0,0); APF flies at task height',
                 x=0.01, ha='left', fontsize=13, weight='bold')
    fig.text(0.01, -0.01, 'Shaded bands = 4 s inspection dwell before each task_completed event. '
             '1 Hz snapshots.', fontsize=8, color=MUTED)
    save(fig, 'fig10_altitude_vs_time')


# ---------------------------------------------------------------------------
# Fig 9b: task timeline (Gantt of dwell periods)
# ---------------------------------------------------------------------------

def fig_timeline():
    fig, axes = plt.subplots(2, 1, figsize=(12.8, 5.6), sharex=True)
    for ax, run, name in ((axes[0], AUC, 'Auction'), (axes[1], APF, 'APF')):
        t_end = run['detail']['window_s']
        first = {k: v['t_s'] for k, v in run['detail']['first_completion'].items()}
        for t, d, tid in run['completions']:
            if t > t_end + 0.1:
                continue
            is_first = abs(first[str(tid)] - t) < 0.05
            ax.barh(d, 4.0, left=t - 4.0, height=0.55, color=DRONE_COLORS[d],
                    alpha=1.0 if is_first else 0.35, edgecolor='white', lw=2)
            ax.text(t - 2.0, d, TASK_NAME[tid], ha='center', va='center', fontsize=9,
                    color='white' if is_first else INK, weight='bold')
        ax.axvline(5.1, color=MUTED, lw=1, ls=':')
        ax.axvline(t_end, color=INK2, lw=1.2, ls='--')
        ax.text(t_end + 0.3, 2.35, f'T = {t_end:.1f} s', fontsize=9, color=INK2)
        ax.set_yticks(range(N_DRONES), [f'D{d}' for d in range(N_DRONES)])
        ax.set_ylim(-0.6, 2.7)
        ax.invert_yaxis()
        ax.set_title(name, loc='left', fontsize=12)
        ax.grid(True, axis='x', color='#efeee9')
    axes[0].text(5.3, -0.45, 'allocation (t ≈ 5.1 s)', fontsize=8, color=MUTED)
    axes[1].set_xlabel('time since mission published (s)')
    axes[1].set_xlim(0, 50)
    fig.suptitle('Inspection dwell timeline (4 s per visit) — solid = first completion, faded = repeat visit',
                 x=0.01, ha='left', fontsize=13, weight='bold')
    save(fig, 'fig09b_task_timeline')


# ---------------------------------------------------------------------------
# Fig 11: preliminary metrics
# ---------------------------------------------------------------------------

def fig_metrics():
    fig, axes = plt.subplots(1, 2, figsize=(12.8, 5.2))
    runs = (('Auction', AUC), ('APF', APF))
    # per-drone distance, grouped by algorithm
    ax = axes[0]
    w = 0.26
    for d in range(N_DRONES):
        vals = [r['detail']['per_drone_distance_m'][str(d)] for _, r in runs]
        xs = [i + (d - 1) * w for i in range(2)]
        bars = ax.bar(xs, vals, width=w - 0.02, color=DRONE_COLORS[d], label=f'D{d}')
        for x, v in zip(xs, vals):
            ax.text(x, v + 1.5, f'{v:.0f}', ha='center', fontsize=9, color=INK2)
    ax.set_xticks([0, 1], [n for n, _ in runs])
    ax.set_ylabel('distance flown in [start, end] (m)')
    ax.set_title('Per-UAV flight distance', loc='left', fontsize=12)
    ax.legend(fontsize=9, frameon=False)
    ax.spines[['top', 'right']].set_visible(False)
    ax.grid(True, axis='y', color='#efeee9')
    ax.set_axisbelow(True)
    # per-drone battery consumed
    ax = axes[1]
    for d in range(N_DRONES):
        vals = [r['detail']['per_drone_battery_consumed_percent'][str(d)] for _, r in runs]
        xs = [i + (d - 1) * w for i in range(2)]
        ax.bar(xs, vals, width=w - 0.02, color=DRONE_COLORS[d], label=f'D{d}')
        for x, v in zip(xs, vals):
            ax.text(x, v + 0.08, f'{v:.2f}', ha='center', fontsize=9, color=INK2)
    ax.set_xticks([0, 1], [n for n, _ in runs])
    ax.set_ylabel('battery consumed (% points)')
    ax.set_ylim(0, 5.5)
    ax.set_title('Per-UAV battery consumed (time-based model)', loc='left', fontsize=12)
    ax.spines[['top', 'right']].set_visible(False)
    ax.grid(True, axis='y', color='#efeee9')
    ax.set_axisbelow(True)
    fig.suptitle('Preliminary results — benchmark scenario, 3 UAVs, one run per algorithm (n = 1)',
                 x=0.01, ha='left', fontsize=13, weight='bold')
    fig.text(0.01, -0.03, f'{RUN_AUCTION} (auction), {RUN_APF} (APF). Battery drains 0.01 % per 100 ms '
             'regardless of motion, so battery tracks mission time, not flight effort.',
             fontsize=8, color=MUTED)
    fig.tight_layout()
    save(fig, 'fig11_preliminary_metrics')


if __name__ == '__main__':
    fig_factory_map()
    fig_task_allocation_map()
    steps = fig_cost_matrix()
    for tid, row, win, _ in steps:
        assert ASSIGN[tid] == win, f'replay disagrees with log for {tid}'
    print('greedy replay matches logged assignment')
    fig_trajectories()
    fig_altitude()
    fig_timeline()
    fig_metrics()
