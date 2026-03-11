#!/usr/bin/env bash
# Read-only validation for TurtleBot3 exploration baseline. Modifies no files.

WS="/home/yiyuchenhu/Desktop/2026spring/CINQ389/Code_repo/quadruped-semantic-navigation/dev/turtlebot3/ros2_ws"

# 1. Source ROS2 Humble
if [ -f /opt/ros/humble/setup.bash ]; then
  source /opt/ros/humble/setup.bash
else
  echo "ERROR: /opt/ros/humble/setup.bash not found"
  exit 1
fi

# 2. Source workspace
if [ -f "${WS}/install/setup.bash" ]; then
  source "${WS}/install/setup.bash"
else
  echo "WARN: ${WS}/install/setup.bash not found (skipping overlay)"
fi

echo ""
echo "===== Exploration baseline validation ====="
echo ""

# 3. Exploration-related packages
echo "--- Exploration-related packages ---"
for pkg in explore_lite explore_lite_msgs slam_toolbox nav2_bringup turtlebot3_gazebo turtlebot3_navigation2; do
  if ros2 pkg list 2>/dev/null | grep -q "^${pkg}$"; then
    echo "  [OK] ${pkg}"
  else
    echo "  [--] ${pkg} (not visible)"
  fi
done
echo ""

# 4. Topic list
echo "--- Topic list ---"
ros2 topic list 2>/dev/null || echo "  (none or ros2 failed)"
echo ""

# 5. Action list
echo "--- Action list ---"
ros2 action list 2>/dev/null || echo "  (none or ros2 failed)"
echo ""

# 6. Node list
echo "--- Node list ---"
ros2 node list 2>/dev/null || echo "  (none or ros2 failed)"
echo ""

# 7. Checks (safe if missing)
echo "--- Baseline checks ---"
MAP_OK=0
ODOM_OK=0
ACTION_OK=0

if ros2 topic list 2>/dev/null | grep -q "^/map$"; then
  echo "  [OK] /map exists"
  MAP_OK=1
else
  echo "  [--] /map missing"
fi

if ros2 topic list 2>/dev/null | grep -qE "^(/odom|/odometry/filtered)$"; then
  echo "  [OK] /odom or /odometry/filtered exists"
  ODOM_OK=1
else
  echo "  [--] /odom and /odometry/filtered missing"
fi

if ros2 action list 2>/dev/null | grep -q "navigate_to_pose"; then
  echo "  [OK] navigate_to_pose action exists"
  ACTION_OK=1
else
  echo "  [--] navigate_to_pose action missing"
fi
echo ""

# 8. Final summary
echo "===== Baseline readiness summary ====="
READY=0
[ $MAP_OK -eq 1 ] && [ $ODOM_OK -eq 1 ] && [ $ACTION_OK -eq 1 ] && READY=1
if [ $READY -eq 1 ]; then
  echo "  READY: /map, odom, and navigate_to_pose are present. Safe to start explore_lite."
else
  echo "  NOT READY: Start TurtleBot3 (sim or bringup), slam_toolbox, and Nav2 first."
  echo "  Missing: map=$MAP_OK odom=$ODOM_OK navigate_to_pose=$ACTION_OK (1=ok 0=missing)"
fi
echo ""
