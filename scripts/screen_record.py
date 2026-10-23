#!/usr/bin/env python3
"""Record the Gazebo GUI window to MP4 with a live annotated top view (used by scripts/record_demo.sh).

    source /opt/ros/jazzy/setup.bash && source factory_patrol_ws/install/setup.bash
    python3 scripts/screen_record.py --out videos/demo.mp4 [--window "Gazebo Sim"] [--fps 15]
        [--caption "RL | benchmark"] [--tasks config/tasks/benchmark.yaml]
        [--obstacles config/environment/factory_obstacles.yaml]

Finds the window by (part of) its title with wmctrl, moves it to the top-left of the screen at
--size, keeps it above other windows and grabs its area with Pillow (X11) until SIGINT/SIGTERM.
Every frame gets:
  - a caption bar: --caption and the mission time (from the mission_started event)
  - a top view in the lower right corner, drawn from the run's ROS topics (the same the metrics
    use): obstacle boxes, every task with its id (green for 3 s after a visit), every drone
    as a numbered dot in its colour (the colours of scripts/sim_markers.py) with its current task and
    a 20 s trail, a red ring and "RADIO LOST" while its communication is down
  - a legend
Gazebo's 3-D view cannot show text labels (TEXT markers are not supported by its renderers), so
names and ids live in the top view. Frames are written with OpenCV's FFmpeg backend (H.264 if
available, else MPEG-4).
"""
import argparse
import json
import math
import os
import signal
import subprocess
import threading
import time
from collections import deque

import cv2
import numpy as np
import yaml
from PIL import ImageGrab

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DRONE_BGR = [(214, 120, 41), (51, 105, 235), (122, 176, 28), (204, 89, 158), (26, 178, 217)]  # sim_markers.DRONE_RGB
RED, GREEN, GREY, WHITE = (40, 40, 235), (60, 215, 25), (150, 150, 150), (255, 255, 255)
STOP = False


def _stop(*_):
    global STOP
    STOP = True


class Live:
    """the run's state from ROS (ground truth, events), updated in a background thread"""

    def __init__(self):
        import rclpy
        from patrol_msgs.msg import DroneState, ExperimentEvent
        from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
        self.lock = threading.Lock()
        self.pos, self.task, self.trail, self.flash, self.lost = {}, {}, {}, {}, set()
        self.t_start = None
        self.gt_seen = set()
        rclpy.init()
        self.node = rclpy.create_node('screen_record')
        qos = QoSProfile(reliability=ReliabilityPolicy.RELIABLE, history=HistoryPolicy.KEEP_LAST, depth=50)
        self.node.create_subscription(DroneState, '/experiment/ground_truth_state', self._gt, qos)
        self.node.create_subscription(DroneState, '/ground_station/drone_state', self._radio, qos)
        self.node.create_subscription(ExperimentEvent, '/experiment/events', self._event, qos)
        self.rclpy = rclpy
        threading.Thread(target=self._spin, daemon=True).start()

    def _spin(self):
        while not STOP and self.rclpy.ok():
            self.rclpy.spin_once(self.node, timeout_sec=0.1)

    def _gt(self, m):
        self.gt_seen.add(m.drone_id)
        self._use(m)

    def _radio(self, m):
        if m.drone_id not in self.gt_seen:
            self._use(m)

    def _use(self, m):
        if m.x == 0.0 and m.y == 0.0 and m.z == 0.0:
            return
        now = time.monotonic()
        with self.lock:
            self.pos[m.drone_id] = (m.x, m.y, -m.z)
            self.task[m.drone_id] = m.current_task_id
            tr = self.trail.setdefault(m.drone_id, deque())
            if not tr or math.dist(tr[-1][1:], (m.x, m.y)) > 0.1:
                tr.append((now, m.x, m.y))
            while tr and now - tr[0][0] > 20.0:
                tr.popleft()

    def _event(self, m):
        try:
            d = json.loads(m.data)
        except json.JSONDecodeError:
            return
        with self.lock:
            if m.event_type == 'mission_started':
                self.t_start = time.monotonic()
            elif m.event_type == 'task_completed':
                self.flash[int(d.get('task_id', 0))] = time.monotonic()
            elif m.event_type == 'comm_loss_started':
                self.lost.add(int(d.get('drone_id', -1)))
            elif m.event_type == 'comm_loss_ended':
                self.lost.discard(int(d.get('drone_id', -1)))


def load_tasks(path):
    data = yaml.safe_load(open(path)) or {}
    return {int(t['id']): (float(t['position'][0]), float(t['position'][1]), str(t.get('label', '')))
            for t in data.get('tasks', [])}


def load_boxes(path):
    data = yaml.safe_load(open(path)) or {}
    out = []
    for o in data.get('obstacles', []):
        if o['id'] in ('floor', 'ceiling_barrier'):
            continue
        (cx, cy, _), (sx, sy, _) = o['center'], o['size']
        out.append((o['id'], cx - sx / 2, cy - sy / 2, cx + sx / 2, cy + sy / 2))
    return out


def draw_map(frame, live, tasks, boxes):
    h, w = frame.shape[:2]
    mw = int(w * 0.36)
    mh = int(mw * 20 / 30)                       # hall 30 x 20 m
    x0, y0 = w - mw - 12, h - mh - 60
    s = mw / 31.0
    to_px = lambda x, y: (int(x0 + (x + 15.5) * s), int(y0 + (10.5 - y) * s))
    panel = frame[y0 - 26:y0 + mh, x0:x0 + mw]
    frame[y0 - 26:y0 + mh, x0:x0 + mw] = (panel * 0.25 + 20).astype(np.uint8)
    cv2.putText(frame, 'Top view (north up)', (x0 + 8, y0 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.55, WHITE, 1, cv2.LINE_AA)
    for _, ax, ay, bx, by in boxes:
        cv2.rectangle(frame, to_px(ax, by), to_px(bx, ay), (95, 95, 95), -1)
    now = time.monotonic()
    with live.lock:
        flash, lost = dict(live.flash), set(live.lost)
        pos, task, trail = dict(live.pos), dict(live.task), {d: list(t) for d, t in live.trail.items()}
    for tid, (x, y, label) in tasks.items():
        c = GREEN if now - flash.get(tid, -1e9) < 3.0 else (210, 210, 210)
        p = to_px(x, y)
        cv2.drawMarker(frame, p, c, cv2.MARKER_DIAMOND, 14, 2, cv2.LINE_AA)
        cv2.putText(frame, f'T{tid}', (p[0] + 9, p[1] - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.45, c, 1, cv2.LINE_AA)
    for d, tr in trail.items():
        col = DRONE_BGR[d % len(DRONE_BGR)]
        pts = np.array([to_px(x, y) for _, x, y in tr], np.int32)
        if len(pts) > 1:
            cv2.polylines(frame, [pts], False, col, 2, cv2.LINE_AA)
    for d, (x, y, z) in sorted(pos.items()):
        col = DRONE_BGR[d % len(DRONE_BGR)]
        p = to_px(x, y)
        tgt = tasks.get(task.get(d, 0))
        if tgt and d not in lost:
            cv2.line(frame, p, to_px(tgt[0], tgt[1]), col, 1, cv2.LINE_AA)
        cv2.circle(frame, p, 9, col, -1, cv2.LINE_AA)
        if d in lost:
            cv2.circle(frame, p, 15, RED, 3, cv2.LINE_AA)
        txt = f'D{d}' + (f'>T{task[d]}' if task.get(d) else '') + f' {z:.1f}m' + ('  RADIO LOST' if d in lost else '')
        cv2.putText(frame, txt, (p[0] + 12, p[1] + 16), cv2.FONT_HERSHEY_SIMPLEX, 0.5, RED if d in lost else WHITE, 2, cv2.LINE_AA)


def overlay(frame, caption, live, tasks, boxes, ndrones):
    h, w = frame.shape[:2]
    cv2.rectangle(frame, (0, 0), (w, 44), (25, 25, 25), -1)
    cv2.putText(frame, caption, (14, 31), cv2.FONT_HERSHEY_SIMPLEX, 0.9, WHITE, 2, cv2.LINE_AA)
    t = '' if live is None or live.t_start is None else f'mission t = {time.monotonic() - live.t_start:5.1f} s'
    cv2.putText(frame, t, (w - 300, 31), cv2.FONT_HERSHEY_SIMPLEX, 0.9, WHITE, 2, cv2.LINE_AA)
    cv2.rectangle(frame, (0, h - 44), (w, h), (25, 25, 25), -1)
    x = 14
    for i in range(ndrones):
        cv2.circle(frame, (x + 10, h - 22), 10, DRONE_BGR[i % len(DRONE_BGR)], -1, cv2.LINE_AA)
        cv2.putText(frame, f'Drone {i}', (x + 28, h - 14), cv2.FONT_HERSHEY_SIMPLEX, 0.65, WHITE, 2, cv2.LINE_AA)
        x += 130
    cv2.putText(frame, 'halo = drone   pillar = task (green: just inspected)   line = current goal   red = radio lost',
                (x + 10, h - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (230, 230, 230), 1, cv2.LINE_AA)
    if live is not None:
        draw_map(frame, live, tasks, boxes)
    return frame


def find_window(title, timeout=60.0):
    t0 = time.time()
    while time.time() - t0 < timeout:
        out = subprocess.run(['wmctrl', '-lG'], capture_output=True, text=True).stdout
        for line in out.splitlines():
            parts = line.split(None, 7)
            if len(parts) == 8 and title.lower() in parts[7].lower():
                return parts[0]
        time.sleep(1.0)
    return None


def geometry(win):
    g = {}
    for line in subprocess.run(['xwininfo', '-id', win], capture_output=True, text=True).stdout.splitlines():
        line = line.strip()
        for key, name in (('Absolute upper-left X:', 'x'), ('Absolute upper-left Y:', 'y'), ('Width:', 'w'), ('Height:', 'h')):
            if line.startswith(key):
                g[name] = int(line.split(':')[1])
    return g['x'], g['y'], g['w'], g['h']


def open_writer(path, fps, size):
    for cc in ('avc1', 'mp4v'):
        w = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*cc), fps, size)
        if w.isOpened():
            return w, cc
    raise SystemExit(f'cannot open {path} for writing')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--window', default='Gazebo Sim')
    ap.add_argument('--out', required=True)
    ap.add_argument('--fps', type=float, default=15.0)
    ap.add_argument('--size', default='1920x1080', help='window size to request before recording (WxH)')
    ap.add_argument('--display', default=os.environ.get('DISPLAY', ':0'))
    ap.add_argument('--caption', default='')
    ap.add_argument('--drones', type=int, default=3)
    ap.add_argument('--tasks', default='config/tasks/benchmark.yaml')
    ap.add_argument('--obstacles', default='config/environment/factory_obstacles.yaml')
    ap.add_argument('--no-map', action='store_true', help='no top view (no ROS needed)')
    a = ap.parse_args()
    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)
    rel = lambda p: p if os.path.isabs(p) else os.path.join(ROOT, p)
    live = None if a.no_map else Live()
    tasks, boxes = load_tasks(rel(a.tasks)), load_boxes(rel(a.obstacles))
    win = find_window(a.window)
    if win is None:
        raise SystemExit(f'no window titled "{a.window}"')
    W, H = (int(v) for v in a.size.split('x'))
    subprocess.run(['wmctrl', '-i', '-r', win, '-b', 'remove,maximized_vert,maximized_horz'])
    subprocess.run(['wmctrl', '-i', '-r', win, '-e', f'0,0,0,{W},{H}'])
    subprocess.run(['wmctrl', '-i', '-r', win, '-b', 'add,above'])
    subprocess.run(['wmctrl', '-i', '-a', win])
    time.sleep(2.0)
    x, y, w, h = geometry(win)
    w, h = w - w % 2, h - h % 2
    writer, codec = open_writer(a.out, a.fps, (w, h))
    t0, n, period = time.time(), 0, 1.0 / a.fps
    print(f'recording window {win} at {x},{y} {w}x{h} ({codec}) -> {a.out}', flush=True)
    while not STOP:
        target = t0 + n * period
        img = ImageGrab.grab(bbox=(x, y, x + w, y + h), xdisplay=a.display)
        frame = overlay(cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR), a.caption, live, tasks, boxes, a.drones)
        while target <= time.time() and not STOP:       # keep the video in real time if a grab is slow
            writer.write(frame)
            n += 1
            target = t0 + n * period
        time.sleep(max(0.0, target - time.time()))
    writer.release()
    subprocess.run(['wmctrl', '-i', '-r', win, '-b', 'remove,above'])
    print(f'wrote {n} frames ({n / a.fps:.1f} s) to {a.out}', flush=True)


if __name__ == '__main__':
    main()
