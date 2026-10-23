# Recording demo videos

The videos in `videos/` (one per algorithm and scenario) show the same experiment the benchmark
measures, with highlighting added for the audience.

| Element | Where | What it shows |
|---|---|---|
| Halo (large translucent sphere) | 3-D view | each drone, in its colour: 0 blue, 1 orange, 2 green |
| Halo turns red | 3-D view and top view | the drone's radio is down (comm-loss scenarios) |
| Trail | 3-D view and top view | the drone's path over the last 20 s |
| Thin line from a drone | 3-D view and top view | the task it is currently flying to |
| Pillar from the floor | 3-D view | a task (inspection point); green for 3 s after any drone inspects it |
| Top view (lower right) | overlay | factory plan with obstacles; tasks labelled T101…; drones labelled `D1>T105 2.8m` (id, current task, height) |
| Caption bar | overlay | algorithm, scenario, mission time (t = 0 when the mission is dispatched) |

Gazebo Harmonic cannot draw text in its 3-D view (TEXT markers are not supported by either
renderer), so every label is in the top view. All highlighting is visual only: no algorithm or
metric sees it.

## Automatic recording

```bash
./scripts/record_demo.sh <algorithm> <scenario> [output.mp4] [max_seconds]
./scripts/record_demo.sh rl safety_stress videos/rl_safety_stress.mp4 330
```

The script:
1. starts the experiment headless;
2. opens a Gazebo window with `config/gazebo/recording_gui.config` (overview camera above the hall);
3. starts `scripts/sim_markers.py`;
4. captures the window with `scripts/screen_record.py` until the run summary is written, then cleans up.

Notes:
- The Gazebo window opens on your desktop (`DISPLAY`, default `:0`), is moved to the top-left and
  stays above other windows while recording. Don't cover or minimise it.
- The output is H.264 MP4 at 15 fps, a few MB per minute.
- Each recording is also an ordinary run: it has its summary in `experiment_results/summaries/`.
- Gazebo's own video-recorder plugin is in the layout, but in this Gazebo version it can only be
  started from its toolbar button, hence the screen capture.

## Recording yourself

If you prefer your own screen recorder (OBS, the GNOME recorder, ...):

```bash
# terminal 1: the experiment, with the Gazebo GUI (no --headless)
./scripts/start_experiment.sh --algorithm rl --scenario safety_stress --drones 3

# terminal 2, once the Gazebo window is up: the highlighting in the 3-D view
source /opt/ros/jazzy/setup.bash && source factory_patrol_ws/install/setup.bash
python3 scripts/sim_markers.py --tasks config/tasks/safety_stress.yaml

# optional, terminal 3: the caption and the labelled top view, recorded into a file
python3 scripts/screen_record.py --out videos/my_run.mp4 --caption "RL | safety_stress" \
    --tasks config/tasks/safety_stress.yaml
```

Notes:
- **Task file:** use the task file of the scenario you run. `config/experiments/<scenario>.yaml` lists it
  under `mission.tasks_file`.
- **Camera:** in the default layout, use the mouse to frame the hall: right-drag to pan, scroll to
  zoom, middle-drag to rotate. For the overview used in the videos, start a GUI client with the
  recording layout instead of the launcher's GUI:
  ```bash
  ./scripts/start_experiment.sh ... --headless
  GZ_SIM_RESOURCE_PATH=$HOME/.simulation-gazebo/models:$PWD/PX4-Autopilot/Tools/simulation/gz/models \
      gz sim -g --gui-config config/gazebo/recording_gui.config
  ```
- **Markers on demand:** `sim_markers.py` can be started or stopped at any time. It removes its
  markers when stopped (Ctrl+C).
