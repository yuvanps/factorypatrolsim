"""Results, discussion and conclusion of the benchmark report.

Every number is read from the suite (B.v: "mean ± CI half-width", B.m: mean); the interpretation was
written against suite_final (suite_tier1 + NMOPSO, two runs per scenario) and states mechanisms, which docs/RESULTS.md also documents.
"""
import report_figures as rf

A = rf.ALGOS
N = rf.NAMES


def text(B, suite, tests):
    v = B.v
    return {'abstract_findings': (
        f'No approach dominates. Auction and APF finish the nominal patrol fastest '
        f'({v("benchmark", "auction", "mission_completion_time_s")} s and '
        f'{v("benchmark", "apf", "mission_completion_time_s")} s, against '
        f'{v("benchmark", "rl", "mission_completion_time_s")} s for RL and '
        f'{v("benchmark", "nmopso", "mission_completion_time_s")} s for NMOPSO), and APF flies the shortest paths. '
        f'In the cluttered stress scenario, however, APF crashed a drone in '
        f'{suite.counts("safety_stress", "apf")[2]} of {suite.counts("safety_stress", "apf")[0]} runs and the '
        f'auction in {suite.counts("safety_stress", "auction")[2]} of {suite.counts("safety_stress", "auction")[0]}, '
        f'while the two planners completed every run (RL {suite.counts("safety_stress", "rl")[0]}, NMOPSO '
        f'{suite.counts("safety_stress", "nmopso")[0]}) with no obstacle or drone contact. NMOPSO, with its legs '
        f'planned ahead and cached, matches RL\'s safety without RL\'s planning stalls (worst decision '
        f'{v("benchmark", "nmopso", "decision_time_max_ms", 1)} ms against {v("benchmark", "rl", "decision_time_max_ms", 0)} ms). '
        f'Under communication loss the auction recovers fastest because its drones patrol autonomously '
        f'without radio, while APF, RL and NMOPSO drones depend on ground-station commands and hover. For a factory, '
        f'where a collision is unacceptable, a planning-based navigator is the safest choice, provided it is '
        f'combined with on-board fallback behaviour and a replicated allocator.')}


def _fig_grid(B, metrics, name, caption, scenarios=None):
    return B.fig(rf.dot_ci_grid(B.s, metrics, B.d / f'{name}.png', scenarios), caption)


def results(B, suite, tests):
    v, m = B.v, B.m
    B.h1('Results')
    B.p('Figures show, for every algorithm, the mean (large dot), its 95 % confidence interval (line) and the '
        'individual runs (light dots), one column per scenario. Appendix A lists every value; Appendix C the '
        'significance tests. NMOPSO was run twice per scenario, the other algorithms five times: its means are '
        'measured, but its 95 % intervals (t with one degree of freedom) are wide, and with two runs no pairwise '
        'test involving NMOPSO can reach significance (the smallest attainable Mann–Whitney p for 2 against 5 runs '
        'is 0.095). NMOPSO is therefore compared by its values and mechanisms, and claims about it are worded as '
        'observations, not as significant differences.')

    # ---------------------------------------------------------------- reliability
    B.h2('Mission completion and reliability')
    B.fig(rf.completion_bars(suite, B.d / 'r_completion.png'),
          'Runs that completed the mission, per scenario; runs in which a drone crashed are marked.')
    sa = {a: suite.counts('safety_stress', a) for a in A}
    B.p(f'All four algorithms completed every nominal and communication-loss run, so the distinguishing '
        f'scenario is safety_stress. There the RL planner completed {sa["rl"][1]} of {sa["rl"][0]} runs, NMOPSO '
        f'{sa["nmopso"][1]} of {sa["nmopso"][0]}, the auction '
        f'{sa["auction"][1]} of {sa["auction"][0]} and APF {sa["apf"][1]} of {sa["apf"][0]}; the failures are '
        f'crashes ({sa["auction"][2]} auction runs and {sa["apf"][2]} APF runs had a drone that hit an obstacle or '
        f'another drone and was lost). Task completion rate in safety_stress is '
        f'{v("safety_stress", "auction", "task_completion_rate_percent")} % for the auction, '
        f'{v("safety_stress", "apf", "task_completion_rate_percent")} % for APF and 100 % for both planners.')
    B.p('<b>Why.</b> This scenario places three inspection points in a line along a rack aisle under the '
        'transit routes, one directly beside the centre corridor and one low inside an aisle. APF pulls each '
        'drone straight at its goal; near a rack the weak repulsion (it only balances the attraction at about '
        '0.6 m) loses to the attraction, and a drone threading between racks touches them or is trapped in a '
        'local minimum. The auction does not look at obstacles at all: it relies on its altitude layers and '
        'the corridor, and the task beside the corridor and the shared corridor itself bring drones of '
        'different layers together during descents, where the proximity hold does not always resolve the '
        'encounter. RL and NMOPSO plan every leg around the obstacle model before flying it, so a task inside '
        'an aisle is approached along a feasible path instead of being pulled at directly.')

    # ---------------------------------------------------------------- efficiency
    B.h2('Efficiency: time, distance, idleness')
    _fig_grid(B, [('mission_completion_time_s', 'Mission completion time (s)', 'low'),
                  ('total_flight_distance_m', 'Total flight distance (m)', 'low'),
                  ('mean_task_idleness_s', 'Average task idleness (s)', 'low')], 'r_efficiency',
              'Efficiency metrics. Time and distance are averaged over completed runs only (APF has none in '
              'safety_stress).')
    B.p(f'<b>Mission completion time.</b> In the nominal benchmark the auction '
        f'({v("benchmark", "auction", "mission_completion_time_s")} s) and APF '
        f'({v("benchmark", "apf", "mission_completion_time_s")} s) are statistically tied and about 15 s faster '
        f'than RL ({v("benchmark", "rl", "mission_completion_time_s")} s). The tie hides two different paths to '
        f'the same time: APF flies the shortest routes, while the auction flies 2.5 times as far '
        f'({v("benchmark", "auction", "total_flight_distance_m")} m against '
        f'{v("benchmark", "apf", "total_flight_distance_m")} m) but at transit altitude, above every obstacle, '
        f'where nothing slows it down. RL is slower for two reasons: it detours around the obstacle model '
        f'(flight distance {v("benchmark", "rl", "total_flight_distance_m")} m, '
        f'{100 * (m("benchmark", "rl", "total_flight_distance_m") / m("benchmark", "apf", "total_flight_distance_m") - 1):.0f} % '
        f'above APF), and its planning '
        f'stalls the coordinator while route decomposition runs (Section 5.5). NMOPSO isolates the second reason: '
        f'its paths are planned around the same obstacle model and are as long as RL\'s '
        f'({v("benchmark", "nmopso", "total_flight_distance_m")} m), but they come from the plan cache, so nothing '
        f'stalls, and it finishes in {v("benchmark", "nmopso", "mission_completion_time_s")} s, about '
        f'{m("benchmark", "rl", "mission_completion_time_s") - m("benchmark", "nmopso", "mission_completion_time_s"):.1f} s '
        f'faster than RL. The remaining gap to the auction and APF is the detour itself.')
    B.p(f'<b>Under communication loss</b> the auction\'s mission time is unchanged '
        f'({v("comm_loss", "auction", "mission_completion_time_s")} s), because the drone without radio keeps '
        f'inspecting its own tasks, while APF ({v("comm_loss", "apf", "mission_completion_time_s")} s) and RL '
        f'({v("comm_loss", "rl", "mission_completion_time_s")} s) lose the hovering drone\'s work until others '
        f'take it over; NMOPSO ({v("comm_loss", "nmopso", "mission_completion_time_s")} s) behaves like RL. Losing '
        f'the orchestrator costs RL most ({v("comm_loss_orchestrator", "rl", "mission_completion_time_s")} s, '
        f'against {v("comm_loss_orchestrator", "nmopso", "mission_completion_time_s")} s for NMOPSO).')
    B.p(f'<b>Idleness.</b> Average task idleness, which measures how fresh the inspection data is, favours the '
        f'auction in every scenario without crashes ({v("benchmark", "auction", "mean_task_idleness_s")} s nominal '
        f'against {v("benchmark", "apf", "mean_task_idleness_s")} s for APF and '
        f'{v("benchmark", "rl", "mean_task_idleness_s")} s for RL and {v("benchmark", "nmopso", "mean_task_idleness_s")} s '
        f'for NMOPSO): each drone loops its tasks without waiting for '
        f'ground-station decisions. In safety_stress the two planners have the lowest idleness '
        f'({v("safety_stress", "rl", "mean_task_idleness_s")} s for RL, {v("safety_stress", "nmopso", "mean_task_idleness_s")} s '
        f'for NMOPSO), because the others leave tasks unvisited after a crash. Battery consumption follows mission time (the simulated battery is a time counter) and adds no '
        f'separate information.')

    # ---------------------------------------------------------------- safety
    B.h2('Safety: obstacles and separation')
    _fig_grid(B, [('min_obstacle_clearance_m', 'Minimum obstacle clearance (m)', 'high'),
                  ('obstacle_contacts', 'Obstacle contacts (episodes < 0.3 m)', 'low'),
                  ('separation_p5_m', 'Swarm separation, 5th percentile (m)', 'high'),
                  ('separation_violations', 'Separation violations (episodes < 1.0 m)', 'low')], 'r_safety',
              'Safety metrics. Clearance is measured to the obstacle boxes for every algorithm; separation '
              'is the minimum over drone pairs at each instant.')
    B.p(f'<b>Obstacle clearance.</b> RL keeps the most consistent clearance: '
        f'{v("benchmark", "rl", "min_obstacle_clearance_m", 2)} m nominal and '
        f'{v("safety_stress", "rl", "min_obstacle_clearance_m", 2)} m under stress, with zero contacts in every '
        f'scenario. NMOPSO, which plans against the same obstacle model, is close behind '
        f'({v("benchmark", "nmopso", "min_obstacle_clearance_m", 2)} m nominal, '
        f'{v("safety_stress", "nmopso", "min_obstacle_clearance_m", 2)} m under stress) and also never came within '
        f'0.6 m of an obstacle. The auction has the largest clearance in the nominal case '
        f'({v("benchmark", "auction", "min_obstacle_clearance_m", 2)} m: its transits are above every obstacle) '
        f'but collapses under stress ({v("safety_stress", "auction", "min_obstacle_clearance_m", 2)} m, '
        f'{v("safety_stress", "auction", "obstacle_contacts")} contacts per run). APF flies closest to obstacles '
        f'in every scenario ({v("benchmark", "apf", "min_obstacle_clearance_m", 2)} m nominal, '
        f'{v("safety_stress", "apf", "obstacle_contacts")} contacts per run under stress, and contacts even in '
        f'the communication-loss scenarios, where reassigned tasks send drones on longer routes past racks).')
    B.fig(rf.separation_cdf(suite, B.d / 'r_sep_cdf.png'),
          'Distribution of the swarm separation s(t) over all runs (pooled): the fraction of time the closest '
          'pair is within x metres. Curves further right are safer; the dashed line is the 1.0 m safety radius.')
    B.p(f'<b>Separation between drones.</b> The percentiles and the distribution (Figure above) show more than '
        f'the single minimum. In the nominal benchmark every algorithm keeps the drones well apart (no pair '
        f'within 1.0 m); the auction has the widest margin (5th percentile '
        f'{v("benchmark", "auction", "separation_p5_m", 2)} m against {v("benchmark", "rl", "separation_p5_m", 2)} m '
        f'for RL and {v("benchmark", "apf", "separation_p5_m", 2)} m for APF), because its transit altitudes are '
        f'separated vertically by layer. Under stress the order reverses at the low end: RL is the only algorithm '
        f'without a separation violation (0 per run, against '
        f'{v("safety_stress", "auction", "separation_violations")} for the auction and '
        f'{v("safety_stress", "apf", "separation_violations")} for APF), and its 1st percentile is the highest '
        f'({v("safety_stress", "rl", "separation_p1_m", 2)} m). The auction\'s drones descend from their layers '
        f'into the same aisle and corridor, where the proximity hold does not always resolve the encounter. '
        f'APF\'s drone repulsion (3 m radius) prevents drone contacts under stress '
        f'({v("safety_stress", "apf", "separation_contacts")} per run) but cannot protect against obstacles at the '
        f'same time. NMOPSO also had no violation under stress, but its separation is the least consistent of the '
        f'planners: each drone\'s path is optimised alone, without an inter-drone term, so the separation depends on '
        f'which cached paths happen to cross (nominal minimum {v("benchmark", "nmopso", "minimum_inter_drone_distance_m", 2)} m '
        f'over its two runs, against {v("benchmark", "rl", "minimum_inter_drone_distance_m", 2)} m for RL).')

    # ---------------------------------------------------------------- fairness
    B.h2('Fairness: workload balance')
    _fig_grid(B, [('workload_imbalance_tasks', 'Workload imbalance, task completions (1 − Jain)', 'low'),
                  ('workload_imbalance_distance', 'Workload imbalance, flight distance (1 − Jain)', 'low')],
              'r_fairness', 'Workload imbalance on two workload definitions (0 = perfectly equal; at most 0.67 '
                            'with three drones).')
    B.p(f'The shared auction caps every drone at ⌈M/N⌉ tasks, so the allocation itself is balanced in every '
        f'algorithm, and nominal imbalance in task completions is near zero '
        f'({v("benchmark", "auction", "workload_imbalance_tasks", 3)}, '
        f'{v("benchmark", "apf", "workload_imbalance_tasks", 3)}, {v("benchmark", "rl", "workload_imbalance_tasks", 3)}, '
        f'{v("benchmark", "nmopso", "workload_imbalance_tasks", 3)} for auction, APF, RL and NMOPSO; the auction\'s small value is one extra visit by drone 0, which loops back to '
        f'its first task before the cycle ends). Distance is less even for the auction '
        f'({v("benchmark", "auction", "workload_imbalance_distance", 3)}, against '
        f'{v("benchmark", "apf", "workload_imbalance_distance", 3)} for APF and '
        f'{v("benchmark", "rl", "workload_imbalance_distance", 3)} for RL and '
        f'{v("benchmark", "nmopso", "workload_imbalance_distance", 3)} for NMOPSO): its drone 0 flies about 100 m and its '
        f'drone 2 about 65 m in one cycle, while APF, RL and NMOPSO drones fly within a few metres of each other. '
        f'Faults are where imbalance becomes large. After a crash the surviving drones do the lost drone\'s work '
        f'(safety_stress: {v("safety_stress", "auction", "workload_imbalance_distance", 2)} for the auction and '
        f'{v("safety_stress", "apf", "workload_imbalance_distance", 2)} for APF, against '
        f'{v("safety_stress", "rl", "workload_imbalance_distance", 3)} for RL, which did not crash). Under '
        f'communication loss the auction is again the least balanced '
        f'({v("comm_loss", "auction", "workload_imbalance_tasks", 2)} on tasks, against '
        f'{v("comm_loss", "rl", "workload_imbalance_tasks", 3)} for RL): the lost drone keeps working its own '
        f'loop while its tasks are also given to another drone, so visits pile up on some drones.')

    # ---------------------------------------------------------------- overhead
    B.h2('Coordination overhead: allocation, reallocations, decision time')
    _fig_grid(B, [('alloc_all_assigned_s', 'Allocation latency: every task assigned (s)', 'low'),
                  ('task_reallocations', 'Task reallocations (count)', 'low'),
                  ('decision_time_max_ms', 'Worst navigation decision time (ms)', 'low')], 'r_overhead',
              'Coordination overhead. Decision time is measured in the coordinator, so the auction (on-board '
              'navigation) has none.')
    B.p(f'<b>Allocation latency</b> is the same for all four algorithms '
        f'({v("benchmark", "auction", "alloc_all_assigned_s", 2)} s nominal) because they share the auction, '
        f'whose 5 s wait for peer states dominates it; the on-board auction step itself takes microseconds. '
        f'The allocation-to-mission ratio ({v("benchmark", "auction", "allocation_to_mct_ratio", 3)} for the '
        f'auction, {v("benchmark", "rl", "allocation_to_mct_ratio", 3)} for RL) is well below the framework\'s 0.3 '
        f'threshold for coordination-bound algorithms. <b>Task reallocations</b> are zero without faults; they '
        f'appear only when the failure detector revokes a lost drone\'s tasks (communication loss of drone 1) and '
        f'are absent when the orchestrator itself is lost, because nobody detects that loss.')
    B.p(f'<b>Decision time</b> is where APF and RL differ most: an APF decision takes '
        f'{v("benchmark", "apf", "decision_time_mean_ms", 2)} ms on average and never more than about 1 ms, while '
        f'an RL decision averages {v("benchmark", "rl", "decision_time_mean_ms")} ms with worst cases of '
        f'{v("benchmark", "rl", "decision_time_max_ms", 0)} ms. The worst cases are legs whose straight line is '
        f'blocked, where the planner rolls out 193 candidates per sub-leg along an A* route. Because the planner '
        f'runs on the coordinator\'s single thread, such a stall delays the commands of every drone, which is '
        f'one of the reasons RL is slower. NMOPSO shows that this is an engineering choice, not a property of '
        f'planning: its search is about fifty times slower than an RL plan (about 5 s per leg), yet its worst '
        f'decision takes {v("benchmark", "nmopso", "decision_time_max_ms", 1)} ms, because its legs are planned '
        f'before the run and any other leg would be planned in a worker thread. In these scenarios every '
        f'non-trivial leg came from the cache; the only legs planned during a run were 3–5 cm hops to the task '
        f'a drone was already at.')

    # ---------------------------------------------------------------- robustness
    B.h2('Robustness: communication loss')
    B.fig(rf.recovery_timeline(suite, B.d / 'r_recovery.png'),
          'Recovery after the 15 s radio blackout (means): detection, reassignment and the time until every task '
          'of the lost drone has been inspected again.')
    _fig_grid(B, [('coverage_restored_s', 'Coverage restored after loss start (s)', 'low'),
                  ('resume_s', 'Lost drone back in service after the link returns (s)', 'low'),
                  ('min_separation_during_loss_m', 'Minimum separation of the lost drone (m)', 'high')],
              'r_robust', 'Recovery metrics in the two blackout scenarios.',
              scenarios=['comm_loss', 'comm_loss_orchestrator'])
    B.p(f'<b>Detection and reassignment</b> take the heartbeat timeout, '
        f'{v("comm_loss", "auction", "detection_s", 2)} s, for every algorithm: detection and reallocation are '
        f'platform functions shared by all four, and the reassignment follows detection within milliseconds. '
        f'<b>Recovery differs because of what the lost drone does without radio.</b> An auction drone keeps '
        f'flying its own task loop, so its tasks keep being inspected: coverage is restored after '
        f'{v("comm_loss", "auction", "coverage_restored_s")} s, and after the link returns the drone is back in '
        f'coordinated service within {v("comm_loss", "auction", "resume_s")} s. APF, RL and NMOPSO drones receive no '
        f'movement commands and hold their last set-point; their tasks are covered only once the other drones '
        f'have flown there (coverage restored {v("comm_loss", "apf", "coverage_restored_s")} s for APF, '
        f'{v("comm_loss", "rl", "coverage_restored_s")} s for RL and {v("comm_loss", "nmopso", "coverage_restored_s")} s '
        f'for NMOPSO), and after reconnection the hovering drone must win a task in a new auction and fly to it '
        f'({v("comm_loss", "apf", "resume_s")} s, {v("comm_loss", "rl", "resume_s")} s and '
        f'{v("comm_loss", "nmopso", "resume_s")} s).')
    B.p(f'<b>Safety during and after the blackout.</b> No algorithm lost separation during the blackout: the '
        f'transient safety degradation index is zero in every run (time below 1.0 m from loss start to 10 s after '
        f'the link returns: {v("comm_loss", "auction", "loss_safety_time_s", 2)} s, '
        f'{v("comm_loss", "apf", "loss_safety_time_s", 2)} s, {v("comm_loss", "rl", "loss_safety_time_s", 2)} s and '
        f'{v("comm_loss", "nmopso", "loss_safety_time_s", 2)} s). The close encounters recorded in these scenarios happen '
        f'later, in the 150 s observation window that follows the first patrol cycle. The auction has the most '
        f'({v("comm_loss", "auction", "separation_contacts")} contacts per run, against '
        f'{v("comm_loss", "apf", "separation_contacts")} for APF, {v("comm_loss", "rl", "separation_contacts")} for '
        f'RL and {v("comm_loss", "nmopso", "separation_contacts")} for NMOPSO), and they repeat at the same moments in every run: about 20 s after the link returns, between the '
        f'reconnected drone 1 and drone 2, which had taken over one of its tasks, and later in the second patrol lap, '
        f'between drones 0 and 1 (also in the orchestrator scenario). These are deterministic conflicts of the '
        f'layered navigation, not random events; the nominal benchmark does not observe them only because it ends '
        f'after the first cycle.')
    B.p(f'<b>Losing the orchestrator</b> (drone 0) exposes the single point of failure of the shared '
        f'allocation layer: the loss is never detected and the lost drone\'s tasks are never reassigned in any '
        f'algorithm; every run completes only because the link returns after 15 s. The auction is again least '
        f'affected (coverage restored within the outage, {v("comm_loss_orchestrator", "auction", "coverage_restored_s")} s), '
        f'while APF ({v("comm_loss_orchestrator", "apf", "coverage_restored_s")} s), NMOPSO '
        f'({v("comm_loss_orchestrator", "nmopso", "coverage_restored_s")} s) and RL '
        f'({v("comm_loss_orchestrator", "rl", "coverage_restored_s")} s) wait for the link and then resume. RL '
        f'takes longest because, on reconnection, it plans drone 0\'s remaining route while the stall delays all '
        f'drones; NMOPSO, flying the same kind of paths from its cache, recovers about '
        f'{m("comm_loss_orchestrator", "rl", "coverage_restored_s") - m("comm_loss_orchestrator", "nmopso", "coverage_restored_s"):.1f} s sooner.')

    # ---------------------------------------------------------------- summary table
    B.h2('Summary per metric')
    rows = [['Metric family', 'Best', 'Runner-up', 'Mechanism']]
    rows += [
        ['Speed (nominal MCT, idleness)', 'Auction ≈ APF', 'NMOPSO, then RL', 'unobstructed transit layers / direct legs vs. detours; RL adds planning stalls'],
        ['Path length', 'APF', 'NMOPSO ≈ RL', 'straight attraction vs. obstacle detours; auction climbs and uses the corridor'],
        ['Task completion under stress', 'RL, NMOPSO', 'Auction', 'planned, obstacle-aware legs; APF and auction crash'],
        ['Obstacle safety', 'RL', 'NMOPSO', 'planning around the obstacle model; APF repulsion too weak'],
        ['Drone-to-drone safety', 'RL (stress, faults)', 'NMOPSO, APF', 'planned paths and yielding; NMOPSO optimises each drone alone; auction drones meet in aisles and corridor'],
        ['Workload balance', 'tie (shared auction)', '–', 'load cap of the auction; faults shift work'],
        ['Allocation latency, reallocations', 'tie (shared auction)', '–', 'same allocation layer'],
        ['Decision time', 'APF', 'NMOPSO', 'closed-form forces; cached plans vs. RL\'s 193 rollouts per leg in the loop'],
        ['Recovery from radio loss', 'Auction', 'APF', 'autonomous patrol without radio vs. hovering'],
        ['Safety during radio loss', 'tie', '–', 'no separation lost during any blackout; auction conflicts after reconnection'],
    ]
    B.table(rows, 'Which algorithm is best at what (best = non-overlapping 95 % intervals or a consistent '
                  'pattern across scenarios; see Appendix A and C).',
            widths=[4.2 * 28.35, 2.6 * 28.35, 2.4 * 28.35, 7.4 * 28.35])


def discussion(B, suite):
    B.h1('Discussion: which algorithm for a factory?')
    B.p('A factory imposes a lexicographic order on these metrics. A collision with a rack, a machine or a '
        'person is not a cost to be traded against seconds of mission time; it ends the mission and may injure '
        'someone. Coverage and inspection freshness come next, and only then path length or energy. Read in this '
        'order, the results point clearly in one direction while also showing what each approach would need.')
    B.h3('Auction with layered navigation')
    B.p('The auction is the most efficient and most robust to radio loss in open layouts: its drones need no '
        'ground-station decisions, it has the lowest idleness, and a drone that loses its radio simply keeps '
        'patrolling. Its navigation, however, has no notion of obstacles; it is safe only while every obstacle '
        'is below the lowest transit layer and the corridor is free. In the stress scenario, which models a '
        'realistic aisle layout with low inspection points, it crashed in a majority of runs. It is suitable '
        'for open halls with high ceilings and well-separated, elevated inspection points, and for missions '
        'where radio dropouts are frequent, but not for dense racking.')
    B.h3('APF')
    B.p('APF gives the shortest paths and negligible computation, and its drone-drone repulsion works well. '
        'Its obstacle avoidance is a local balance of forces and cannot guarantee clearance where inspection '
        'points sit next to obstacles: increasing the repulsion pushes drones away from the very points they '
        'must inspect, and local minima remain. It crashed in every stress run, came within 0.6 m of obstacles '
        'in the nominal scenario and touched them in both communication-loss scenarios. On its own it is not suitable for a cluttered factory; '
        'it is a good reactive safety layer underneath a planner, or a navigator for open areas.')
    B.h3('RL leg planner')
    B.p('The RL planner and NMOPSO are the only approaches that completed every run of every scenario without '
        'touching an obstacle; RL has the most consistent clearance and no separation violation under stress. Its drones are '
        'not contact-free in every case: in the longer communication-loss runs one RL run had a drone contact in '
        'the second patrol lap, against several per run for the auction. It pays roughly a third '
        'more mission time and a larger worst-case decision time, and, like APF, its drones hover without '
        'radio. These costs are largely engineering, not intrinsic: planning in a worker thread removes the '
        'stalls, caching plans for the fixed patrol legs removes most planning altogether, and an on-board '
        'fallback (continue the last planned path, or return along it) would give it the auction\'s behaviour '
        'under radio loss.')
    B.h3('NMOPSO')
    B.p('NMOPSO completed every run of every scenario without an obstacle or drone contact and with clearance '
        'close to RL\'s, so on this evidence it is as safe as RL in the cluttered layout. It was faster than RL in the '
        'nominal and orchestrator-loss scenarios and level with it under the loss of drone 1, because its legs are '
        'planned before the mission, which removes the planning stalls; under stress its two runs were slightly '
        'slower on average, within their wide interval. It has the lowest '
        'decision time of the two planners. The price is planning time: about 5 s per leg even vectorised (369 s '
        'for the authors\' MATLAB code), so it fits a patrol whose legs are known in advance; a route that changes '
        'during the mission waits for a background plan. Its separation between drones is less consistent than '
        'RL\'s, because each drone\'s path is optimised alone. With two runs per scenario these are observations, '
        'not significant differences; five runs would put it on the same statistical footing as the others.')
    B.h3('The allocation layer')
    B.p('All four share one weakness that the orchestrator scenario exposed: allocation and failure '
        'detection run on drone 0 only. A factory deployment should replicate them (for example, run the '
        'auctioneer at the ground station with a standby on a drone, or use a consensus-based auction) so that '
        'the loss of any single drone or link is detected and its tasks reallocated.')
    B.p('<b>Recommendation.</b> For an indoor factory with racks and machines, use a planning-based navigator '
        '(the RL planner, or NMOPSO with precomputed legs for a fixed patrol) with the market-based allocation, add '
        'an on-board continuation behaviour for radio loss, and replicate the allocator. Between the two '
        'planners, NMOPSO suits fixed patrol rounds in a static layout, where every leg can be planned ahead; RL '
        'suits layouts or routes that change, because it plans any leg in a fraction of a second. Use APF only as a local '
        'reactive layer, and layered auction navigation only in open, high-ceiling areas.')


def conclusion(B, suite):
    B.h1('Conclusion')
    B.p('This benchmark compared a market-based auction, reactive potential fields, a PPO-trained leg '
        'planner and the NMOPSO particle swarm planner on one PX4/Gazebo platform, with shared allocation and instrumentation, across a nominal '
        'patrol, a spatial-conflict stress test and two communication-blackout faults, using the review '
        'framework\'s metrics extended with obstacle clearance, idleness, decision time and transient safety.')
    B.bullets([
        'No algorithm is best on every metric. Efficiency (time, path length, idleness) favours the auction '
        'and APF; safety and reliability favour the two planners, RL and NMOPSO; recovery from radio loss favours '
        'the auction.',
        'The decisive differences come from mechanisms, not tuning: whether navigation plans around obstacles '
        '(RL, NMOPSO) or reacts locally (APF) or ignores them (auction layers), and whether a drone can work '
        'without its radio (auction) or depends on the ground station (APF, RL, NMOPSO).',
        'In the cluttered stress scenario, both planners completed every run without contact, while APF '
        'crashed in every run and the auction in most. For factory deployment, where collisions are '
        'unacceptable, an obstacle-aware planner is required.',
        'Allocation latency, reallocation and failure detection are properties of the shared allocation '
        'layer; its single point of failure on drone 0 must be removed in any deployment.',
        'NMOPSO, run twice per scenario, matched RL\'s safety and was faster in the nominal and orchestrator-loss '
        'scenarios, because its legs are planned before the mission and never stall the control loop. RL\'s slower missions are therefore partly an engineering '
        'limit that asynchronous planning and plan caching remove.',
        'The remaining costs of the planners (hovering without radio, and for NMOPSO seconds per new leg) need '
        'an on-board continuation behaviour and, for changing routes, a fast planner such as RL.'])
    B.p('The platform, the metrics and the analysis scripts are reusable: a new coordination algorithm '
        'implements one interface and is scored by the same suite, so the comparison can be extended to '
        'consensus auctions, bio-inspired allocation, larger swarms and hardware.')
