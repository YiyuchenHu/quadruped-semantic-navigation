# Local Planner

Local path planning and obstacle avoidance for real-time navigation.

## Input/Output

- **Input**:
  - Current pose: `(x, y, theta)`
  - Target waypoint: `(x, y)`
  - Obstacle data: `List[Tuple[float, float]]` (obstacle positions)
  - Sensor readings: `Dict` (LiDAR, camera, etc.)
  
- **Output**:
  - Velocity command: `(linear_velocity, angular_velocity)`

## Example

```python
from src.navigation.local_planner import LocalPlanner

planner = LocalPlanner()
cmd = planner.compute_velocity(
    current_pose=(0, 0, 0),
    target=(5, 5),
    obstacles=obstacle_list
)
```
