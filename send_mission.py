import sys
import os

# Auto-add ROS 2 Jazzy and workspace Python paths if executed without sourcing
ros_paths = [
    '/opt/ros/jazzy/lib/python3.12/site-packages',
    '/home/mrweirdo/factory_patrol_sim/factory_patrol_ws/install/patrol_msgs/lib/python3.12/site-packages',
    '/home/mrweirdo/factory_patrol_sim/factory_patrol_ws/install/px4_msgs/lib/python3.12/site-packages',
]
for p in ros_paths:
    if os.path.exists(p) and p not in sys.path:
        sys.path.insert(0, p)

import rclpy
from rclpy.node import Node
from patrol_msgs.msg import Mission, Task
import time

def main():
    rclpy.init()
    node = Node('ground_station_publisher')
    pub = node.create_publisher(Mission, '/ground_station/mission', 10)

    # Wait for subscribers to connect
    print("[Ground Station] Waiting for drone swarm controllers to connect (3 seconds)...")
    time.sleep(3.0)

    mission = Mission()
    mission.mission_id = 1

    # Pre-calculated factory patrol points partitioned by sectors and clearance:
    # Drone 0 (South Aisle & Entry corridor)
    # Drone 1 (East Corridor & Machinery C/D)
    # Drone 2 (West Corridor & Machinery A/B)
    waypoints = [
        {'id': 101, 'x': 2.0, 'y': -4.0, 'z': -2.5, 'priority': 1, 'type': 0, 'hover': 3.0}, # South-East Aisle
        {'id': 102, 'x': -3.0, 'y': -4.0, 'z': -2.5, 'priority': 1, 'type': 0, 'hover': 3.0}, # South-West Aisle
        {'id': 103, 'x': 5.0, 'y': -1.0, 'z': -3.2, 'priority': 1, 'type': 0, 'hover': 4.0}, # Machine C Inspection
        {'id': 104, 'x': 5.0, 'y': 6.0, 'z': -3.2, 'priority': 1, 'type': 0, 'hover': 4.0},  # Machine D Inspection
        {'id': 105, 'x': -4.0, 'y': -0.5, 'z': -4.0, 'priority': 1, 'type': 0, 'hover': 4.0}, # Machine A West
        {'id': 106, 'x': -7.0, 'y': 1.0, 'z': -3.0, 'priority': 1, 'type': 0, 'hover': 4.0},  # Machine B Inspection (standoff)
    ]

    for wp in waypoints:
        t = Task()
        t.task_id = wp['id']
        t.x = wp['x']
        t.y = wp['y']
        t.z = wp['z']
        t.priority = wp['priority']
        t.inspection_type = wp['type']
        t.hover_duration = wp['hover']
        mission.tasks.append(t)

    print(f"[Ground Station] Publishing Mission {mission.mission_id} with {len(mission.tasks)} tasks to /ground_station/mission...")
    pub.publish(mission)
    time.sleep(0.5)
    print("[Ground Station] Mission published successfully!")

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
