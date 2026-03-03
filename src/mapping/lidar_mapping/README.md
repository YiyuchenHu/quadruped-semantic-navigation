# LiDAR Mapping

LiDAR-based SLAM implementation for building occupancy maps.

## Input/Output

- **Input**:
  - LiDAR scan: `numpy.ndarray` (range measurements)
  - Odometry: `(x, y, theta)`
  - Previous map: `numpy.ndarray` (optional)
  
- **Output**:
  - Updated occupancy map: `numpy.ndarray`
  - Pose estimate: `(x, y, theta)`

## Example

```python
from src.mapping.lidar_mapping import LidarSLAM

slam = LidarSLAM()
map, pose = slam.update(scan=lidar_data, odom=odometry)
```
