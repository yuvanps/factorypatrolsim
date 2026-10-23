#!/bin/bash
# =============================================================================
# One experiment run with a watchdog: start_experiment.sh, stopped as soon as its run summary is
# written, after MAX_SECONDS, when the disk runs low or a PX4 log grows too big; then every
# simulation process is cleaned up so the next run starts from a clean state.
#
#   ./scripts/run_guarded.sh <max_seconds> <start_experiment.sh options...>
#   ./scripts/run_guarded.sh 300 --algorithm rl --scenario benchmark --drones 3 --headless
#
# Prints "RUN <run_id> <stop reason>" (run_id empty if no summary was written).
# =============================================================================
MAX=$1; shift
P="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$P" || exit 1
mkdir -p experiment_results/summaries
LOG="${RUN_LOG:-/dev/shm/factory_patrol_run.log}"
before=$(ls experiment_results/summaries | wc -l)
setsid ./scripts/start_experiment.sh "$@" > "$LOG" 2>&1 &
SID=$!
t0=$(date +%s)
reason=""
while true; do
    sleep 2
    [ $(( $(date +%s) - t0 )) -ge "$MAX" ] && reason="time limit ${MAX}s" && break
    [ "$(ls experiment_results/summaries | wc -l)" -gt "$before" ] && sleep 3 && reason="summary written" && break
    [ "$(df --output=avail -k / | tail -1)" -lt "${MIN_FREE_KB:-1500000}" ] && reason="disk below $(( ${MIN_FREE_KB:-1500000} / 1000000 )).$(( ${MIN_FREE_KB:-1500000} / 100000 % 10 )) GB" && break
    big=$(find "$P" -maxdepth 1 -name 'drone*.log' -size +200M | head -1)
    [ -n "$big" ] && reason="log too big: $big" && break
    kill -0 $SID 2>/dev/null || { reason="launcher exited"; break; }
done
kill -INT -- -$SID 2>/dev/null; sleep 5
for pat in "px4_sitl_default/bin/px4" "patrol_controller" "coordinator_node" "metrics_collector" "simulation-gazebo" "gz sim"; do
    pkill -f "$pat"
done
pkill -x MicroXRCEAgent; sleep 3
for pat in "px4_sitl_default/bin/px4" "gz sim" "patrol_controller"; do pkill -9 -f "$pat"; done
for p in $(pgrep -x sleep); do grep -q infinity /proc/$p/cmdline 2>/dev/null && kill $p; done   # PX4 stdin holders
( source /opt/ros/jazzy/setup.bash >/dev/null 2>&1 && fastdds shm clean >/dev/null 2>&1 ) || true
new=""
[ "$(ls experiment_results/summaries | wc -l)" -gt "$before" ] && new=$(ls -t experiment_results/summaries | head -1 | cut -d_ -f1-3)
echo "RUN ${new} ${reason} after $(( $(date +%s) - t0 )) s"
