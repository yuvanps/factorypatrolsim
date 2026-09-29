"""Particle Swarm Optimization coordination algorithm.

STATUS: Not yet implemented — placeholder stub.

PSO will optimize task-to-drone assignment by treating the assignment
problem as a particle swarm optimization. Each particle represents a
complete assignment mapping, and the swarm converges on the globally
optimal assignment.

When implemented, this algorithm will:
1. Receive drone states and task list
2. Run PSO iterations to find optimal assignment
3. Return task assignments via AlgorithmResult.assignments
"""

from patrol_coordinator.algorithm_base import (
    CoordinationAlgorithm, AlgorithmResult, TaskInfo
)


class PSOAlgorithm(CoordinationAlgorithm):
    """Particle Swarm Optimization for task allocation (NOT YET IMPLEMENTED)."""

    def get_name(self) -> str:
        return "PSO (stub — not implemented)"

    def initialize(self, num_drones: int, tasks: list[TaskInfo]) -> None:
        self._num_drones = num_drones
        self._tasks = list(tasks)
        raise NotImplementedError(
            "PSO algorithm is not yet implemented. "
            "To implement: subclass CoordinationAlgorithm in this file, "
            "implement compute() to run PSO iterations and return TaskAssignments."
        )

    def compute(self, timestamp_ns: int) -> AlgorithmResult:
        raise NotImplementedError("PSO algorithm is not yet implemented.")

    def reset(self) -> None:
        super().reset()
