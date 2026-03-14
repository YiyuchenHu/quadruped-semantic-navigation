#!/usr/bin/env bash
# ROS2 workspace diagnostic script. Read-only; does not modify any files.

WS="/home/yiyuchenhu/Desktop/2026spring/CINQ389/Code_repo/quadruped-semantic-navigation/dev/turtlebot3/ros2_ws"

# Colors (no-op if not a tty)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'
if [ ! -t 1 ]; then RED=''; GREEN=''; YELLOW=''; CYAN=''; NC=''; fi

pass() { echo -e "${GREEN}[PASS]${NC} $*"; }
fail() { echo -e "${RED}[FAIL]${NC} $*"; }
info() { echo -e "${CYAN}[INFO]${NC} $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }

ROS_OK=0
STRUCT_OK=0
PKG_OK=0
OVERLAY_OK=0

echo ""
echo -e "${CYAN}===== ROS2 workspace diagnostic: ${WS} =====${NC}"
echo ""

# ---------------------------------------------------------------------------
# 1. Check ROS2 installation
# ---------------------------------------------------------------------------
echo -e "${YELLOW}--- 1. ROS2 installation ---${NC}"
if [ -d "/opt/ros/humble" ]; then
  pass "/opt/ros/humble exists"
else
  fail "/opt/ros/humble not found"
  ROS_OK=1
fi
if [ -n "${ROS_DISTRO}" ]; then
  info "ROS_DISTRO (current shell): ${ROS_DISTRO}"
else
  info "ROS_DISTRO not set in current shell (will be set after sourcing)"
fi
# Ensure we have Humble available for later steps
if [ ! -f /opt/ros/humble/setup.bash ]; then
  fail "/opt/ros/humble/setup.bash missing"
  ROS_OK=1
fi
if [ "${ROS_OK}" -eq 0 ]; then pass "ROS2 install check"; else fail "ROS2 install check"; fi
echo ""

# ---------------------------------------------------------------------------
# 2. Workspace structure
# ---------------------------------------------------------------------------
echo -e "${YELLOW}--- 2. Workspace structure ---${NC}"
for dir in src build install log; do
  if [ -d "${WS}/${dir}" ]; then
    pass "${dir}/ exists"
  else
    fail "${dir}/ missing"
    STRUCT_OK=1
  fi
done
if [ "${STRUCT_OK}" -eq 0 ]; then pass "Workspace structure"; else fail "Workspace structure"; fi
echo ""

# ---------------------------------------------------------------------------
# 3. Package detection (colcon list)
# ---------------------------------------------------------------------------
echo -e "${YELLOW}--- 3. Package detection (colcon list) ---${NC}"
if [ ! -d "${WS}/src" ]; then
  fail "No src/ directory; skipping colcon list"
  PKG_OK=1
else
  cd "${WS}" || true
  colcon list 2>/dev/null || { fail "colcon list failed"; PKG_OK=1; }
  n=$(colcon list --names-only 2>/dev/null | wc -l)
  info "Detected ${n} package(s) above"
  [ "${n}" -eq 0 ] && warn "No packages in src/"
  cd - >/dev/null 2>/dev/null || true
fi
echo ""

# ---------------------------------------------------------------------------
# 4. Overlay environment
# ---------------------------------------------------------------------------
echo -e "${YELLOW}--- 4. Overlay environment ---${NC}"
if [ ! -f /opt/ros/humble/setup.bash ]; then
  fail "Cannot source ROS2; skipping overlay check"
  OVERLAY_OK=1
elif [ ! -f "${WS}/install/setup.bash" ]; then
  fail "install/setup.bash not found; overlay not available"
  OVERLAY_OK=1
else
  # Source in subshell to avoid changing caller's environment
  (
    source /opt/ros/humble/setup.bash
    source "${WS}/install/setup.bash"
    echo "AMENT_PREFIX_PATH: ${AMENT_PREFIX_PATH:-<not set>}"
    echo "COLCON_PREFIX_PATH: ${COLCON_PREFIX_PATH:-<not set>}"
  )
  if [ $? -eq 0 ]; then
    pass "Overlay environment (sourced in subshell)"
  else
    fail "Overlay environment"
    OVERLAY_OK=1
  fi
fi
echo ""

# ---------------------------------------------------------------------------
# 5. ROS2 package visibility (explore)
# ---------------------------------------------------------------------------
echo -e "${YELLOW}--- 5. ROS2 package visibility (ros2 pkg list | grep explore) ---${NC}"
(
  source /opt/ros/humble/setup.bash 2>/dev/null
  [ -f "${WS}/install/setup.bash" ] && source "${WS}/install/setup.bash" 2>/dev/null
  out=$(ros2 pkg list 2>/dev/null | grep -E "explore" || true)
  if [ -n "${out}" ]; then
    echo "${out}"
    pass "Found explore-related packages"
  else
    warn "No packages matching 'explore' in ros2 pkg list"
  fi
)
echo ""

# ---------------------------------------------------------------------------
# 6. Launch files
# ---------------------------------------------------------------------------
echo -e "${YELLOW}--- 6. Launch files (launch/*.py in src) ---${NC}"
launch_count=0
[ -d "${WS}/src" ] && while IFS= read -r f; do
  info "$f"
  launch_count=$((launch_count + 1))
done < <(find "${WS}/src" -path "*/launch/*.py" -type f 2>/dev/null)
if [ "${launch_count}" -eq 0 ]; then
  warn "No launch/*.py files found in src/"
else
  pass "Found ${launch_count} launch file(s)"
fi
echo ""

# ---------------------------------------------------------------------------
# 7. Build success indicators
# ---------------------------------------------------------------------------
echo -e "${YELLOW}--- 7. Build success ---${NC}"
if [ -f "${WS}/install/setup.bash" ]; then
  pass "install/setup.bash exists"
else
  fail "install/setup.bash missing"
fi
if [ -d "${WS}/build" ] && [ -n "$(ls -A "${WS}/build" 2>/dev/null)" ]; then
  pass "build/ is not empty"
else
  warn "build/ missing or empty"
fi
echo ""

# ---------------------------------------------------------------------------
# 8. Final summary
# --------------------------------------------------------------------------
echo -e "${CYAN}===== Summary =====${NC}"
[ "${ROS_OK}" -eq 0 ] && pass "ROS2 install" || fail "ROS2 install"
[ "${STRUCT_OK}" -eq 0 ] && pass "Workspace structure" || fail "Workspace structure"
[ "${PKG_OK}" -eq 0 ] && pass "Package detection" || fail "Package detection"
[ "${OVERLAY_OK}" -eq 0 ] && pass "Overlay environment" || fail "Overlay environment"
echo ""

total=$((ROS_OK + STRUCT_OK + PKG_OK + OVERLAY_OK))
if [ "${total}" -eq 0 ]; then
  echo -e "${GREEN}All checks passed.${NC}"
  exit 0
else
  echo -e "${RED}Some checks failed (${total} category/ies).${NC}"
  exit 1
fi
