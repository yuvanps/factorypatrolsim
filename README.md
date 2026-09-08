##Start QGC

./QGroundcontrol (whatever the appimage is)

## start Micro SRCE DDS service to communicate with ROS
MicroXRCEAgent udp4 -p 8888

##start Gazebo with custom factory world and access to PX4 resources 
cd PX4-Autopilot

python3 Tools/simulation/gz/simulation-gazebo \
    --world factory \
    --model_store ~/.simulation-gazebo

##spawn in X500 model
cd PX4-Autopilot

make px4_sitl gz_x500

##start ROS2 script
source /opt/ros/jazzy/setup.bash
source factory_patrol_ws/install/setup.bash

ros2 run patrol_controller patrol_controller


**NOTE:** Start all these in seperate terminals !!!
