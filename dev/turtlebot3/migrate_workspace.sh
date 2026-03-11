#!/usr/bin/env bash
# Safe migration: turtlebot3_ws/src -> ros2_ws/src (source packages only).
# Uses rsync, preserves permissions, verifies package.xml after copy.

set -e

OLD_SRC="/home/yiyuchenhu/turtlebot3_ws/src"
NEW_SRC="/home/yiyuchenhu/Desktop/2026spring/CINQ389/Code_repo/quadruped-semantic-navigation/dev/turtlebot3/ros2_ws/src"

PACKAGES=( "m-explore-ros2" )

echo "=== Workspace migration (source only) ==="
echo "From: ${OLD_SRC}"
echo "To:   ${NEW_SRC}"
echo ""

if [ ! -d "${OLD_SRC}" ]; then
  echo "ERROR: Old workspace src not found: ${OLD_SRC}"
  exit 1
fi

mkdir -p "${NEW_SRC}"

for pkg in "${PACKAGES[@]}"; do
  src_path="${OLD_SRC}/${pkg}"
  if [ ! -d "${src_path}" ]; then
    echo "SKIP: ${pkg} (not found at ${src_path})"
    continue
  fi
  echo "[Migrating] ${pkg}"
  rsync -a --exclude='build' --exclude='install' --exclude='log' \
    "${src_path}/" "${NEW_SRC}/${pkg}/"
  echo "  -> ${NEW_SRC}/${pkg}/"
done

echo ""
echo "=== Verifying package.xml ==="
missing=0
for pkg in "${PACKAGES[@]}"; do
  dest="${NEW_SRC}/${pkg}"
  if [ ! -d "${dest}" ]; then
    continue
  fi
  found=$(find "${dest}" -name "package.xml" 2>/dev/null | wc -l)
  if [ "${found}" -eq 0 ]; then
    echo "  FAIL: No package.xml under ${pkg}"
    missing=1
  else
    echo "  OK:   ${pkg} (${found} package.xml)"
  fi
done

if [ "${missing}" -ne 0 ]; then
  echo ""
  echo "ERROR: Some packages have no package.xml. Migration may be incomplete."
  exit 1
fi

echo ""
echo "=== Migration complete ==="
