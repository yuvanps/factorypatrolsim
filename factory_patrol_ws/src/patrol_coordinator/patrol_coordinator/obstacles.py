"""Static factory obstacle model shared by all coordination algorithms.

Obstacles are axis-aligned boxes described in the common factory frame
(x = Gazebo X / east, y = Gazebo Y / north, z = -height, negative = above ground),
the same frame used by DroneState and the task files. No perception is involved:
the geometry is read from a YAML file that mirrors the collision boxes of
worlds/factory.sdf, so every algorithm sees exactly the same environment.

YAML format (config/environment/factory_obstacles.yaml):

    obstacles:
      - id: rack_row_1
        type: box
        center: [x, y, z]     # factory frame
        size: [sx, sy, sz]    # full extents along x, y, z (metres)
"""

import math
from dataclasses import dataclass

import yaml


@dataclass(frozen=True)
class BoxObstacle:
    """Axis-aligned box in the factory frame."""
    obstacle_id: str
    min_corner: tuple[float, float, float]
    max_corner: tuple[float, float, float]

    @classmethod
    def from_center_size(cls, obstacle_id: str, center, size) -> 'BoxObstacle':
        half = [abs(float(s)) / 2.0 for s in size]
        c = [float(v) for v in center]
        return cls(
            obstacle_id=obstacle_id,
            min_corner=tuple(c[i] - half[i] for i in range(3)),
            max_corner=tuple(c[i] + half[i] for i in range(3)),
        )

    def closest_point(self, p) -> tuple[float, float, float]:
        """Closest point of the box (surface or interior) to p."""
        return tuple(min(max(p[i], self.min_corner[i]), self.max_corner[i]) for i in range(3))

    def outward_normal_inside(self, p) -> tuple[float, float, float]:
        """For a point inside the box: unit normal of the nearest face (the shortest way out)."""
        best_axis, best_sign, best_depth = 0, 1.0, math.inf
        for i in range(3):
            for sign, depth in ((-1.0, p[i] - self.min_corner[i]), (1.0, self.max_corner[i] - p[i])):
                if depth < best_depth:
                    best_axis, best_sign, best_depth = i, sign, depth
        n = [0.0, 0.0, 0.0]
        n[best_axis] = best_sign
        return tuple(n)


def load_obstacles(path: str) -> list[BoxObstacle]:
    """Load box obstacles from a YAML file. Raises on unknown types or malformed entries."""
    with open(path, 'r') as f:
        data = yaml.safe_load(f) or {}
    obstacles = []
    for entry in data.get('obstacles', []):
        kind = entry.get('type', 'box')
        if kind != 'box':
            raise ValueError(f"Obstacle '{entry.get('id')}': unsupported type '{kind}' (only 'box')")
        center, size = entry['center'], entry['size']
        if len(center) != 3 or len(size) != 3:
            raise ValueError(f"Obstacle '{entry.get('id')}': center and size must have 3 values")
        obstacles.append(BoxObstacle.from_center_size(str(entry['id']), center, size))
    return obstacles
