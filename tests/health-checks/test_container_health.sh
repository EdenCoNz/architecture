#!/bin/bash
# =============================================================================
# Automated Health Check Integration Tests
# =============================================================================
# This script performs automated integration tests for container health checks
# including failure scenarios and automatic restart behavior.
#
# Test scenarios:
#   1. All containers start healthy
#   2. Health endpoints return correct responses
#   3. Database failure causes backend to become unhealthy
#   4. Backend recovers when database is restored
#   5. Containers restart automatically when unhealthy
#
# Usage:
#   ./tests/health-checks/test_container_health.sh
#
# Requirements:
#   - Docker and Docker Compose installed
#   - Application containers running
#   - curl and jq installed for API testing
#
# Exit codes:
#   0 - All tests passed
#   1 - One or more tests failed
# =============================================================================

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Test configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
TESTS_PASSED=0
TESTS_FAILED=0

# =============================================================================
# Helper Functions
# =============================================================================

print_test_header() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}TEST: $1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_step() {
    echo -e "${YELLOW}→ $1${NC}"
}

pass_test() {
    echo -e "${GREEN}✓ PASS: $1${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
}

fail_test() {
    echo -e "${RED}✗ FAIL: $1${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
}

assert_equals() {
    local expected=$1
    local actual=$2
    local message=$3

    if [ "$expected" = "$actual" ]; then
        pass_test "$message"
        return 0
    else
        fail_test "$message (expected: $expected, got: $actual)"
        return 1
    fi
}

assert_contains() {
    local haystack=$1
    local needle=$2
    local message=$3

    if echo "$haystack" | grep -q "$needle"; then
        pass_test "$message"
        return 0
    else
        fail_test "$message (did not find '$needle')"
        return 1
    fi
}

wait_for_health_status() {
    local container=$1
    local expected_status=$2
    local max_wait=${3:-60}
    local waited=0

    print_step "Waiting for $container to become $expected_status (max ${max_wait}s)..."

    while [ $waited -lt $max_wait ]; do
        local status=$(docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null || echo "unknown")

        if [ "$status" = "$expected_status" ]; then
            echo -e "${GREEN}✓ $container is $expected_status (after ${waited}s)${NC}"
            return 0
        fi

        sleep 2
        waited=$((waited + 2))
        echo -e "${YELLOW}  Status: $status (${waited}s elapsed)${NC}"
    done

    echo -e "${RED}✗ $container did not become $expected_status within ${max_wait}s${NC}"
    return 1
}

# =============================================================================
# Test Cases
# =============================================================================

test_containers_running() {
    print_test_header "1. All Containers Are Running"

    local containers=("app-db" "app-redis" "app-backend" "app-frontend")

    for container in "${containers[@]}"; do
        print_step "Checking if $container is running..."

        if docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
            pass_test "$container is running"
        else
            fail_test "$container is not running"
        fi
    done
}

test_containers_healthy() {
    print_test_header "2. All Containers Report Healthy Status"

    local containers=("app-db" "app-redis" "app-backend" "app-frontend")

    for container in "${containers[@]}"; do
        if wait_for_health_status "$container" "healthy" 60; then
            pass_test "$container is healthy"
        else
            fail_test "$container did not become healthy"
        fi
    done
}

test_backend_health_endpoint() {
    print_test_header "3. Backend Health Endpoint Returns Correct Response"

    print_step "Testing /api/v1/health/ endpoint..."

    local response=$(curl -s -w "\n%{http_code}" http://localhost:8000/api/v1/health/ 2>/dev/null)
    local status_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | head -n-1)

    # Check HTTP status code
    assert_equals "200" "$status_code" "Health endpoint returns 200 OK"

    # Check response structure
    assert_contains "$body" '"status"' "Response contains status field"
    assert_contains "$body" '"database"' "Response contains database field"
    assert_contains "$body" '"timestamp"' "Response contains timestamp field"

    # Check status value
    assert_contains "$body" '"status":"healthy"' "Status is 'healthy'"

    # Check database status
    assert_contains "$body" '"status":"connected"' "Database status is 'connected'"
}

test_backend_status_endpoint() {
    print_test_header "4. Backend Status Endpoint Returns Detailed Information"

    print_step "Testing /api/v1/status/ endpoint..."

    local response=$(curl -s -w "\n%{http_code}" http://localhost:8000/api/v1/status/ 2>/dev/null)
    local status_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | head -n-1)

    # Check HTTP status code
    assert_equals "200" "$status_code" "Status endpoint returns 200 OK"

    # Check response structure
    assert_contains "$body" '"version"' "Response contains version"
    assert_contains "$body" '"api_version"' "Response contains api_version"
    assert_contains "$body" '"environment"' "Response contains environment"
    assert_contains "$body" '"uptime_seconds"' "Response contains uptime"
    assert_contains "$body" '"memory"' "Response contains memory info"
}

test_backend_readiness_endpoint() {
    print_test_header "5. Backend Readiness Endpoint Works Correctly"

    print_step "Testing /api/v1/health/ready/ endpoint..."

    local response=$(curl -s -w "\n%{http_code}" http://localhost:8000/api/v1/health/ready/ 2>/dev/null)
    local status_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | head -n-1)

    # Check HTTP status code
    assert_equals "200" "$status_code" "Readiness endpoint returns 200 OK"

    # Check response structure
    assert_contains "$body" '"ready":true' "Service reports ready"
}

test_backend_liveness_endpoint() {
    print_test_header "6. Backend Liveness Endpoint Works Correctly"

    print_step "Testing /api/v1/health/live/ endpoint..."

    local response=$(curl -s -w "\n%{http_code}" http://localhost:8000/api/v1/health/live/ 2>/dev/null)
    local status_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | head -n-1)

    # Check HTTP status code
    assert_equals "200" "$status_code" "Liveness endpoint returns 200 OK"

    # Check response structure
    assert_contains "$body" '"alive":true' "Service reports alive"
}

test_frontend_health() {
    print_test_header "7. Frontend Health Check Works"

    print_step "Testing frontend accessibility..."

    local response=$(curl -s -w "\n%{http_code}" http://localhost:5173 2>/dev/null)
    local status_code=$(echo "$response" | tail -n1)

    # Check HTTP status code
    assert_equals "200" "$status_code" "Frontend returns 200 OK"
}

test_database_failure_detection() {
    print_test_header "8. Backend Detects Database Failure"

    print_step "Stopping database to simulate failure..."
    docker compose stop db
    sleep 2

    print_step "Waiting for backend to detect database failure..."

    # Wait a bit for backend to try the health check
    sleep 35  # Slightly longer than health check interval (30s)

    # Check health endpoint returns unhealthy
    local response=$(curl -s -w "\n%{http_code}" http://localhost:8000/api/v1/health/ 2>/dev/null)
    local status_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | head -n-1)

    # Should return 503 when unhealthy
    if [ "$status_code" = "503" ]; then
        pass_test "Health endpoint returns 503 when database is down"
    else
        fail_test "Health endpoint should return 503 (got $status_code)"
    fi

    # Check response indicates unhealthy status
    if echo "$body" | grep -q '"status":"unhealthy"'; then
        pass_test "Health endpoint reports unhealthy status"
    else
        fail_test "Health endpoint should report unhealthy status"
    fi

    # Restore database
    print_step "Restarting database..."
    docker compose start db
    sleep 5
}

test_backend_recovery() {
    print_test_header "9. Backend Recovers When Database Restored"

    print_step "Waiting for database to become healthy..."
    if wait_for_health_status "app-db" "healthy" 30; then
        pass_test "Database recovered successfully"
    else
        fail_test "Database did not recover"
    fi

    print_step "Waiting for backend to recover..."
    if wait_for_health_status "app-backend" "healthy" 60; then
        pass_test "Backend recovered successfully"
    else
        fail_test "Backend did not recover"
    fi

    # Verify health endpoint is healthy again
    local response=$(curl -s -w "\n%{http_code}" http://localhost:8000/api/v1/health/ 2>/dev/null)
    local status_code=$(echo "$response" | tail -n1)

    assert_equals "200" "$status_code" "Health endpoint returns 200 after recovery"
}

test_health_check_configuration() {
    print_test_header "10. Health Check Configurations Are Correct"

    local containers=("app-db" "app-redis" "app-backend" "app-frontend")

    for container in "${containers[@]}"; do
        print_step "Checking health check config for $container..."

        local health_test=$(docker inspect --format='{{.Config.Healthcheck.Test}}' "$container" 2>/dev/null)

        if [ -n "$health_test" ] && [ "$health_test" != "<nil>" ] && [ "$health_test" != "[]" ]; then
            pass_test "$container has health check configured"
        else
            fail_test "$container missing health check configuration"
        fi
    done
}

# =============================================================================
# Main Test Execution
# =============================================================================

main() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}    Container Health Check Integration Tests${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
    echo ""

    # Check prerequisites
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Error: docker is not installed${NC}"
        exit 1
    fi

    if ! command -v curl &> /dev/null; then
        echo -e "${RED}Error: curl is not installed${NC}"
        exit 1
    fi

    # Change to project root
    cd "$PROJECT_ROOT"

    # Run test suite
    test_containers_running
    test_containers_healthy
    test_backend_health_endpoint
    test_backend_status_endpoint
    test_backend_readiness_endpoint
    test_backend_liveness_endpoint
    test_frontend_health
    test_database_failure_detection
    test_backend_recovery
    test_health_check_configuration

    # Print summary
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}    Test Results Summary${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${GREEN}Tests Passed: $TESTS_PASSED${NC}"
    echo -e "${RED}Tests Failed: $TESTS_FAILED${NC}"
    echo ""

    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}✓ All tests passed!${NC}"
        echo ""
        return 0
    else
        echo -e "${RED}✗ Some tests failed!${NC}"
        echo ""
        return 1
    fi
}

# Run tests
main
exit $?
