#!/usr/bin/env python3
"""Live highlighting of a running experiment in the Gazebo GUI (for demos and recordings).

    source /opt/ros/jazzy/setup.bash && source factory_patrol_ws/install/setup.bash
    python3 scripts/sim_markers.py [--tasks config/tasks/benchmark.yaml] [--label "RL (vB)"]

Run it alongside scripts/start_experiment.sh, with the Gazebo GUI open (the GUI's Marker manager
plugin draws the markers; it is in the default layout). It reads the same ROS topics as the
metrics collector and draws, in the Gazebo world frame (x east, y north, z up = -factory z):
  tasks     a translucent pillar from the floor to each task point, grey, turning green for 3 s
            whenever a drone completes the task (any drone, any algorithm)
  drones    a large translucent halo in the drone's colour around each drone (0 blue, 1 orange,
            2 green), a fading trail (last 20 s), and a line to the task it is flying to
  faults    the halo turns red while the drone's communication is down (comm_loss_* events)
Gazebo's renderers do not support TEXT markers, so there are no labels in the 3-D view: ids and
names are in the top view that scripts/screen_record.py draws onto the recording.
Markers are visual only (no physics, not seen by any algorithm or metric).
"""
import argparse
import json
import math
import os
import time
from collections import deque

import rclpy
import yaml
from gz.msgs10 import marker_pb2, marker_v_pb2, boolean_pb2
from gz.transport13 import Node as GzNode
from patrol_msgs.msg import DroneState, ExperimentEvent
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DRONE_RGB = [(0.16, 0.47, 0.84), (0.92, 0.41, 0.20), (0.11, 0.69, 0.48), (0.62, 0.35, 0.80), (0.85, 0.70, 0.10)]
GREY, GREEN, RED, WHITE = (0.55, 0.55, 0.55), (0.10, 0.85, 0.25), (0.95, 0.10, 0.10), (1.0, 1.0, 1.0)
T = marker_pb2.Marker


def colour(mat, rgb, a=1.0, glow=0.6):
    for c in (mat.ambient, mat.diffuse):
        c.r, c.g, c.b, c.a = (*rgb, a)
    mat.emissive.r, mat.emissive.g, mat.emissive.b, mat.emissive.a = (*(glow * v for v in rgb), a)


class Markers(Node):
    def __init__(self, tasks, label, rate_hz):
        super().__init__('sim_markers')
        self.gz = GzNode()
        self.tasks = tasks                           # id -> (x, y, z_up, label)
        self.label = label
        self.state = {}                              # drone -> DroneState
        self.trail = {}                              # drone -> deque[(t, x, y, z)]
        self.flash = {}                              # task -> time of last visit
        self.radio_lost = set()
        self.t_start = None
        self.algorithm = label or ''
        self.scenario = ''
        qos = QoSProfile(reliability=ReliabilityPolicy.RELIABLE, history=HistoryPolicy.KEEP_LAST, depth=50)
        self.gt_seen = set()
        self.create_subscription(DroneState, '/experiment/ground_truth_state', self._gt, qos)
        self.create_subscription(DroneState, '/ground_station/drone_state', self._radio, qos)
        self.create_subscription(ExperimentEvent, '/experiment/events', self._event, qos)
        self._send([self._clear()])
        self._draw_tasks()
        self.create_timer(1.0 / rate_hz, self._update)

    # --- input ------------------------------------------------------------------------------------
    def _gt(self, msg):
        self.gt_seen.add(msg.drone_id)
        self._use(msg)

    def _radio(self, msg):
        if msg.drone_id not in self.gt_seen:
            self._use(msg)

    def _use(self, msg):
        if msg.x == 0.0 and msg.y == 0.0 and msg.z == 0.0:
            return                                   # placeholder before odometry
        self.state[msg.drone_id] = msg
        tr = self.trail.setdefault(msg.drone_id, deque())
        now = time.monotonic()
        if not tr or math.dist(tr[-1][1:], (msg.x, msg.y, -msg.z)) > 0.15:
            tr.append((now, msg.x, msg.y, -msg.z))
        while tr and now - tr[0][0] > 20.0:
            tr.popleft()

    def _event(self, msg):
        try:
            data = json.loads(msg.data)
        except json.JSONDecodeError:
            return
        if msg.event_type == 'mission_started':
            self.t_start = time.monotonic()
            self.algorithm = self.label or str(data.get('algorithm', '')).upper()
            self.scenario = str(data.get('scenario', ''))
        elif msg.event_type == 'task_completed':
            self.flash[int(data.get('task_id', 0))] = time.monotonic()
        elif msg.event_type == 'comm_loss_started':
            self.radio_lost.add(int(data.get('drone_id', -1)))
        elif msg.event_type == 'comm_loss_ended':
            self.radio_lost.discard(int(data.get('drone_id', -1)))

    # --- markers ----------------------------------------------------------------------------------
    def _marker(self, ns, mid, mtype):
        """marker ns/mid+1: id 0 means "unset" to the Marker manager, which then creates a new
        marker on every update instead of modifying the existing one"""
        m = T()
        m.ns, m.id, m.action, m.type = ns, mid + 1, T.ADD_MODIFY, mtype
        return m

    def _clear(self):
        m = T()
        m.action = T.DELETE_ALL
        return m

    def _send(self, markers):
        req = marker_v_pb2.Marker_V()
        req.marker.extend(markers)
        self.gz.request('/marker_array', req, marker_v_pb2.Marker_V, boolean_pb2.Boolean, 1000)

    def _draw_tasks(self, now=None):
        out = []
        for i, (tid, (x, y, z, label)) in enumerate(sorted(self.tasks.items())):
            visited = now is not None and now - self.flash.get(tid, -1e9) < 3.0
            rgb = GREEN if visited else GREY
            p = self._marker('task_pillar', i, T.CYLINDER)
            p.pose.position.x, p.pose.position.y, p.pose.position.z = x, y, z / 2
            p.scale.x = p.scale.y = 0.35
            p.scale.z = max(z, 0.1)
            colour(p.material, rgb, 0.35)
            s = self._marker('task_point', i, T.SPHERE)
            s.pose.position.x, s.pose.position.y, s.pose.position.z = x, y, z
            s.scale.x = s.scale.y = s.scale.z = 0.5 if visited else 0.35
            colour(s.material, rgb, 0.9, 1.0)
            out += [p, s]
        self._send(out)

    def _update(self):
        now = time.monotonic()
        out = []
        for d, s in sorted(self.state.items()):
            x, y, z = s.x, s.y, -s.z
            lost = d in self.radio_lost
            rgb = RED if lost else DRONE_RGB[d % len(DRONE_RGB)]
            halo = self._marker('drone_halo', d, T.SPHERE)
            halo.pose.position.x, halo.pose.position.y, halo.pose.position.z = x, y, z
            halo.scale.x = halo.scale.y = halo.scale.z = 1.4
            colour(halo.material, rgb, 0.35, 0.8)
            out.append(halo)
            tr = self.trail.get(d)
            if tr and len(tr) > 1:
                line = self._marker('drone_trail', d, T.LINE_STRIP)
                for _, px, py, pz in tr:
                    pt = line.point.add()
                    pt.x, pt.y, pt.z = px, py, pz
                colour(line.material, rgb, 0.9, 0.8)
                out.append(line)
            tgt = self.tasks.get(s.current_task_id)
            link = self._marker('drone_goal', d, T.LINE_LIST)
            if tgt and not lost:
                for px, py, pz in ((x, y, z), tgt[:3]):
                    pt = link.point.add()
                    pt.x, pt.y, pt.z = px, py, pz
                colour(link.material, rgb, 0.5, 0.5)
            else:
                link.action = T.DELETE_MARKER
            out.append(link)
        if out:
            self._send(out)
        if any(now - t < 3.5 for t in self.flash.values()) or int(now * 2) % 10 == 0:
            self._draw_tasks(now)


def load_tasks(path):
    data = yaml.safe_load(open(path)) or {}
    return {int(t['id']): (float(t['position'][0]), float(t['position'][1]), -float(t['position'][2]),
                           str(t.get('label', ''))) for t in data.get('tasks', [])}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--tasks', default='config/tasks/benchmark.yaml')
    ap.add_argument('--label', default='', help='caption label (default: the algorithm name)')
    ap.add_argument('--rate', type=float, default=10.0, help='marker update rate (Hz)')
    a = ap.parse_args()
    path = a.tasks if os.path.isabs(a.tasks) else os.path.join(ROOT, a.tasks)
    rclpy.init()
    node = Markers(load_tasks(path), a.label, a.rate)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node._send([node._clear()])
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
