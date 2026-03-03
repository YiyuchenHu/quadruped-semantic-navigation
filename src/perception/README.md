# Perception Module

This module contains perception algorithms for object detection, tracking, and scene understanding.

## Structure

- `detectors/`: Object detection implementations
- `tracking/`: Multi-object tracking

## Input/Output Conventions

### Object Detection
- **Input**: Image frame: `numpy.ndarray`
- **Output**: Detections: `List[Dict]` with keys: `bbox`, `class_id`, `confidence`

### Tracking
- **Input**: Current detections, previous tracks
- **Output**: Updated tracks with IDs

## Usage

See individual subdirectory READMEs for detailed usage.
