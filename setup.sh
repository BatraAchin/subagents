#!/bin/bash

# Subagents Setup Script
# This script helps users set up the tech news agent

echo "🚀 Setting up Subagents Tech News Agent..."
echo "=========================================="

# Check if we're in the right directory
if [ ! -f "tech-news/requirements.txt" ]; then
    echo "❌ Error: Please run this script from the subagents root directory"
    exit 1
fi

# Check Python version
echo "🐍 Checking Python version..."
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Error: Python 3 is required but not installed"
    exit 1
fi

# Install dependencies
echo "📦 Installing Python dependencies..."
cd tech-news
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to install dependencies"
    exit 1
fi

# Create config file from example
echo "⚙️  Setting up configuration..."
if [ ! -f "config/gemini.yaml" ]; then
    if [ -f "config/gemini.yaml.example" ]; then
        cp config/gemini.yaml.example config/gemini.yaml
        echo "📝 Created config/gemini.yaml from example"
        echo "⚠️  Please edit config/gemini.yaml and add your Gemini API key"
    else
        echo "❌ Error: Configuration example not found"
        exit 1
    fi
else
    echo "✅ Configuration file already exists"
fi

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x ../fetch-tech-news
chmod +x run_tests.py

# Run tests to verify setup
echo "🧪 Running tests to verify setup..."
python3 run_tests.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Setup complete!"
    echo ""
    echo "Next steps:"
    echo "1. Edit tech-news/config/gemini.yaml and add your Gemini API key"
    echo "2. Run: ./fetch-tech-news --summarize"
    echo ""
    echo "For more information, see the README.md file"
else
    echo "❌ Setup completed but tests failed. Please check the error messages above."
    exit 1
fi
