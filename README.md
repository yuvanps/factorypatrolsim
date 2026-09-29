# Factory Patrol Simulation — Multi-UAV Benchmarking Framework

A modular benchmarking framework for comparing swarm coordination algorithms in a PX4 + Gazebo + ROS 2 Jazzy multi-UAV factory patrol simulation.

## Architecture

```
                    ┌────────────────────────┐
                    │   Experiment Config     │
                    │   (config/*.yaml)       │
                    └──────────┬─────────────┘
                               │
                    ┌──────────▼─────────────┐
                    │   Coordinator Node      │
                    │   (patrol_coordinator)  │
                    │                         │
                    │  ┌───────────────────┐  │
                    │  │ Algorithm Select  │  │
                    │  │  ┌─────────────┐  │  │
                    │  │  │ Auction     │  │  │
                    │  │  │ PSO (stub)  │  │  │
                    │  │  │ APF         │  │  │
                    │  │  └─────────────┘  │  │
                    │  └───────────────────┘  │
                    └──────────┬─────────────┘
                               │
              /ground_station/mission
              /swarm/task_assignment
              /swarm/movement_command (APF)
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                     │
  ┌───────▼────────┐  ┌───────▼────────┐  ┌────────▼───────┐
  │ Patrol Ctrl 0  │  │ Patrol Ctrl 1  │  │ Patrol Ctrl N  │
  │ (C / rclc)     │  │ (C / rclc)     │  │ (C / rclc)     │
  │ + Auctioneer   │  │                │  │                │
  └───────┬────────┘  └───────┬────────┘  └────────┬───────┘
          │                    │                     │
  ┌───────▼────────┐  ┌───────▼────────┐  ┌────────▼───────┐
  │  PX4 SITL 0    │  │  PX4 SITL 1    │  │  PX4 SITL N    │
  └───────┬────────┘  └───────┬────────┘  └────────┬───────┘
          │                    │                     │
          └────────────────────┼─────────────────────┘
                               │
                    ┌──────────▼─────────────┐
                    │   Gazebo Simulation     │
                    │   (Factory World)       │
                    └──────────┬─────────────┘
                               │
                    ┌──────────▼─────────────┐
                    │   Metrics Collector     │
                    │   (JSONL + CSV output)  │
                    └────────────────────────┘
```

### Component Overview

| Component | Language | Location | Purpose |
|---|---|---|---|
| **Patrol Controller** | C (rclc) | `patrol_controller/` | PX4 interface, navigation state machine, zone patrol loop |
| **Auction Logic** | C | `patrol_controller/src/auction_logic.c` | Native auction-based task allocation (baseline algorithm) |
| **Coordinator Node** | Python (rclpy) | `src/patrol_coordinator/` | Algorithm selection, mission dispatch, experiment orchestration |
| **Metrics Collector** | Python (rclpy) | `src/patrol_coordinator/` | Data collection (events JSONL + drone states CSV) |
| **Patrol Messages** | ROS 2 IDL | `src/patrol_msgs/` | Task, Mission, DroneState, TaskBid, TaskAssignment, SwarmStatus, ExperimentEvent |
| **Factory World** | SDF | `worlds/factory.sdf` | Gazebo factory environment with racks, machines, aisles |

## Directory Structure

```
factory_patrol_sim/
├── config/
│   ├── algorithms/
│   │   └── apf.yaml             # APF parameters (scenario-independent)
│   ├── environment/
│   │   └── factory_obstacles.yaml  # Static factory boxes (mirrors worlds/factory.sdf)
│   ├── experiments/             # Scenario configs (one per scenario)
│   │   ├── benchmark.yaml       # Nominal patrol mission (default)
│   │   └── safety_stress.yaml   # Collision-avoidance stress mission
│   └── tasks/                   # Task/waypoint sets referenced by the scenarios
│       ├── benchmark.yaml
│       ├── safety_stress.yaml
│       └── apf_crossing_test.yaml  # 2-drone crossing loops (drone-repulsion test)
├── factory_patrol_ws/
│   ├── patrol_controller/       # C patrol controller package
│   │   ├── include/
│   │   │   └── auction_logic.h  # Auction data structures & API
│   │   └── src/
│   │       ├── patrol_controller.c  # Main controller (PX4 + nav)
│   │       └── auction_logic.c      # Auction algorithm
│   └── src/
│       ├── patrol_coordinator/  # Python coordination framework
│       │   └── patrol_coordinator/
│       │       ├── algorithm_base.py    # Abstract algorithm interface
│       │       ├── algorithms/
│       │       │   ├── auction.py       # Auction passthrough
│       │       │   ├── pso_stub.py      # PSO placeholder
│       │       │   └── apf.py           # Artificial Potential Field
│       │       ├── obstacles.py         # Box obstacle model (shared geometry)
│       │       ├── coordinator_node.py  # Experiment coordinator
│       │       └── metrics_collector.py # Data collection
│       │   └── test/test_apf.py         # APF / obstacle / registry unit tests
│       ├── patrol_msgs/         # ROS 2 message definitions
│       └── px4_msgs/            # PX4 message definitions
├── worlds/
│   └── factory.sdf              # Gazebo factory world
├── scripts/
│   └── start_experiment.sh      # Unified experiment launcher
├── start_swarm.sh               # PX4 instance spawner
├── start_controllers.sh         # Controller launcher
├── send_mission.py              # Standalone mission sender
└── send_mission.sh              # Mission sender wrapper
```

## Quick Start

### Prerequisites

- Ubuntu 24.04
- ROS 2 Jazzy
- PX4-Autopilot (built with `make px4_sitl_default`)
- Gazebo (Harmonic)
- MicroXRCEAgent

### Build

```bash
cd factory_patrol_sim/factory_patrol_ws
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
```

### Launch (Unified Script)

```bash
# Default: 3 drones, auction algorithm
./scripts/start_experiment.sh

# 5 drones with auction
./scripts/start_experiment.sh --algorithm auction --drones 5

# 3 drones with Artificial Potential Field movement coordination
./scripts/start_experiment.sh --algorithm apf --drones 3

# Without the Gazebo GUI
./scripts/start_experiment.sh --algorithm apf --drones 3 --headless
```

### Launch (Manual — Separate Terminals)

```bash
# Terminal 1: Gazebo
cd PX4-Autopilot
python3 Tools/simulation/gz/simulation-gazebo --world factory

# Terminal 2: PX4 swarm (N drones)
./start_swarm.sh 3

# Terminal 3: Controllers  (use "./start_controllers.sh 3 external" for APF)
./start_controllers.sh 3

# Terminal 4: Mission dispatch
./send_mission.sh
# or with coordinator:
source factory_patrol_ws/install/setup.bash
ros2 run patrol_coordinator coordinator_node \
    --ros-args -p algorithm:=auction -p num_drones:=3
```

## Configuration

### Algorithm Selection

```bash
# Via start_experiment.sh
./scripts/start_experiment.sh --algorithm auction
./scripts/start_experiment.sh --algorithm pso
./scripts/start_experiment.sh --algorithm apf

# Via ROS 2 parameter
ros2 run patrol_coordinator coordinator_node --ros-args -p algorithm:=auction

```

### Scenario Selection

The scenario (task set + metrics sampling) is selected independently of the algorithm:

| Scenario | Config | Purpose |
|---|---|---|
| `benchmark` (default) | `config/experiments/benchmark.yaml` | Nominal patrol. No task lies under another task's transit route, so it measures allocation/coordination, not route-geometry crashes. |
| `safety_stress` | `config/experiments/safety_stress.yaml` | Original (collinear) layout plus a task beside the centre corridor and a low in-aisle task. Crossing routes by design; collisions are a recorded outcome. Drone states sampled at 5 Hz. |

```bash
./scripts/start_experiment.sh --scenario benchmark     --algorithm auction --drones 3
./scripts/start_experiment.sh --scenario safety_stress --algorithm auction --drones 3
```

### Number of Drones

```bash
# Via start_experiment.sh
./scripts/start_experiment.sh --drones 5

# Via individual scripts
./start_swarm.sh 5
./start_controllers.sh 5

# Default when --drones / num_drones is not given: config/experiments/<scenario>.yaml
experiment:
  num_drones: 5
```

Each controller is started as `patrol_controller <drone_id> <num_drones> [internal|external]`
(`external` = APF navigation mode, chosen automatically by `start_experiment.sh`); only drone IDs
`0..num_drones-1` can take part in the auction.

Supported: 1, 2, 3, 5, 10 (limited by `MAX_DRONES=10` in C code and system resources).

### Task/Waypoint Configuration

Edit the scenario's task file (`config/tasks/<scenario>.yaml`). Coordinates are in the factory
frame = Gazebo world frame: x = Gazebo X (east), y = Gazebo Y (north), z = -height (negative = above ground).

```yaml
tasks:
  - id: 101
    position: [-10.75, -2.0, -2.5]   # [x, y, z] in factory frame
    priority: 1
    inspection_type: 0
    hover_duration: 4.0
    label: "Storage Aisle 1"
```

## How to Add a New Algorithm

1. **Create the algorithm file** in `patrol_coordinator/algorithms/`:

```python
# patrol_coordinator/algorithms/my_algorithm.py
from patrol_coordinator.algorithm_base import (
    CoordinationAlgorithm, AlgorithmResult, TaskInfo, TaskAssignment
)

class MyAlgorithm(CoordinationAlgorithm):
    def get_name(self) -> str:
        return "My Algorithm"

    def initialize(self, num_drones: int, tasks: list[TaskInfo]) -> None:
        self._num_drones = num_drones
        self._tasks = list(tasks)
        # Your initialization here

    def compute(self, timestamp_ns: int) -> AlgorithmResult:
        assignments = []
        # Your algorithm logic here
        # Example: assignments.append(TaskAssignment(task_id=101, drone_id=0))
        return AlgorithmResult(assignments=assignments)
```

2. **Register it** in `patrol_coordinator/algorithms/__init__.py`:

```python
ALGORITHM_REGISTRY = {
    'auction': '...',
    'pso': '...',
    'apf': '...',
    'my_algo': 'patrol_coordinator.algorithms.my_algorithm.MyAlgorithm',  # ADD THIS
}
```

3. **Use it**:

```bash
./scripts/start_experiment.sh --algorithm my_algo --drones 3
```

### Algorithm Interface

The `CoordinationAlgorithm` base class defines:

| Method | Purpose |
|---|---|
| `get_name()` | Display name |
| `initialize(num_drones, tasks)` | Setup with drone count and task list |
| `update_drone_state(state)` | Receive telemetry updates |
| `update_tasks(tasks)` | Receive task list updates |
| `compute(timestamp_ns)` | **Core**: run one coordination step, return results |
| `reset()` | Reset for new experiment run |
| `on_task_completed(task_id, drone_id)` | Optional hook |
| `on_drone_failed(drone_id)` | Optional hook |
| `get_metrics()` | Optional: return algorithm-specific metrics |

The `AlgorithmResult` supports two output types:
- **`assignments`**: List of `TaskAssignment(task_id, drone_id)` — for task-based algorithms (auction, PSO)
- **`movement_commands`**: List of `MovementCommand(drone_id, target_x, ...)` — for reactive algorithms (APF)

## Preliminary Metrics (per-run summary CSV)

> These are preliminary simulation metrics intended to validate the benchmarking framework and demonstrate progress. They are not yet sufficient for statistically meaningful algorithmic conclusions.

Every run automatically writes **one** summary CSV (one row) — no manual conversion step.
The metrics are computed by the metrics collector (`patrol_coordinator/metrics_summary.py`)
from the same telemetry and events for every algorithm; algorithms never write metric files.

**Location:** `experiment_results/summaries/<run_id>_<algorithm>_<scenario>_<N>drones.csv`,
e.g. `experiment_results/summaries/run_20260929_211041_auction_benchmark_3drones.csv`.
`run_id` is the existing run directory name (`experiment_results/<run_id>/`), which also receives
`metrics_detail.json` (per-drone distance and battery, first-completion times, excluded drones).

**When it is written:** as soon as the mission completes; otherwise with `status=timeout` after
`metrics.mission_timeout_s` (scenario config, default 600 s), or `status=aborted` if the run is
stopped first. Incomplete runs keep every metric that is valid; missing values are left empty.

### Definitions

| # | Metric | Definition |
|---|---|---|
| 1 | Mission completion time | `end - start` in seconds. **Start** = the coordinator's `mission_started` event (the moment the mission is published). **End** = the `task_completed` event that completes the last mission task not yet completed, i.e. every task has been completed at least once (one patrol cycle). Empty if the mission did not complete. |
| 2 | Task completion rate | `completed_tasks / total_tasks * 100`. A task counts as completed only when a patrol controller's mission logic marks it completed (it then publishes a `task_completed` event); repeat visits do not count again. |
| 3 | Total flight distance | Sum over drones of the 3D path length between consecutive valid `/ground_station/drone_state` samples (10 Hz, corrected world frame, no frame conversion) inside [start, end]. |
| 4 | Per-drone workload | `drone_<i>_tasks` = number of mission tasks whose **first** completion was performed by drone *i* (columns sum to `completed_tasks`). `workload_min` / `workload_max` over the spawned drones. |
| 5 | Minimum inter-drone distance | Minimum 3D distance between any two valid drones inside [start, end], evaluated on a common 20 Hz timeline with linear interpolation of each drone's telemetry. `N/A` with fewer than two drones. |
| 6 | Battery consumption | Per drone: first valid battery sample in the window minus the last valid one; `total_battery_consumed_percent` = sum over drones. In this simulation battery drains at a fixed rate per time step, so this metric follows mission duration, not flight effort. |

**Validity / failed drones.** Phantom IDs (≥ `num_drones`) are ignored.
*Pre-odometry placeholder:* a controller publishes `DroneState` with position exactly (0, 0, 0) until
its first PX4 odometry arrives (this happens when the last-spawned PX4 is still starting at mission
start). Such samples carry no position: they are not used for distance or separation (the first
real sample becomes the reference), but their battery value is used.
*Isolated impossible jumps:* a transition implying > 15 m/s is rejected (no distance counted across
it, no separation interpolated across it); the new sample becomes the reference and collection
continues. Rejected transitions are listed in `notes` and, with raw values, in `metrics_detail.json`.
*Permanent exclusion:* a drone's samples are used until the first of: state `FAILED`; non-finite
values; position outside the factory walls, below the floor or above the ceiling; or, after having
been airborne, < 0.3 m height for ≥ 5 s while still reporting PATROLLING/INSPECTING (crashed but
still publishing).
From then on the drone contributes no distance, separation or battery samples (its pre-failure
distance and last valid battery value are kept, and tasks it completed still count); the `notes`
column says which drone was excluded and why. Drones with no valid battery samples are reported in
`notes` and excluded from the battery total (no value is fabricated). Timestamps are the ROS
clock of the experiment nodes (there is no simulation-time clock in this setup).

### CSV columns

| Column | Unit | Meaning |
|---|---|---|
| `run_id` | – | Run directory name `run_YYYYMMDD_HHMMSS` |
| `timestamp` | ISO 8601 | Mission start time |
| `algorithm`, `scenario`, `num_drones` | – | From the coordinator's `mission_started` event |
| `status` | – | `completed`, `timeout` or `aborted` |
| `total_tasks`, `completed_tasks` | count | Mission tasks / tasks completed at least once |
| `task_completion_rate_percent` | % | 2 decimals |
| `mission_completion_time_s` | s | 3 decimals; empty if not completed |
| `total_flight_distance_m` | m | 3 decimals |
| `minimum_inter_drone_distance_m` | m | 3 decimals, or `N/A` |
| `total_battery_consumed_percent` | % | 2 decimals |
| `workload_min`, `workload_max` | tasks | Over the spawned drones |
| `drone_0_tasks` … `drone_<N-1>_tasks` | tasks | One column per spawned drone |
| `notes` | – | Excluded drones, missing battery, N/A reasons |

### Commands

```bash
./scripts/start_experiment.sh --scenario benchmark --algorithm auction --drones 3
./scripts/start_experiment.sh --scenario benchmark --algorithm apf     --drones 3
# -> experiment_results/summaries/run_<timestamp>_<algorithm>_benchmark_3drones.csv
```

Example rows (live 3-drone runs, same scenario and task set):

```csv
run_id,timestamp,algorithm,scenario,num_drones,status,total_tasks,completed_tasks,task_completion_rate_percent,mission_completion_time_s,total_flight_distance_m,minimum_inter_drone_distance_m,total_battery_consumed_percent,workload_min,workload_max,drone_0_tasks,drone_1_tasks,drone_2_tasks,notes
run_20260929_211041,2026-09-29T21:10:49,auction,benchmark,3,completed,6,6,100.0,44.114,254.275,2.19,13.2,2,2,2,2,2,
run_20260929_211505,2026-09-29T21:15:13,apf,benchmark,3,completed,6,6,100.0,44.295,99.884,2.006,13.23,2,2,2,2,2,
```

Combine runs with e.g. `pandas.concat(pd.read_csv(f) for f in glob.glob('experiment_results/summaries/*.csv'))`.

## How to Add a New Metric

The metrics framework collects raw data — metric computation is done in post-processing.

### What's Already Collected

**Events** (`experiment_events.jsonl`):
- `coordinator_started`, `mission_started`
- `task_assigned` (with task_id, drone_id)
- `bid_received` (with task_id, drone_id, cost)
- `swarm_status` (e.g., all drones low battery)
- `task_completed` (drone_id, task_id, hover_s) — published by the patrol controllers when their mission logic completes a task
- `run_summary_written` (path, status) — the summary CSV was written
- APF only: `apf_diagnostics` (per commanded drone, 1 Hz), `apf_clearance` (1 Hz), `apf_stall` (see [APF](#artificial-potential-field-apf))

**State snapshots** (`drone_states.csv`):
- timestamp, drone_id, x, y, z, battery_level, state, current_task_id (recorded every `metrics.state_snapshot_interval` seconds)

### Adding a New Event

Emit events from the coordinator or algorithm:

```python
# In coordinator_node.py or your algorithm
self._emit_event('my_custom_event', {
    'drone_id': 0,
    'metric_value': 42.0,
})
```

Events are automatically recorded to `experiment_events.jsonl`.

### Post-Processing

Results are saved to `experiment_results/run_YYYYMMDD_HHMMSS/`:

```bash
experiment_results/
└── run_20260929_113000/
    ├── experiment_events.jsonl   # One JSON object per line
    ├── drone_states.csv          # Periodic state snapshots
    └── metrics_detail.json       # Per-drone distance/battery behind the summary row
experiment_results/summaries/
└── run_20260929_113000_auction_benchmark_3drones.csv   # One-row run summary
```

Example analysis:
```python
import json
import pandas as pd

# Load events
events = [json.loads(line) for line in open('experiment_events.jsonl')]
assignments = [e for e in events if e['event_type'] == 'task_assigned']

# Load drone states
states = pd.read_csv('drone_states.csv')
```

## ROS 2 Topics

| Topic | Type | Direction | Purpose |
|---|---|---|---|
| `/ground_station/mission` | `patrol_msgs/Mission` | Coordinator → Controllers | Mission dispatch |
| `/ground_station/drone_state` | `patrol_msgs/DroneState` | Controllers → All | Drone telemetry (100ms) |
| `/swarm/task_bid` | `patrol_msgs/TaskBid` | Controllers → All | Auction bids |
| `/swarm/task_assignment` | `patrol_msgs/TaskAssignment` | Auctioneer → All | Task assignments |
| `/swarm/movement_command` | `patrol_msgs/MovementCommand` | Coordinator → Controllers | APF position setpoints (factory frame), external nav mode only |
| `/ground_station/swarm_status` | `patrol_msgs/SwarmStatus` | Drone 0 → All | Swarm alerts |
| `/experiment/events` | `patrol_msgs/ExperimentEvent` | Coordinator, Controllers → Metrics | Experiment events (controllers publish `task_completed` only) |

## Known Issues

1. **Drone instability**: Occasionally one PX4 SITL instance may crash or become unresponsive. This is a known PX4 SITL behavior preserved from the original implementation. The swarm handles this via heartbeat timeout + task reassignment.
2. **PSO not implemented**: `auction` and `apf` are functional. Selecting `pso` reports "not implemented".
3. **Auction runs in C controller**: The `auction` algorithm runs natively inside the C patrol controller (Drone 0 as auctioneer). The Python coordinator node is passive when `algorithm=auction`. With `algorithm=apf` the same native auction still allocates tasks, and the coordinator additionally computes and publishes movement commands (see [APF](#artificial-potential-field-apf)).
4. **MicroXRCEAgent**: Must be running before PX4 instances start. The scripts auto-start it if not found.

## Existing Auction Algorithm

The baseline auction algorithm is a centralized single-round market-based allocation:

**Cost function**:
```
cost(d, t) = EuclideanDistance(d, t) + 15 × N_assigned(d) + 0.2 × (100 − battery(d))
```

**Allocation**: Greedy sequential — for each unassigned task, find the lowest-cost healthy drone (with cap: `max_per_drone = ceil(tasks / healthy_drones)`).

**Features**: Continuous patrol looping, heartbeat-based failure detection (5s timeout), automatic task reassignment on drone failure, low battery return-to-base.

See `algorithm_explainer.md` for a detailed technical breakdown.

## Artificial Potential Field (APF)

APF is the behaviour-based coordination baseline. It is **reactive movement coordination**:
each drone is pulled toward its current patrol goal and pushed away from nearby factory
obstacles and nearby drones. It does not allocate tasks.

```bash
./scripts/start_experiment.sh --algorithm apf --drones 3
```

### Task/goal handling

Task allocation is unchanged. The native auction in the patrol controllers assigns zones, and
each controller loops its zones exactly as in `auction` mode. The only difference is **how a drone
flies between tasks**:

| Phase | `auction` (controller nav mode `internal`) | `apf` (controller nav mode `external`) |
|---|---|---|
| Allocation | native auction | native auction (same code) |
| Takeoff | stagger, climb to per-drone transit layer | same stagger, vertical climb to the task altitude |
| Transit | via centre corridor (0,0) on per-drone altitude layers + proximity hold | **APF** MovementCommands |
| Arrival | 3D distance to task < `WAYPOINT_RADIUS` (1.2 m) | same |
| Inspection | hold task point, ~4 s hover (`hover_duration`) | same |
| Low battery / failure | corridor return-to-base, 5 s heartbeat timeout, reassignment | same |

Each controller publishes the task it is working on in `DroneState.current_task_id`. APF steers
each drone in state `PATROLLING` toward that task, using the same altitude rule as the controller
(task z, or the drone's patrol altitude if z ≥ -1). Controllers only accept a MovementCommand
whose `task_id` matches their current task. If commands stop arriving for 0.5 s, the controller
keeps its last setpoint, which is at most one command horizon ahead.

### Formulation

All vectors are in the common factory frame (below). The APF output is a velocity (m/s):

```
F_att   = k_att (g - p),                 saturated: |F_att| <= v_max
F_obs   = Σ_boxes   k_obs   (1/d - 1/ρ_obs)   (1/d²) n     for d < ρ_obs     (0 otherwise)
F_drone = Σ_drones  k_drone (1/d - 1/ρ_drone) (1/d²) n     for d < ρ_drone   (0 otherwise)

F_total = F_att + F_obs + F_drone
v       = (1 - a) F_total + a v_prev,   then |v| <= v_max      (a = velocity_smoothing)
target  = p + v · T_h                                          (T_h = command_horizon)
```

- **Attraction**: this is the gradient of the combined quadratic/conic potential. Near the goal,
  speed is proportional to the distance (k_att = 0.5 /s). Beyond `v_max/k_att` = 3 m, speed is
  constant at `v_max`.
- **Obstacle repulsion**: this is Khatib's FIRAS gradient. `d` is the distance from the drone to
  the **closest point of the box**, and `n` is the unit vector from that point to the drone. The
  force is summed over every box within `ρ_obs`. If the drone is inside a box (`d = 0`), `n` is the
  outward normal of the nearest face.
- **Drone repulsion**: this is the same Khatib law between drone centres, in full 3D. Only
  *active* drones participate: `drone_id < num_drones` (spawned), a DroneState heard within the
  last 5 s (the controllers' heartbeat timeout), and state ≠ FAILED. Phantom, silent and failed
  drones are therefore never neighbours. Low-battery drones that are `RETURNING` are still
  airborne, so they remain neighbours.
- **Numerics**: `d` is floored at `min_distance` (0.1 m) inside the repulsion terms, so `d ≈ 0` is
  safe. Coincident drones are separated along ±x (deterministically, in opposite directions for the
  pair). A non-finite result is replaced by zero velocity, and the controller also rejects
  non-finite commands.
- **Goal capture**: within `goal_tolerance` of the goal, the command is the goal itself and
  repulsion is ignored. Once the controller detects arrival it holds the exact task point while
  inspecting, so residual repulsion cannot make the drone oscillate around the goal.
- **Command**: the controller tracks `target` with PX4 offboard *position* control, so PX4's own
  position loop is the low-level tracker. APF never talks to PX4.

### Parameters (`config/algorithms/apf.yaml`)

| Parameter | Default | Meaning / origin |
|---|---|---|
| `goal_gain` | 0.5 | k_att (C++ reference `k_position`) |
| `max_velocity` | 1.5 m/s | cap on attraction and on the command (C++ reference `max_vel`) |
| `obstacle_repulsion_gain` | 0.5 | k_obs |
| `obstacle_influence_radius` | 1.5 m | ρ_obs (Python reference `REPULSE_RANGE` law, scaled from 0.4 m/s to 1.5 m/s) |
| `drone_repulsion_gain` | 10.0 | k_drone (balances full attraction at ~1.5 m separation) |
| `drone_influence_radius` | 3.0 m | ρ_drone (C++ reference `safe_distance`) |
| `goal_tolerance` | 1.2 m | capture radius (= controller `WAYPOINT_RADIUS`, the arrival criterion for all algorithms) |
| `min_distance` | 0.1 m | distance floor in repulsion terms |
| `velocity_smoothing` | 0.2 | weight of previous command (C++ reference damping) |
| `command_horizon` | 1.0 s | setpoint look-ahead |
| `update_rate_hz` | 10 Hz | APF loop rate (telemetry rate is 10 Hz) |
| `heartbeat_timeout` | 5.0 s | neighbour liveness (= controller failure timeout) |
| `diagnostics_interval`, `stall_speed`, `stall_time` | 1 s, 0.1 m/s, 5 s | diagnostics only |

The parameters are the same for every scenario. To override one for a sensitivity experiment,
pass it as a ROS parameter on the coordinator (use a float literal), e.g.
`ros2 run patrol_coordinator coordinator_node --ros-args -p algorithm:=apf -p apf.goal_gain:=0.7`.
The values actually used are recorded in the `mission_started` event (`algorithm_params`).

### Obstacle representation

`config/environment/factory_obstacles.yaml` lists 18 axis-aligned boxes: floor, ceiling barrier,
4 walls, the central partition, 4 rack rows, the loading dock, and the machines/stations. They
mirror the `<collision>` boxes of `worlds/factory.sdf` (no model is rotated). The only conversion
is `z_factory = -z_gazebo` for box centres. The 2 cm floor markings are omitted. Scenarios reference
the file through `simulation.obstacles_file`, so every algorithm gets the same geometry. No
perception is involved, and Gazebo is not queried.

### Coordinate frame

APF consumes the corrected drone state from `/ground_station/drone_state` directly. That state is in
the common factory frame: x = Gazebo X (east), y = Gazebo Y (north), z = -height (negative = above
ground), the same frame as the task files. APF performs no NED conversion and no spawn offset. The
single PX4 conversion stays in the patrol controller, where it already existed.

**The simulation supplies drone positions directly through simulated PX4 telemetry. No physical
localization sensors (GPS, UWB, LiDAR, cameras, SLAM, tags) are modelled.** All algorithms are
compared under identical simulated state information.

### Diagnostics (`experiment_events.jsonl`)

- `apf_diagnostics` (1 Hz per commanded drone): `task_id`, `goal_distance`, `f_att`, `f_obs`,
  `f_drone`, `f_total` (magnitudes, m/s), `nearest_obstacle`, `nearest_drone`
- `apf_clearance` (1 Hz): active drone set, plus the minimum inter-drone separation and minimum
  obstacle clearance seen at 10 Hz since the previous event
- `apf_stall`: emitted once per goal when a drone stays below `stall_speed` outside
  `goal_tolerance` for `stall_time` (an APF local minimum)

### Unit tests

```bash
cd factory_patrol_ws/src/patrol_coordinator && python3 -m pytest test -q
```

### Limitations

- Classic APF local minima are not escaped. Examples are a head-on meeting at exactly the same
  altitude, or a goal shadowed by an obstacle. `apf_stall` records such events instead of hiding
  them.
- Clearance is reactive. With the default gains at 1.5 m/s, flying 0.2–0.5 m over the 3.5 m
  rack/partition tops (as the task altitudes require), measured clearance from obstacle surfaces
  goes down to ~0.3 m (drone centre).
- APF flights are capped at 1.5 m/s. `auction` transit has no explicit cap (PX4 limits, ~3 m/s
  median). Time-based metrics therefore reflect this speed difference.
