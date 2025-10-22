#!/bin/bash
#
# Test runner script for the backend testing infrastructure.
#
# This script runs different test suites and generates coverage reports.
# Run this after setting up the virtual environment and installing dependencies.
#
# Usage:
#   ./run_tests.sh              # Run all tests
#   ./run_tests.sh unit         # Run only unit tests
#   ./run_tests.sh integration  # Run only integration tests
#   ./run_tests.sh coverage     # Run with coverage report
#

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the backend directory
if [ ! -f "manage.py" ]; then
    echo -e "${RED}Error: This script must be run from the backend/ directory${NC}"
    exit 1
fi

# Function to print section headers
print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

# Function to print success messages
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print info messages
print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Default test suite
TEST_SUITE="all"

# Parse command line arguments
if [ $# -gt 0 ]; then
    TEST_SUITE=$1
fi

# Run tests based on suite
case $TEST_SUITE in
    unit)
        print_header "Running Unit Tests"
        pytest -m unit -v
        ;;
    integration)
        print_header "Running Integration Tests"
        pytest -m integration -v
        ;;
    e2e)
        print_header "Running End-to-End Tests"
        pytest -m e2e -v
        ;;
    acceptance)
        print_header "Running Acceptance Tests"
        pytest -m acceptance -v
        ;;
    coverage)
        print_header "Running Tests with Coverage Report"
        pytest --cov=apps --cov-report=term-missing --cov-report=html -v
        print_success "Coverage report generated"
        print_info "Open htmlcov/index.html to view detailed coverage report"
        ;;
    fast)
        print_header "Running Fast Tests (Parallel Execution)"
        pytest -n auto -v
        ;;
    smoke)
        print_header "Running Smoke Tests (Quick Validation)"
        pytest -m "not slow" -x
        ;;
    all)
        print_header "Running All Tests"
        pytest -v
        ;;
    verify)
        print_header "Verifying Testing Infrastructure"

        # Check if pytest is available
        print_info "Checking pytest installation..."
        python -c "import pytest; print(f'pytest version: {pytest.__version__}')"
        print_success "pytest is installed"

        # Check if factory-boy is available
        print_info "Checking factory-boy installation..."
        python -c "import factory; print(f'factory-boy version: {factory.__version__}')"
        print_success "factory-boy is installed"

        # Check if test files can be collected
        print_info "Collecting test files..."
        pytest --collect-only -q
        print_success "Test collection successful"

        # Run a quick smoke test
        print_info "Running quick smoke test..."
        pytest -m "not slow" -x --tb=short
        print_success "Smoke test passed"

        print_header "Testing Infrastructure Verified Successfully"
        ;;
    *)
        echo -e "${RED}Unknown test suite: $TEST_SUITE${NC}"
        echo ""
        echo "Usage: $0 [suite]"
        echo ""
        echo "Available test suites:"
        echo "  all          - Run all tests (default)"
        echo "  unit         - Run only unit tests"
        echo "  integration  - Run only integration tests"
        echo "  e2e          - Run only end-to-end tests"
        echo "  acceptance   - Run only acceptance tests"
        echo "  coverage     - Run tests with coverage report"
        echo "  fast         - Run tests in parallel"
        echo "  smoke        - Run quick smoke tests"
        echo "  verify       - Verify testing infrastructure"
        exit 1
        ;;
esac

# Print summary
echo ""
print_success "Test suite '$TEST_SUITE' completed successfully"
