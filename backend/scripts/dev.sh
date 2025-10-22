#!/usr/bin/env bash

# Development Server Startup Script
# Starts the Django development server with hot reload enabled
# This script is for local development only - DO NOT use in production

set -e

# Script directory (absolute path)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Default values
HOST="${DEV_HOST:-127.0.0.1}"
PORT="${DEV_PORT:-8000}"
SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-config.settings.development}"

echo ""
echo "=================================================="
echo -e "${BLUE}Backend API - Development Server${NC}"
echo "=================================================="
echo ""

# Change to project root
cd "$PROJECT_ROOT"

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo -e "${YELLOW}⚠ Virtual environment not activated${NC}"
    echo "Checking for virtual environment in project..."

    if [[ -d "venv/bin" ]]; then
        echo -e "${GREEN}Found virtual environment, activating...${NC}"
        source venv/bin/activate
    elif [[ -d ".venv/bin" ]]; then
        echo -e "${GREEN}Found virtual environment, activating...${NC}"
        source .venv/bin/activate
    else
        echo -e "${RED}Error: No virtual environment found!${NC}"
        echo "Please create one with: python3 -m venv venv"
        echo "Then activate it: source venv/bin/activate"
        exit 1
    fi
fi

echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo "  Location: $VIRTUAL_ENV"
echo ""

# Check if .env file exists
if [[ ! -f "$PROJECT_ROOT/.env" ]]; then
    echo -e "${YELLOW}⚠ .env file not found${NC}"
    if [[ -f "$PROJECT_ROOT/.env.example" ]]; then
        echo "Creating .env from .env.example..."
        cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
        echo -e "${GREEN}✓ .env file created${NC}"
        echo -e "${YELLOW}⚠ Please edit .env with your configuration before continuing${NC}"
        exit 1
    else
        echo -e "${RED}Error: .env.example not found${NC}"
        exit 1
    fi
fi

# Set Django settings module
export DJANGO_SETTINGS_MODULE="$SETTINGS_MODULE"

echo "Configuration:"
echo "  Settings: $DJANGO_SETTINGS_MODULE"
echo "  Host: $HOST"
echo "  Port: $PORT"
echo ""

# Check database connectivity
echo "Checking database connection..."
if python manage.py check_database --quiet 2>/dev/null; then
    echo -e "${GREEN}✓ Database connection successful${NC}"
else
    echo -e "${YELLOW}⚠ Database check failed or not configured${NC}"
    echo "  The server will start, but you may need to configure the database."
fi
echo ""

# Check for pending migrations
echo "Checking for pending migrations..."
if python manage.py showmigrations --plan | grep -q "\[ \]"; then
    echo -e "${YELLOW}⚠ Pending migrations detected${NC}"
    echo ""
    read -p "Would you like to run migrations now? (y/N) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Running migrations..."
        python manage.py migrate
        echo -e "${GREEN}✓ Migrations complete${NC}"
    else
        echo "Skipping migrations. Run manually with: python manage.py migrate"
    fi
else
    echo -e "${GREEN}✓ No pending migrations${NC}"
fi
echo ""

# Display useful information
echo "=================================================="
echo "Starting Development Server"
echo "=================================================="
echo ""
echo "Server URL: http://${HOST}:${PORT}/"
echo "Admin URL: http://${HOST}:${PORT}/admin/"
echo "API Docs: http://${HOST}:${PORT}/api/docs/"
echo "Health Check: http://${HOST}:${PORT}/api/health/"
echo ""
echo "Hot reload is ENABLED - code changes will automatically restart the server"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=================================================="
echo ""

# Trap Ctrl+C and cleanup
trap 'echo -e "\n${YELLOW}Shutting down development server...${NC}"; exit 0' INT TERM

# Start the development server with auto-reload
# The --noreload flag is NOT used, so hot reload is enabled by default
python manage.py runserver "${HOST}:${PORT}"
