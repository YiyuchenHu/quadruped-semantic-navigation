#!/bin/bash
# One-click setup script for Raspberry Pi
# This script clones upstream repos, applies patches, and sets up the environment

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=========================================="
echo "Quadruped Semantic Navigation Setup"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running on Raspberry Pi
if [ ! -f /proc/device-tree/model ] || ! grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null; then
    echo -e "${YELLOW}Warning: This script is designed for Raspberry Pi${NC}"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Step 1: Fetch upstream dependencies
echo -e "${GREEN}[1/4] Fetching upstream dependencies...${NC}"
"$SCRIPT_DIR/fetch_picamera2.sh"

# Step 2: Apply patches
echo -e "${GREEN}[2/4] Applying patches...${NC}"
"$SCRIPT_DIR/apply_patches_picamera2.sh"

# Step 3: Install Python dependencies
echo -e "${GREEN}[3/4] Installing Python dependencies...${NC}"
if [ -f "$REPO_ROOT/requirements.txt" ]; then
    pip3 install -r "$REPO_ROOT/requirements.txt"
else
    echo -e "${YELLOW}Warning: requirements.txt not found${NC}"
    echo "Installing basic dependencies..."
    pip3 install numpy opencv-python pillow tensorflow-lite-runtime
fi

# Step 4: Verify installation
echo -e "${GREEN}[4/4] Verifying installation...${NC}"
python3 -c "import picamera2; import cv2; import numpy; print('✓ Core dependencies OK')" || {
    echo -e "${RED}Error: Some dependencies are missing${NC}"
    exit 1
}

echo ""
echo -e "${GREEN}=========================================="
echo "Setup completed successfully!"
echo "==========================================${NC}"
echo ""
echo "Next steps:"
echo "  1. Read docs/01-quickstart.md for usage"
echo "  2. Run demo: cd demos/rpi_yolov5_tflite && python yolo_v5_real_time_with_labels.py"
echo ""
