"""Figures, equations and diagrams of the benchmark report (presentation/scripts/build_report.py).

Every number comes from a suite directory (scripts/run_suite.sh + scripts/aggregate_suite.py):
<suite>/aggregate.csv, <suite>/runs.csv and each run's experiment_results/<run_id>/metrics_detail.json.
Charts: one categorical colour per algorithm (validated slots 1-3, the same as suite_figures.py),
dot = mean, line = 95 % confidence interval, light dots = individual runs.
"""
import csv
import json
import math
import subprocess
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
ALGOS = ['auction', 'apf', 'rl', 'nmopso']
NAMES = {'auction': 'Auction', 'apf': 'APF', 'rl': 'RL (vB)', 'nmopso': 'NMOPSO'}
COLORS = {'auction': '#2a78d6', 'apf': '#eb6834', 'rl': '#1baf7a', 'nmopso': '#c2185b'}   # 4th: CVD dE >= 12
SCENARIOS = ['benchmark', 'safety_stress', 'comm_loss', 'comm_loss_orchestrator']
SCEN_NAMES = {'benchmark': 'benchmark', 'safety_stress': 'safety_stress', 'comm_loss': 'comm_loss',
              'comm_loss_orchestrator': 'comm_loss_orch.'}
INK, INK2, GRID, SURFACE = '#0b0b0b', '#52514e', '#e6e5e0', '#ffffff'
COMPLETED_ONLY = {'mission_completion_time_s', 'total_flight_distance_m', 'total_battery_consumed_percent',
                  'allocation_to_mct_ratio'}
INFRA_STOPS = ('disk below', 'log too big')

plt.rcParams.update({
    'font.family': 'DejaVu Sans', 'font.size': 9, 'axes.edgecolor': GRID, 'axes.labelcolor': INK2,
    'xtick.color': INK2, 'ytick.color': INK, 'axes.titlesize': 9.5, 'axes.titleweight': 'bold',
    'axes.titlecolor': INK, 'figure.facecolor': SURFACE, 'axes.facecolor': SURFACE, 'savefig.facecolor': SURFACE,
    'mathtext.fontset': 'dejavuserif',
})


def num(v):
    try:
        x = float(v)
        return x if math.isfinite(x) else None
    except (TypeError, ValueError):
        return None


class Suite:
    """aggregate.csv + runs.csv (+ per-run details) of one suite."""

    def __init__(self, path):
        self.path = Path(path).resolve()
        self.agg = {(r['scenario'], r['algorithm'], r['metric']): r
                    for r in csv.DictReader(open(self.path / 'aggregate.csv'))}
        self.runs = defaultdict(list)
        for r in csv.DictReader(open(self.path / 'runs.csv')):
            if not r.get('stop_reason', '').startswith(INFRA_STOPS):
                self.runs[(r['scenario'], r['algorithm'])].append(r)
        self.scenarios = [s for s in SCENARIOS if any((s, a) in self.runs for a in ALGOS)]

    def stat(self, scen, algo, metric):
        """(mean, ci half-width, n) or None"""
        r = self.agg.get((scen, algo, metric))
        if not r or r['mean'] == '':
            return None
        m = float(r['mean'])
        hw = float(r['ci_hi']) - m if r['ci_hi'] not in ('', None) else 0.0
        return m, hw, int(r['n'])

    def values(self, scen, algo, metric):
        rows = self.runs.get((scen, algo), [])
        return [v for v in (num(r.get(metric)) for r in rows
                            if metric not in COMPLETED_ONLY or r.get('status') == 'completed') if v is not None]

    def counts(self, scen, algo):
        rows = self.runs.get((scen, algo), [])
        return (len(rows), sum(r.get('status') == 'completed' for r in rows),
                sum('excluded' in (r.get('notes') or '') for r in rows))

    def detail(self, run):
        f = ROOT / 'experiment_results' / run['run_id'] / 'metrics_detail.json'
        try:
            return json.load(open(f))
        except (OSError, ValueError):
            return {}


def _style(ax):
    ax.grid(axis='x', color=GRID, lw=1)
    ax.set_axisbelow(True)
    for side in ('top', 'right', 'left'):
        ax.spines[side].set_visible(False)
    ax.tick_params(axis='y', length=0)


def dot_ci_grid(suite, metrics, out, scenarios=None, width=7.2):
    """rows = metrics (key, title, better), columns = scenarios; per panel one row per algorithm."""
    scenarios = scenarios or suite.scenarios
    row_h = 1.15
    fig_h = row_h * len(metrics) + 0.7
    fig, axes = plt.subplots(len(metrics), len(scenarios), figsize=(width, fig_h), squeeze=False)
    top_pad, row_gap = 0.62 / fig_h, 0.42 / fig_h
    fig.subplots_adjust(left=0.105, right=0.985, bottom=0.25 / fig_h, top=1 - top_pad,
                        wspace=0.18, hspace=row_gap * len(metrics) / (1 - top_pad) * 1.9)
    for i, (key, title, better) in enumerate(metrics):
        for j, scen in enumerate(scenarios):
            ax = axes[i][j]
            for k, a in enumerate(reversed(ALGOS)):
                vals = suite.values(scen, a, key)
                ax.scatter(vals, [k] * len(vals), s=12, color=COLORS[a], alpha=0.35, linewidths=0, zorder=2)
                st = suite.stat(scen, a, key)
                if st:
                    m, hw, _ = st
                    ax.plot([m - hw, m + hw], [k, k], color=COLORS[a], lw=2, solid_capstyle='round', zorder=3)
                    ax.scatter([m], [k], s=40, color=COLORS[a], edgecolors=SURFACE, linewidths=1.5, zorder=4)
                elif not vals:
                    ax.text(0.03, k, 'n/a', transform=ax.get_yaxis_transform(), va='center', color=INK2, fontsize=7.5)
            ax.set_yticks(range(len(ALGOS)))
            ax.set_yticklabels([NAMES[a] for a in reversed(ALGOS)] if j == 0 else [])
            ax.set_ylim(-0.6, len(ALGOS) - 0.4)
            ax.tick_params(axis='x', labelsize=7)
            ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(4))
            ax.margins(x=0.12)
            _style(ax)
            if i == 0:
                bb = ax.get_position()
                fig.text((bb.x0 + bb.x1) / 2, 1 - 0.08 / fig_h, SCEN_NAMES[scen], ha='center', va='top',
                         fontsize=8.5, fontweight='bold', color=INK2)
        bb = axes[i][0].get_position()
        fig.text(0.01, bb.y1 + 0.06 / fig_h * 1.5, f'{title}  ({"lower" if better == "low" else "higher"} is better)',
                 fontsize=8.5, fontweight='bold', color=INK, va='bottom')
    fig.savefig(out, dpi=200)
    plt.close(fig)
    return out


def separation_cdf(suite, out, scenarios=None, d_safe=1.0, xmax=6.0):
    """CDF of the swarm separation s(t) (all runs of an algorithm pooled), one panel per scenario."""
    scenarios = scenarios or suite.scenarios
    fig, axes = plt.subplots(1, len(scenarios), figsize=(7.2, 2.3), sharey=True, squeeze=False)
    for j, scen in enumerate(scenarios):
        ax = axes[0][j]
        for a in ALGOS:
            hist = defaultdict(int)
            for r in suite.runs.get((scen, a), []):
                for b, c in (suite.detail(r).get('separation_histogram_m') or {}).items():
                    hist[float(b)] += c
            if not hist:
                continue
            xs = sorted(hist)
            tot = sum(hist.values())
            cum, ys = 0, []
            for x in xs:
                cum += hist[x]
                ys.append(cum / tot)
            ax.step([x + 0.25 for x in xs], ys, where='post', color=COLORS[a], lw=2, label=NAMES[a])
        ax.axvline(d_safe, color=INK2, lw=1, ls=(0, (3, 3)))
        ax.text(d_safe + 0.08, 0.92, f'$d_{{safe}}$ = {d_safe:g} m', fontsize=7.5, color=INK2)
        ax.set_xlim(0, xmax)
        ax.set_ylim(0, 1.02)
        ax.set_title(SCEN_NAMES[scen], fontsize=9)
        ax.set_xlabel('swarm separation s(t) (m)', fontsize=8)
        ax.grid(color=GRID, lw=1)
        ax.set_axisbelow(True)
        for side in ('top', 'right'):
            ax.spines[side].set_visible(False)
        ax.tick_params(labelsize=7.5)
    axes[0][0].set_ylabel('fraction of time\nwith s(t) <= x', fontsize=8)
    axes[0][-1].legend(frameon=False, fontsize=7.5, loc='lower right')
    fig.tight_layout()
    fig.savefig(out, dpi=200)
    plt.close(fig)
    return out


def recovery_timeline(suite, out):
    """comm-loss recovery phases per algorithm: detection, reassignment, coverage restored (mean)."""
    scens = [s for s in ('comm_loss', 'comm_loss_orchestrator') if s in suite.scenarios]
    fig, axes = plt.subplots(len(scens), 1, figsize=(7.2, 1.35 * len(scens) + 0.6), squeeze=False)
    for i, scen in enumerate(scens):
        ax = axes[i][0]
        for k, a in enumerate(reversed(ALGOS)):
            g = lambda m: (suite.stat(scen, a, m) or (None,))[0]
            det, rea, cov, dur = g('detection_s'), g('reassignment_s'), g('coverage_restored_s'), g('comm_loss_duration_s')
            res = g('resume_s')
            x0 = 0.0
            for end, alpha, label in ((det, 1.0, 'detect'), (rea, 0.65, 'reassign'), (cov, 0.3, 'until restored')):
                if end is None or end <= x0:
                    continue
                ax.barh(k, end - x0, left=x0, height=0.55, color=COLORS[a], alpha=alpha, edgecolor=SURFACE, lw=1.5)
                x0 = end
            if det is None and cov is not None:            # orchestrator: never detected, no reassignment
                ax.barh(k, cov, left=0, height=0.55, color=COLORS[a], alpha=0.3, edgecolor=SURFACE, lw=1.5)
            if cov is not None:
                ax.text(cov + 0.6, k, f'{cov:.1f} s', va='center', fontsize=7.5, color=INK)
            if dur is not None and res is not None:
                ax.scatter([dur + res], [k], marker='|', s=120, color=INK, zorder=5)
        if (s := suite.stat(scen, 'auction', 'comm_loss_duration_s')):
            ax.axvline(s[0], color=INK2, lw=1, ls=(0, (3, 3)))
            ax.text(s[0], len(ALGOS) - 0.35, ' link restored', fontsize=7.5, color=INK2)
        ax.set_yticks(range(len(ALGOS)))
        ax.set_yticklabels([NAMES[a] for a in reversed(ALGOS)])
        ax.set_title(f'{SCEN_NAMES[scen]}: time from loss start (s)', loc='left', fontsize=9)
        ax.set_xlim(left=0)
        _style(ax)
    fig.text(0.01, 0.01, 'Solid: detection (5 s heartbeat timeout); medium: until reassignment; light: until every task\n'
             'of the lost drone is visited again. Tick: lost drone back in service after the link returns.',
             fontsize=7, color=INK2)
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    fig.savefig(out, dpi=200)
    plt.close(fig)
    return out


def completion_bars(suite, out):
    """runs completed / with a crashed drone per scenario and algorithm (grouped horizontal bars)."""
    fig, axes = plt.subplots(1, len(suite.scenarios), figsize=(7.2, 1.9), sharey=True, squeeze=False)
    for j, scen in enumerate(suite.scenarios):
        ax = axes[0][j]
        for k, a in enumerate(reversed(ALGOS)):
            n, done, crash = suite.counts(scen, a)
            if not n:
                continue
            ax.barh(k, done, height=0.55, color=COLORS[a], edgecolor=SURFACE, lw=1.5)
            ax.text(n + 0.15, k, f'{done}/{n}' + (f'  ({crash} crash)' if crash else ''), va='center',
                    fontsize=7.5, color=INK)
        ax.set_xlim(0, 9.5)
        ax.set_xticks([0, 5])
        ax.set_yticks(range(len(ALGOS)))
        ax.set_yticklabels([NAMES[a] for a in reversed(ALGOS)])
        ax.set_title(SCEN_NAMES[scen], fontsize=9)
        _style(ax)
    fig.supxlabel('runs that completed the mission', fontsize=8, color=INK2)
    fig.tight_layout()
    fig.savefig(out, dpi=200)
    plt.close(fig)
    return out


def equation(tex, out, size=11):
    """render a mathtext equation to a tight PNG; returns (path, width_pt, height_pt)."""
    fig = plt.figure(figsize=(0.01, 0.01))
    t = fig.text(0, 0, f'${tex}$', fontsize=size, color=INK)
    fig.savefig(out, dpi=300, bbox_inches='tight', pad_inches=0.04, transparent=False)
    w, h = fig.get_size_inches()
    plt.close(fig)
    from PIL import Image as PI
    im = PI.open(out)
    return out, im.size[0] / 300 * 72, im.size[1] / 300 * 72


def dot(src, out):
    """render graphviz source to PNG (200 dpi)."""
    subprocess.run(['dot', '-Tpng', '-Gdpi=200', '-o', str(out)], input=src.encode(), check=True)
    return out


GV_HEAD = '''graph [fontname="DejaVu Sans", fontsize=11, bgcolor="white", pad=0.2, nodesep=0.35, ranksep=0.38];
node [fontname="DejaVu Sans", fontsize=10, shape=box, style="rounded,filled", fillcolor="#f4f4f2", color="#8a8984", penwidth=1.2];
edge [fontname="DejaVu Sans", fontsize=9, color="#52514e", penwidth=1.1, arrowsize=0.7];'''

DIAGRAMS = {
    'architecture': f'''digraph G {{ {GV_HEAD} rankdir=LR; compound=true;
  subgraph cluster_sim {{ label="Simulation (one machine)"; style="rounded,dashed"; color="#b9b8b2"; fontsize=10;
    gz [label="Gazebo Harmonic\\nfactory world\\n(18 obstacle boxes)"];
    px4 [label="PX4 SITL x3\\n(x500, offboard\\nposition control)"];
    xrce [label="Micro XRCE-DDS\\nagent"];
  }}
  subgraph cluster_drone {{ label="On board (per drone, C / rclc)"; style="rounded,dashed"; color="#b9b8b2"; fontsize=10;
    ctrl [label="patrol_controller\\nstate machine, auction (drone 0),\\nheartbeat monitor, fault injection", fillcolor="#e3eefb"];
  }}
  subgraph cluster_gs {{ label="Ground station (Python / rclpy)"; style="rounded,dashed"; color="#b9b8b2"; fontsize=10;
    coord [label="coordinator_node\\nmission + algorithm.compute()\\nAPF / RL at 10 Hz", fillcolor="#fde9df"];
    met [label="metrics_collector\\n-> RunMetrics\\nsummary CSV, detail JSON", fillcolor="#e0f3ec"];
  }}
  gz -> px4 [label="sensors"]; px4 -> gz [label="motors"];
  px4 -> xrce [dir=both, label="uORB"]; xrce -> ctrl [dir=both, label="fmu/in, fmu/out"];
  coord -> ctrl [dir=both, label="Mission, MovementCommand (down)\\nDroneState heartbeat (up)"];
  ctrl -> ctrl [label="bids, assignments"];
  ctrl -> met [label="ground truth,\\nevents"]; coord -> met [label="events"];
}}''',
    'auction': f'''digraph G {{ {GV_HEAD} rankdir=TB;
  m [label="Mission received\\n(M tasks, all unassigned)", shape=box];
  w [label="drone 0 waits 5 s\\n(peer states arrive)"];
  sel [label="next unassigned task j\\n(file order)"];
  cost [label="for each eligible drone i\\n(healthy, n_i < ceil(M / N_h)):\\nc_ij = |p_i - q_j| + 15 n_i + 0.2 (100 - b_i)"];
  win [label="assign j to argmin_i c_ij\\npublish TaskAssignment", fillcolor="#e3eefb"];
  more [label="unassigned\\ntasks left?", shape=diamond, style=filled, fillcolor="#ffffff"];
  loop [label="every drone loops\\nits own tasks", fillcolor="#e0f3ec"];
  hb [label="heartbeat silent 5 s\\nor battery < 20 %", shape=diamond, style=filled, fillcolor="#ffffff"];
  rev [label="mark FAILED, revoke its tasks\\n(-> unassigned)", fillcolor="#fde9df"];
  m -> w -> sel -> cost -> win -> more; more -> sel [label="yes"]; more -> loop [label="no"];
  loop -> hb; hb -> rev [label="yes"]; rev -> sel; hb -> loop [label="no"];
}}''',
    'statemachine': f'''digraph G {{ {GV_HEAD} rankdir=LR;
  s0 [label="0 WAIT_STAGGER\\n3 s x drone id"];
  s1 [label="1 ASCEND\\nto transit layer\\n5.0 / 6.25 / 7.5 m"];
  s2 [label="2 TRANSIT_CENTER\\nfly to corridor (0,0)"];
  s3 [label="3 TRANSIT_TARGET\\nfly above task"];
  s4 [label="4 DESCEND + INSPECT\\nhover (task dwell)", fillcolor="#e0f3ec"];
  h [label="proximity hold:\\nlower-id peer < 2.5 m\\nof my target", fillcolor="#fde9df"];
  s0 -> s1 -> s2 -> s3 -> s4; s4 -> s1 [label="next task\\nin my loop"];
  s2 -> h [style=dashed]; s3 -> h [style=dashed]; h -> s2 [style=dashed, label="clear"];
}}''',
    'apf': f'''digraph G {{ {GV_HEAD} rankdir=TB;
  in [label="10 Hz tick: states of active drones\\n(heartbeat < 5 s)"];
  g [label="goal g = task point of the drone's\\ncurrent assignment (from the auction)"];
  cap [label="|g - p| < 1.2 m ?", shape=diamond, style=filled, fillcolor="#ffffff"];
  exact [label="command = g"];
  f [label="F = F_att + F_obs + F_drone\\n(attraction, Khatib box repulsion,\\nKhatib drone repulsion)", fillcolor="#fde9df"];
  v [label="v = 0.8 F + 0.2 v_prev ; |v| <= 1.5 m/s"];
  out [label="MovementCommand: p + v * 1 s\\n-> PX4 offboard position setpoint", fillcolor="#e3eefb"];
  in -> g -> cap; cap -> exact [label="yes"]; cap -> f [label="no"]; f -> v -> out; exact -> out;
}}''',
    'rl': f'''digraph G {{ {GV_HEAD} rankdir=TB;
  a [label="drone starts a leg: start p, goal = assigned task\\n(allocation: the same on-board auction)"];
  b [label="PPO policy proposals for the direct leg: 48 conditions\\n(12 threat budgets u x 4 preferences w) x (1 deterministic + 3 sampled)\\n+ the straight path = 193 candidate paths", fillcolor="#e0f3ec"];
  e [label="each proposal = 10 nodes (r, psi, phi) in NMOPSO's encoding,\\nscored with MyCost F = (J1 length, J2 threat, J3 altitude, J4 smoothness)"];
  f [label="any feasible\\n(finite F, inside\\nkeep-in box)?", shape=diamond, style=filled, fillcolor="#ffffff"];
  pick [label="short-safe pick: threat J2 within 10 % of the lowest,\\nthen the shortest (J1)", fillcolor="#e3eefb"];
  cem [label="CEM refinement from the\\nleast-violating proposals"];
  f2 [label="feasible?", shape=diamond, style=filled, fillcolor="#ffffff"];
  r [label="route decomposition: A* route on a 0.5 m grid,\\nline-of-sight via points, plan each sub-leg (split again, depth <= 4)"];
  fl [label="no feasible plan: hold,\\nretry every 2 s (no fallback)", fillcolor="#fde9df"];
  fo [label="fly on own layer (1.8 m + 1.0 m x id):\\ncarrot follower 1.5 m/s, yield to lower id < 2.5 m", fillcolor="#e3eefb"];
  a -> b -> e -> f; f -> pick [label="yes"]; f -> cem [label="no"]; cem -> f2; f2 -> pick [label="yes"];
  f2 -> r [label="no"]; r -> pick [label="all sub-legs ok"]; r -> fl [label="fails"]; pick -> fo;
}}''',
    'nmopso': f'''digraph G {{ {GV_HEAD} rankdir=TB;
  subgraph cluster_s {{ label="NMOPSO search for one leg (authors' NMOPSO.m)"; fontname="DejaVu Sans"; fontsize=9; color="#c9c8c2";
    i [label="100 random particles x = (r, psi, phi) x 10 nodes\nre-drawn until one path is feasible"];
    ev [label="decode + score all particles in one batch\nMyCost F = (J1, J2, J3, J4)", fillcolor="#f6dde8"];
    rp [label="repository R: non-dominated feasible paths\n(max 50, crowded grid cells pruned)"];
    ld [label="leader per particle from the hypergrid\nP(cell) ~ exp(-2 N_cell)"];
    mv [label="velocity + position update (w, c1, c2)\nmirror at bounds; mutation with p_m(t)"];
    it [label="500\niterations?", shape=diamond, style=filled, fillcolor="#ffffff"];
    pk [label="short-safe member of R", fillcolor="#e3eefb"];
    i -> ev -> rp -> it; it -> pk [label="done"]; it -> ld [label="no"]; ld -> mv; mv -> ev [constraint=false];
  }}
  subgraph cluster_r {{ label="run time"; fontname="DejaVu Sans"; fontsize=9; color="#c9c8c2";
    st [label="drone starts a leg to its assigned task"];
    ca [label="leg in the plan cache\n(start within 1 m)?", shape=diamond, style=filled, fillcolor="#ffffff"];
    use [label="use the cached path (instant)", fillcolor="#e3eefb"];
    bg [label="plan in the background thread\n(route decomposition if blocked);\ndrone holds meanwhile"];
    fo [label="fly on own layer: carrot follower,\nyield to lower id (as RL)", fillcolor="#e3eefb"];
    st -> ca; ca -> use [label="yes"]; ca -> bg [label="no"]; use -> fo; bg -> fo [label="plan arrives"];
  }}
}}''',
    'ppo': f'''digraph G {{ {GV_HEAD} rankdir=LR;
  sample [label="sample 8192 legs\\n(70 % real-leg lengths),\\npreference w, budget u"];
  roll [label="roll out policy\\n10 steps / episode"];
  rew [label="reward: dense threat per\\nsegment + terminal\\n-(w . F / F_scale) - budget pen."];
  gae [label="advantages\\n(GAE, gamma = lambda = 1)"];
  upd [label="PPO-clip update\\n(eps = 0.2, KL stop 0.02,\\n10 epochs)", fillcolor="#e0f3ec"];
  sample -> roll -> rew -> gae -> upd; upd -> sample [label="2000 iterations"];
}}''',
    'metrics': f'''digraph G {{ {GV_HEAD} rankdir=LR;
  ev [label="controllers: ground-truth state 10 Hz,\\ntask_completed, task_assigned,\\nfault + compute_stats events"];
  col [label="metrics_collector\\n(evaluation window)"];
  rm [label="RunMetrics\\n20 Hz interpolated timeline", fillcolor="#e0f3ec"];
  sum [label="per-run summary CSV\\n+ metrics_detail.json"];
  agg [label="aggregate_suite.py\\nmean, 95 % CI (t), best/tie"];
  rep [label="figures + this report"];
  ev -> col -> rm -> sum -> agg -> rep;
}}''',
}
