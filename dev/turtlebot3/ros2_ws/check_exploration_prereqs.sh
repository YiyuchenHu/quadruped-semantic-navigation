#!/usr/bin/env bash
# Read-only diagnostic: TurtleBot3 autonomous exploration baseline prerequisites.
# Does not modify any files.

WS="/home/yiyuchenhu/Desktop/2026spring/CINQ389/Code_repo/quadruped-semantic-navigation/dev/turtlebot3/ros2_ws"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'
[ ! -t 1 ] && RED='' GREEN='' YELLOW='' CYAN='' NC=''

pass() { echo -e "  ${GREEN}[PASS]${NC} $*"; }
fail() { echo -e "  ${RED}[FAIL]${NC} $*"; }
warn() { echo -e "  ${YELLOW}[WARN]${NC} $*"; }
info() { echo -e "  ${CYAN}[INFO]${NC} $*"; }

CHK_ROS=0
CHK_WS=0
CHK_PKG=0
CHK_GRAPH=0
CHK_TF=0

echo ""
echo -e "${CYAN}===== TurtleBot3 exploration prerequisites =====${NC}"
echo ""

# ---------------------------------------------------------------------------
# 1. ROS2 Humble installed and sourceable
# ---------------------------------------------------------------------------
echo -e "${YELLOW}--- 1. ROS2 Humble ---${NC}"
if [ ! -f /opt/ros/humble/setup.bash ]; then
  fail "ROS2 Humble not found at /opt/ros/humble"
  CHK_ROS=1
else
  pass "/opt/ros/humble exists"
  # Source and verify in subshell
  if (source /opt/ros/humble/setup.bash 2>/dev/null && [ "${ROS_DISTRO}" = "humble" ]); then
    pass "ROS2 Humble sourceable (ROS_DISTRO=humble)"
  else
    fail "Sourcing Humble did not set ROS_DISTRO=humble"
    CHK_ROS=1
  fi
fi
echo ""

# ---------------------------------------------------------------------------
# 2. Workspace install/setup.bash exists
# ---------------------------------------------------------------------------
echo -e "${YELLOW}--- 2. Workspace ---${NC}"
if [ -f "${WS}/install/setup.bash" ]; then
  pass "install/setup.bash exists"
else
  fail "install/setup.bash not found"
  CHK_WS=1
fi
echo ""

# ---------------------------------------------------------------------------
# 3. Package visibility (if available)
# ---------------------------------------------------------------------------
echo -e "${YELLOW}--- 3. Package visibility ---${NC}"
(
  source /opt/ros/humble/setup.bash 2>/dev/null
  [ -f "${WS}/install/setup.bash" ] && source "${WS}/install/setup.bash" 2>/dev/null
  pkgs=(explore_lite explore_lite_msgs multirobot_map_merge slam_toolbox nav2_bringup turtlebot3_navigation2 turtlebot3_gazebo)
  missing=0
  for p in "${pkgs[@]}"; do
    if ros2 pkg list 2>/dev/null | grep -q "^${p}$"; then
      pass "${p}"
    else
      warn "${p} not visible"
      missing=$((missing + 1))
    fi
  done
  [ $missing -gt 0 ] && exit 1
  exit 0
) || CHK_PKG=1
echo ""

# ---------------------------------------------------------------------------
# 4. ROS graph (topics / action) — only if ROS is running
# ---------------------------------------------------------------------------
echo -e "${YELLOW}--- 4. ROS graph (topics / action) ---${NC}"
(
  source /opt/ros/humble/setup.bash 2>/dev/null
  [ -f "${WS}/install/setup.bash" ] && source "${WS}/install/setup.bash" 2>/dev/null
  # Topics
  for t in /map /map_updates /global_costmap/costmap; do
    if ros2 topic list 2>/dev/null | grep -q "^${t}$"; then
      pass "topic ${t}"
    else
      warn "topic ${t} not present"
    fi
  done
  # Odom: at least one of the two
  if ros2 topic list 2>/dev/null | grep -qE "^(/odom|/odometry/filtered)$"; then
    pass "topic /odom or /odometry/filtered"
  else
    warn "neither /odom nor /odometry/filtered present"
  fi
  # Action
  if ros2 action list 2>/dev/null | grep -q "navigate_to_pose"; then
    pass "action navigate_to_pose"
  else
    warn "action navigate_to_pose not present"
  fi
) 2>/dev/null
# Graph check is informational (nodes may not be running); only fail if ros2 fails badly
echo ""

# ---------------------------------------------------------------------------
# 5. TF chain (map -> odom, odom -> base_link)
# ---------------------------------------------------------------------------
echo -e "${YELLOW}--- 5. TF chain ---${NC}"
(
  source /opt/ros/humble/setup.bash 2>/dev/null
  [ -f "${WS}/install/setup.bash" ] && source "${WS}/install/setup.bash" 2>/dev/null
  for pair in "map odom" "odom base_link"; do
    read -r parent child <<< "$pair"
    out=$(timeout 2 ros2 run tf2_ros tf2_echo "$parent" "$child" 2>/dev/null | head -1)
    if echo "$out" | grep -q "At time"; then
      pass "TF ${parent} -> ${child}"
    else
      warn "TF ${parent} -> ${child} not available (run SLAM/robot first)"
    fi
  done
) 2>/dev/null
# TF is only available when graph is running; we don't set CHK_TF from here
echo ""

# ---------------------------------------------------------------------------
# 6. Summary
# ---------------------------------------------------------------------------
echo -e "${CYAN}===== Summary =====${NC}"
[ $CHK_ROS -eq 0 ] && pass "ROS2 Humble" || fail "ROS2 Humble"
[ $CHK_WS -eq 0 ]  && pass "Workspace install" || fail "Workspace install"
[ $CHK_PKG -eq 0 ] && pass "Package visibility" || fail "Package visibility (some optional)"
info "ROS graph and TF require running nodes (SLAM, Nav2, robot); see warnings above."
echo ""

if [ $CHK_ROS -eq 0 ] && [ $CHK_WS -eq 0 ]; then
  echo -e "${GREEN}Core prerequisites OK. Start SLAM + Nav2 + robot to satisfy graph/TF checks.${NC}"
  exit 0
else
  echo -e "${RED}Fix ROS2 or workspace before running exploration.${NC}"
  exit 1
fi
