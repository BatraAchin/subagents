#!/bin/bash

# Subagents Installation Script
# This script installs the fetch-tech-news command globally

echo "🚀 Installing Subagents Tech News Command..."
echo "==========================================="

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TECH_NEWS_DIR="$SCRIPT_DIR/tech-news"

# Check if tech-news directory exists
if [ ! -d "$TECH_NEWS_DIR" ]; then
    echo "❌ Error: tech-news directory not found. Please run this from the subagents root directory."
    exit 1
fi

# Check if requirements.txt exists
if [ ! -f "$TECH_NEWS_DIR/requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found in tech-news directory."
    exit 1
fi

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

# Set up virtual environment
VENV_DIR="$TECH_NEWS_DIR/venv"
echo "🐍 Setting up virtual environment at: $VENV_DIR"

if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo "❌ Error: Failed to create virtual environment"
        exit 1
    fi
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Install dependencies in virtual environment
echo "📦 Installing dependencies in virtual environment..."
"$VENV_DIR/bin/pip" install --upgrade pip
"$VENV_DIR/bin/pip" install -r "$TECH_NEWS_DIR/requirements.txt"

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to install dependencies"
    exit 1
fi
echo "✅ Dependencies installed successfully"

# Create a wrapper script
WRAPPER_SCRIPT="$HOME/.local/bin/fetch-tech-news"
WRAPPER_DIR="$(dirname "$WRAPPER_SCRIPT")"

echo "📁 Creating wrapper script at: $WRAPPER_SCRIPT"

# Create .local/bin directory if it doesn't exist
mkdir -p "$WRAPPER_DIR"

# Create the wrapper script
cat > "$WRAPPER_SCRIPT" << EOF
#!/bin/bash

# Subagents Tech News Fetcher Wrapper
# This script runs the fetch-tech-news command from anywhere

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
TECH_NEWS_DIR="$TECH_NEWS_DIR"
VENV_DIR="$VENV_DIR"

# Check if tech-news directory exists
if [ ! -d "\$TECH_NEWS_DIR" ]; then
    echo "❌ Error: tech-news directory not found at \$TECH_NEWS_DIR"
    echo "Please reinstall subagents or check the installation path."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "\$VENV_DIR" ]; then
    echo "❌ Error: Virtual environment not found at \$VENV_DIR"
    echo "Please reinstall subagents or run ./install.sh"
    exit 1
fi

# Change to tech-news directory and activate virtual environment
cd "\$TECH_NEWS_DIR"
source "\$VENV_DIR/bin/activate"

# Run the command with the virtual environment's Python
exec python src/main.py "\$@"
EOF

# Make the wrapper script executable
chmod +x "$WRAPPER_SCRIPT"

# Add .local/bin to PATH if not already there
if ! echo "$PATH" | grep -q "$WRAPPER_DIR"; then
    echo "🔧 Adding $WRAPPER_DIR to PATH in $SHELL_CONFIG"
    
    # Add PATH export to shell config
    echo "" >> "$SHELL_CONFIG"
    echo "# Subagents - Tech News Command" >> "$SHELL_CONFIG"
    echo "export PATH=\"\$PATH:$WRAPPER_DIR\"" >> "$SHELL_CONFIG"
    
    echo "✅ Added $WRAPPER_DIR to PATH"
    echo "⚠️  Please run 'source $SHELL_CONFIG' or restart your terminal to use the command"
else
    echo "✅ $WRAPPER_DIR is already in PATH"
fi

# Test the installation
echo "🧪 Testing installation..."
if [ -x "$WRAPPER_SCRIPT" ]; then
    echo "✅ Wrapper script created successfully"
    
    # Test if the command works (just check help)
    if "$WRAPPER_SCRIPT" --help > /dev/null 2>&1; then
        echo "✅ Command test successful"
    else
        echo "⚠️  Command created but test failed. You may need to install dependencies first."
        echo "   Run: cd $TECH_NEWS_DIR && pip3 install -r requirements.txt"
    fi
else
    echo "❌ Failed to create wrapper script"
    exit 1
fi

echo ""
echo "🎉 Installation complete!"
echo ""
echo "Usage:"
echo "  fetch-tech-news                    # Fetch articles only"
echo "  fetch-tech-news --summarize       # Fetch and create daily digest"
echo "  fetch-tech-news --help            # Show help"
echo ""
echo "Note: If the command is not found, run:"
echo "  source $SHELL_CONFIG"
echo "  or restart your terminal"
