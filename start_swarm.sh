#!/bin/bash
# start_swarm.sh
# This script spawns 3 PX4 instances (SITL) in Gazebo for the factory patrol simulation.
# Note: You should start the Gazebo server and MicroXRCEAgent in separate terminals as usual, 
# Start MicroXRCEAgent if not already running
if ! pgrep -x "MicroXRCEAgent" > /dev/null; then
    echo "Starting MicroXRCEAgent on port 8888..."
    MicroXRCEAgent udp4 -p 8888 &
    sleep 2
fi

cd /home/mrweirdo/factory_patrol_sim/PX4-Autopilot

echo "Spawning Drone 0..."
PX4_GZ_NO_FOLLOW=1 PX4_UXRCE_DDS_NS=px4_0 PX4_SYS_AUTOSTART=4001 PX4_GZ_MODEL=x500 PX4_GZ_MODEL_POSE="0,-1,0,0,0,0" ./build/px4_sitl_default/bin/px4 -i 0 > drone0.log 2>&1 &

sleep 5

echo "Spawning Drone 1..."
PX4_GZ_NO_FOLLOW=1 PX4_UXRCE_DDS_NS=px4_1 PX4_SYS_AUTOSTART=4001 PX4_GZ_MODEL=x500 PX4_GZ_MODEL_POSE="0,-3,0,0,0,0" ./build/px4_sitl_default/bin/px4 -i 1 > drone1.log 2>&1 &

sleep 5

echo "Spawning Drone 2..."
PX4_GZ_NO_FOLLOW=1 PX4_UXRCE_DDS_NS=px4_2 PX4_SYS_AUTOSTART=4001 PX4_GZ_MODEL=x500 PX4_GZ_MODEL_POSE="0,-5,0,0,0,0" ./build/px4_sitl_default/bin/px4 -i 2 > drone2.log 2>&1 &

echo "3 Drones spawned."
wait
