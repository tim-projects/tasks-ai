#!/bin/bash

# Exit on error
set -e

# Default values
MODE="local"
DEST_DIR="$HOME/.local/bin"
USE_SUDO=""

# Parse arguments
for arg in "$@"; do
  case $arg in
    --system)
      MODE="system"
      DEST_DIR="/usr/local/bin"
      USE_SUDO="sudo"
      ;;
    --local)
      MODE="local"
      DEST_DIR="$HOME/.local/bin"
      USE_SUDO=""
      ;;
  esac
done

# Check for python3
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed."
    exit 1
fi

# Install dependencies
echo "Installing dependencies ($MODE)..."
if [ "$MODE" == "system" ]; then
    sudo pip3 install python-frontmatter --break-system-packages || sudo pip3 install python-frontmatter || {
        echo "Warning: System pip install failed. Ensure dependencies are met manually."
    }
else
    pip3 install --user python-frontmatter || {
        echo "Warning: Local pip install failed. Ensure dependencies are met manually."
    }
fi

# Define source and destination
SOURCE_FILE="tasks.py"
DEST_PATH="$DEST_DIR/tasks"

# Check if script exists
if [ ! -f "$SOURCE_FILE" ]; then
    echo "Error: $SOURCE_FILE not found in current directory."
    exit 1
fi

# Ensure destination directory exists for local install
if [ "$MODE" == "local" ]; then
    mkdir -p "$DEST_DIR"
fi

# Copy and make executable
echo "Installing tasks-ai to $DEST_PATH..."
$USE_SUDO cp "$SOURCE_FILE" "$DEST_PATH"
$USE_SUDO chmod +x "$DEST_PATH"

echo "Installation complete!"
if [ "$MODE" == "local" ]; then
    echo "Make sure $DEST_DIR is in your PATH."
    echo "You can add it by adding 'export PATH=\$PATH:\$HOME/.local/bin' to your .bashrc or .zshrc"
fi
echo "You can now use 'tasks' from anywhere."
