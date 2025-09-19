#!/bin/bash

# Subagents Uninstallation Script
# This script removes the fetch-tech-news command from your system

echo "🗑️  Uninstalling Subagents Tech News Command..."
echo "=============================================="

# Detect shell
SHELL_NAME=$(basename "$SHELL")
echo "🐚 Detected shell: $SHELL_NAME"

# Determine shell config file
if [ "$SHELL_NAME" = "zsh" ]; then
    SHELL_CONFIG="$HOME/.zshrc"
elif [ "$SHELL_NAME" = "bash" ]; then
    SHELL_CONFIG="$HOME/.bashrc"
else
    echo "⚠️  Warning: Unsupported shell ($SHELL_NAME). Defaulting to .bashrc"
    SHELL_CONFIG="$HOME/.bashrc"
fi

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TECH_NEWS_DIR="$SCRIPT_DIR/tech-news"
VENV_DIR="$TECH_NEWS_DIR/venv"

# Remove virtual environment
if [ -d "$VENV_DIR" ]; then
    echo "🗑️  Removing virtual environment: $VENV_DIR"
    rm -rf "$VENV_DIR"
    echo "✅ Virtual environment removed"
else
    echo "ℹ️  Virtual environment not found at $VENV_DIR"
fi

# Remove wrapper script
WRAPPER_SCRIPT="$HOME/.local/bin/fetch-tech-news"

if [ -f "$WRAPPER_SCRIPT" ]; then
    echo "🗑️  Removing wrapper script: $WRAPPER_SCRIPT"
    rm "$WRAPPER_SCRIPT"
    echo "✅ Wrapper script removed"
else
    echo "ℹ️  Wrapper script not found at $WRAPPER_SCRIPT"
fi

# Remove PATH entry from shell config
if [ -f "$SHELL_CONFIG" ]; then
    echo "🔧 Removing PATH entry from $SHELL_CONFIG"
    
    # Create a temporary file without the subagents entries
    grep -v "Subagents - Tech News Command" "$SHELL_CONFIG" | \
    grep -v "export PATH.*\.local/bin" > "$SHELL_CONFIG.tmp"
    
    # Replace the original file
    mv "$SHELL_CONFIG.tmp" "$SHELL_CONFIG"
    
    echo "✅ PATH entry removed from shell config"
else
    echo "ℹ️  Shell config file not found at $SHELL_CONFIG"
fi

echo ""
echo "🎉 Uninstallation complete!"
echo ""
echo "Note: You may need to restart your terminal or run:"
echo "  source $SHELL_CONFIG"
echo "  to see the changes take effect"
