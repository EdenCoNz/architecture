#!/usr/bin/env bash

# Database Seeding Script
# Seeds the database with test data for development and testing
# NEVER use this script in production!

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
CLEAR_DATA=false
CREATE_ADMIN=false
NUM_USERS=10
SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-config.settings.development}"

# Help message
show_help() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS]

Seed the database with test data for development and testing.

⚠ WARNING: This script should NEVER be used in production!

OPTIONS:
    --clear                 Clear existing data before seeding (DANGEROUS!)
    --admin                 Create admin user (admin@example.com / admin123)
    --users NUM             Number of test users to create (default: 10)
    -h, --help              Show this help message

EXAMPLES:
    $(basename "$0")                    # Seed with default settings
    $(basename "$0") --admin            # Seed and create admin user
    $(basename "$0") --users 50         # Seed with 50 test users
    $(basename "$0") --clear --admin    # Clear data and seed with admin

SEEDED DATA:
    - Test users (testuser1@example.com, testuser2@example.com, ...)
      Password: password123
    - Admin user (if --admin flag used): admin@example.com
      Password: admin123

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --clear)
            CLEAR_DATA=true
            shift
            ;;
        --admin)
            CREATE_ADMIN=true
            shift
            ;;
        --users)
            NUM_USERS="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        -*)
            echo -e "${RED}Error: Unknown option $1${NC}"
            show_help
            exit 1
            ;;
        *)
            echo -e "${RED}Error: Unknown argument $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

echo ""
echo "=================================================="
echo -e "${BLUE}Backend API - Database Seeding${NC}"
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

# Set Django settings module
export DJANGO_SETTINGS_MODULE="$SETTINGS_MODULE"

echo "Configuration:"
echo "  Settings: $DJANGO_SETTINGS_MODULE"
echo "  Clear existing data: $CLEAR_DATA"
echo "  Create admin user: $CREATE_ADMIN"
echo "  Number of test users: $NUM_USERS"
echo ""

# Safety check: ensure DEBUG is True
echo "Running safety checks..."
DEBUG_STATUS=$(python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', '$SETTINGS_MODULE')
import django
django.setup()
from django.conf import settings
print('True' if settings.DEBUG else 'False')
" 2>/dev/null)

if [[ "$DEBUG_STATUS" != "True" ]]; then
    echo -e "${RED}✗ ERROR: Cannot seed data when DEBUG=False!${NC}"
    echo "  This is a safety measure to prevent accidental data seeding in production."
    echo "  Use development or testing settings module."
    exit 1
fi

echo -e "${GREEN}✓ Safety checks passed (DEBUG=True)${NC}"

# Check database connectivity
echo "Checking database connection..."
if python manage.py check_database --quiet 2>/dev/null; then
    echo -e "${GREEN}✓ Database connection successful${NC}"
else
    echo -e "${RED}✗ Database connection failed!${NC}"
    exit 1
fi

# Check if migrations are applied
echo "Checking migrations..."
if python manage.py showmigrations --plan | grep -q "\[ \]"; then
    echo -e "${YELLOW}⚠ Pending migrations detected!${NC}"
    echo ""
    read -p "Would you like to run migrations now? (y/N) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Running migrations..."
        python manage.py migrate
        echo -e "${GREEN}✓ Migrations complete${NC}"
    else
        echo -e "${RED}Cannot seed database without applying migrations.${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ All migrations applied${NC}"
fi

echo ""
echo "=================================================="
echo "Seeding Database"
echo "=================================================="
echo ""

# Build the seed command
SEED_CMD="python manage.py seed_data --users $NUM_USERS"

if [[ "$CLEAR_DATA" == true ]]; then
    SEED_CMD="$SEED_CMD --clear"
fi

if [[ "$CREATE_ADMIN" == true ]]; then
    SEED_CMD="$SEED_CMD --admin"
fi

# Run the seeding command
if eval "$SEED_CMD"; then
    EXIT_CODE=0
    echo ""
    echo "=================================================="
    echo -e "${GREEN}✓ Database seeded successfully!${NC}"
    echo "=================================================="
    echo ""

    if [[ "$CREATE_ADMIN" == true ]]; then
        echo "Admin Login:"
        echo "  Email: admin@example.com"
        echo "  Password: admin123"
        echo ""
    fi

    echo "Test User Login:"
    echo "  Email: testuser1@example.com (or testuser2, testuser3, ...)"
    echo "  Password: password123"
    echo ""
else
    EXIT_CODE=1
    echo ""
    echo "=================================================="
    echo -e "${RED}✗ Database seeding failed!${NC}"
    echo "=================================================="
    echo ""
fi

exit $EXIT_CODE
