# Software Stack

## Core Dependencies

### Python Environment
- **Python**: 3.9+ (Python 3.11 recommended)
- **Package Manager**: pip or uv

### Computer Vision
- **Picamera2**: Latest (patched version, see `upstream/picamera2.version`)
- **OpenCV**: 4.8+
- **NumPy**: 1.24+
- **Pillow**: 10.0+

### Deep Learning
- **TensorFlow Lite**: 2.13+ (for YOLOv5 inference on RPi)
- **PyTorch**: Optional (for training, typically on development machine)

### Robotics (Optional)
- **ROS 2**: Humble or Iron (for TurtleBot3 integration)
- **Unitree SDK**: Latest (for Go2 integration)

## Upstream Dependencies

### Picamera2
- **Source**: https://github.com/raspberrypi/picamera2
- **Version**: See `upstream/picamera2.version`
- **Patches**: See `patches/picamera2/` and `docs/patches/picamera2.md`

### YOLOv5 Reference
- **Source**: https://github.com/ultralytics/yolov5
- **Version**: See `upstream/yolov5-demo.version` (if applicable)
- **Note**: We use TensorFlow Lite models, not the full PyTorch implementation

## Version Tracking

All upstream dependencies are tracked in `upstream/` directory:
- Each `.version` file contains the commit hash or tag that was tested
- Patches are designed to be replayable on these specific versions

## Installation

### Automated Installation
```bash
./scripts/setup_rpi.sh
```

### Manual Installation
```bash
# Install system dependencies
sudo apt update
sudo apt install -y python3-picamera2 python3-opencv python3-numpy

# Install Python packages
pip install tensorflow-lite-runtime opencv-python numpy pillow
```

## Development Environment

### Recommended Tools
- **Code Editor**: VS Code with Python extension
- **Version Control**: Git
- **Virtual Environment**: venv or uv

### Setup Development Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt  # If available
```
