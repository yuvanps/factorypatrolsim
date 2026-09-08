#!/bin/bash
# send_mission.sh
# Sends the factory patrol inspection mission to the drone swarm.

source /opt/ros/jazzy/setup.bash
source /home/mrweirdo/factory_patrol_sim/factory_patrol_ws/install/setup.bash

python3 /home/mrweirdo/factory_patrol_sim/send_mission.py "$@"
