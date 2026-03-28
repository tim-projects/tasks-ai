#!/bin/bash

# Default values
MODE="local"
DEST_DIR="$HOME/.local/tasks-ai"
SYMLINK_DIR="$HOME/.local/bin"
UNINSTALL=false
FORCE=false
UPGRADE=false
INTERACTIVE=false

# Detect if running from a local tasks-ai repo
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
IS_LOCAL_REPO=false

if [ -f "$SCRIPT_DIR/tasks.py" ] && [ -d "$SCRIPT_DIR/tasks_ai" ]; then
    IS_LOCAL_REPO=true
fi

# Parse arguments
for arg in "$@"; do
  case $arg in
    upgrade)
      UPGRADE=true
      ;;
    --system)
      MODE="system"
      DEST_DIR="/opt/tasks-ai"
      SYMLINK_DIR="/usr/local/bin"
      ;;
    --uninstall)
      UNINSTALL=true
      ;;
    --force)
      FORCE=true
      ;;
    -i|--interactive)
      INTERACTIVE=true
      ;;
    -h|--help)
      echo "Tasks AI Installer"
      echo ""
      echo "Usage: ./install.sh [COMMAND]"
      echo ""
      echo "Commands:"
      echo "  upgrade         Download and install latest from GitHub"
      echo "  --system        Install to /opt/tasks-ai (requires sudo)"
      echo ""
      echo "Options:"
      echo "  -i, --interactive  Run interactive installer"
      echo "  --force         Force reinstall"
      echo "  --uninstall     Remove existing installation"
      echo "  -h, --help      Show this help message"
      echo ""
      echo "Examples:"
      echo "  ./install.sh              # Show this help"
      echo "  ./install.sh -i           # Interactive installer"
      echo "  ./install.sh upgrade      # Download and install latest"
      echo "  sudo ./install.sh --system # Install system-wide"
      exit 0
      ;;
  esac
done

# Handle uninstall
if [ "$UNINSTALL" == "true" ]; then
  echo "Uninstalling..."
  rm -rf "$DEST_DIR"
  rm -f "$SYMLINK_DIR/tasks"
  rm -f "$SYMLINK_DIR/repo"
  rm -f "$SYMLINK_DIR/r"
  rm -f "$SYMLINK_DIR/check"
  echo "Uninstallation complete!"
  exit 0
fi

# Check for python3
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed. Tasks AI requires Python 3."
    exit 1
fi

# If no arguments, show help and ask
if [ -z "$1" ]; then
    echo "Tasks AI Installer - Use --help for full options"
    echo ""
    echo "Quick usage:"
    echo "  ./install.sh              # Show this help"
    echo "  ./install.sh -i           # Interactive installer"
    echo "  ./install.sh upgrade      # Download latest from GitHub"
    echo "  sudo ./install.sh --system # Install system-wide"
    echo ""
    read -p "Run interactive installer? [y/N]: " yn
    case "$yn" in
        [yY])
            INTERACTIVE=true
            ;;
        *)
            exit 0
            ;;
    esac
elif [ "$1" == "upgrade" ]; then
    UPGRADE=true
elif [ "$1" == "-i" ] || [ "$1" == "--interactive" ]; then
    INTERACTIVE=true
fi

# Skip interactive if running upgrade or system
if [ "$UPGRADE" == "true" ] || [ "$MODE" == "system" ]; then
    if [ "$MODE" == "system" ] && [ "$EUID" -ne 0 ]; then
        echo "Error: System-wide installation requires root privileges."
        echo "Please run with sudo: sudo $0 $@"
        exit 1
    fi
else
    # Run interactive mode
    if [ "$INTERACTIVE" == "true" ]; then
        echo ""
        echo "Tasks AI Installer"
        echo "=================="
        echo "1) Install (user mode - ~/.local/tasks-ai)"
        echo "2) Install (system mode - /opt/tasks-ai - requires sudo)"
        echo "3) Upgrade (download latest from GitHub)"
        echo "4) Uninstall"
        echo "5) Quit"
        echo ""
        read -p "Select option [1]: " choice
        
        case "$choice" in
            2)
                MODE="system"
                DEST_DIR="/opt/tasks-ai"
                SYMLINK_DIR="/usr/local/bin"
                ;;
            3)
                UPGRADE=true
                ;;
            4)
                echo "Uninstalling..."
                rm -rf "$DEST_DIR"
                rm -f "$SYMLINK_DIR/tasks"
                rm -f "$SYMLINK_DIR/repo"
                rm -f "$SYMLINK_DIR/r"
                rm -f "$SYMLINK_DIR/check"
                echo "Uninstallation complete!"
                exit 0
                ;;
            5|"")
                exit 0
                ;;
            *)
                MODE="local"
                ;;
        esac
    fi
fi

# Ensure destination directory exists
if [ ! -d "$DEST_DIR" ]; then
    echo "Creating directory $DEST_DIR..."
    mkdir -p "$DEST_DIR"
fi

# Ensure symlink directory exists
if [ ! -d "$SYMLINK_DIR" ]; then
    mkdir -p "$SYMLINK_DIR"
fi

echo "Installing Tasks AI..."

if [ "$UPGRADE" == "true" ]; then
    echo "Upgrading (downloading from GitHub)..."
    curl -sSL "https://raw.githubusercontent.com/tim-projects/tasks-ai/main/tasks.py" -o "$DEST_DIR/tasks.py"
    curl -sSL "https://raw.githubusercontent.com/tim-projects/tasks-ai/main/check.py" -o "$DEST_DIR/check.py"
    curl -sSL "https://raw.githubusercontent.com/tim-projects/tasks-ai/main/repo.py" -o "$DEST_DIR/repo.py"
    curl -sSL "https://raw.githubusercontent.com/tim-projects/tasks-ai/main/install.sh" -o "$DEST_DIR/install.sh"
    
    mkdir -p "$DEST_DIR/tasks_ai"
    for module in cli.py help_text.py constants.py file_task.py task.py; do
        curl -sSL "https://raw.githubusercontent.com/tim-projects/tasks-ai/main/tasks_ai/$module" -o "$DEST_DIR/tasks_ai/$module"
    done
elif [ "$IS_LOCAL_REPO" == "true" ]; then
    echo "Using local files from $SCRIPT_DIR"
    cp "$SCRIPT_DIR/tasks.py" "$DEST_DIR/"
    cp "$SCRIPT_DIR/check.py" "$DEST_DIR/"
    cp "$SCRIPT_DIR/repo.py" "$DEST_DIR/"
    cp "$SCRIPT_DIR/install.sh" "$DEST_DIR/"
    
    if [ -d "$SCRIPT_DIR/tasks_ai" ]; then
        rm -rf "$DEST_DIR/tasks_ai"
        cp -r "$SCRIPT_DIR/tasks_ai" "$DEST_DIR/"
    fi
else
    echo "Downloading from GitHub..."
    curl -sSL "https://raw.githubusercontent.com/tim-projects/tasks-ai/main/tasks.py" -o "$DEST_DIR/tasks.py"
    curl -sSL "https://raw.githubusercontent.com/tim-projects/tasks-ai/main/check.py" -o "$DEST_DIR/check.py"
    curl -sSL "https://raw.githubusercontent.com/tim-projects/tasks-ai/main/repo.py" -o "$DEST_DIR/repo.py"
    curl -sSL "https://raw.githubusercontent.com/tim-projects/tasks-ai/main/install.sh" -o "$DEST_DIR/install.sh"
    
    mkdir -p "$DEST_DIR/tasks_ai"
    for module in cli.py help_text.py constants.py file_task.py task.py; do
        curl -sSL "https://raw.githubusercontent.com/tim-projects/tasks-ai/main/tasks_ai/$module" -o "$DEST_DIR/tasks_ai/$module"
    done
fi

# Set executable permissions
chmod +x "$DEST_DIR/tasks.py"
chmod +x "$DEST_DIR/check.py"
chmod +x "$DEST_DIR/repo.py"

# Create symlinks
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
echo "Installed to: $DEST_DIR"
echo "Symlinks: $SYMLINK_DIR"
if [ "$MODE" == "local" ]; then
    if [[ ":$PATH:" != *":$SYMLINK_DIR:"* ]]; then
        echo "Warning: $SYMLINK_DIR is not in your PATH."
    fi
fi
echo "You can now run: tasks -h"
echo "--------------------------------------------------"