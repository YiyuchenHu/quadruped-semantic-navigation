# YOLOv5 Real-Time Detection Demo

This demo demonstrates real-time object detection using YOLOv5 TensorFlow Lite models on Raspberry Pi with camera input.

## Prerequisites

- Raspberry Pi 4 with camera module
- Picamera2 library (patched version)
- TensorFlow Lite runtime
- YOLOv5 TFLite model file

## Setup

1. Ensure upstream dependencies are fetched and patched:
   ```bash
   ./scripts/setup_rpi.sh
   ```

2. Download YOLOv5 TFLite model:
   ```bash
   cd models
   # Download appropriate .tflite model file
   # Example: yolov5s-int8.tflite
   ```

## Usage

### Basic Usage
```bash
python yolo_v5_real_time_with_labels.py
```

### With Custom Model
```bash
python yolo_v5_real_time_with_labels.py --model models/yolov5s-int8.tflite
```

### With Custom Resolution
```bash
python yolo_v5_real_time_with_labels.py --width 640 --height 480
```

## Model Files

Place your `.tflite` model files in the `models/` directory. The demo expects:
- Input: RGB image (typically 640x640)
- Output: Detection results with bounding boxes and class labels

## Notes

- This demo uses the patched Picamera2 library for camera access
- Performance depends on model size and quantization (INT8 recommended)
- For best performance, use quantized models optimized for Raspberry Pi
