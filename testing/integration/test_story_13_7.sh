#!/bin/bash
# =============================================================================
# Test Runner for Story 13.7: Test Assessment Data Submission
# =============================================================================
# This script runs the integration tests for assessment data submission
# Usage: ./test_story_13_7.sh [options]
# Options:
#   --verbose     Show detailed test output
#   --coverage    Generate coverage report
#   --html        Generate HTML report
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TESTING_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PROJECT_ROOT="$(cd "$TESTING_ROOT/.." && pwd)"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Parse arguments
VERBOSE=""
COVERAGE=""
HTML=""

for arg in "$@"; do
    case $arg in
        --verbose)
            VERBOSE="-vv"
            ;;
        --coverage)
            COVERAGE="--cov=apps.assessments --cov-report=term --cov-report=html"
            ;;
        --html)
            HTML="--html=reports/html/story-13.7-report.html --self-contained-html"
            ;;
    esac
done

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Story 13.7: Test Assessment Data Submission${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if running in Docker or local
if [ -f "/.dockerenv" ]; then
    echo -e "${YELLOW}Running in Docker container${NC}"
    cd /app/testing
else
    echo -e "${YELLOW}Running locally${NC}"
    cd "$TESTING_ROOT"
fi

echo -e "${YELLOW}Running integration tests for assessment data submission...${NC}"
echo ""

# Run pytest with Story 13.7 tests
pytest integration/test_assessment_submission.py \
    -m assessment \
    $VERBOSE \
    $COVERAGE \
    $HTML \
    --tb=short \
    --color=yes \
    || {
        echo ""
        echo -e "${RED}Tests failed!${NC}"
        exit 1
    }

echo ""
echo -e "${GREEN}All tests passed!${NC}"
echo ""

if [ -n "$COVERAGE" ]; then
    echo -e "${GREEN}Coverage report generated at: reports/coverage/index.html${NC}"
fi

if [ -n "$HTML" ]; then
    echo -e "${GREEN}HTML report generated at: reports/html/story-13.7-report.html${NC}"
fi
