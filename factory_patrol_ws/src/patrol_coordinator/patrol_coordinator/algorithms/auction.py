"""Auction-based coordination algorithm.

This is a PASSTHROUGH implementation. The actual auction algorithm runs
natively inside the C patrol controller (Drone 0 acts as auctioneer).

This stub exists so the framework can treat 'auction' as a valid algorithm
selection. When algorithm='auction':

1. The coordinator node publishes the mission to /ground_station/mission
2. Each C controller computes its own bids and publishes to /swarm/task_bid  
3. Drone 0's C controller runs auction_run_allocation() and publishes
   to /swarm/task_assignment
4. This Python class does NOT interfere — compute() returns empty results

The auction cost function is:
    cost(d,t) = EuclideanDistance(d,t) + 15*N_assigned(d) + 0.2*(100-battery(d))

See auction_logic.c for the complete implementation.
"""

from patrol_coordinator.algorithm_base import (
    CoordinationAlgorithm, AlgorithmResult, TaskInfo
)


class AuctionAlgorithm(CoordinationAlgorithm):
    """Passthrough for the native C auction algorithm."""

    def get_name(self) -> str:
        return "auction (native C)"

    def initialize(self, num_drones: int, tasks: list[TaskInfo]) -> None:
        self._num_drones = num_drones
        self._tasks = list(tasks)
        # No initialization needed — C controller handles everything

    def compute(self, timestamp_ns: int) -> AlgorithmResult:
        # Auction runs in the C controller (Drone 0 auctioneer).
        # Return empty result — do not interfere.
        return AlgorithmResult()

    def reset(self) -> None:
        super().reset()
