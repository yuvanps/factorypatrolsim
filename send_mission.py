#!/usr/bin/env python3
"""Ground Station — Dispatch inspection mission to the drone swarm.

Loads tasks from a YAML config file and publishes them as a Mission message.

Usage:
    python3 send_mission.py                              # default tasks
    python3 send_mission.py config/tasks/benchmark.yaml    # explicit file
    ./send_mission.sh                                    # via wrapper
"""

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
import yaml


def load_tasks_from_yaml(yaml_path: str) -> list[dict]:
    """Load task definitions from a YAML file."""
    with open(yaml_path, 'r') as f:
        data = yaml.safe_load(f) or {}
    tasks_raw = data.get('tasks', [])
    tasks = []
    for t in tasks_raw:
        pos = t.get('position', [0, 0, -3])
        tasks.append({
            'id': t['id'],
            'x': float(pos[0]),
            'y': float(pos[1]),
            'z': float(pos[2]),
            'priority': t.get('priority', 1),
            'type': t.get('inspection_type', 0),
            'hover': t.get('hover_duration', 4.0),
            'label': t.get('label', ''),
        })
    return tasks


def get_default_tasks() -> list[dict]:
    """Fallback hardcoded tasks if no YAML file is available."""
    return [
        {'id': 101, 'x': -10.75, 'y': 0.0, 'z': -4.0, 'priority': 1, 'type': 0, 'hover': 4.0},
        {'id': 102, 'x': -8.25,  'y': 0.0, 'z': -4.0, 'priority': 1, 'type': 0, 'hover': 4.0},
        {'id': 103, 'x': -5.75,  'y': 0.0, 'z': -4.0, 'priority': 1, 'type': 0, 'hover': 4.0},
        {'id': 104, 'x':  5.0,   'y': 4.0, 'z': -3.5, 'priority': 1, 'type': 0, 'hover': 4.0},
        {'id': 105, 'x': 10.0,   'y': 4.0, 'z': -3.5, 'priority': 1, 'type': 0, 'hover': 4.0},
        {'id': 106, 'x':  7.0,   'y': -4.0, 'z': -3.5, 'priority': 1, 'type': 0, 'hover': 4.0},
    ]


def main():
    rclpy.init()
    node = Node('ground_station_publisher')
    pub = node.create_publisher(Mission, '/ground_station/mission', 10)

    # Determine tasks source
    tasks_file = None
    if len(sys.argv) > 1:
        tasks_file = sys.argv[1]
    else:
        # Try default locations
        candidates = [
            'config/tasks/benchmark.yaml',
            '/home/mrweirdo/factory_patrol_sim/config/tasks/benchmark.yaml',
        ]
        for c in candidates:
            if os.path.exists(c):
                tasks_file = c
                break

    if tasks_file and os.path.exists(tasks_file):
        waypoints = load_tasks_from_yaml(tasks_file)
        print(f"[Ground Station] Loaded {len(waypoints)} tasks from {tasks_file}")
    else:
        waypoints = get_default_tasks()
        print(f"[Ground Station] Using {len(waypoints)} default tasks")

    # Wait for subscribers to connect
    print("[Ground Station] Waiting for drone swarm controllers to connect (3 seconds)...")
    time.sleep(3.0)

    mission = Mission()
    mission.mission_id = 1

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
