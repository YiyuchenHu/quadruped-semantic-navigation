# Troubleshooting

## Common Issues

### Camera Not Detected

**Symptoms**: Camera initialization fails or no video feed

**Solutions**:
1. Check camera connection:
   ```bash
   libcamera-hello --list-cameras
   ```

2. Verify camera interface is enabled:
   ```bash
   sudo raspi-config
   # Interface Options > Camera > Enable
   ```

3. Check permissions:
   ```bash
   groups  # Should include 'video' group
   sudo usermod -a -G video $USER
   # Log out and log back in
   ```

### Patch Application Fails

**Symptoms**: `git apply` fails when applying patches

**Solutions**:
1. Verify upstream version matches:
   ```bash
   cat upstream/picamera2.version
   cd /path/to/picamera2
   git rev-parse HEAD
   ```

2. Check patch compatibility:
   ```bash
   git apply --check patches/picamera2/*.patch
   ```

3. Re-fetch upstream:
   ```bash
   ./scripts/fetch_picamera2.sh
   ./scripts/apply_patches_picamera2.sh
   ```

### YOLOv5 Model Not Found

**Symptoms**: FileNotFoundError when loading model

**Solutions**:
1. Check model path in demo script
2. Download model if missing:
   ```bash
   cd demos/rpi_yolov5_tflite/models
   # Download appropriate .tflite model
   ```

3. Verify model file permissions

### Performance Issues

**Symptoms**: Low FPS, high CPU usage

**Solutions**:
1. Reduce input resolution in config
2. Use quantized models (INT8)
3. Enable GPU acceleration (if available)
4. Close unnecessary background processes

### Import Errors

**Symptoms**: ModuleNotFoundError

**Solutions**:
1. Verify virtual environment is activated
2. Install missing dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Check Python path:
   ```bash
   python -c "import sys; print(sys.path)"
   ```

## Getting Help

1. Check existing patches documentation: `docs/patches/`
2. Review upstream project issues
3. Check logs in `logs/` directory (if available)
4. Open an issue with:
   - Error message
   - Steps to reproduce
   - System information (`uname -a`, Python version, etc.)
