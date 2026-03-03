# Quick Start Guide

## Prerequisites

- Raspberry Pi 4 (8GB recommended) running Raspberry Pi OS Bookworm
- Camera module (Pi Camera v2 or v3)
- Optional: TurtleBot3 or Unitree Go2 for full navigation stack

## Installation Steps

### 1. Clone the Repository

```bash
git clone <repository-url>
cd quadruped-semantic-navigation
```

### 2. Run Setup Script

The setup script will automatically:
- Clone upstream repositories
- Apply necessary patches
- Install dependencies
- Set up demo environments

```bash
chmod +x scripts/setup_rpi.sh
./scripts/setup_rpi.sh
```

### 3. Run YOLOv5 Demo

```bash
cd demos/rpi_yolov5_tflite
python yolo_v5_real_time_with_labels.py
```

## Manual Setup (Alternative)

If you prefer manual setup:

1. **Fetch upstream dependencies**:
   ```bash
   ./scripts/fetch_picamera2.sh
   ```

2. **Apply patches**:
   ```bash
   ./scripts/apply_patches_picamera2.sh
   ```

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Next Steps

- Read [Hardware Setup](02-hardware.md) for detailed hardware configuration
- Check [Software Stack](03-software-stack.md) for component versions
- Explore `src/` directory for core algorithm implementations
