#!/bin/bash
# start_controllers.sh
# This script starts the 3 ROS 2 patrol controllers for each drone.

source /opt/ros/jazzy/setup.bash
source /home/mrweirdo/factory_patrol_sim/factory_patrol_ws/install/setup.bash

echo "Starting Controller for Drone 0..."
ros2 run patrol_controller patrol_controller 0 &

echo "Starting Controller for Drone 1..."
ros2 run patrol_controller patrol_controller 1 &

echo "Starting Controller for Drone 2..."
ros2 run patrol_controller patrol_controller 2 &

wait
