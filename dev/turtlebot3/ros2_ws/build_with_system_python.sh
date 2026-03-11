#!/usr/bin/env bash
# Build ROS2 workspace using system Python (avoids conda 'em' module error).
# Run from anywhere; or: cd ros2_ws && ./build_with_system_python.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

# Use system Python so rosidl_adapter finds the 'em' module
export PATH="/usr/bin:${PATH}"

source /opt/ros/humble/setup.bash
colcon build --symlink-install "$@"
