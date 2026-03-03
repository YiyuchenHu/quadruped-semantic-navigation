# Multi-Object Tracking

Multi-object tracking implementation for maintaining object identities across frames.

## Input/Output

- **Input**:
  - Current detections: `List[Dict]` (from detector)
  - Previous tracks: `List[Dict]` (with track IDs)
  
- **Output**:
  - Updated tracks: `List[Dict]` with `track_id` field added

## Example

```python
from src.perception.tracking import MultiObjectTracker

tracker = MultiObjectTracker()
tracks = tracker.update(detections=current_detections)
```
