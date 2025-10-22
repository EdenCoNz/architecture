#!/bin/bash
# Setup script for backend development environment

set -e

echo "================================================"
echo "Backend API - Development Setup"
echo "================================================"
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version || { echo "Error: Python 3 is not installed"; exit 1; }

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv || { echo "Error: Could not create virtual environment. Install python3-venv: sudo apt install python3-venv"; exit 1; }
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
if [ -f "requirements/dev.txt" ]; then
    pip install -r requirements/dev.txt
else
    echo "Warning: requirements/dev.txt not found"
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file with your configuration!"
    echo "   Generate a SECRET_KEY using: python -c \"import secrets; print(secrets.token_urlsafe(50))\""
fi

# Check database connection
echo ""
echo "Checking database connection..."
echo "Make sure PostgreSQL is running and configured in .env"

# Check Redis connection
echo "Make sure Redis is running (redis-server)"

echo ""
echo "================================================"
echo "Setup complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Edit .env with your configuration"
echo "2. Create database: createdb backend_db"
echo "3. Run migrations: python manage.py migrate"
echo "4. Create superuser: python manage.py createsuperuser"
echo "5. Run server: python manage.py runserver"
echo ""
echo "Or use the Makefile:"
echo "  make migrate  - Apply migrations"
echo "  make run      - Start development server"
echo "  make test     - Run tests"
echo ""
