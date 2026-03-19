#!/usr/bin/env python3
"""
Map-aware gating for fake semantic navigation.

Algorithm
---------
1. Subscribe to nav_msgs/OccupancyGrid (e.g. /map from SLAM).
2. For each predefined object goal (world x, y in map frame):
   - Convert (world_x, world_y) to grid indices (col, row) using:
     grid_x = (world_x - origin.x) / resolution
     grid_y = (world_y - origin.y) / resolution
   - Clamp indices to [0, width-1] and [0, height-1].
   - Index into data: cell = data[row * width + col].
3. OccupancyGrid semantics:
   - -1 = unknown (unexplored)
   - 0 = free
   - 100 = occupied
4. If cell != -1, the cell is "known" (explored); mark object as available.
5. If cell == -1, the region is still unknown; reject the navigation request.

Assumptions
-----------
- Semantic goal poses use the same frame_id as the map (typically "map").
- Map is 2D; goal z is ignored for gating (only x, y are used).
- Map origin and resolution are in the same units as semantic_goals (meters).
- We gate on a single cell at the goal point (no inflation or radius).

Limitations
-----------
- Single-cell check: no safety margin; goal could be right at an obstacle edge.
- No temporal smoothing: we do not require "known for N seconds".
- Race condition: map can change between check and Nav2 execution (acceptable for prototype).
- If no map has been received yet, the implementation should treat as "unknown" (reject).
"""

from typing import Tuple


def world_to_grid(
    world_x: float,
    world_y: float,
    resolution: float,
    origin_x: float,
    origin_y: float,
) -> Tuple[int, int]:
    """
    Convert world coordinates (meters, map frame) to grid cell indices.

    Args:
        world_x, world_y: Position in map frame (m).
        resolution: Map resolution (m/cell).
        origin_x, origin_y: Map origin in world coordinates (m).

    Returns:
        (grid_x, grid_y) as integers (column, row). Not clamped; caller may clamp to map bounds.
    """
    if resolution <= 0.0:
        raise ValueError("resolution must be positive")
    grid_x = int((world_x - origin_x) / resolution)
    grid_y = int((world_y - origin_y) / resolution)
    return (grid_x, grid_y)


def is_cell_known(
    data: list,
    width: int,
    height: int,
    grid_x: int,
    grid_y: int,
) -> bool:
    """
    Return True if the grid cell at (grid_x, grid_y) is known (not unknown).

    OccupancyGrid: -1 = unknown, 0 = free, 100 = occupied. Any value other than -1 is "known".

    Args:
        data: Flat list of cell values (row-major: index = row * width + col).
        width, height: Map dimensions in cells.
        grid_x, grid_y: Column and row indices (can be out of bounds).

    Returns:
        True if the cell is within bounds and its value is not -1 (unknown).
        False if out of bounds or cell value is -1.
    """
    if grid_x < 0 or grid_x >= width or grid_y < 0 or grid_y >= height:
        return False
    idx = grid_y * width + grid_x
    if idx < 0 or idx >= len(data):
        return False
    return data[idx] != -1


def is_goal_known_in_map(
    occupancy_grid,  # nav_msgs.msg.OccupancyGrid
    world_x: float,
    world_y: float,
) -> bool:
    """
    Return True if the world position (world_x, world_y) lies in a known (explored) map cell.

    Uses the grid's resolution and origin from occupancy_grid.info.
    Out-of-bounds cells are treated as not known.

    Args:
        occupancy_grid: nav_msgs.msg.OccupancyGrid (has .info and .data).
        world_x, world_y: Position in the same frame as the map (m).

    Returns:
        True if the corresponding cell is within map bounds and is not unknown (-1).
    """
    info = occupancy_grid.info
    resolution = info.resolution
    origin_x = info.origin.position.x
    origin_y = info.origin.position.y
    width = info.width
    height = info.height
    gx, gy = world_to_grid(world_x, world_y, resolution, origin_x, origin_y)
    return is_cell_known(list(occupancy_grid.data), width, height, gx, gy)
