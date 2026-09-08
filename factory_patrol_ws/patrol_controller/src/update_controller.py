import os
import re

file_path = "/home/mrweirdo/factory_patrol_sim/factory_patrol_ws/patrol_controller/src/patrol_controller.c"
with open(file_path, "r") as f:
    content = f.read()

# I will write a simple python script to generate the entire patrol_controller.c and overwrite it.
# To ensure all auction, ROS2 publishers, and PX4 things work together.
