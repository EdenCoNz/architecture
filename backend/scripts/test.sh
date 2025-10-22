#!/usr/bin/env bash

# Test Runner Script
# Runs tests with various options and configurations
# Supports different test types, coverage, and parallel execution

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
COVERAGE=false
PARALLEL=false
VERBOSE=false
FAIL_FAST=false
TEST_TYPE="all"
KEEP_DB=false
MARKERS=""
TEST_PATH=""

# Help message
show_help() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS] [TEST_PATH]

Run backend tests with various configurations.

OPTIONS:
    -c, --coverage          Run tests with coverage report
    -p, --parallel          Run tests in parallel (uses all CPU cores)
    -v, --verbose           Verbose output
    -f, --fail-fast         Stop on first failure
    -k, --keep-db           Keep test database between runs (faster)
    -m, --marker MARKER     Run tests with specific pytest marker
                            (unit, integration, e2e, acceptance, slow)
    -t, --type TYPE         Run specific test type (unit, integration, e2e, acceptance, all)
    -h, --help              Show this help message

EXAMPLES:
    $(basename "$0")                              # Run all tests
    $(basename "$0") -c                           # Run all tests with coverage
    $(basename "$0") -p                           # Run tests in parallel
    $(basename "$0") -c -p                        # Coverage + parallel
    $(basename "$0") -t unit                      # Run only unit tests
    $(basename "$0") -m slow                      # Run only tests marked as slow
    $(basename "$0") tests/unit/test_models.py    # Run specific test file
    $(basename "$0") -v -f                        # Verbose + stop on first failure

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--coverage)
            COVERAGE=true
            shift
            ;;
        -p|--parallel)
            PARALLEL=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -f|--fail-fast)
            FAIL_FAST=true
            shift
            ;;
        -k|--keep-db)
            KEEP_DB=true
            shift
            ;;
        -m|--marker)
            MARKERS="$2"
            shift 2
            ;;
        -t|--type)
            TEST_TYPE="$2"
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
            TEST_PATH="$1"
            shift
            ;;
    esac
done

echo ""
echo "=================================================="
echo -e "${BLUE}Backend API - Test Runner${NC}"
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

# Set test settings
export DJANGO_SETTINGS_MODULE="config.settings.testing"

# Build pytest command
PYTEST_ARGS=()

# Add test path if specified
if [[ -n "$TEST_PATH" ]]; then
    PYTEST_ARGS+=("$TEST_PATH")
else
    PYTEST_ARGS+=("tests/")
fi

# Add marker filter
if [[ -n "$MARKERS" ]]; then
    PYTEST_ARGS+=("-m" "$MARKERS")
elif [[ "$TEST_TYPE" != "all" ]]; then
    PYTEST_ARGS+=("-m" "$TEST_TYPE")
fi

# Add verbosity
if [[ "$VERBOSE" == true ]]; then
    PYTEST_ARGS+=("-vv")
else
    PYTEST_ARGS+=("-v")
fi

# Add fail-fast
if [[ "$FAIL_FAST" == true ]]; then
    PYTEST_ARGS+=("-x")
fi

# Add parallel execution
if [[ "$PARALLEL" == true ]]; then
    PYTEST_ARGS+=("-n" "auto")
    echo -e "${BLUE}Parallel execution enabled (using all CPU cores)${NC}"
fi

# Add database reuse
if [[ "$KEEP_DB" == true ]]; then
    PYTEST_ARGS+=("--reuse-db")
    echo -e "${BLUE}Database reuse enabled${NC}"
fi

# Add coverage options
if [[ "$COVERAGE" == true ]]; then
    PYTEST_ARGS+=("--cov=apps")
    PYTEST_ARGS+=("--cov-report=term-missing")
    PYTEST_ARGS+=("--cov-report=html")
    PYTEST_ARGS+=("--cov-report=xml")
    PYTEST_ARGS+=("--cov-branch")
    echo -e "${BLUE}Coverage tracking enabled${NC}"
fi

# Display configuration
echo "Test Configuration:"
echo "  Settings: $DJANGO_SETTINGS_MODULE"
echo "  Coverage: $COVERAGE"
echo "  Parallel: $PARALLEL"
echo "  Verbose: $VERBOSE"
echo "  Fail Fast: $FAIL_FAST"
echo "  Test Type: $TEST_TYPE"
if [[ -n "$MARKERS" ]]; then
    echo "  Markers: $MARKERS"
fi
if [[ -n "$TEST_PATH" ]]; then
    echo "  Test Path: $TEST_PATH"
fi
echo ""

# Run pre-test checks
echo "Running pre-test checks..."

# Check if pytest is installed
if ! command -v pytest >/dev/null 2>&1; then
    echo -e "${RED}Error: pytest is not installed!${NC}"
    echo "Install it with: pip install -r requirements/dev.txt"
    exit 1
fi

echo -e "${GREEN}✓ pytest is available${NC}"

# Check database connectivity
if python manage.py check_database --quiet 2>/dev/null; then
    echo -e "${GREEN}✓ Test database connection successful${NC}"
else
    echo -e "${YELLOW}⚠ Test database check failed${NC}"
    echo "  Tests may fail if database is required"
fi

echo ""
echo "=================================================="
echo "Running Tests"
echo "=================================================="
echo ""

# Run the tests
if pytest "${PYTEST_ARGS[@]}"; then
    EXIT_CODE=0
    echo ""
    echo "=================================================="
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo "=================================================="

    if [[ "$COVERAGE" == true ]]; then
        echo ""
        echo "Coverage report saved to: htmlcov/index.html"
        echo "View coverage: open htmlcov/index.html"
    fi
else
    EXIT_CODE=1
    echo ""
    echo "=================================================="
    echo -e "${RED}✗ Some tests failed${NC}"
    echo "=================================================="
fi

echo ""
exit $EXIT_CODE
