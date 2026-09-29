"""Abstract base class for swarm coordination algorithms.

All coordination algorithms must implement this interface.
The interface is intentionally minimal — algorithms may produce
task assignments, movement targets, or both, depending on their nature.

Examples:
    - Auction produces task-to-drone assignments
    - PSO may produce optimized task-to-drone mappings
    - APF may produce local movement/velocity commands

The coordinator node handles adapting algorithm outputs to drive
the patrol controller layer.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DroneState:
    """Snapshot of a single drone's state."""
    drone_id: int
    x: float
    y: float
    z: float
    battery_level: float
    state: int  # 0=IDLE, 1=PATROLLING, 2=INSPECTING, 3=RETURNING, 4=FAILED
    timestamp_ns: int = 0
    current_task_id: int = 0  # task the drone is flying to / inspecting (0 = none)


@dataclass
class TaskInfo:
    """A patrol task / waypoint."""
    task_id: int
    x: float
    y: float
    z: float
    priority: int = 1
    inspection_type: int = 0
    hover_duration: float = 4.0
    label: str = ""


@dataclass
class TaskAssignment:
    """Output: assign a task to a drone."""
    task_id: int
    drone_id: int


@dataclass
class MovementCommand:
    """Output: direct movement target for a drone (used by reactive algorithms like APF).

    Factory frame (x = east, y = north, z = -height). task_id names the goal the command
    steers toward; the controller ignores commands for any other task.
    """
    drone_id: int
    target_x: float
    target_y: float
    target_z: float
    velocity_x: float = 0.0
    velocity_y: float = 0.0
    velocity_z: float = 0.0
    task_id: int = 0


@dataclass
class AlgorithmResult:
    """Combined output from a coordination step.
    
    Algorithms fill in whichever fields are applicable:
    - Task-based algorithms (auction, PSO) fill assignments
    - Reactive algorithms (APF) fill movement_commands
    - Hybrid algorithms may fill both
    """
    assignments: list[TaskAssignment] = field(default_factory=list)
    movement_commands: list[MovementCommand] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)  # Algorithm-specific data for metrics.
    # metadata['events'] may hold (event_type, data) tuples; the coordinator emits them as experiment events.


class CoordinationAlgorithm(ABC):
    """Abstract base class for swarm coordination algorithms.
    
    Lifecycle:
        1. __init__(config) — receive experiment configuration
        2. initialize(num_drones, tasks) — set up with drone count and task list
        3. update_drone_state(state) — called whenever drone telemetry arrives
        4. compute(timestamp_ns) — run one coordination step, return results
        5. reset() — reset for a new experiment run
    
    The coordinator node calls these methods. Algorithms should NOT
    directly publish ROS messages or interact with PX4.
    """

    def __init__(self, config: dict):
        """Initialize with experiment configuration.
        
        Args:
            config: Dictionary from the scenario config (config/experiments/<scenario>.yaml)
        """
        self._config = config

    @abstractmethod
    def get_name(self) -> str:
        """Return the algorithm's display name."""
        ...

    @abstractmethod
    def initialize(self, num_drones: int, tasks: list[TaskInfo]) -> None:
        """Set up the algorithm with the drone count and task list.
        
        Called once before the coordination loop begins.
        """
        ...

    def update_drone_state(self, state: DroneState) -> None:
        """Update the algorithm's knowledge of a drone's state.
        
        Called whenever new telemetry arrives. Default implementation
        stores states in self._drone_states dict.
        """
        if not hasattr(self, '_drone_states'):
            self._drone_states: dict[int, DroneState] = {}
        self._drone_states[state.drone_id] = state

    def update_tasks(self, tasks: list[TaskInfo]) -> None:
        """Update the task list (e.g., when tasks are added/removed dynamically).
        
        Default implementation stores in self._tasks.
        """
        if not hasattr(self, '_tasks'):
            self._tasks: list[TaskInfo] = []
        self._tasks = list(tasks)

    @abstractmethod
    def compute(self, timestamp_ns: int) -> AlgorithmResult:
        """Run one coordination step.
        
        This is the core algorithm method. Called periodically by the
        coordinator node. Should return task assignments and/or movement
        commands.
        
        Args:
            timestamp_ns: Current ROS time in nanoseconds
            
        Returns:
            AlgorithmResult with assignments and/or movement commands
        """
        ...

    def get_update_period(self) -> float:
        """Seconds between compute() calls (coordinator timer period)."""
        return 0.5

    def uses_external_navigation(self) -> bool:
        """True if the algorithm drives transit through MovementCommands.

        The patrol controllers must then be started in 'external' navigation mode
        (scripts/start_experiment.sh does this automatically).
        """
        return False

    def reset(self) -> None:
        """Reset algorithm state for a new experiment run.
        
        Default implementation clears drone states and tasks.
        """
        if hasattr(self, '_drone_states'):
            self._drone_states.clear()
        if hasattr(self, '_tasks'):
            self._tasks.clear()

    def on_task_completed(self, task_id: int, drone_id: int) -> None:
        """Optional hook: called when a task is completed."""
        pass

    def on_drone_failed(self, drone_id: int) -> None:
        """Optional hook: called when a drone fails."""
        pass

    def get_metrics(self) -> dict:
        """Optional: return algorithm-specific metrics for logging."""
        return {}
