#!/bin/bash
# start_swarm.sh
# Spawns N PX4 SITL instances in Gazebo for the factory patrol simulation.
#
# Usage:
#   ./start_swarm.sh          # default: 3 drones
#   ./start_swarm.sh 5        # spawn 5 drones
#
# Prerequisites:
#   - Gazebo server running with the factory world
#   - MicroXRCEAgent running (this script starts it if not found)

NUM_DRONES=${1:-3}
PX4_DIR="/home/mrweirdo/factory_patrol_sim/PX4-Autopilot"

echo "============================================"
echo "  Factory Patrol Swarm Launcher"
echo "  Drones: $NUM_DRONES"
echo "============================================"

# Start MicroXRCEAgent if not already running
if ! pgrep -x "MicroXRCEAgent" > /dev/null; then
    echo "Starting MicroXRCEAgent on port 8888..."
    MicroXRCEAgent udp4 -p 8888 &
    sleep 2
fi

cd "$PX4_DIR"

for i in $(seq 0 $((NUM_DRONES - 1))); do
    # Spawn positions: south area y=-8.5, spaced 2m apart along X starting at x=-6
    # Clearances: south wall 1.35m, partition 4.5m, packing 0.5m, racks 2.5m
    SPAWN_X=$(echo "$i * 4 - 8" | bc)
    SPAWN_Y="7"
    POSE="${SPAWN_X},${SPAWN_Y},0,0,0,0"

    echo "Spawning Drone $i at (${SPAWN_X}, ${SPAWN_Y}, 0)..."
    PX4_GZ_NO_FOLLOW=1 \
    PX4_UXRCE_DDS_NS=px4_${i} \
    PX4_SYS_AUTOSTART=4001 \
    PX4_GZ_MODEL=x500 \
    PX4_GZ_MODEL_POSE="$POSE" \
    ./build/px4_sitl_default/bin/px4 -i $i > drone${i}.log 2>&1 &

    sleep 5
done

echo ""
echo "$NUM_DRONES drone(s) spawned."
wait
