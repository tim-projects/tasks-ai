#!/bin/bash

# Exit on error
set -e

# Default values
MODE="local"
DEST_DIR="$HOME/.local/tasks-ai"
SYMLINK_DIR="$HOME/.local/bin"
UNINSTALL=false

# Detect if running from a local tasks-ai repo
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
IS_LOCAL_REPO=false

# Parse arguments
for arg in "$@"; do
  case $arg in
    -g|--system)
      MODE="system"
      DEST_DIR="/opt/tasks-ai"
      SYMLINK_DIR="/usr/local/bin"
      ;;
    -u|--user)
      MODE="local"
      DEST_DIR="$HOME/.local/tasks-ai"
      SYMLINK_DIR="$HOME/.local/bin"
      ;;
    --uninstall)
      UNINSTALL=true
      ;;
    -h|--help)
      echo "Usage: install.sh [OPTIONS]"
      echo ""
      echo "Options:"
      echo "  -u, --user      Install locally to ~/.local/tasks-ai with symlinks in ~/.local/bin"
      echo "  -g, --system    Install system-wide to /opt/tasks-ai with symlinks in /usr/local/bin"
      echo "  --uninstall     Remove existing installation"
      echo "  -h, --help      Show this help message"
      exit 0
      ;;
  esac
done

# If no mode specified and no uninstall, ask user
if [ "$MODE" == "local" ] && [ -z "$1" ]; then
  echo "Select installation mode:"
  echo "  1) User (installs to ~/.local/bin)"
  echo "  2) System-wide (installs to /usr/local/bin - requires sudo)"
  read -p "Enter choice [1]: " choice
  choice=${choice:-1}
  if [ "$choice" == "2" ]; then
    MODE="system"
    DEST_DIR="/usr/local/bin"
  fi
fi

# If system mode, check for sudo
if [ "$MODE" == "system" ] && [ "$EUID" -ne 0 ]; then
  echo "Error: System-wide installation requires root privileges."
  echo "Please run with sudo: sudo $0 $@"
  exit 1
fi

# Check for existing installations and remove them
remove_existing() {
  local path="$1"
  if [ -f "$path" ]; then
    echo "Removing existing installation at $path..."
    rm -f "$path"
  fi
}

echo "Checking for existing installations..."

# Clean destination dir
remove_existing "$DEST_DIR/tasks"
remove_existing "$DEST_DIR/repo"
remove_existing "$DEST_DIR/check"
remove_existing "$DEST_DIR/tasks.py"
remove_existing "$DEST_DIR/repo.py"
remove_existing "$DEST_DIR/check.py"
remove_existing "$DEST_DIR/install.sh"

# Also clean symlinks
remove_existing "$SYMLINK_DIR/tasks"
remove_existing "$SYMLINK_DIR/repo"
remove_existing "$SYMLINK_DIR/check"
echo "Done."

# Handle uninstall
if [ "$UNINSTALL" == "true" ]; then
  echo "Uninstallation complete!"
  exit 0
fi

# Check for python3
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed. Tasks AI requires Python 3."
    exit 1
fi

# Ensure destination directory exists
if [ ! -d "$DEST_DIR" ]; then
    echo "Creating directory $DEST_DIR..."
    mkdir -p "$DEST_DIR"
fi

echo "Installing Tasks AI..."

if [ "$IS_LOCAL_REPO" == "true" ]; then
    echo "Using local files from $SCRIPT_DIR"
    # Copy from local repo
    cp "$SCRIPT_DIR/tasks.py" "$DEST_DIR/"
    cp "$SCRIPT_DIR/check.py" "$DEST_DIR/"
    cp "$SCRIPT_DIR/repo.py" "$DEST_DIR/"
    cp "$SCRIPT_DIR/install.sh" "$DEST_DIR/"
    
    # Copy tasks_ai directory
    if [ -d "$SCRIPT_DIR/tasks_ai" ]; then
        rm -rf "$DEST_DIR/tasks_ai"
        cp -r "$SCRIPT_DIR/tasks_ai" "$DEST_DIR/"
    fi
else
    echo "Downloading from GitHub..."
    # Download files from GitHub
    curl -sSL "https://raw.githubusercontent.com/tim-projects/tasks-ai/main/tasks.py" -o "$DEST_DIR/tasks.py"
    curl -sSL "https://raw.githubusercontent.com/tim-projects/tasks-ai/main/check.py" -o "$DEST_DIR/check.py"
    curl -sSL "https://raw.githubusercontent.com/tim-projects/tasks-ai/main/repo.py" -o "$DEST_DIR/repo.py"
    curl -sSL "https://raw.githubusercontent.com/tim-projects/tasks-ai/main/install.sh" -o "$DEST_DIR/install.sh"
    
    # Download tasks_ai directory
    mkdir -p "$DEST_DIR/tasks_ai"
    for module in cli.py help_text.py constants.py file_task.py task.py; do
        curl -sSL "https://raw.githubusercontent.com/tim-projects/tasks-ai/main/tasks_ai/$module" -o "$DEST_DIR/tasks_ai/$module"
    done
fi

# Set executable permissions
chmod +x "$DEST_DIR/tasks.py"
chmod +x "$DEST_DIR/check.py"
chmod +x "$DEST_DIR/repo.py"

# Ensure symlink directory exists
if [ ! -d "$SYMLINK_DIR" ]; then
    mkdir -p "$SYMLINK_DIR"
fi

# Create symlinks in SYMLINK_DIR (remove first if exists)
rm -f "$SYMLINK_DIR/tasks"
ln -s "$DEST_DIR/tasks.py" "$SYMLINK_DIR/tasks"

rm -f "$SYMLINK_DIR/repo"
ln -s "$DEST_DIR/repo.py" "$SYMLINK_DIR/repo"

rm -f "$SYMLINK_DIR/r"
ln -s "$DEST_DIR/repo.py" "$SYMLINK_DIR/r"

rm -f "$SYMLINK_DIR/check"
ln -s "$DEST_DIR/check.py" "$SYMLINK_DIR/check"

echo "--------------------------------------------------"
echo "Installation complete!"
if [ "$MODE" == "local" ]; then
    if [[ ":$PATH:" != *":$DEST_DIR:"* ]]; then
        echo "Warning: $DEST_DIR is not in your PATH."
        echo "Add this to your .bashrc or .zshrc:"
        echo "  export PATH=\$PATH:\$HOME/.local/bin"
    fi
fi
echo "You can now run: tasks -h"
echo "                 check lint"
echo "--------------------------------------------------"