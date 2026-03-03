# Camera Mapping

Camera-based visual mapping and SLAM.

## Input/Output

- **Input**:
  - Camera image: `numpy.ndarray` (BGR or RGB)
  - Camera intrinsics: `Dict`
  - Previous map: `Dict` (optional)
  
- **Output**:
  - Feature map: `Dict` (keypoints, descriptors)
  - Pose estimate: `(x, y, theta)`

## Example

```python
from src.mapping.camera_mapping import VisualSLAM

vslam = VisualSLAM()
map, pose = vslam.update(image=camera_frame, intrinsics=camera_params)
```
