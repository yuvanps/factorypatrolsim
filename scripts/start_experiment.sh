#!/bin/bash
# =============================================================================
# start_experiment.sh
# =============================================================================
# Unified experiment launcher for the Factory Patrol Benchmarking Framework.
#
# Usage:
#   ./scripts/start_experiment.sh                                  # defaults (benchmark, auction, 3)
#   ./scripts/start_experiment.sh --algorithm auction --drones 3   # explicit
#   ./scripts/start_experiment.sh --scenario safety_stress --algorithm auction --drones 3
#   ./scripts/start_experiment.sh --drones 1                       # single drone
#   ./scripts/start_experiment.sh --algorithm rl --rl-checkpoint rl-nmopso-factory-patrol/results/ckpt/v2.pt
#
# Scenario and algorithm are independent: the scenario (config/experiments/<name>.yaml)
# selects the task set and metrics sampling; the algorithm selects the coordination strategy.
#
# This script:
#   1. Parses command-line arguments
#   2. Starts Gazebo with the factory world
#   3. Spawns N PX4 SITL instances
#   4. Starts N ROS 2 patrol controllers
#   5. Starts the coordinator node (algorithm selection + mission dispatch)
#   6. Starts the metrics collector
#
# Prerequisites:
#   - PX4-Autopilot built (make px4_sitl_default)
#   - factory_patrol_ws built (colcon build)
#   - MicroXRCEAgent installed

set -e

# =============================================================================
# Defaults
# =============================================================================
ALGORITHM="auction"
SCENARIO="benchmark"
NUM_DRONES=3
CONFIG_FILE=""        # default: config/experiments/$SCENARIO.yaml
TASKS_FILE=""         # default: the scenario's mission.tasks_file
MISSION_DELAY=5.0
HEADLESS=0
RL_CHECKPOINT=""      # default: rl.checkpoint in config/algorithms/rl.yaml
RL_PYTHON="${RL_PYTHON:-}"   # default: rl-nmopso-factory-patrol/.venv/bin/python
COMM_LOSS="-"         # default: the scenario's faults.comm_loss ("" = none)
OBSERVE="-"           # default: the scenario's metrics.observation_window_s (0 = end at mission completion)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PX4_DIR="$PROJECT_DIR/PX4-Autopilot"
WS_DIR="$PROJECT_DIR/factory_patrol_ws"

# =============================================================================
# Parse arguments
# =============================================================================
while [[ $# -gt 0 ]]; do
    case $1 in
        --algorithm|-a)
            ALGORITHM="$2"
            shift 2
            ;;
        --scenario|-s)
            SCENARIO="$2"
            shift 2
            ;;
        --drones|-n)
            NUM_DRONES="$2"
            shift 2
            ;;
        --config|-c)
            CONFIG_FILE="$2"
            shift 2
            ;;
        --tasks|-t)
            TASKS_FILE="$2"
            shift 2
            ;;
        --delay|-d)
            MISSION_DELAY="$2"
            shift 2
            ;;
        --headless)
            HEADLESS=1
            shift
            ;;
        --rl-checkpoint)
            RL_CHECKPOINT="$2"
            shift 2
            ;;
        --rl-python)
            RL_PYTHON="$2"
            shift 2
            ;;
        --comm-loss)
            COMM_LOSS="$2"
            shift 2
            ;;
        --observe)
            OBSERVE="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --algorithm, -a  Coordination algorithm (auction|pso|apf|rl|nmopso) [default: auction]"
            echo "  --scenario, -s   Scenario: any config/experiments/<name>.yaml (benchmark|safety_stress|comm_loss|comm_loss_orchestrator) [default: benchmark]"
            echo "  --drones, -n     Number of drones to spawn [default: 3]"
            echo "  --config, -c     Path to scenario config YAML [default: config/experiments/<scenario>.yaml]"
            echo "  --tasks, -t      Path to tasks YAML [default: scenario's mission.tasks_file]"
            echo "  --delay, -d      Mission publish delay in seconds [default: 5.0]"
            echo "  --headless       Run Gazebo without the GUI"
            echo "  --rl-checkpoint  rl only: policy checkpoint (.pt), relative to the project or absolute"
            echo "                   [default: rl.checkpoint in config/algorithms/rl.yaml]"
            echo "  --rl-python      rl only: Python with torch + rlpatrol [default: rl-nmopso-factory-patrol/.venv/bin/python]"
            echo "  --comm-loss SPEC fault injection: drone:start_s:duration_s[,...] (radio loss, times from mission start)"
            echo "                   [default: faults.comm_loss of the scenario; \"\" = none]"
            echo "  --observe S      observe for S seconds from mission start before writing the summary (recovery,"
            echo "                   idleness) [default: metrics.observation_window_s of the scenario; 0 = until completion]"
            echo "  --help, -h       Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

if [ -z "$CONFIG_FILE" ]; then
    CONFIG_FILE="config/experiments/${SCENARIO}.yaml"
fi
if [ ! -f "$PROJECT_DIR/$CONFIG_FILE" ]; then
    echo "ERROR: scenario config not found: $PROJECT_DIR/$CONFIG_FILE"
    echo "Available scenarios: $(ls "$PROJECT_DIR/config/experiments" | sed 's/\.yaml$//' | tr '\n' ' ')"
    exit 1
fi
# Reactive algorithms drive transit through /swarm/movement_command, so their controllers
# run in 'external' navigation mode; allocation-only algorithms keep the built-in transit.
case "$ALGORITHM" in
    apf|rl|nmopso) NAV_MODE="external" ;;
    *)      NAV_MODE="internal" ;;
esac

# RL: the coordinator runs in the RL virtual environment (torch); check the policy loads BEFORE
# starting the simulation, so a bad checkpoint or environment fails here instead of mid-run.
COORD_CMD=(ros2 run patrol_coordinator coordinator_node)
RL_ARGS=()
if [ "$ALGORITHM" = "rl" ]; then
    RL_REPO="$PROJECT_DIR/rl-nmopso-factory-patrol"
    RL_PYTHON="${RL_PYTHON:-$RL_REPO/.venv/bin/python}"
    if [ ! -x "$RL_PYTHON" ]; then
        echo "ERROR: RL Python not found: $RL_PYTHON (create the venv, see rl-nmopso-factory-patrol/README.md)"
        exit 1
    fi
    if [ -n "$RL_CHECKPOINT" ]; then
        case "$RL_CHECKPOINT" in /*) ;; *) RL_CHECKPOINT="$PROJECT_DIR/$RL_CHECKPOINT" ;; esac
        RL_ARGS=(-p rl.checkpoint:="$RL_CHECKPOINT")
        CKPT_FOR_CHECK="$RL_CHECKPOINT"
    else
        CKPT_FOR_CHECK="$PROJECT_DIR/$(python3 -c "import yaml,sys; print(yaml.safe_load(open(sys.argv[1]))['rl']['checkpoint'])" "$PROJECT_DIR/config/algorithms/rl.yaml")"
    fi
    echo "RL preflight: loading $CKPT_FOR_CHECK with $RL_PYTHON ..."
    if ! "$RL_PYTHON" -c "import sys; sys.path.insert(0, sys.argv[1]); from rlpatrol.planner import LegPlanner; p = LegPlanner(sys.argv[2], threads=2); r = p.plan_route((-8.0, 7.0), (7.0, -4.0)); assert r.feasible, r.reason; print('RL preflight OK:', p.ckpt_info, 'test leg', r.method, round(r.plan_time_s, 3), 's')" "$RL_REPO" "$CKPT_FOR_CHECK"; then
        echo "ERROR: RL preflight failed (see above). Nothing was started."
        exit 1
    fi
    COORD_CMD=("$RL_PYTHON" -m patrol_coordinator.coordinator_node)
elif [ "$ALGORITHM" = "nmopso" ]; then
    # NMOPSO uses the RL repository's world model and MyCost port (torch); its plan cache is built
    # beforehand by scripts/precompute_nmopso_cache.py (legs not in it are planned during the run).
    RL_REPO="$PROJECT_DIR/rl-nmopso-factory-patrol"
    RL_PYTHON="${RL_PYTHON:-$RL_REPO/.venv/bin/python}"
    if ! "$RL_PYTHON" -c "import sys; sys.path.insert(0, sys.argv[1]); from rlpatrol.nmopso import NMOPSOPlanner" "$RL_REPO"; then
        echo "ERROR: cannot import rlpatrol.nmopso with $RL_PYTHON. Nothing was started."
        exit 1
    fi
    [ -f "$PROJECT_DIR/config/algorithms/nmopso_cache.json" ] || \
        echo "WARNING: no NMOPSO plan cache (scripts/precompute_nmopso_cache.py): every leg is planned during the run"
    COORD_CMD=("$RL_PYTHON" -m patrol_coordinator.coordinator_node)
fi

SNAPSHOT_INTERVAL=$(python3 -c "import yaml,sys; c=yaml.safe_load(open(sys.argv[1])) or {}; print(float((c.get('metrics') or {}).get('state_snapshot_interval', 1.0)))" "$PROJECT_DIR/$CONFIG_FILE")
MISSION_TIMEOUT=$(python3 -c "import yaml,sys; c=yaml.safe_load(open(sys.argv[1])) or {}; print(float((c.get('metrics') or {}).get('mission_timeout_s', 600.0)))" "$PROJECT_DIR/$CONFIG_FILE")
if [ "$OBSERVE" = "-" ]; then
    OBSERVE=$(python3 -c "import yaml,sys; c=yaml.safe_load(open(sys.argv[1])) or {}; print(float((c.get('metrics') or {}).get('observation_window_s', 0.0)))" "$PROJECT_DIR/$CONFIG_FILE")
fi
if [ "$COMM_LOSS" = "-" ]; then
    COMM_LOSS=$(python3 -c "import yaml,sys; c=yaml.safe_load(open(sys.argv[1])) or {}; print((c.get('faults') or {}).get('comm_loss', '') or '')" "$PROJECT_DIR/$CONFIG_FILE")
fi

echo "============================================================"
echo "  FACTORY PATROL EXPERIMENT"
echo "============================================================"
echo "  Scenario:   $SCENARIO"
echo "  Algorithm:  $ALGORITHM"
echo "  Drones:     $NUM_DRONES"
echo "  Nav mode:   $NAV_MODE"
echo "  Config:     $CONFIG_FILE"
echo "  Tasks:      ${TASKS_FILE:-(from scenario config)}"
[ "$ALGORITHM" = "rl" ] && echo "  RL policy:  $CKPT_FOR_CHECK"
[ -n "$COMM_LOSS" ] && echo "  Comm loss:  $COMM_LOSS (drone:start_s:duration_s)"
[ "$OBSERVE" != "0.0" ] && [ "$OBSERVE" != "0" ] && echo "  Observe:    ${OBSERVE} s"
echo "============================================================"
echo ""

# =============================================================================
# Cleanup function
# =============================================================================
PIDS=()

cleanup() {
    echo ""
    echo "[Experiment] Shutting down..."
    for pid in "${PIDS[@]}"; do
        kill "$pid" 2>/dev/null || true
    done
    # `ros2 run` does not pass the signal on to the node it started, and background jobs of a
    # script ignore Ctrl+C, so the nodes are killed by name: a controller left over from this run
    # would keep sending setpoints to its drone in the next run.
    kill_sim_nodes
    echo "[Experiment] Done."
}

kill_sim_nodes() {   # [-9]: kill at once (a leftover metrics collector then writes no summary)
    local pat sig=${1:--15}
    for pat in "lib/patrol_controller/patrol_controller" "lib/patrol_coordinator/coordinator_node" \
               "lib/patrol_coordinator/metrics_collector" "px4_sitl_default/bin/px4"; do
        pkill "$sig" -f "$pat" 2>/dev/null || true
    done
    pkill -x MicroXRCEAgent 2>/dev/null || true
    pkill -f "gz sim -r" 2>/dev/null || true      # the Gazebo server (a GUI client, gz sim -g, is left alone)
    sleep 1
    for pat in "lib/patrol_controller/patrol_controller" "px4_sitl_default/bin/px4"; do
        pkill -9 -f "$pat" 2>/dev/null || true
    done
    # shared-memory files of killed DDS participants can stall the next run's PX4 <-> ROS traffic
    ( source /opt/ros/jazzy/setup.bash > /dev/null 2>&1 && fastdds shm clean > /dev/null 2>&1 ) || true
}

# Nodes left over from an earlier run (e.g. one stopped with Ctrl+C before this fix) would fight
# this run's nodes for the same drones: stop them first.
if pgrep -f "lib/patrol_controller/patrol_controller|lib/patrol_coordinator/coordinator_node|px4_sitl_default/bin/px4" > /dev/null; then
    echo "[Experiment] Stopping processes left over from an earlier run..."
    pkill -f "gz sim" 2>/dev/null || true       # a leftover Gazebo server would host the old world
    kill_sim_nodes -9
fi

trap cleanup EXIT INT TERM

# =============================================================================
# Source ROS 2
# =============================================================================
source /opt/ros/jazzy/setup.bash
if [ -f "$WS_DIR/install/setup.bash" ]; then
    source "$WS_DIR/install/setup.bash"
else
    echo "ERROR: Workspace not built. Run: cd $WS_DIR && colcon build"
    exit 1
fi

# =============================================================================
# 1. Start MicroXRCEAgent
# =============================================================================
if ! pgrep -x "MicroXRCEAgent" > /dev/null; then
    echo "[1/6] Starting MicroXRCEAgent..."
    MicroXRCEAgent udp4 -p 8888 > /dev/null 2>&1 &
    PIDS+=($!)
    sleep 2
else
    echo "[1/6] MicroXRCEAgent already running."
fi

# =============================================================================
# 2. Start Gazebo
# =============================================================================
echo "[2/6] Starting Gazebo factory world..."
cd "$PX4_DIR"
GZ_ARGS=(--world factory)
[ "$HEADLESS" = "1" ] && GZ_ARGS+=(--headless)
python3 Tools/simulation/gz/simulation-gazebo "${GZ_ARGS[@]}" > /dev/shm/factory_patrol_gz.log 2>&1 &
PIDS+=($!)
sleep 5

# =============================================================================
# 3. Spawn PX4 instances
# =============================================================================
echo "[3/6] Spawning $NUM_DRONES PX4 instances..."
for i in $(seq 0 $((NUM_DRONES - 1))); do
    SPAWN_X=$(echo "$i * 4 - 8" | bc)
    SPAWN_Y="7"
    POSE="${SPAWN_X},${SPAWN_Y},0,0,0,0"
    echo "  Drone $i at (${SPAWN_X}, ${SPAWN_Y}, 0)"
    # stdin = a pipe that stays open and never delivers input: when the launcher has no terminal (or
    # stdin is at EOF), PX4's pxh shell otherwise re-prints its prompt endlessly (~1 GB of drone<i>.log
    # per 10 min). Startup and flight behaviour are unchanged.
    # NAV_DLL_ACT=0: the x500 airframe sets 2, which makes a MAVLink ground station (QGC) a
    # pre-arm requirement; the drones are commanded over ROS 2 (offboard), so without this
    # every run silently stays on the ground whenever QGC is not open.
    PX4_GZ_NO_FOLLOW=1 \
    PX4_UXRCE_DDS_NS=px4_${i} \
    PX4_PARAM_NAV_DLL_ACT=0 \
    PX4_SYS_AUTOSTART=4001 \
    PX4_GZ_MODEL=x500 \
    PX4_GZ_MODEL_POSE="$POSE" \
    ./build/px4_sitl_default/bin/px4 -i $i < <(sleep infinity) > "$PROJECT_DIR/drone${i}.log" 2>&1 &
    PIDS+=($!)
    sleep 5
done

# =============================================================================
# 4. Start patrol controllers
# =============================================================================
echo "[4/6] Starting $NUM_DRONES patrol controllers..."
for i in $(seq 0 $((NUM_DRONES - 1))); do
    echo "  Controller $i"
    PATROL_COMM_LOSS="$COMM_LOSS" ros2 run patrol_controller patrol_controller $i $NUM_DRONES $NAV_MODE &
    PIDS+=($!)
done
sleep 2

# =============================================================================
# 5. Start metrics collector
# =============================================================================
echo "[5/6] Starting metrics collector..."
ros2 run patrol_coordinator metrics_collector \
    --ros-args \
    -p output_dir:="$PROJECT_DIR/experiment_results" \
    -p state_snapshot_interval:=$SNAPSHOT_INTERVAL \
    -p mission_timeout_s:=$MISSION_TIMEOUT \
    -p observation_window_s:=$OBSERVE &
PIDS+=($!)
sleep 1

# =============================================================================
# 6. Start coordinator (algorithm selection + mission dispatch)
# =============================================================================
echo "[6/6] Starting coordinator (algorithm=$ALGORITHM)..."
TASKS_ARGS=()
if [ -n "$TASKS_FILE" ]; then
    TASKS_ARGS=(-p tasks_file:="$PROJECT_DIR/$TASKS_FILE")
fi
"${COORD_CMD[@]}" \
    --ros-args \
    -p algorithm:="$ALGORITHM" \
    -p num_drones:=$NUM_DRONES \
    -p config_file:="$PROJECT_DIR/$CONFIG_FILE" \
    "${TASKS_ARGS[@]}" \
    "${RL_ARGS[@]}" \
    -p mission_delay:=$MISSION_DELAY &
PIDS+=($!)

echo ""
echo "============================================================"
echo "  EXPERIMENT RUNNING"
echo "  Press Ctrl+C to stop"
echo "============================================================"
echo ""

# Wait for all processes
wait
