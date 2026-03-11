#!/usr/bin/env bash
# Build ROS2 workspace (Humble). Uses system Python to avoid conda 'em' module errors.

set -e

WS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${WS_ROOT}"

echo "=== Building ROS2 workspace ==="
echo "Workspace: ${WS_ROOT}"
echo ""

# Force system Python (avoids conda 'em' module error; overrides CMake cache)
export PATH="/usr/bin:${PATH}"
export Python3_EXECUTABLE="/usr/bin/python3"

source /opt/ros/humble/setup.bash

# Once: clear cached build for msg packages so CMake uses system Python (not conda)
MARKER="${WS_ROOT}/.build_used_system_python"
for pkg in explore_lite_msgs; do
  if [ -d "${WS_ROOT}/build/${pkg}" ] && [ ! -f "${MARKER}" ]; then
    rm -rf "${WS_ROOT}/build/${pkg}" "${WS_ROOT}/install/${pkg}"
    echo "Cleaned ${pkg} (force reconfigure with system Python)"
  fi
done

colcon build --symlink-install --cmake-args -DPython3_EXECUTABLE=/usr/bin/python3 "$@"
result=$?

echo ""
if [ ${result} -ne 0 ]; then
  echo "=== Build FAILED (exit code ${result}) ==="
  exit ${result}
fi

touch "${MARKER}" 2>/dev/null || true

echo "=== Build SUCCESS ==="
echo "Built packages:"
for d in "${WS_ROOT}/install/"*/; do
  name=$(basename "$d")
  [ "$name" = "COLCON_IGNORE" ] && continue
  echo "  - ${name}"
done
echo "  (source: ${WS_ROOT}/install/setup.bash)"
echo ""
