#!/bin/bash
# Fetch upstream Picamera2 repository
# This script clones or updates the Picamera2 repository to the version specified in upstream/picamera2.version

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
UPSTREAM_DIR="$REPO_ROOT/upstream"
PICAMERA2_DIR="$UPSTREAM_DIR/picamera2"
VERSION_FILE="$UPSTREAM_DIR/picamera2.version"

PICAMERA2_REPO="https://github.com/raspberrypi/picamera2.git"

echo "Fetching Picamera2 upstream..."

# Read version from version file
if [ -f "$VERSION_FILE" ]; then
    VERSION=$(grep -v '^#' "$VERSION_FILE" | grep -v '^$' | head -1 | xargs)
else
    echo "Warning: $VERSION_FILE not found. Using latest version."
    VERSION=""
fi

# Clone or update repository
if [ -d "$PICAMERA2_DIR" ]; then
    echo "Updating existing Picamera2 repository..."
    cd "$PICAMERA2_DIR"
    git fetch origin
    if [ -n "$VERSION" ]; then
        git checkout "$VERSION" || {
            echo "Warning: Could not checkout version $VERSION, using current HEAD"
        }
    else
        git pull origin main || git pull origin master
    fi
else
    echo "Cloning Picamera2 repository..."
    mkdir -p "$UPSTREAM_DIR"
    cd "$UPSTREAM_DIR"
    git clone "$PICAMERA2_REPO" picamera2
    cd "$PICAMERA2_DIR"
    if [ -n "$VERSION" ]; then
        git checkout "$VERSION" || {
            echo "Warning: Could not checkout version $VERSION, using default branch"
        }
    fi
fi

# Display current version
CURRENT_VERSION=$(cd "$PICAMERA2_DIR" && git rev-parse HEAD)
echo "Picamera2 repository ready at: $PICAMERA2_DIR"
echo "Current commit: $CURRENT_VERSION"
