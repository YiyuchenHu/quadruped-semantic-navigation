# Hardware Requirements

## Minimum Requirements

### Raspberry Pi Setup
- **Board**: Raspberry Pi 4 Model B (4GB minimum, 8GB recommended)
- **OS**: Raspberry Pi OS Bookworm (64-bit)
- **Camera**: Raspberry Pi Camera Module v2 or v3
- **Storage**: 32GB+ microSD card (Class 10 or better)
- **Power**: Official Raspberry Pi 5V/3A USB-C power supply

### Optional Hardware
- **Robot Platform**: 
  - TurtleBot3 Burger/Waffle
  - Unitree Go2
  - Custom quadruped platform
- **Sensors**:
  - LiDAR (e.g., RPLIDAR A1/A2)
  - IMU
  - Additional cameras for stereo vision

## Hardware Configuration

### Camera Setup

1. **Enable Camera Interface**:
   ```bash
   sudo raspi-config
   # Navigate to Interface Options > Camera > Enable
   ```

2. **Verify Camera**:
   ```bash
   libcamera-hello --list-cameras
   ```

### Network Configuration

For remote development:
- Enable SSH: `sudo systemctl enable ssh`
- Configure static IP (optional)
- Set up SSH keys for passwordless access

## Platform-Specific Notes

### Raspberry Pi 4
- Ensure adequate cooling (heatsink/fan recommended)
- Use official power supply to avoid throttling
- Enable GPU memory split: `gpu_mem=128` in `/boot/config.txt`

### TurtleBot3
- Follow official TurtleBot3 setup guide
- Ensure ROS 2 is properly installed
- Configure network between RPi and robot

### Unitree Go2
- Follow Unitree SDK documentation
- Configure network connection
- Set up authentication keys
