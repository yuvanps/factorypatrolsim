#!/bin/bash
# =============================================================================
# Benchmark suite: every algorithm x scenario, REPEATS times each, one guarded run at a time.
# Runs are interleaved (repeat 1 of every pair first) so slow drift of the machine affects all
# algorithms alike. Appends one line per run to <suite dir>/manifest.csv; resumable: a pair that
# already has REPEATS runs in the manifest is skipped.
#
#   ./scripts/run_suite.sh <suite_name> [repeats=5] [algorithms="auction apf rl"]
#                          [scenarios="benchmark safety_stress comm_loss comm_loss_orchestrator"]
#   python3 scripts/aggregate_suite.py experiment_results/suites/<suite_name>
# =============================================================================
NAME=${1:?suite name}
REPEATS=${2:-5}
ALGOS=${3:-"auction apf rl"}
SCENARIOS=${4:-"benchmark safety_stress comm_loss comm_loss_orchestrator"}
P="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIR="$P/experiment_results/suites/$NAME"
mkdir -p "$DIR"
M="$DIR/manifest.csv"
[ -f "$M" ] || echo "run_id,algorithm,scenario,repeat,stop_reason,started" > "$M"

limit() {   # watchdog per scenario: the mission timeout / observation window plus start-up time
    case $1 in
        comm_loss*) echo 240 ;;
        safety_stress) echo 330 ;;
        *) echo 240 ;;
    esac
}

for rep in $(seq 1 "$REPEATS"); do
    for scen in $SCENARIOS; do
        for algo in $ALGOS; do
            have=$(awk -F, -v a="$algo" -v s="$scen" '$2==a && $3==s && $1!=""' "$M" | wc -l)
            [ "$have" -ge "$rep" ] && continue
            started=$(date -Iseconds)
            echo "[$started] $algo / $scen / repeat $rep"
            out=$("$P/scripts/run_guarded.sh" "$(limit "$scen")" --algorithm "$algo" --scenario "$scen" --drones 3 --headless | tail -1)
            run=$(echo "$out" | awk '{print $2}')
            reason=$(echo "$out" | cut -d' ' -f3- | tr ',' ';')
            echo "${run},${algo},${scen},${rep},${reason},${started}" >> "$M"
            echo "    -> ${run:-no summary} (${reason})"
            sleep 5
        done
    done
done
echo "suite $NAME done: $M"
