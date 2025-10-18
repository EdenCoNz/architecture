#!/bin/bash
# Setup development environment for FastAPI backend

set -e  # Exit on error

echo "======================================"
echo "FastAPI Backend - Development Setup"
echo "======================================"
echo ""

# Check if running in project root
if [ ! -f "requirements.txt" ]; then
    echo "Error: Must run from backend/ directory"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✓ Python version: $PYTHON_VERSION"

# Install python3-venv if needed
if ! python3 -m venv --help &> /dev/null; then
    echo "Installing python3-venv..."
    sudo apt update
    sudo apt install -y python3.12-venv
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Activate virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Copy .env.example to .env and configure:"
echo "   cp .env.example .env"
echo ""
echo "3. Start database services:"
echo "   make db-up"
echo ""
echo "4. Run database migrations:"
echo "   make migrate"
echo ""
echo "5. Start development server:"
echo "   make dev"
echo ""
