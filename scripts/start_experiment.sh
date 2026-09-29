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
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --algorithm, -a  Coordination algorithm (auction|pso|apf) [default: auction]"
            echo "  --scenario, -s   Scenario (benchmark|safety_stress) [default: benchmark]"
            echo "  --drones, -n     Number of drones to spawn [default: 3]"
            echo "  --config, -c     Path to scenario config YAML [default: config/experiments/<scenario>.yaml]"
            echo "  --tasks, -t      Path to tasks YAML [default: scenario's mission.tasks_file]"
            echo "  --delay, -d      Mission publish delay in seconds [default: 5.0]"
            echo "  --headless       Run Gazebo without the GUI"
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
    apf) NAV_MODE="external" ;;
    *)   NAV_MODE="internal" ;;
esac

SNAPSHOT_INTERVAL=$(python3 -c "import yaml,sys; c=yaml.safe_load(open(sys.argv[1])) or {}; print(float((c.get('metrics') or {}).get('state_snapshot_interval', 1.0)))" "$PROJECT_DIR/$CONFIG_FILE")
MISSION_TIMEOUT=$(python3 -c "import yaml,sys; c=yaml.safe_load(open(sys.argv[1])) or {}; print(float((c.get('metrics') or {}).get('mission_timeout_s', 600.0)))" "$PROJECT_DIR/$CONFIG_FILE")

echo "============================================================"
echo "  FACTORY PATROL EXPERIMENT"
echo "============================================================"
echo "  Scenario:   $SCENARIO"
echo "  Algorithm:  $ALGORITHM"
echo "  Drones:     $NUM_DRONES"
echo "  Nav mode:   $NAV_MODE"
echo "  Config:     $CONFIG_FILE"
echo "  Tasks:      ${TASKS_FILE:-(from scenario config)}"
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
    # Kill any remaining PX4 instances
    pkill -f "px4_sitl_default/bin/px4" 2>/dev/null || true
    echo "[Experiment] Done."
}

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
python3 Tools/simulation/gz/simulation-gazebo "${GZ_ARGS[@]}" > /dev/null 2>&1 &
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
    PX4_GZ_NO_FOLLOW=1 \
    PX4_UXRCE_DDS_NS=px4_${i} \
    PX4_SYS_AUTOSTART=4001 \
    PX4_GZ_MODEL=x500 \
    PX4_GZ_MODEL_POSE="$POSE" \
    ./build/px4_sitl_default/bin/px4 -i $i > "$PROJECT_DIR/drone${i}.log" 2>&1 &
    PIDS+=($!)
    sleep 5
done

# =============================================================================
# 4. Start patrol controllers
# =============================================================================
echo "[4/6] Starting $NUM_DRONES patrol controllers..."
for i in $(seq 0 $((NUM_DRONES - 1))); do
    echo "  Controller $i"
    ros2 run patrol_controller patrol_controller $i $NUM_DRONES $NAV_MODE &
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
    -p mission_timeout_s:=$MISSION_TIMEOUT &
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
ros2 run patrol_coordinator coordinator_node \
    --ros-args \
    -p algorithm:="$ALGORITHM" \
    -p num_drones:=$NUM_DRONES \
    -p config_file:="$PROJECT_DIR/$CONFIG_FILE" \
    "${TASKS_ARGS[@]}" \
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
