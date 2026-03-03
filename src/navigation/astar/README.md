# A* Path Planning

A* algorithm implementation for global path planning.

## Input/Output

- **Input**: 
  - Start position: `(x, y, theta)`
  - Goal position: `(x, y, theta)`
  - Occupancy grid map: `numpy.ndarray` (0=free, 1=occupied)
  
- **Output**: 
  - Path: `List[Tuple[float, float, float]]` (list of waypoints)

## Example

```python
from src.navigation.astar import AStarPlanner

planner = AStarPlanner()
path = planner.plan(start=(0, 0, 0), goal=(10, 10, 0), map=occupancy_map)
```
