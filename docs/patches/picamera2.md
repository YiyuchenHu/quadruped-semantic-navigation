# Picamera2 Patches

## Overview

This document describes the patches applied to the upstream Picamera2 library to ensure compatibility with our quadruped navigation system.

## Upstream Version

See `upstream/picamera2.version` for the tested upstream commit hash or tag.

## Patches

### 0001-fix-compat-xxx.patch

**Purpose**: Fix compatibility issues with specific camera modules or Raspberry Pi OS versions.

**Changes**:
- [Describe specific changes]

**Verification**:
```bash
# Test camera initialization
python3 -c "from picamera2 import Picamera2; cam = Picamera2(); cam.start(); print('OK')"
```

### 0002-add-labels-xxx.patch

**Purpose**: Add support for custom metadata labels in camera frames.

**Changes**:
- [Describe specific changes]

**Verification**:
```bash
# Run demo that uses labels
cd demos/rpi_yolov5_tflite
python yolo_v5_real_time_with_labels.py
```

## Applying Patches

Patches are automatically applied by `scripts/apply_patches_picamera2.sh`. For manual application:

```bash
cd /path/to/picamera2
git apply /path/to/quadruped-semantic-navigation/patches/picamera2/*.patch
```

## Updating Patches

When upstream Picamera2 is updated:

1. Update `upstream/picamera2.version` with new commit hash
2. Test patches against new version
3. Regenerate patches if needed:
   ```bash
   cd /path/to/picamera2
   git format-patch -N <base-commit> --stdout > patches/picamera2/0001-new-patch.patch
   ```

## Troubleshooting

See [Troubleshooting Guide](../04-troubleshooting.md) for patch-related issues.
