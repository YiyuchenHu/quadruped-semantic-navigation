# Object Detectors

Object detection implementations for various models (YOLO, etc.).

## Input/Output

- **Input**:
  - Image: `numpy.ndarray` (BGR or RGB, HxWx3)
  - Model configuration: `Dict` (optional)
  
- **Output**:
  - Detections: `List[Dict]` where each dict contains:
    - `bbox`: `[x1, y1, x2, y2]` or `[x, y, w, h]`
    - `class_id`: `int`
    - `class_name`: `str`
    - `confidence`: `float`

## Example

```python
from src.perception.detectors import YOLODetector

detector = YOLODetector(model_path="models/yolov5s.tflite")
detections = detector.detect(image=frame)
```
