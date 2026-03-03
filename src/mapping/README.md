# Mapping Module

This module contains mapping algorithms for building and maintaining environment maps.

## Structure

- `lidar_mapping/`: LiDAR-based mapping (SLAM)
- `camera_mapping/`: Camera-based mapping and visual SLAM

## Input/Output Conventions

### SLAM
- **Input**: Sensor data (LiDAR scans, camera images, IMU)
- **Output**: Occupancy map, pose estimate

### Visual Mapping
- **Input**: Camera images, odometry
- **Output**: Feature map, pose estimate

## Usage

See individual subdirectory READMEs for detailed usage.
