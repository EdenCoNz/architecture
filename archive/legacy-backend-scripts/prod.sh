#!/usr/bin/env bash

# Production Server Startup Script
# Starts the Django production server with Gunicorn (WSGI server)
# This script uses production-optimized settings

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

# Default production values
HOST="${PROD_HOST:-0.0.0.0}"
PORT="${PROD_PORT:-8000}"
WORKERS="${GUNICORN_WORKERS:-4}"
TIMEOUT="${GUNICORN_TIMEOUT:-30}"
MAX_REQUESTS="${GUNICORN_MAX_REQUESTS:-1000}"
MAX_REQUESTS_JITTER="${GUNICORN_MAX_REQUESTS_JITTER:-100}"
SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-config.settings.production}"

echo ""
echo "=================================================="
echo -e "${BLUE}Backend API - Production Server${NC}"
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
    echo -e "${RED}Error: .env file not found!${NC}"
    echo "Production requires a properly configured .env file"
    exit 1
fi

# Check if gunicorn is installed
if ! command -v gunicorn >/dev/null 2>&1; then
    echo -e "${RED}Error: Gunicorn is not installed!${NC}"
    echo "Install it with: pip install gunicorn"
    exit 1
fi

# Set Django settings module
export DJANGO_SETTINGS_MODULE="$SETTINGS_MODULE"

echo "Configuration:"
echo "  Settings: $DJANGO_SETTINGS_MODULE"
echo "  Host: $HOST"
echo "  Port: $PORT"
echo "  Workers: $WORKERS"
echo "  Timeout: ${TIMEOUT}s"
echo "  Max Requests: $MAX_REQUESTS (+/-${MAX_REQUESTS_JITTER})"
echo ""

# Production readiness checks
echo "=================================================="
echo "Running Production Readiness Checks"
echo "=================================================="
echo ""

# Check SECRET_KEY is not insecure
echo "1. Checking SECRET_KEY security..."
if python -c "
import os
from config.env_config import get_config
secret = get_config('SECRET_KEY', required=True)
if 'django-insecure' in secret.lower() or len(secret) < 50:
    print('ERROR: SECRET_KEY is not production-ready')
    exit(1)
print('OK')
" 2>/dev/null; then
    echo -e "${GREEN}✓ SECRET_KEY is secure${NC}"
else
    echo -e "${RED}✗ SECRET_KEY is not production-ready!${NC}"
    echo "  Generate a secure key: python -c \"import secrets; print(secrets.token_urlsafe(50))\""
    exit 1
fi

# Check DEBUG is False
echo "2. Checking DEBUG setting..."
if python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', '$SETTINGS_MODULE')
import django
django.setup()
from django.conf import settings
if settings.DEBUG:
    print('ERROR: DEBUG is True')
    exit(1)
print('OK')
" 2>/dev/null; then
    echo -e "${GREEN}✓ DEBUG is False${NC}"
else
    echo -e "${RED}✗ DEBUG is True in production!${NC}"
    exit 1
fi

# Check ALLOWED_HOSTS is configured
echo "3. Checking ALLOWED_HOSTS..."
if python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', '$SETTINGS_MODULE')
import django
django.setup()
from django.conf import settings
if not settings.ALLOWED_HOSTS or settings.ALLOWED_HOSTS == ['*']:
    print('ERROR: ALLOWED_HOSTS not properly configured')
    exit(1)
print('OK')
" 2>/dev/null; then
    echo -e "${GREEN}✓ ALLOWED_HOSTS is configured${NC}"
else
    echo -e "${RED}✗ ALLOWED_HOSTS not properly configured!${NC}"
    exit 1
fi

# Check database connectivity
echo "4. Checking database connection..."
if python manage.py check_database --quiet 2>/dev/null; then
    echo -e "${GREEN}✓ Database connection successful${NC}"
else
    echo -e "${RED}✗ Database connection failed!${NC}"
    exit 1
fi

# Check for pending migrations
echo "5. Checking migrations..."
if python manage.py showmigrations --plan | grep -q "\[ \]"; then
    echo -e "${RED}✗ Pending migrations detected!${NC}"
    echo "  Run migrations before starting production server: python manage.py migrate"
    exit 1
else
    echo -e "${GREEN}✓ All migrations applied${NC}"
fi

# Run Django deployment checks
echo "6. Running Django deployment checks..."
if python manage.py check --deploy --fail-level WARNING 2>&1 | grep -v "System check identified" | tail -5; then
    echo -e "${GREEN}✓ Deployment checks passed${NC}"
else
    echo -e "${YELLOW}⚠ Some deployment checks failed (see above)${NC}"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Collect static files
echo "7. Collecting static files..."
if python manage.py collectstatic --noinput --clear 2>&1 | tail -3; then
    echo -e "${GREEN}✓ Static files collected${NC}"
else
    echo -e "${YELLOW}⚠ Static file collection had issues${NC}"
fi

echo ""
echo "=================================================="
echo -e "${GREEN}All production checks passed!${NC}"
echo "=================================================="
echo ""

# Display useful information
echo "Starting Production Server with Gunicorn"
echo "=================================================="
echo ""
echo "Server URL: http://${HOST}:${PORT}/"
echo ""
echo "Note: Hot reload is DISABLED in production mode"
echo "      Restart the server to apply code changes"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=================================================="
echo ""

# Trap Ctrl+C and cleanup
trap 'echo -e "\n${YELLOW}Shutting down production server...${NC}"; exit 0' INT TERM

# Start Gunicorn with production settings
# See: https://docs.gunicorn.org/en/stable/settings.html
exec gunicorn config.wsgi:application \
    --bind "${HOST}:${PORT}" \
    --workers "$WORKERS" \
    --timeout "$TIMEOUT" \
    --max-requests "$MAX_REQUESTS" \
    --max-requests-jitter "$MAX_REQUESTS_JITTER" \
    --worker-class sync \
    --worker-tmp-dir /dev/shm \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --capture-output \
    --enable-stdio-inheritance
