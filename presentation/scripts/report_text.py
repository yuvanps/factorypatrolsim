"""Text of the benchmark report (presentation/scripts/build_report.py).

write(B, suite, tests) appends every section to B.story; numbers come from the suite through B.v / B.m,
so the text and the figures always describe the same data.
"""
from datetime import date

from reportlab.lib.units import cm
from reportlab.platypus import PageBreak, Paragraph, Spacer

import report_figures as rf

A = rf.ALGOS
N = rf.NAMES


def front_matter(B, suite, toc):
    from build_report import ST
    n_runs = sum(len(v) for v in suite.runs.values())
    out = [Spacer(1, 2.2 * cm),
           Paragraph('Benchmarking swarm coordination algorithms for factory drone patrol', ST['title']),
           Paragraph('Market-based auction, artificial potential fields, a PPO leg planner and NMOPSO in PX4/Gazebo: '
                     'methods, metrics, results and recommendations', ST['subtitle']),
           Paragraph(f'Benchmark suite <font name="Mono">{suite.path.name}</font> &nbsp;·&nbsp; {n_runs} simulated '
                     f'missions &nbsp;·&nbsp; generated {date.today().isoformat()}', ST['caption']),
           Spacer(1, 0.8 * cm), Paragraph('<b>Abstract</b>', ST['h3']),
           Paragraph(abstract(B), ST['abstract']), Spacer(1, 0.8 * cm), toc, PageBreak()]
    return out


def abstract(B):
    return (
        'Indoor factory patrol with small multirotors needs coordination that is efficient, safe in cluttered '
        'aisles and robust to the radio fading typical of metal-rich halls. We benchmark four coordination '
        'approaches on one platform (ROS 2 Jazzy, PX4 SITL, Gazebo Harmonic, three x500 quadrotors): a '
        'centralised sequential single-item <b>auction</b> with fixed transit layers, reactive '
        '<b>artificial potential field (APF)</b> navigation, a <b>reinforcement-learning (PPO) leg planner</b> '
        'trained on the NMOPSO path model, and <b>NMOPSO</b> itself, a multi-objective particle swarm path '
        'planner. All four share the same task allocation, failure detector and measurement pipeline, so '
        'differences are attributable to navigation and fault behaviour. Four scenarios (nominal patrol, a '
        'spatial-conflict stress test, and two communication-blackout faults) are repeated and scored on '
        'efficiency, effectiveness, safety, fairness, coordination '
        'overhead and robustness metrics, following a recent review framework for industrial drone swarms. '
        + rt_abstract_findings(B))


def rt_abstract_findings(B):
    return RESULTS.get('abstract_findings', '')


RESULTS = {}      # filled by report_results.py (interpretation, written against the suite's data)


def write(B, suite, tests):
    import report_results
    RESULTS.update(report_results.text(B, suite, tests))
    intro(B)
    platform(B)
    algorithms(B)
    metrics(B)
    report_results.results(B, suite, tests)
    report_results.discussion(B, suite)
    report_results.conclusion(B, suite)
    limitations(B)
    appendix(B, suite, tests)


# ------------------------------------------------------------------------------------------------- 1
def intro(B):
    B.h1('Introduction')
    B.p('Drone swarms are increasingly proposed for routine inspection in manufacturing plants: reading gauges, '
        'checking machines and racks, and watching for anomalies between scheduled maintenance rounds. A '
        'factory hall is a difficult airspace. It is GPS-denied, dense with tall racks and machines, shared '
        'with people, and its steel structure causes multipath fading that can silence a drone\'s radio for '
        'seconds at a time. A coordination algorithm for such a swarm must therefore be judged not only by '
        'how fast it finishes a patrol but also by how close it lets drones come to obstacles and to each '
        'other, how evenly it spreads work, how much coordination it costs, and how it behaves when a '
        'drone drops off the network.')
    B.p('This report benchmarks four coordination approaches that represent three families in the '
        'literature, implemented on a common simulation platform:')
    B.bullets([
        '<b>Auction</b> (market-based): a centralised sequential single-item auction allocates inspection '
        'tasks; drones fly between tasks on fixed per-drone altitude layers through a shared centre corridor.',
        '<b>APF</b> (behaviour-based): the same allocation, with reactive navigation by artificial potential '
        'fields (goal attraction, Khatib repulsion from obstacles and from other drones).',
        '<b>RL (vB)</b> (learning-based): the same allocation, with each leg planned by a proximal policy '
        'optimisation (PPO) policy trained on the NMOPSO multi-objective path model, conditioned on a threat '
        'budget and on a precomputed shortest-route hint.',
        '<b>NMOPSO</b> (swarm-intelligence planner): the same allocation, with each leg planned by '
        'navigation-variable multi-objective particle swarm optimisation (Duong, Bui and Phung, 2025), '
        'the optimiser whose problem the RL policy was trained on.'])
    B.p('The comparison is deliberately controlled: all four use the same on-board auction for task '
        'allocation, the same heartbeat-based failure detector, the same PX4 flight stack and the same '
        'instrumentation. Differences in the results therefore come from <i>navigation</i> (how a drone gets '
        'from one task to the next) and from <i>what a drone does when it has no radio</i>. The metric set follows '
        'the ten core metrics of a recent review framework for industrial drone networks (mission completion '
        'time, task completion rate, flight distance, energy, workload imbalance, allocation time, task '
        'reallocations, messages exchanged, minimum inter-drone distance and failure recovery time), extended '
        'with obstacle clearance, patrol idleness and decision latency.')
    B.p('Section 2 describes the platform and scenarios, Section 3 the algorithms with their equations, '
        'Section 4 every metric and the statistical method, Section 5 the results metric by metric, Section 6 '
        'discusses suitability for factory deployment, Section 7 concludes and Section 8 lists limitations.')


# ------------------------------------------------------------------------------------------------- 2
def platform(B):
    B.h1('Simulation platform and scenarios')
    B.h2('Architecture')
    B.p('Every experiment runs the full flight stack in software-in-the-loop (Figure 1). Gazebo Harmonic '
        'simulates a 30 m × 20 m × 12 m factory hall with 18 obstacle boxes (rack rows, machines, a partition, '
        'conveyors). Three PX4 SITL instances fly x500 quadrotors in offboard position control and expose '
        'their uORB topics to ROS 2 through a Micro XRCE-DDS agent. On every drone a C controller (rclc) runs the '
        'patrol state machine, the auction (on drone 0), the heartbeat monitor and the fault injector. A '
        'ground-station coordinator (Python) publishes the mission and, for APF, RL and NMOPSO, runs the navigation '
        'algorithm at 10 Hz and publishes one MovementCommand per drone. A metrics collector records '
        'ground-truth states and events and computes every metric.')
    B.fig(rf.dot(rf.DIAGRAMS['architecture'], B.d / 'dg_architecture.png'),
          'Platform architecture. Radio traffic (DroneState heartbeats, bids, assignments, movement commands) '
          'is what the fault injector silences; the ground-truth state and events are instrumentation and '
          'are never silenced.')
    B.fig(rf.ROOT / 'presentation' / 'figures' / 'fig01_factory_map.png',
          'Factory world (top view) with the drone start positions and the six benchmark tasks (T1–T6 = '
          'task ids 101–106). The cross at (0, 0) is the auction\'s transit corridor.', width=15.5 * cm)
    B.h2('Scenarios and protocol')
    B.table([
        ['Scenario', 'Tasks', 'Fault', 'Window', 'Purpose'],
        ['benchmark', '6 tasks over racks and machines (Figure 2), 4 s inspection hover', 'none',
         'until every task is inspected once', 'nominal efficiency'],
        ['safety_stress', '8 tasks: three collinear rack-aisle tasks under transit routes, a task beside the '
                          'centre corridor (1.5, 0.5, 4.5 m), a low task inside a rack aisle (2.0 m)', 'none',
         'until every task is inspected once (watchdog 330 s)', 'spatial conflicts, safety'],
        ['comm_loss', 'benchmark tasks', 'drone 1: radio silent from t + 20 s for 15 s', '150 s',
         'failure detection and recovery'],
        ['comm_loss_orchestrator', 'benchmark tasks', 'drone 0 (auctioneer and heartbeat monitor) silent '
                                                      'from t + 20 s for 15 s', '150 s',
         'single point of failure'],
    ], 'Scenarios. A blackout silences the drone\'s radio both ways (no heartbeat, bids, assignments or '
       'commands), while it keeps flying its own state machine.', widths=[2.6 * cm, 5.0 * cm, 3.0 * cm, 2.6 * cm, 3.4 * cm])
    B.p('Each of the 12 algorithm–scenario cells is repeated five times; runs are interleaved (repeat 1 of '
        'every cell before repeat 2) so slow drift of the host affects all algorithms alike, and every run '
        'is started from a clean process state by a watchdog that also records why a run stopped. Runs '
        'stopped for an infrastructure reason (disk, log size) are excluded; runs in which a drone crashes '
        'are kept and counted, because a crash is an outcome of the algorithm.')
    B.p('Two properties of the platform shape the interpretation and are stated up front. First, the '
        'simulated battery is a time counter (0.1 % per second of mission per drone), so battery consumption '
        'measures flight time, not physical energy. Second, in every algorithm a drone inspects its first '
        'assigned task twice in a row (an artefact of the controller\'s zone loop that affects all four '
        'equally), which lengthens every mission by roughly one dwell.')


# ------------------------------------------------------------------------------------------------- 3
def algorithms(B):
    B.h1('Coordination algorithms')
    B.p('A coordination algorithm answers two questions: <i>who</i> does which task (allocation) and '
        '<i>how</i> each drone gets there without collisions (navigation). In this benchmark all four '
        'algorithms share the allocation layer of Section 3.1; they differ in navigation (Sections 3.2–3.5).')

    B.h2('Shared allocation: centralised sequential single-item auction')
    B.p('When the mission arrives, all M tasks are unassigned. After 5 s (so that every peer state has '
        'arrived), drone 0 acts as auctioneer and assigns the tasks one at a time, in file order. The cost '
        'of drone i for task j combines the 3-D distance to the task, the drone\'s current load and its '
        'battery deficit:')
    B.eq(r'c_{ij} \;=\; \|\mathbf{p}_i-\mathbf{q}_j\|_2 \;+\; 15\,n_i \;+\; 0.2\,(100-b_i)')
    B.p('where p<sub>i</sub> is the drone position, q<sub>j</sub> the task position, n<sub>i</sub> the number of '
        'tasks already assigned to drone i and b<sub>i</sub> its battery level in percent. Task j goes to the '
        'cheapest eligible drone; eligibility caps the load so that every healthy drone receives an equal '
        'share:')
    B.eq(r'i^{*}(j) \;=\; \arg\min_{i\in\mathcal{E}}\; c_{ij},\qquad '
         r'\mathcal{E} \;=\; \{\, i \;:\; h_i = 1,\;\; n_i < \lceil M / N_h \rceil \,\}')
    B.p('with h<sub>i</sub> the health flag and N<sub>h</sub> the number of healthy drones. Each drone then '
        'loops over its own tasks indefinitely (continuous patrol). Every controller also publishes bids, '
        'but the auctioneer recomputes the costs from its own view of the peer states, so the mechanism is '
        'a centralised greedy auction run on board drone 0, not a distributed consensus protocol.')
    B.p('<b>Failure detection and reallocation.</b> Every drone broadcasts its state at 10 Hz; this is the '
        'heartbeat. Drone 0 declares a peer FAILED when it has been silent for longer than the timeout, or '
        'when its battery is below 20 %, revokes its tasks and re-auctions them among the remaining drones:')
    B.eq(r't - t_i^{\,\mathrm{last}} > T_{hb} = 5\ \mathrm{s} \;\;\Rightarrow\;\; h_i \leftarrow 0,\;\; '
         r'\{\,j : i^{*}(j) = i\,\} \;\to\; \mathrm{re\!-\!auction}')
    B.p('A drone whose heartbeat returns is marked healthy again and can win tasks in later auctions. The '
        'scheme is simple and fast, but drone 0 is a single point of failure: if drone 0 itself goes '
        'silent, no other drone runs the detector or the auction (scenario comm_loss_orchestrator).')
    B.fig(rf.dot(rf.DIAGRAMS['auction'], B.d / 'dg_auction.png'),
          'Allocation and failure handling (shared by all four algorithms).', width=9.5 * cm)

    B.h2('Auction navigation: altitude layers and a centre corridor')
    B.p('With the auction algorithm, each drone also navigates on board (Figure 4). Drones take off '
        'staggered by 3 s per id, climb to a private transit layer, fly to the centre corridor (0, 0), then '
        'to above the task, and descend to the inspection point:')
    B.eq(r'h_i^{\,\mathrm{transit}} = 5.0 + 1.25\, i\ \ \mathrm{m}\ \ (\leq 10\ \mathrm{m}),\qquad '
         r'h_i^{\,\mathrm{patrol}} = 2.5 + i\ \ \mathrm{m}')
    B.p('Separate layers keep drones apart vertically, and the corridor keeps transits away from walls. '
        'A proximity rule resolves remaining conflicts: a drone holds while a lower-id drone is within 2.5 m '
        'of its target. The method needs no obstacle model; it is safe as long as every obstacle is below '
        'the lowest layer and the corridor is free, and it relies on peer positions arriving over the radio.')
    B.fig(rf.dot(rf.DIAGRAMS['statemachine'], B.d / 'dg_statemachine.png'),
          'On-board navigation state machine of the auction algorithm. APF, RL and NMOPSO replace states 1–3 by '
          'external movement commands; state 4 (descend and inspect) is shared.')

    B.h2('APF: artificial potential field navigation')
    B.p('APF is a reactive, behaviour-based method: at every tick (10 Hz) the ground station sums three '
        'virtual forces on each active drone and turns the result into a velocity command. The attraction '
        'pulls the drone towards its goal g with a saturated linear law:')
    B.eq(r'\mathbf{F}_{att} = k_{att}\,(\mathbf{g}-\mathbf{p}),\qquad \|\mathbf{F}_{att}\| \leq v_{max}')
    B.p('Obstacles and other drones repel with the Khatib potential: for every obstacle box k with surface '
        'distance d<sub>k</sub> inside the influence radius ρ<sub>o</sub>, and every other drone m within '
        'ρ<sub>d</sub>,')
    B.eq(r'\mathbf{F}_{obs} = \sum_{k:\,d_k<\rho_o} k_{o}\left(\frac{1}{d_k}-\frac{1}{\rho_o}\right)'
         r'\frac{1}{d_k^{2}}\;\mathbf{n}_k,\qquad '
         r'\mathbf{F}_{drone} = \sum_{m:\,d_m<\rho_d} k_{d}\left(\frac{1}{d_m}-\frac{1}{\rho_d}\right)'
         r'\frac{1}{d_m^{2}}\;\mathbf{n}_m', size=10.5)
    B.p('where n is the unit vector pointing away from the obstacle or drone and d is floored at 0.1 m. The '
        'command is smoothed, clipped and sent as a position set-point one horizon ahead:')
    B.eq(r'\mathbf{v}_t = \mathrm{clip}_{v_{max}}\!\left(0.8\,(\mathbf{F}_{att}+\mathbf{F}_{obs}+\mathbf{F}_{drone})'
         r' + 0.2\,\mathbf{v}_{t-1}\right),\qquad \mathbf{p}^{\,sp} = \mathbf{p} + \tau\,\mathbf{v}_t')
    B.table([
        ['Parameter', 'Symbol', 'Value', 'Meaning'],
        ['goal gain', 'k_att', '0.5 1/s', 'attraction slope'],
        ['maximum speed', 'v_max', '1.5 m/s', 'limit on attraction and command'],
        ['obstacle gain / radius', 'k_o / ρ_o', '0.5 / 1.5 m', 'repulsion balances full attraction at ~0.6 m'],
        ['drone gain / radius', 'k_d / ρ_d', '10 / 3.0 m', 'repulsion balances full attraction at ~1.5 m'],
        ['goal tolerance', '–', '1.2 m', 'inside it, the command is the goal itself'],
        ['smoothing / horizon', '–, τ', '0.2 / 1.0 s', 'velocity filter, set-point look-ahead'],
    ], 'APF parameters (config/algorithms/apf.yaml); identical in every scenario, not tuned per scenario.',
        widths=[3.8 * cm, 2.2 * cm, 2.6 * cm, 8.0 * cm])
    B.p('APF needs an obstacle model but no planning: decisions take well under a millisecond. Its known '
        'weaknesses are local minima (forces cancel before the goal) and the trade-off between repulsion '
        'strength and the ability to reach goals close to obstacles: inspection points sit next to racks and '
        'machines, so the repulsion cannot be made arbitrarily strong.')
    B.fig(rf.dot(rf.DIAGRAMS['apf'], B.d / 'dg_apf.png'), 'APF control loop (ground station, 10 Hz).', width=8.5 * cm)

    B.h2('RL (vB): a PPO leg planner on the NMOPSO path model')
    B.p('The learning-based approach replaces navigation by a policy that plans each leg (the path from '
        'the drone\'s position to its next task). It was trained with proximal policy optimisation (PPO) on '
        'the leg-planning problem of NMOPSO, a multi-objective particle-swarm path planner, so that its '
        'outputs are ordinary NMOPSO paths and can be scored with NMOPSO\'s own cost.')
    B.h3('Path model and action')
    B.p('A path has n = 10 nodes between start s and goal g. Node k is encoded in spherical coordinates '
        '(r<sub>k</sub>, ψ<sub>k</sub>, φ<sub>k</sub>) relative to the previous node, with chained transforms:')
    B.eq(r'\mathbf{T}_k = \mathbf{T}_{k-1}\,R_z(\phi_k)\,R_y(-\psi_k)\,T_x(r_k),\qquad '
         r'r_k\in[\frac{r_{max}}{9},\, r_{max}],\;\; r_{max}=\frac{3\,\|\mathbf{g}-\mathbf{s}\|}{10},\;\; '
         r'|\psi_k|,|\phi_k|\leq\frac{\pi}{4}', size=10.5)
    B.p('An episode has one step per node. The action a ∈ (−1, 1)<sup>3</sup> is a residual around the straight '
        'path: a<sub>r</sub> scales the even-spacing step r<sub>nom</sub> (remaining distance over remaining '
        'segments) by e<sup>a<sub>r</sub></sup>; a<sub>ψ</sub> turns the bearing from the goal bearing by up to '
        '±90°; a<sub>z</sub> sets the height inside the patrol band. The zero action is "straight at the goal".')
    B.h3('Objectives (NMOPSO MyCost)')
    B.p('A completed path P is scored with four objectives: length overhead, threat (proximity to obstacles '
        'modelled as cylinders of radius R<sub>m</sub>), altitude deviation and turning:')
    B.eq(r'J_1 = \left|1-\frac{\|\mathbf{g}-\mathbf{s}\|}{L(P)}\right|,\qquad '
         r'J_2 = \frac{1}{S\,M}\sum_{s=1}^{S}\sum_{m=1}^{M}\mathrm{clip}_{[0,1]}\!'
         r'\left(1-\frac{d_{sm}-\delta-R_m}{10\,\delta}\right)', size=10.5)
    B.eq(r'J_3 = \frac{1}{n}\sum_{k}\frac{|z_k-\bar z|}{\Delta z/2},\qquad '
         r'J_4 = \frac{1}{n}\sum_{k}\frac{\angle(\mathbf{e}_k,\mathbf{e}_{k+1})}{\pi}', size=10.5)
    B.p('Here d<sub>sm</sub> is the distance from segment s to cylinder m, δ the drone size (0.1 m), L(P) '
        'the path length, z̄ and Δz the centre and height of the band, and e<sub>k</sub> the segment directions. '
        'A path is infeasible (J<sub>1</sub> or J<sub>2</sub> = ∞) if a segment is too short or enters an '
        'inflated cylinder.')
    B.h3('Reward, threat budget and conditioning')
    B.p('Each training episode draws a preference w over (J<sub>1</sub>, J<sub>3</sub>, J<sub>4</sub>) and a threat '
        'budget u ∈ [0.15, 1.2] that limits J<sub>2</sub> to u times the threat of the straight path; both are '
        'observed by the policy. The terminal reward of a feasible path is the negative scaled cost plus a '
        'penalty for exceeding the budget, capped at S<sub>max</sub> = 5; an infeasible path receives a lower '
        'reward than any feasible one:')
    B.eq(r'r_T = -\min\!\left(\sum_{i\neq 2}\frac{w_i J_i}{F_i}\;+\;\lambda_b\,'
         r'\frac{\max(0,\;J_2 - u\,J_2^{\,str})}{F_2},\;\; S_{max}\right),\qquad '
         r'r_T^{\,infeasible} = -(S_{max}+1+\min(v,3))', size=10)
    B.p('with F<sub>i</sub> fixed scales (the 95th percentile of NMOPSO fronts), λ<sub>b</sub> = 50 and v a soft '
        'violation measure. In vB the threat term is paid densely, segment by segment, so that credit '
        'reaches the step that caused it (the return is unchanged), and a straight-path prior '
        '−0.02 ‖a<sub>k</sub>‖² per step keeps the policy on the straight line unless deviating pays. The '
        'observation (40 values) contains the goal in the chain frame, the reach left, height, clamping '
        'offset, steps left, leg length, heading relative to the goal bearing, 16 obstacle range rays, a '
        'route hint (bearing of the farthest visible waypoint of the shortest collision-free route, route '
        'length over the reach left and over the straight distance), the budget left and the straight '
        'path\'s threat-to-go, the budget u and the preference w.')
    B.h3('Training')
    B.p('The policy is trained with PPO-clip. With probability ratio ρ<sub>t</sub>(θ) = π<sub>θ</sub>(a<sub>t</sub>|o<sub>t</sub>)'
        ' / π<sub>θ<sub>old</sub></sub>(a<sub>t</sub>|o<sub>t</sub>) and generalised advantage estimates Â<sub>t</sub>,')
    B.eq(r'L^{CLIP}(\theta)=\mathbb{E}_t\!\left[\min\!\left(\rho_t(\theta)\,\hat A_t,\;'
         r'\mathrm{clip}(\rho_t(\theta),1-\epsilon,1+\epsilon)\,\hat A_t\right)\right],\qquad '
         r'\hat A_t=\sum_{l\geq 0}(\gamma\lambda)^l\,\delta_{t+l}', size=10.5)
    B.table([
        ['Setting', 'Value', 'Setting', 'Value'],
        ['iterations × episodes', '2000 × 8192 legs', 'actor / critic', 'MLP 3×256 tanh, conditioning fed to every layer'],
        ['PPO clip ε / KL stop', '0.2 / 0.02', 'learning rate actor / critic', '3·10⁻⁴ / 10⁻³'],
        ['γ, λ (GAE)', '1.0, 1.0 (10-step episodes)', 'epochs per iteration', '10'],
        ['policy', 'tanh-squashed Gaussian', 'training legs', '70 % with real-leg lengths, rest random'],
        ['budget penalty λ_b', '50', 'straight prior', '0.02 ‖a‖²'],
    ], 'Training configuration of the released policy vB (seed 2 of three trained seeds).',
        widths=[3.6 * cm, 3.6 * cm, 3.8 * cm, 5.6 * cm])
    B.fig(rf.dot(rf.DIAGRAMS['ppo'], B.d / 'dg_ppo.png'), 'PPO training loop.')
    B.h3('Deployment')
    B.p('At run time (flowchart at the end of this section), the planner rolls out the policy for 48 conditions (12 threat budgets × 4 '
        'preferences), one deterministic and three sampled rollouts each, plus the straight path: 193 '
        'candidates per leg, scored with the same cost. Among the feasible candidates it picks the '
        '"short-safe" path:')
    B.eq(r'\mathcal{C}=\{\,c:\; J_2^{\,c}\leq \min_{\tilde{c}} J_2^{\,\tilde{c}} + 0.1\,'
         r'(\max_{\tilde{c}} J_2^{\,\tilde{c}}-\min_{\tilde{c}} J_2^{\,\tilde{c}})\,\},\qquad '
         r'c^{*}=\arg\min_{c\in\mathcal{C}} J_1^{\,c}', size=10.5)
    B.p('If no candidate is feasible, a cross-entropy refinement is tried, and then a decomposition of the '
        'leg along an A* route into line-of-sight sub-legs, each planned by the policy. Each drone flies its '
        'path on its own layer (1.8 m + 1.0 m × id) with a carrot follower at 1.5 m/s and yields to a '
        'lower-id drone within 2.5 m. There is no fallback to an unchecked straight line: a leg without a '
        'feasible plan is held and retried. The planner runs on the coordinator\'s single thread, so a slow '
        'plan delays the commands of every drone.')
    B.fig(rf.dot(rf.DIAGRAMS['rl'], B.d / 'dg_rl.png'), 'RL leg planning at run time.', width=12 * cm)

    nmopso_section(B)

    B.h2('Summary of the four approaches')
    B.table([
        ['', 'Auction', 'APF', 'RL (vB)', 'NMOPSO'],
        ['Family', 'market-based allocation + rule-based navigation', 'behaviour-based (reactive)',
         'learning-based planner', 'swarm-intelligence planner'],
        ['Allocation', 'sequential single-item auction (drone 0)', 'same', 'same', 'same'],
        ['Navigation runs', 'on board', 'ground station, 10 Hz', 'ground station, per leg + 10 Hz follower',
         'cached / background per leg + 10 Hz follower'],
        ['Obstacle model', 'none (altitude layers, corridor)', '18 boxes', '87 cylinders (NMOPSO model)',
         '87 cylinders (NMOPSO model)'],
        ['Drone deconfliction', 'altitude layers + proximity hold', 'repulsion (3 m radius)',
         'altitude layers + yield rule', 'altitude layers + yield rule'],
        ['Without radio', 'keeps patrolling its own tasks', 'holds its last set-point', 'holds its last set-point',
         'holds its last set-point'],
        ['Planning cost', 'negligible', '< 1 ms', '10–2000 ms per plan, in the control loop',
         'about 5 s per leg, outside the control loop'],
    ], 'Properties of the four approaches.', widths=[2.6 * cm, 3.6 * cm, 3.2 * cm, 3.6 * cm, 3.6 * cm])


def nmopso_section(B):
    B.h2('NMOPSO: multi-objective particle swarm leg planning')
    B.p('NMOPSO (navigation-variable-based multi-objective particle swarm optimisation; Duong, Bui and Phung, '
        'Neural Computing and Applications 37, 2025) solves the same leg-planning problem as the RL policy: the '
        'same 10-node navigation-variable encoding (Eq. 8), bounds and MyCost objectives J<sub>1</sub>–J<sub>4</sub> '
        '(Eqs. 9–10). Instead of a trained policy it searches each leg with a swarm of P particles '
        'x<sub>i</sub> = (r, ψ, φ) ∈ ℝ<super>3n</super>, each with velocity v<sub>i</sub> and personal best p<sub>i</sub>:')
    B.eq(r'\mathbf{v}_i \leftarrow w\,\mathbf{v}_i + c_1\,\mathbf{r}_1\odot(\mathbf{p}_i-\mathbf{x}_i)'
         r' + c_2\,\mathbf{r}_2\odot(\mathbf{l}_i-\mathbf{x}_i),\qquad |\mathbf{v}_i|\leq\frac{1}{2}(x_{max}-x_{min}),'
         r'\qquad \mathbf{x}_i \leftarrow \mathrm{clip}(\mathbf{x}_i+\mathbf{v}_i)', size=10)
    B.p('with r<sub>1</sub>, r<sub>2</sub> uniform random vectors, the velocity mirrored where a variable left its '
        'bounds, and inertia w damped by 0.98 per iteration. Because the four objectives conflict, there is no '
        'single global best. NMOPSO keeps a repository R of non-dominated paths (Pareto dominance: '
        'a ≺ b if a is no worse in every objective and better in one) and draws each particle\'s leader '
        'l<sub>i</sub> from a hypergrid over R, preferring sparsely occupied cells:')
    B.eq(r'P(\mathrm{cell}\ c)=\frac{e^{-\beta N_c}}{\sum_{c\prime} e^{-\beta N_{c\prime}}},\qquad '
         r'p_m(t)=\left(1-\frac{t-1}{T-1}\right)^{1/\mu},\qquad '
         r'\mathbf{x}_i^{\,mut}=\mathbf{x}_i+\mathcal{N}(0,1)\odot\mathbf{p}_i\,\tanh(\delta\,|R|)', size=10)
    B.p('N<sub>c</sub> is the number of repository members in cell c. With the decaying probability p<sub>m</sub> a '
        'particle is mutated; the mutant replaces it if it dominates it, or with probability 0.5 if neither '
        'dominates. When R exceeds its size, members of crowded cells are deleted (probability ∝ e<super>γN<sub>c</sub></super>). '
        'After the last iteration, the deployed path is the short-safe member of R (Eq. 13), the same rule as '
        'for RL.')
    B.table([
        ['Parameter', 'Value', 'Parameter', 'Value'],
        ['swarm size P', '100', 'iterations T', '500'],
        ['repository size', '50', 'inertia w, damping', '1.0, 0.98'],
        ['c₁, c₂', '1.5, 1.5', 'grid divisions per objective', '5 (inflation 0.1)'],
        ['leader / deletion pressure β, γ', '2, 2', 'mutation μ, δ', '0.5, 20'],
    ], 'NMOPSO parameters: the authors\' published code, unchanged.', widths=[4.4 * cm, 3.0 * cm, 4.6 * cm, 4.6 * cm])
    B.h3('Implementation and planning time')
    B.p('The planner is a vectorised port of the authors\' MATLAB NMOPSO.m: the whole swarm is decoded and scored '
        'in one batched MyCost evaluation per iteration (PyTorch, verified against the MATLAB cost), which cuts the '
        'time per leg from a median of 369 s for the MATLAB original on the 73 factory legs to about 5 s. One '
        'detail of the authors\' code is corrected: their mutation clamps every mutated variable to its lower '
        'bound; the port clamps to [x<sub>min</sub>, x<sub>max</sub>] as the paper describes. Five seconds is still '
        'fifty coordination ticks, so planning never runs inside the 10 Hz loop:')
    B.bullets([
        '<b>Plan cache.</b> The legs between the scenario\'s fixed points (each drone\'s take-off point to every '
        'task, and every task to every other task) are planned before the run, in parallel, with the same '
        'planner and seeds; at run time a leg starting within 1 m of a cached start uses the cached path.',
        '<b>Background planning.</b> Any other leg (for example from wherever a drone was holding when its radio '
        'returned) is planned in a worker thread while the drone holds its position; the result is applied '
        'when it arrives and added to the cache.',
        '<b>Shared remainder.</b> Route decomposition of blocked legs, the per-drone layers, the carrot follower '
        'and the yield rule are the RL algorithm\'s code, so RL and NMOPSO differ only in how the candidate '
        'paths of a leg are produced.',
    ])
    B.fig(rf.dot(rf.DIAGRAMS['nmopso'], B.d / 'dg_nmopso.png'), 'NMOPSO search for one leg (left) and its use at '
          'run time (right).', width=14 * cm)


# ------------------------------------------------------------------------------------------------- 4
def metrics(B):
    B.h1('Metrics and methodology')
    B.p('All metrics are computed by the same collector for every algorithm, from the controllers\' '
        'ground-truth state stream (10 Hz per drone) and their events (task completed, task assigned, '
        'fault and compute-time events). Positions are interpolated onto a common 20 Hz timeline for every '
        'distance-based metric. The mission window runs from the mission dispatch to the first completion of '
        'the last task; in the fault scenarios an observation window of 150 s is used for fault, safety and '
        'patrol metrics, so that recovery after the first patrol cycle is measured.')
    B.fig(rf.dot(rf.DIAGRAMS['metrics'], B.d / 'dg_metrics.png'), 'Measurement pipeline.')
    B.h2('Efficiency and effectiveness')
    B.eq(r'\mathrm{MCT} = t_{end}-t_0,\qquad \mathrm{TCR} = 100\,\frac{|\{\,j : j\ \mathrm{completed}\,\}|}{M},'
         r'\qquad \mathrm{TFD}=\sum_{i}\sum_{k}\|\mathbf{p}_{i,k}-\mathbf{p}_{i,k-1}\|')
    B.p('MCT is the mission completion time (dispatch to the completion of the last not-yet-completed task), '
        'TCR the task completion rate and TFD the total 3-D flight distance over all drones. Battery consumed '
        'is reported for completeness; because the simulated battery is a time counter, it is proportional to '
        'mission time. Patrol <b>idleness</b>, the standard multi-robot patrolling measure, is the time since a '
        'task was last inspected, I<sub>j</sub>(t) = t − (last visit of j); we report its time average over tasks '
        'and the window (average idleness) and its maximum (worst coverage gap):')
    B.eq(r'\bar I = \frac{1}{M\,T}\sum_{j=1}^{M}\int_0^{T} I_j(t)\,dt,\qquad I_{max} = \max_{j,t} I_j(t)')
    B.h2('Safety')
    B.p('<b>Obstacle clearance</b> is the distance from a drone\'s centre to the nearest obstacle box (0 inside a '
        'box; the floor is excluded and only airborne samples above 0.5 m count). A <i>near miss</i> is time below '
        '0.6 m (twice the airframe half-size), a <i>contact</i> an episode below 0.3 m, where the airframe touches '
        'the box. Between drones, the review framework\'s <b>minimum inter-drone distance</b> is complemented by '
        'the swarm separation profile, its percentiles and violations of the safety radius d<sub>safe</sub> = 1.0 m:')
    B.eq(r's(t) = \min_{i\neq j}\|\mathbf{p}_i(t)-\mathbf{p}_j(t)\|,\qquad \mathrm{MIDD}=\min_t s(t),\qquad '
         r's_{p1},\, s_{p5} = \mathrm{1st,\ 5th\ percentile\ of\ } s(t)')
    B.p('Violations count episodes with s(t) &lt; d<sub>safe</sub>; drone contacts count episodes of a pair closer '
        'than 0.6 m. A crashed drone (outside the hall, on the ground while in a flying state, or reporting '
        'FAILED) is excluded from later position samples and its run is counted as a run with a crash.')
    B.h2('Fairness')
    B.p('Workload imbalance is computed on two workload definitions, as the review framework recommends: '
        'task completions per drone and flight distance per drone, w<sub>i</sub>, over the evaluation window. '
        'We report one minus Jain\'s fairness index and the Gini coefficient:')
    B.eq(r'\mathrm{WI} = 1-\frac{(\sum_i w_i)^2}{N\sum_i w_i^2}\;\in[0,\,1-\frac{1}{N}],\qquad '
         r'G = \frac{\sum_i\sum_j |w_i-w_j|}{2\,N^2\,\bar w}')
    B.h2('Coordination overhead')
    B.p('<b>Allocation latency</b> is the time from mission dispatch to the first task assignment and to the '
        'moment every task has been assigned once; the ratio of the latter to MCT is the share of the mission '
        'spent organising (the framework flags ratios above 0.3 as coordination-bound). <b>Task '
        'reallocations</b> count assignments that move a task to a different drone (re-assigning a task to the '
        'same drone is not counted), in total and per minute. <b>Decision time</b> is the wall time of one '
        'navigation decision in the coordinator (APF, RL and NMOPSO; the mean, 95th percentile and maximum), and '
        'allocation time the on-board auction step. Message volume (MBE in the framework) is not yet '
        'instrumented; Section 8 discusses it.')
    B.h2('Robustness to communication loss')
    B.p('For the injected blackout starting at t<sub>0</sub> and ending at t<sub>1</sub>, the failure-recovery time '
        'of the framework is decomposed into its components:')
    B.eq(r't_{detect}=t_{FAILED}-t_0,\quad t_{reassign}=t_{1st\ reassignment}-t_0,\quad '
         r'T_{recovery}=\max_{j\in\mathcal{L}}\; t_{revisit}(j)-t_0', size=10.5)
    B.p('where 𝓛 is the set of tasks the lost drone held. Further: <i>rejoin</i> (link back to heartbeat '
        'accepted), <i>back in service</i> (link back to the lost drone\'s next completed task), the minimum '
        'separation between the lost drone and the others while positions are not shared, and the framework\'s '
        '<i>transient safety degradation</i> over [t<sub>0</sub>, t<sub>1</sub> + 10 s]: its depth, '
        'max(0, d<sub>safe</sub> − min s(t)), and its duration, the time with s(t) &lt; d<sub>safe</sub>.')
    B.h2('Statistics')
    B.p('Each cell has n = 5 runs for auction, APF and RL and n = 2 for NMOPSO (fewer for metrics that only exist in completed runs). We report the mean '
        'with a 95 % confidence interval from the t distribution (n − 1 degrees of freedom). An algorithm is '
        'called best on a metric only if its interval does not overlap the runner-up\'s; otherwise the result '
        'is a tie. Because several metrics are bounded or skewed, we additionally apply the non-parametric '
        'Kruskal–Wallis test across the four algorithms and pairwise two-sided Mann–Whitney U tests with '
        'Holm correction, reporting the rank-biserial correlation r as effect size (Appendix C). With five '
        'runs per group, the smallest attainable pairwise p-value is 0.008, so only consistent, complete '
        'separations reach significance; for NMOPSO (two runs against five) it is 0.095, so no pairwise test '
        'involving NMOPSO can be significant. The paired Wilcoxon test suggested by the framework is not used: '
        'runs of different algorithms are not paired, and with n = 5 it cannot reach p &lt; 0.05.')
    B.table([
        ['Review-framework metric', 'This benchmark', 'Status'],
        ['Mission completion time (MCT)', 'mission_completion_time_s', 'measured'],
        ['Task completion rate (TCR)', 'task_completion_rate_percent', 'measured'],
        ['Total flight distance (TFD)', 'total_flight_distance_m', 'measured'],
        ['Total energy consumed (TEC)', 'total_battery_consumed_percent', 'modelled as time (see 2.2)'],
        ['Workload imbalance (WI)', 'workload_imbalance_tasks / _distance, Gini', 'measured (new)'],
        ['Allocation time (AT)', 'alloc_first_assignment_s, alloc_all_assigned_s, ratio to MCT', 'measured (new)'],
        ['Task reallocations (TR)', 'task_reallocations, per minute', 'measured (new)'],
        ['Messages/bytes exchanged (MBE)', '–', 'not instrumented'],
        ['Minimum inter-drone distance (MIDD)', 'minimum, 1st/5th percentile, violations of 1.0 m', 'measured (extended)'],
        ['Failure recovery time (FRT)', 't_detect, t_reassign, T_recovery, rejoin, resume, transient safety', 'measured'],
        ['– (added)', 'obstacle clearance, near misses, contacts; idleness; decision time', 'measured'],
    ], 'Mapping of the review framework\'s ten core metrics to this benchmark.', widths=[5.0 * cm, 8.3 * cm, 3.3 * cm])


# ------------------------------------------------------------------------------------------------- 8
def limitations(B):
    B.h1('Limitations and threats to validity')
    B.bullets([
        '<b>Simulation only.</b> PX4 SITL in Gazebo, without wind, sensor noise beyond PX4 defaults or '
        'radio models other than the injected blackout. Absolute times and distances will differ on hardware; '
        'the ranking of mechanisms (Section 6) is the transferable result.',
        '<b>Five runs per cell, two for NMOPSO.</b> Outcomes that are bimodal (crash or no crash) produce wide '
        'intervals; ties in such cells mean "not separable with five runs". NMOPSO was run twice per scenario '
        'for time reasons: its means are measured, but its intervals are wide and its differences to the others '
        'cannot be tested for significance.',
        '<b>Different windows.</b> The benchmark and safety_stress runs end after the first patrol cycle, '
        'while the communication-loss runs are observed for 150 s, i.e. two to three cycles. Safety counts '
        '(contacts, violations) in the communication-loss scenarios therefore include later laps that the '
        'nominal benchmark never observes; they are not all caused by the blackout.',
        '<b>Blackout timing and NMOPSO\'s plan cache.</b> In both communication-loss scenarios the blackout '
        'starts 20 s into the mission, which in every run fell while the lost drone was inspecting a task. On '
        'reconnection its next leg therefore started at a task point and came from NMOPSO\'s plan cache '
        'instantly; the only legs planned during a run were 3–5 cm hops. A blackout that starts mid-flight, '
        'followed by a change of task, would leave the drone at a point no cached leg starts from: it would hover '
        'while the leg is planned in the background (about 5 s, about 20 s if the leg must be decomposed). '
        'NMOPSO\'s recovery times (Section 5.6) hold for these scenarios and would be longer for mid-flight '
        'blackouts, where RL plans a leg in 0.1–1.6 s (but stalls every drone\'s commands while it does). '
        'The other drones are not affected: legs to reassigned tasks start at the task they just inspected and '
        'are cached.',
        '<b>One configuration per algorithm.</b> APF uses one parameter set, RL one policy (vB, seed 2) and '
        'NMOPSO the authors\' published parameters. '
        'None was tuned for these scenarios; a parameter study could move APF along its speed–safety '
        'trade-off.',
        '<b>Shared allocation.</b> All four use the same auction, so allocation latency, reallocations and '
        'detection measure the platform, not the navigation method. Other allocation families (consensus '
        'auctions such as CBBA, bio-inspired allocation) are outside this benchmark.',
        '<b>Energy and messages.</b> The battery is a time counter, so no energy ranking is possible; message '
        'volume is not instrumented yet.',
        '<b>Fixable engineering effects.</b> RL\'s planning runs on the coordinator\'s single thread (worst '
        'decisions near 2 s), and allocation and failure detection run on drone 0 only. Both are platform '
        'choices that a deployment would change, not properties of the algorithms.',
        '<b>Three drones, one hall.</b> Scalability to larger swarms and other layouts is not tested.'])


# ------------------------------------------------------------------------------------------------- appendix
APPX_METRICS = [
    ('task_completion_rate_percent', 'Task completion (%)', 0), ('mission_completion_time_s', 'Mission time (s)', 1),
    ('total_flight_distance_m', 'Flight distance (m)', 1), ('total_battery_consumed_percent', 'Battery (%)', 2),
    ('mean_task_idleness_s', 'Average idleness (s)', 1), ('max_task_idleness_s', 'Worst idleness (s)', 1),
    ('min_obstacle_clearance_m', 'Min obstacle clearance (m)', 2), ('obstacle_near_miss_s', 'Obstacle near miss (drone-s)', 2),
    ('obstacle_contacts', 'Obstacle contacts', 1), ('minimum_inter_drone_distance_m', 'MIDD (m)', 2),
    ('separation_p1_m', 'Separation p1 (m)', 2), ('separation_p5_m', 'Separation p5 (m)', 2),
    ('separation_violations', 'Violations < 1.0 m', 1), ('separation_contacts', 'Drone contacts', 1),
    ('workload_imbalance_tasks', 'WI tasks (1 − Jain)', 3), ('workload_imbalance_distance', 'WI distance (1 − Jain)', 3),
    ('workload_gini_distance', 'Gini distance', 3), ('task_reallocations', 'Task reallocations', 1),
    ('alloc_all_assigned_s', 'All tasks assigned (s)', 2), ('allocation_to_mct_ratio', 'Allocation / MCT', 3),
    ('decision_time_mean_ms', 'Decision time mean (ms)', 2), ('decision_time_max_ms', 'Decision time max (ms)', 1),
    ('detection_s', 'Detection (s)', 2), ('reassignment_s', 'Reassignment (s)', 2),
    ('coverage_restored_s', 'Coverage restored (s)', 1), ('resume_s', 'Back in service (s)', 1),
    ('min_separation_during_loss_m', 'Min sep. lost drone (m)', 2), ('loss_safety_depth_m', 'Safety depth (m)', 2),
    ('loss_safety_time_s', 'Time below 1.0 m (s)', 2),
]


def appendix(B, suite, tests):
    B.story.append(PageBreak())
    B.h1('Appendix')
    B.h2('A. Results per scenario')
    for scen in suite.scenarios:
        rows = [['Metric'] + [N[a] for a in A]]
        cnt = ['Runs completed / with crash'] + [f'{suite.counts(scen, a)[1]}/{suite.counts(scen, a)[0]} / '
                                                 f'{suite.counts(scen, a)[2]}' for a in A]
        rows.append(cnt)
        for key, label, d in APPX_METRICS:
            cells = [B.v(scen, a, key, d) for a in A]
            if all(c == '–' for c in cells):
                continue
            rows.append([label] + cells)
        B.table(rows, f'{scen}: mean ± 95 % CI half-width over the runs (time, distance, battery and the '
                      f'allocation ratio: completed runs only; NMOPSO: two runs).',
                widths=[4.4 * cm] + [(16.6 - 4.4) / len(A) * cm] * len(A))
    B.h2('B. Reproduction')
    B.p('<font name="Mono" size="8">./scripts/run_suite.sh &lt;name&gt; 5</font> runs the suite (resumable); '
        '<font name="Mono" size="8">python3 scripts/aggregate_suite.py experiment_results/suites/&lt;name&gt;</font> '
        'writes the tables; '
        '<font name="Mono" size="8">presentation/.venv/bin/python presentation/scripts/build_report.py '
        'experiment_results/suites/&lt;name&gt;</font> rebuilds this report. Metric definitions with every '
        'threshold are in docs/METRICS.md; the RL training log is rl-nmopso-factory-patrol/LOOP.md.')
    B.h2('C. Significance tests')
    B.p('Kruskal–Wallis p-value across the four algorithms, and pairwise Mann–Whitney U tests (two-sided, '
        'Holm-corrected p) with the rank-biserial correlation r (r &gt; 0: the first algorithm of the pair has '
        'larger values; |r| = 1: complete separation). Only metrics with variation are listed.')
    keys = [('mission_completion_time_s', 'Mission time'), ('total_flight_distance_m', 'Flight distance'),
            ('mean_task_idleness_s', 'Average idleness'), ('min_obstacle_clearance_m', 'Obstacle clearance'),
            ('obstacle_contacts', 'Obstacle contacts'), ('separation_p5_m', 'Separation p5'),
            ('separation_violations', 'Violations'), ('workload_imbalance_distance', 'WI distance'),
            ('task_reallocations', 'Reallocations'), ('coverage_restored_s', 'Coverage restored'),
            ('resume_s', 'Back in service')]
    short = {'auction': 'Auc', 'apf': 'APF', 'rl': 'RL', 'nmopso': 'NM'}
    rows = [['Scenario', 'Metric', 'KW p', 'Pairs: p (Holm), r']]
    for scen in suite.scenarios:
        for key, label in keys:
            res = tests(suite, scen, key)
            if not res:
                continue
            kw, pairs = res
            pr = '; '.join(f'{short[a]}–{short[b]}: {p:.3f}, {r:+.2f}' for (a, b), p, r in pairs)
            rows.append([scen, label, f'{kw:.3f}', pr])
    B.table(rows, 'Non-parametric tests per scenario and metric.', widths=[3.2 * cm, 2.8 * cm, 1.4 * cm, 9.2 * cm])
