#!/usr/bin/env bash
# =============================================================================
# Test Orchestration Script (Feature #13 - Story 13.1)
# =============================================================================
# Runs end-to-end tests in an isolated test environment.
# Ensures test services are running, executes test suites, and collects
# artifacts in the testing/ folder structure.
#
# Usage:
#   ./testing/run-tests.sh                  # Run all tests
#   ./testing/run-tests.sh --suite e2e      # Run specific test suite
#   ./testing/run-tests.sh --clean          # Clean and rebuild test environment
#   ./testing/run-tests.sh --help           # Show usage information
# =============================================================================

set -euo pipefail

# Script directory (absolute path)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
TEST_ENV_FILE="${PROJECT_ROOT}/.env.test"
COMPOSE_FILES="-f ${PROJECT_ROOT}/docker-compose.yml -f ${PROJECT_ROOT}/compose.test.yml"
COMPOSE_PROJECT="app-test"
REPORTS_DIR="${SCRIPT_DIR}/reports"

# Test suites
TEST_SUITE_ALL="all"
TEST_SUITE_E2E="e2e"
TEST_SUITE_INTEGRATION="integration"
TEST_SUITE_VISUAL="visual"
TEST_SUITE_PERFORMANCE="performance"

# Default options
SUITE="${TEST_SUITE_ALL}"
CLEAN=false
VERBOSE=false
HEADLESS=true

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------

log_info() {
    echo -e "${BLUE}[INFO]${NC} $*"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*"
}

print_header() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$*${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
}

show_usage() {
    cat << EOF
Test Orchestration Script (Feature #13 - Story 13.1)

USAGE:
    ./testing/run-tests.sh [OPTIONS]

OPTIONS:
    -s, --suite SUITE       Test suite to run (all|e2e|integration|visual|performance)
                           Default: all

    -c, --clean            Clean test environment before running tests
                           (removes volumes and rebuilds containers)

    -v, --verbose          Verbose output (show all logs)

    --headed               Run E2E tests in headed mode (visible browser)

    -h, --help             Show this help message

EXAMPLES:
    # Run all tests with clean environment
    ./testing/run-tests.sh --clean

    # Run only E2E tests
    ./testing/run-tests.sh --suite e2e

    # Run E2E tests with visible browser
    ./testing/run-tests.sh --suite e2e --headed

    # Run integration tests with verbose output
    ./testing/run-tests.sh --suite integration --verbose

TEST ENVIRONMENT:
    The test environment is isolated from development and production:
    - Separate database (port 5433)
    - Separate Redis cache (port 6380)
    - Separate backend instance (port 8001)
    - Separate frontend instance (port 5174)
    - Test artifacts stored in: ${REPORTS_DIR}

ARTIFACTS:
    Test results, logs, screenshots, and reports are stored in:
    ${SCRIPT_DIR}/reports/

    Subdirectories:
    - logs/         Application and test execution logs
    - screenshots/  E2E test failure screenshots
    - videos/       E2E test recordings
    - coverage/     Code coverage reports
    - html/         HTML test reports
    - json/         JSON test reports

EOF
}

# -----------------------------------------------------------------------------
# Argument Parsing
# -----------------------------------------------------------------------------

parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -s|--suite)
                SUITE="$2"
                shift 2
                ;;
            -c|--clean)
                CLEAN=true
                shift
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            --headed)
                HEADLESS=false
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done

    # Validate test suite
    case "${SUITE}" in
        all|e2e|integration|visual|performance)
            ;;
        *)
            log_error "Invalid test suite: ${SUITE}"
            log_info "Valid options: all, e2e, integration, visual, performance"
            exit 1
            ;;
    esac
}

# -----------------------------------------------------------------------------
# Environment Setup
# -----------------------------------------------------------------------------

setup_test_environment() {
    print_header "Setting Up Test Environment"

    # Check if .env.test exists
    if [[ ! -f "${TEST_ENV_FILE}" ]]; then
        log_error "Test environment file not found: ${TEST_ENV_FILE}"
        exit 1
    fi

    # Create reports directory structure
    log_info "Creating reports directory structure..."
    mkdir -p "${REPORTS_DIR}"/{logs,screenshots,videos,coverage,html,json}

    # Clean environment if requested
    if [[ "${CLEAN}" == "true" ]]; then
        log_info "Cleaning test environment..."
        docker compose ${COMPOSE_FILES} --env-file "${TEST_ENV_FILE}" down -v
        docker compose ${COMPOSE_FILES} --env-file "${TEST_ENV_FILE}" build --no-cache
    fi

    log_success "Test environment setup complete"
}

# -----------------------------------------------------------------------------
# Service Management
# -----------------------------------------------------------------------------

start_test_services() {
    print_header "Starting Test Services"

    log_info "Starting test infrastructure (database, redis, backend, frontend, proxy)..."

    if [[ "${VERBOSE}" == "true" ]]; then
        docker compose ${COMPOSE_FILES} --env-file "${TEST_ENV_FILE}" up -d
    else
        docker compose ${COMPOSE_FILES} --env-file "${TEST_ENV_FILE}" up -d > /dev/null 2>&1
    fi

    # Wait for services to be healthy
    log_info "Waiting for services to be healthy..."
    wait_for_services

    log_success "All test services are running and healthy"
}

wait_for_services() {
    local max_attempts=60
    local attempt=0
    local services=("db" "redis" "backend" "frontend" "proxy")

    for service in "${services[@]}"; do
        attempt=0
        while [[ $attempt -lt $max_attempts ]]; do
            if docker compose ${COMPOSE_FILES} --env-file "${TEST_ENV_FILE}" ps "${service}" | grep -q "healthy"; then
                log_success "${service} is healthy"
                break
            fi

            attempt=$((attempt + 1))
            if [[ $attempt -eq $max_attempts ]]; then
                log_error "${service} failed to become healthy"
                docker compose ${COMPOSE_FILES} --env-file "${TEST_ENV_FILE}" logs "${service}"
                exit 1
            fi

            sleep 2
        done
    done
}

stop_test_services() {
    print_header "Stopping Test Services"

    log_info "Stopping test services..."
    docker compose ${COMPOSE_FILES} --env-file "${TEST_ENV_FILE}" down

    if [[ "${CLEAN}" == "true" ]]; then
        log_info "Removing test volumes..."
        docker compose ${COMPOSE_FILES} --env-file "${TEST_ENV_FILE}" down -v
    fi

    log_success "Test services stopped"
}

# -----------------------------------------------------------------------------
# Test Execution
# -----------------------------------------------------------------------------

run_e2e_tests() {
    print_header "Running E2E Tests (Playwright)"

    local playwright_opts="--reporter=html,json,list"

    if [[ "${HEADLESS}" == "true" ]]; then
        playwright_opts="${playwright_opts}"
    else
        playwright_opts="${playwright_opts} --headed"
    fi

    log_info "Executing E2E test suite..."

    docker compose ${COMPOSE_FILES} --env-file "${TEST_ENV_FILE}" \
        run --rm test-runner \
        npx playwright test ${playwright_opts} \
        --output="${REPORTS_DIR}" \
        || return 1

    log_success "E2E tests completed"
}

run_integration_tests() {
    print_header "Running Integration Tests (pytest)"

    log_info "Executing integration test suite..."

    docker compose ${COMPOSE_FILES} --env-file "${TEST_ENV_FILE}" \
        run --rm test-runner \
        pytest integration/ \
        --verbose \
        --tb=short \
        --html="${REPORTS_DIR}/html/integration-report.html" \
        --json-report \
        --json-report-file="${REPORTS_DIR}/json/integration-report.json" \
        --cov=backend \
        --cov-report=html:"${REPORTS_DIR}/coverage/integration" \
        || return 1

    log_success "Integration tests completed"
}

run_visual_tests() {
    print_header "Running Visual Regression Tests"

    log_info "Executing visual regression test suite..."

    docker compose ${COMPOSE_FILES} --env-file "${TEST_ENV_FILE}" \
        run --rm test-runner \
        npx playwright test \
        --config=visual/playwright.config.ts \
        --reporter=html,json,list \
        --output="${REPORTS_DIR}" \
        || return 1

    log_success "Visual regression tests completed"
}

run_performance_tests() {
    print_header "Running Performance Tests (Locust)"

    log_info "Executing performance test suite with threshold validation..."

    # Ensure reports directories exist
    mkdir -p "${REPORTS_DIR}/html"
    mkdir -p "${REPORTS_DIR}/json"
    mkdir -p "${REPORTS_DIR}/csv"

    # Run Locust load tests with performance threshold validation
    docker compose ${COMPOSE_FILES} --env-file "${TEST_ENV_FILE}" \
        run --rm test-runner \
        bash -c "cd /app/testing && locust \
        -f performance/locustfile.py \
        --host=http://proxy:80 \
        --headless \
        --users 50 \
        --spawn-rate 5 \
        --run-time 120s \
        --html=reports/html/performance-report.html \
        --csv=reports/csv/performance-data \
        --json" \
        || return 1

    log_info "Performance tests completed - analyzing results..."

    # Generate comprehensive performance reports
    docker compose ${COMPOSE_FILES} --env-file "${TEST_ENV_FILE}" \
        run --rm test-runner \
        python3 performance/report_generator.py \
        --input reports/csv/performance-data_stats.json \
        --output-dir reports/ \
        || log_warning "Performance report generation failed (non-critical)"

    log_success "Performance tests and analysis completed"
    log_info "View reports:"
    log_info "  HTML: ${REPORTS_DIR}/html/performance-report.html"
    log_info "  JSON: ${REPORTS_DIR}/json/performance-report.json"
    log_info "  CSV:  ${REPORTS_DIR}/csv/performance-data*.csv"
}

run_all_tests() {
    print_header "Running All Test Suites"

    local failed=0

    run_e2e_tests || failed=1
    run_integration_tests || failed=1
    run_visual_tests || failed=1
    run_performance_tests || failed=1

    return $failed
}

execute_tests() {
    local exit_code=0

    case "${SUITE}" in
        all)
            run_all_tests || exit_code=1
            ;;
        e2e)
            run_e2e_tests || exit_code=1
            ;;
        integration)
            run_integration_tests || exit_code=1
            ;;
        visual)
            run_visual_tests || exit_code=1
            ;;
        performance)
            run_performance_tests || exit_code=1
            ;;
    esac

    return $exit_code
}

# -----------------------------------------------------------------------------
# Results and Cleanup
# -----------------------------------------------------------------------------

display_results() {
    print_header "Test Results Summary"

    log_info "Test artifacts location: ${REPORTS_DIR}"

    if [[ -d "${REPORTS_DIR}/html" ]]; then
        log_info "HTML reports:"
        find "${REPORTS_DIR}/html" -name "*.html" -type f | while read -r report; do
            echo "  - ${report}"
        done
    fi

    if [[ -d "${REPORTS_DIR}/screenshots" ]]; then
        local screenshot_count=$(find "${REPORTS_DIR}/screenshots" -type f | wc -l)
        log_info "Screenshots: ${screenshot_count}"
    fi

    if [[ -d "${REPORTS_DIR}/videos" ]]; then
        local video_count=$(find "${REPORTS_DIR}/videos" -type f | wc -l)
        log_info "Videos: ${video_count}"
    fi

    echo ""
    log_info "View reports:"
    echo "  - HTML: open ${REPORTS_DIR}/html/index.html"
    echo "  - Coverage: open ${REPORTS_DIR}/coverage/index.html"
    echo "  - Playwright: npx playwright show-report ${REPORTS_DIR}/playwright-report"
}

cleanup_on_exit() {
    local exit_code=$?

    if [[ $exit_code -ne 0 ]]; then
        log_warning "Tests failed with exit code: ${exit_code}"

        # Collect logs on failure
        log_info "Collecting service logs..."
        docker compose ${COMPOSE_FILES} --env-file "${TEST_ENV_FILE}" logs > "${REPORTS_DIR}/logs/services.log" 2>&1
    fi

    # Stop services unless --keep option is used
    if [[ "${CLEAN}" != "true" ]] && [[ -z "${KEEP_RUNNING:-}" ]]; then
        stop_test_services
    fi
}

# -----------------------------------------------------------------------------
# Main Execution
# -----------------------------------------------------------------------------

main() {
    # Parse command line arguments
    parse_arguments "$@"

    # Set up cleanup handler
    trap cleanup_on_exit EXIT

    # Run test workflow
    setup_test_environment
    start_test_services

    if execute_tests; then
        log_success "All tests passed!"
        display_results
        exit 0
    else
        log_error "Some tests failed"
        display_results
        exit 1
    fi
}

# Run main function
main "$@"
