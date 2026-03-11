#!/usr/bin/env bash
# Create a clean ROS2 (Humble) workspace under dev/turtlebot3/ros2_ws
# Idempotent: safe to run multiple times. Does not modify /home/yiyuchenhu/turtlebot3_ws

set -e

REPO_PATH="/home/yiyuchenhu/Desktop/2026spring/CINQ389/Code_repo/quadruped-semantic-navigation/dev/turtlebot3"
WORKSPACE_ROOT="${REPO_PATH}/ros2_ws"
LEGACY_WS="/home/yiyuchenhu/turtlebot3_ws"

echo "=== ROS2 workspace setup (turtlebot3/ros2_ws) ==="
echo "Workspace root: ${WORKSPACE_ROOT}"
echo "Legacy workspace (unchanged): ${LEGACY_WS}"
echo ""

# 1. Create ros2_ws and src only
echo "[1/4] Creating workspace directories..."
mkdir -p "${WORKSPACE_ROOT}/src"
echo "  Created: ros2_ws/, ros2_ws/src/"
echo ""

# 2. Verify ROS2 Humble
echo "[2/4] Verifying ROS2 Humble..."
if [ ! -f /opt/ros/humble/setup.bash ]; then
  echo "  ERROR: ROS2 Humble not found at /opt/ros/humble. Install it first."
  exit 1
fi
# Source and check
source /opt/ros/humble/setup.bash
if [ -z "${ROS_DISTRO}" ]; then
  echo "  ERROR: ROS_DISTRO not set after sourcing Humble."
  exit 1
fi
if [ "${ROS_DISTRO}" != "humble" ]; then
  echo "  ERROR: Expected ROS_DISTRO=humble, got ${ROS_DISTRO}."
  exit 1
fi
echo "  OK: ROS2 Humble is available (ROS_DISTRO=${ROS_DISTRO})"
echo ""

# 3. Generate build/install/log via colcon
echo "[3/4] Running colcon to create build/, install/, log/..."
cd "${WORKSPACE_ROOT}"
colcon build --symlink-install
echo "  Done: build/, install/, log/ created by colcon."
echo ""

# 4. Print workspace structure
echo "[4/4] Workspace structure:"
echo ""
if command -v tree &>/dev/null; then
  tree -L 2 "${WORKSPACE_ROOT}" || true
else
  find "${WORKSPACE_ROOT}" -maxdepth 2 -type d | sort
fi
echo ""
echo "=== Setup complete. To use this workspace:"
echo "  source ${WORKSPACE_ROOT}/install/setup.bash"
echo ""
