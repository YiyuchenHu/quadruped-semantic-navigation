#!/bin/bash
# Apply patches to Picamera2
# This script applies all patches from patches/picamera2/ to the upstream repository

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PICAMERA2_DIR="$REPO_ROOT/upstream/picamera2"
PATCHES_DIR="$REPO_ROOT/patches/picamera2"

echo "Applying Picamera2 patches..."

# Check if Picamera2 directory exists
if [ ! -d "$PICAMERA2_DIR" ]; then
    echo "Error: Picamera2 directory not found. Run fetch_picamera2.sh first."
    exit 1
fi

# Check if patches directory exists
if [ ! -d "$PATCHES_DIR" ]; then
    echo "Warning: No patches directory found at $PATCHES_DIR"
    echo "Skipping patch application."
    exit 0
fi

# Count patch files
PATCH_COUNT=$(find "$PATCHES_DIR" -name "*.patch" | wc -l)
if [ "$PATCH_COUNT" -eq 0 ]; then
    echo "No patch files found in $PATCHES_DIR"
    exit 0
fi

echo "Found $PATCH_COUNT patch file(s)"

# Apply patches in order
cd "$PICAMERA2_DIR"

# Ensure we're on a clean state (optional, can be commented out for development)
# git reset --hard HEAD

# Apply patches
for patch_file in "$PATCHES_DIR"/*.patch; do
    if [ -f "$patch_file" ]; then
        echo "Applying $(basename "$patch_file")..."
        if git apply --check "$patch_file" 2>/dev/null; then
            git apply "$patch_file"
            echo "  ✓ Applied successfully"
        else
            echo "  ✗ Patch failed to apply (may already be applied or incompatible)"
            echo "    Try: git apply --check $patch_file for details"
            # Uncomment the next line to fail on patch errors
            # exit 1
        fi
    fi
done

echo "Patch application complete."
