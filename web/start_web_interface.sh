#!/bin/bash

# MCP CrewAI Web Interface Launcher
echo "🚀 Starting MCP CrewAI Web Interface..."

# Check if python3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is required but not installed"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install main project in development mode
echo "📦 Installing MCP CrewAI server..."
cd ..
pip install -e .
cd web

# Install web interface requirements
echo "📦 Installing web interface requirements..."
pip install -r requirements.txt

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)/../src"

# Create data directory if it doesn't exist
mkdir -p ../data

# Start the web interface
echo "🌐 Starting web server at http://localhost:8080"
echo "📊 Dashboard will be available at http://localhost:8080"
echo ""
echo "Press Ctrl+C to stop the server"
python3 api_bridge.py