# YOLOv8nano Demo — Usage Guide

Real-time object detection using YOLOv8nano on Raspberry Pi 4 small car platform via MJPEG HTTP server.

## Demo Video

[Demo video](https://drive.google.com/file/d/1nYlZcVOUjUOCVYoeJ4OVAHvZrnRQvLq0/view?usp=sharing) Google Drive

## Quick Start

```bash
# From repo root
cd demos/smallcar_yolov8nano
source venv/bin/activate
python3 yolov8_mjpeg_server.py
```

Open browser: `http://<pi-ip>:8080/` (find IP with `hostname -I` on Pi)

👉 [Installation guide](./setup.md)

## Smoke Test (No GUI)

```bash
cd demos/smallcar_yolov8nano
source venv/bin/activate
python3 yolov8_smoketest_no_gui.py
```

Expected output: `frame 0: detections=3`, `frame 1: detections=2`, etc.

## Expected Performance

**320×240 @ imgsz=320:**
- FPS: ~10-15
- CPU: 40-60%
- Memory: ~150-200 MB

## Parameter Tuning

Edit `yolov8_mjpeg_server.py`:

| Parameter | Default | Suggested Values | Notes |
|-----------|---------|------------------|-------|
| `FRAME_W, FRAME_H` | 640, 480 | 320, 240 | Lower = faster |
| `IMG_SIZE` | 320 | 224, 256, 320, 416 | Lower = faster |
| `CONF_THRES` | 0.4 | 0.3-0.5 | Higher = fewer false positives |
| `JPEG_QUALITY` | 80 | 60-80 | Lower = faster transmission |
| `TARGET_FPS` | 10 | 5-10 | 0 = unlimited |

**If too slow:** Reduce resolution to 320×240, set `IMG_SIZE=224`, `TARGET_FPS=5`

**If too many false positives:** Increase `CONF_THRES` to 0.5

**If missing detections:** Decrease `CONF_THRES` to 0.3, increase `IMG_SIZE` to 416

## Files

- `yolov8_mjpeg_server.py` - MJPEG HTTP server with detection overlay
- `yolov8_smoketest_no_gui.py` - Quick verification script (no GUI)
- `dev/yolov8n_picam2_smoketest.py` - Additional smoke test script
- `setup.md` - Installation and setup instructions

## Report Template

| resolution (WxH) | imgsz | conf | jpeg_quality | target_fps | observed_fps | cpu | mem | notes |
|------------------|-------|------|--------------|------------|--------------|-----|-----|-------|
|                  |       |      |              |            |              |     |     |       |
