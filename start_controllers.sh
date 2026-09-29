#!/bin/bash
# start_controllers.sh
# Starts N ROS 2 patrol controllers, one per drone.
#
# Usage:
#   ./start_controllers.sh        # default: 3 controllers
#   ./start_controllers.sh 5      # start 5 controllers
#   ./start_controllers.sh 3 external   # APF: transit driven by /swarm/movement_command

NUM_DRONES=${1:-3}
NAV_MODE=${2:-internal}   # internal (auction/built-in transit) | external (APF)

source /opt/ros/jazzy/setup.bash
source /home/mrweirdo/factory_patrol_sim/factory_patrol_ws/install/setup.bash

echo "============================================"
echo "  Factory Patrol Controllers"
echo "  Drones: $NUM_DRONES"
echo "============================================"

for i in $(seq 0 $((NUM_DRONES - 1))); do
    echo "Starting Controller for Drone $i..."
    ros2 run patrol_controller patrol_controller $i $NUM_DRONES $NAV_MODE &
done

wait
