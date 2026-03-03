# YOLOv8nano Demo — Usage Guide

This demo provides real-time object detection using YOLOv8nano on Raspberry Pi 4 small car platform. The demo streams detection results via MJPEG HTTP server, avoiding GUI dependencies and VNC latency issues.

## Demo Video

📹 [Watch Demo Video](./video/2026.3.2.-YOLOV8%20Nano%20in%20small%20car-demo.mp4)

## What This Demo Does

**Purpose:**
Visual confirmation that YOLOv8nano runs successfully on the small car hardware. This is a **visual demo stage** to validate the detection pipeline before integrating with car control logic.

**YOLOv8n vs YOLOv5 TFLite Tradeoff:**

- **YOLOv8n**: Generally heavier on compute, but provides better accuracy and more flexible model options. Memory usage can be optimized through resolution and inference size tuning.
- **YOLOv5 TFLite**: Lighter weight, but requires model conversion and may have accuracy tradeoffs.
- **Main Risk**: Compute performance on Pi 4. If too slow, reduce resolution (`320×240`) or inference size (`imgsz=320`).

**Current Stage:**

- ✅ Visual demo (detection + MJPEG streaming)
- ⏳ Future: Use detections to control car movement

## Quick Start

👉 [For installation and environment setup, click here to jump to setup.md.](./setup.md)


### 1. Activate Virtual Environment

```bash
cd demos/smallcar_yolov8nano
source venv/bin/activate
```

### 2. Run MJPEG Server

```bash
python3 yolov8_mjpeg_server.py
```

Expected output:

```
[INFO] Server running: http://0.0.0.0:8080/
[INFO] Open from your laptop: http://<pi-ip>:8080/
[INFO] Ctrl+C to stop.
```

### 3. Open Browser

**Find Pi IP Address:**

```bash
# Run on Raspberry Pi (not macOS)
hostname -I
# Example output: 192.168.1.100
```

**Access Stream:**
Open browser on your laptop/desktop:

```
http://192.168.1.100:8080/
```

Replace `192.168.1.100` with your Pi's actual IP address.

## Smoke Test (No GUI)

For quick verification without browser access:

```bash
source venv/bin/activate
python3 yolov8_smoketest_no_gui.py
```

This script:

- Captures 20 frames
- Runs YOLOv8n inference
- Prints detection counts per frame
- No GUI or network required

Expected output:

```
frame 0: detections=3
frame 1: detections=2
frame 2: detections=1
...
```

## Configuration Parameters

### Default Settings

The MJPEG server uses these defaults (defined in `yolov8_mjpeg_server.py`):

```python
FRAME_W, FRAME_H = 640, 480    # Camera resolution
IMG_SIZE = 320                  # Model inference size
CONF_THRES = 0.4                # Confidence threshold
PORT = 8080                     # HTTP server port
JPEG_QUALITY = 80               # JPEG compression (1-100)
TARGET_FPS = 10                 # Soft FPS cap (0 = unlimited)
```

### Tuning Parameters

**If Too Slow:**

1. **Reduce Resolution:**
  ```python
   FRAME_W, FRAME_H = 320, 240  # Change in script
  ```
2. **Reduce Inference Size:**
  ```python
   IMG_SIZE = 320  # Try 224 or 256 for faster inference
  ```
3. **Reduce JPEG Quality:**
  ```python
   JPEG_QUALITY = 60  # Lower = smaller/faster transmission
  ```
4. **Cap FPS:**
  ```python
   TARGET_FPS = 5  # Limit to 5 FPS
  ```

**If Too Many False Positives:**

```python
CONF_THRES = 0.5  # Increase threshold (0.0-1.0)
```

**If Missing Detections:**

```python
CONF_THRES = 0.3  # Decrease threshold
IMG_SIZE = 416    # Increase inference size (slower)
```

## Performance Notes

### Expected Performance (Pi 4 Model B, 4GB)

**640×480 @ imgsz=320:**

- FPS: ~5-10 (depending on scene complexity)
- CPU: 60-80%
- Memory: ~200-300 MB

**320×240 @ imgsz=320:**

- FPS: ~10-15
- CPU: 40-60%
- Memory: ~150-200 MB

### Optimization Tips

1. **Use Lower Resolution:**
  - 320×240 provides good detection quality with better performance
  - 640×480 is only needed for distant objects
2. **Reduce Inference Size:**
  - `imgsz=320` is a good balance
  - `imgsz=224` is faster but may miss small objects
  - `imgsz=416` is more accurate but slower
3. **Adjust JPEG Quality:**
  - Quality 80: Good balance
  - Quality 60: Faster transmission, slight quality loss
  - Quality 40: Fastest, noticeable compression artifacts
4. **Cap FPS:**
  - Set `TARGET_FPS = 5` for consistent performance
  - Set `TARGET_FPS = 0` for maximum speed (may be unstable)
5. **Close Background Processes:**
  ```bash
   # Check running processes
   top
   # Kill unnecessary services if needed
  ```

## Finding Pi IP Address

**On Raspberry Pi:**

```bash
hostname -I
# Example: 192.168.1.100
```

**From Another Device (same network):**

```bash
# macOS/Linux
arp -a | grep raspberrypi

# Or scan network (if nmap installed)
nmap -sn 192.168.1.0/24 | grep -B 2 "Raspberry"
```

**Note:** The IP address shown by `hostname -I` on the Pi is the correct one to use. Do not use the IP from macOS `ifconfig` or other devices.

## Troubleshooting

### Server Starts But Browser Shows Nothing

1. **Check Firewall:**
  ```bash
   sudo ufw status
   # If active, allow port 8080:
   sudo ufw allow 8080
  ```
2. **Verify Server is Running:**
  ```bash
   # On Pi
   netstat -tlnp | grep 8080
   # Should show Python process listening
  ```
3. **Test from Pi:**
  ```bash
   curl http://localhost:8080/
   # Should return HTML
  ```

### Low FPS / High CPU

- Reduce resolution to 320×240
- Reduce `IMG_SIZE` to 224
- Set `TARGET_FPS = 5`
- Lower `JPEG_QUALITY` to 60

### Model Download Fails

The script auto-downloads `yolov8n.pt` on first run. If download fails:

```bash
# Manual download
wget https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n.pt
mv yolov8n.pt ~/.ultralytics/weights/
```

### Connection Refused

- Ensure Pi and laptop are on same network
- Verify IP address with `hostname -I` on Pi
- Check server is running (should show `[INFO]` messages)

## Next Steps

Once visual demo is stable:

1. **Integrate with Car Control:**
  - Parse detection results (`results[0].boxes`)
  - Implement obstacle avoidance logic
  - Control motors based on detections
2. **Optimize for Real-Time:**
  - Fine-tune resolution and inference size
  - Implement detection filtering (e.g., ignore distant objects)
  - Add detection tracking to reduce computation
3. **Add Features:**
  - Multiple model support (switch between yolov8n/yolov8s)
  - Detection logging/recording
  - Web interface for parameter tuning

## Files

- `yolov8_mjpeg_server.py` - MJPEG HTTP server with detection overlay
- `yolov8_smoketest_no_gui.py` - Quick verification script (no GUI)
- `setup.md` - Installation and setup instructions

