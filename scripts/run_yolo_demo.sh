#!/bin/bash
# Run YOLOv5 demo script
# Convenience script to run the YOLOv5 real-time detection demo

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DEMO_DIR="$REPO_ROOT/demos/rpi_yolov5_tflite"
DEMO_SCRIPT="$DEMO_DIR/yolo_v5_real_time_with_labels.py"

echo "Running YOLOv5 demo..."

# Check if demo script exists
if [ ! -f "$DEMO_SCRIPT" ]; then
    echo "Error: Demo script not found at $DEMO_SCRIPT"
    exit 1
fi

# Change to demo directory
cd "$DEMO_DIR"

# Run the demo
python3 "$DEMO_SCRIPT" "$@"
