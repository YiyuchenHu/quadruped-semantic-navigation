# Setup and Execution Scripts

This directory contains shell scripts for automated setup and execution.

## Purpose

Scripts automate:
- Environment setup
- Upstream dependency fetching
- Patch application
- Demo execution

## Scripts

- `setup_rpi.sh` - One-click setup for Raspberry Pi (fetches dependencies, applies patches, installs packages)
- `fetch_picamera2.sh` - Clone/update Picamera2 upstream repository
- `apply_patches_picamera2.sh` - Apply patches to Picamera2
- `run_yolo_demo.sh` - Run YOLOv5 detection demo

## Usage

Make scripts executable and run:

```bash
chmod +x scripts/*.sh
./scripts/setup_rpi.sh
```
