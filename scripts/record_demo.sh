#!/bin/bash
# =============================================================================
# Record one experiment run as a video, with tasks and drones highlighted (for presentations).
#
#   ./scripts/record_demo.sh <algorithm> <scenario> [output.mp4] [max_seconds]
#   ./scripts/record_demo.sh rl safety_stress videos/rl_safety_stress.mp4
#
# 1. starts the experiment with the Gazebo server only (start_experiment.sh --headless)
# 2. opens a Gazebo GUI on $DISPLAY with config/gazebo/recording_gui.config (overview camera,
#    Marker manager)
# 3. runs scripts/sim_markers.py (task pillars, drone halos, trails, goal lines, radio-loss
#    highlight in the 3-D view)
# 4. records the GUI window (scripts/screen_record.py: caption, legend and a live top view with
#    task and drone labels; the window is moved to the top-left and kept above other windows)
#    until the run summary is written (or max_seconds), and cleans up every process.
#
# Needs a desktop session (DISPLAY, default :0); the Gazebo window appears on that desktop.
# Gazebo Harmonic's own video recorder has no service to start it, hence the screen capture.
# To record by hand instead, see docs/DEMO_RECORDING.md.
# =============================================================================
ALGO=${1:?algorithm}; SCEN=${2:?scenario}
P="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT=${3:-$P/videos/${ALGO}_${SCEN}.mp4}
case "$OUT" in /*) ;; *) OUT="$P/$OUT" ;; esac
MAX=${4:-300}
export DISPLAY=${DISPLAY:-:0}
mkdir -p "$(dirname "$OUT")"
cd "$P" || exit 1
source /opt/ros/jazzy/setup.bash
source factory_patrol_ws/install/setup.bash
LOG=/dev/shm/factory_patrol_record.log
TASKS=$(python3 -c "import yaml,sys; print((yaml.safe_load(open(sys.argv[1])).get('mission') or {}).get('tasks_file', 'config/tasks/benchmark.yaml'))" "config/experiments/$SCEN.yaml")
LABEL=$(echo "$ALGO" | tr a-z A-Z)

ls experiment_results/summaries > /dev/shm/factory_patrol_summaries_before
new_summary() { ls experiment_results/summaries | grep -vxFf /dev/shm/factory_patrol_summaries_before | head -1; }
setsid ./scripts/start_experiment.sh --algorithm "$ALGO" --scenario "$SCEN" --drones 3 --headless --delay 15.0 > "$LOG" 2>&1 &
SID=$!

echo "waiting for the Gazebo server..."
for _ in $(seq 60); do gz service -l 2>/dev/null | grep -q "^/world/factory/" && break; sleep 1; done
GZ_SIM_RESOURCE_PATH="$HOME/.simulation-gazebo/models:$P/PX4-Autopilot/Tools/simulation/gz/models:$P/PX4-Autopilot/Tools/simulation/gz/worlds" \
    setsid gz sim -g --gui-config "$P/config/gazebo/recording_gui.config" > /dev/shm/factory_patrol_gui.log 2>&1 &
GUI=$!
echo "waiting for the GUI..."
for _ in $(seq 60); do gz service -l 2>/dev/null | grep -qx "/marker_array" && break; sleep 1; done
python3 scripts/sim_markers.py --tasks "$TASKS" --label "$LABEL" > /dev/shm/factory_patrol_markers.log 2>&1 &
MK=$!
sleep 3
python3 scripts/screen_record.py --window "Gazebo Sim" --out "$OUT" --display "$DISPLAY" \
    --caption "$LABEL  |  $SCEN  |  3 drones" --tasks "$TASKS" > /dev/shm/factory_patrol_screen.log 2>&1 &
REC=$!
echo "recording (pid $REC)..."

t0=$(date +%s)
while [ $(( $(date +%s) - t0 )) -lt "$MAX" ]; do
    [ -n "$(new_summary)" ] && sleep 4 && break
    kill -0 $SID 2>/dev/null || break
    sleep 2
done

kill -INT $REC 2>/dev/null; wait $REC                      # finishes and closes the video file
cat /dev/shm/factory_patrol_screen.log
kill $MK 2>/dev/null; sleep 1
kill -- -$GUI 2>/dev/null
kill -INT -- -$SID 2>/dev/null; sleep 5
for pat in "start_experiment.sh" "px4_sitl_default/bin/px4" "patrol_controller" "coordinator_node" "metrics_collector" "simulation-gazebo" "gz sim"; do
    pkill -f "$pat"
done
pkill -x MicroXRCEAgent; sleep 3
for pat in "px4_sitl_default/bin/px4" "gz sim" "patrol_controller"; do pkill -9 -f "$pat"; done
for p in $(pgrep -x sleep); do grep -q infinity /proc/$p/cmdline 2>/dev/null && kill $p; done
fastdds shm clean > /dev/null 2>&1 || true
echo "run summary: $(new_summary)"
ls -la "$OUT" 2>/dev/null || echo "no video written: see docs/DEMO_RECORDING.md for recording by hand"
