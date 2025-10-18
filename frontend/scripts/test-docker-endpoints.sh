#!/usr/bin/env bash

#==============================================================================
# Docker Container Endpoint Regression Test Script
#==============================================================================
#
# Purpose:
#   Automated testing of Docker container endpoints to prevent regressions.
#   Tests both health check endpoint and application root endpoint.
#
# Features:
#   - Validates /health endpoint returns 200 status and "healthy" text
#   - Validates / endpoint returns 200 status and valid HTML with DOCTYPE
#   - Verifies HTML contains React app div (id="root")
#   - Fail-fast with clear error messages indicating which endpoint failed
#   - Executable both locally and in CI/CD environments
#
# Usage:
#   Local:
#     ./scripts/test-docker-endpoints.sh [container-name] [port]
#
#   CI/CD:
#     docker run -d --name test-container -p 8080:8080 myimage:latest
#     ./scripts/test-docker-endpoints.sh test-container 8080
#
# Arguments:
#   $1 - Container name (default: "frontend-test")
#   $2 - Port number (default: "8080")
#
# Exit Codes:
#   0 - All tests passed
#   1 - Health endpoint test failed
#   2 - Root endpoint test failed (DOCTYPE check)
#   3 - Root endpoint test failed (React div check)
#   4 - Container not running
#   5 - Invalid arguments
#
# Requirements:
#   - curl (for HTTP requests)
#   - docker (for container status checks)
#   - Running Docker container on specified port
#
# Author: DevOps Engineer (Claude Code)
# Created: 2025-10-18
# Bug Reference: github-issue-10
#
#==============================================================================

set -euo pipefail  # Exit on error, undefined variable, or pipe failure

#==============================================================================
# Configuration
#==============================================================================

# Colors for output (disabled in CI environments)
if [[ -t 1 ]] && [[ "${CI:-false}" != "true" ]]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    NC='\033[0m' # No Color
else
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    NC=''
fi

# Default values
CONTAINER_NAME="${1:-frontend-test}"
PORT="${2:-8080}"
MAX_WAIT_TIME=30  # Maximum seconds to wait for endpoints to be ready
RETRY_INTERVAL=1   # Seconds between retries

#==============================================================================
# Utility Functions
#==============================================================================

print_header() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

#==============================================================================
# Validation Functions
#==============================================================================

validate_dependencies() {
    local missing_deps=()

    if ! command -v curl &> /dev/null; then
        missing_deps+=("curl")
    fi

    if ! command -v docker &> /dev/null; then
        missing_deps+=("docker")
    fi

    if [ ${#missing_deps[@]} -gt 0 ]; then
        print_error "Missing required dependencies: ${missing_deps[*]}"
        echo "Please install the missing dependencies and try again."
        exit 5
    fi
}

validate_container_running() {
    print_info "Checking if container '$CONTAINER_NAME' is running..."

    if ! docker ps --filter "name=$CONTAINER_NAME" --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
        print_error "Container '$CONTAINER_NAME' is not running"
        echo ""
        echo "Available running containers:"
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        echo ""
        echo "To start a container for testing, run:"
        echo "  docker run -d --name $CONTAINER_NAME -p $PORT:8080 frontend:latest"
        exit 4
    fi

    print_success "Container '$CONTAINER_NAME' is running"

    # Show container details
    echo ""
    echo "Container details:"
    docker ps --filter "name=$CONTAINER_NAME" --format "  Name:   {{.Names}}\n  Status: {{.Status}}\n  Ports:  {{.Ports}}"
    echo ""
}

#==============================================================================
# Test Functions
#==============================================================================

test_health_endpoint() {
    local endpoint="http://localhost:${PORT}/health"
    local attempts=0

    print_header "Test 1: Health Check Endpoint"
    print_info "Testing endpoint: $endpoint"
    print_info "Maximum wait time: ${MAX_WAIT_TIME}s"
    echo ""

    # Wait for health endpoint to be ready
    while [ $attempts -lt $MAX_WAIT_TIME ]; do
        if curl -f -s "$endpoint" > /dev/null 2>&1; then
            break
        fi

        attempts=$((attempts + 1))
        if [ $attempts -lt $MAX_WAIT_TIME ]; then
            echo "  Attempt $attempts/$MAX_WAIT_TIME - waiting for health endpoint..."
            sleep $RETRY_INTERVAL
        fi
    done

    # Test 1.1: HTTP status code check
    print_info "Test 1.1: Checking HTTP status code..."

    local http_status
    http_status=$(curl -s -o /dev/null -w "%{http_code}" "$endpoint" 2>/dev/null || echo "000")

    if [ "$http_status" != "200" ]; then
        print_error "Health endpoint returned HTTP $http_status (expected 200)"
        echo ""
        echo "Troubleshooting:"
        echo "  1. Check container logs: docker logs $CONTAINER_NAME"
        echo "  2. Verify nginx configuration includes /health endpoint"
        echo "  3. Ensure container is listening on port 8080"
        exit 1
    fi

    print_success "Health endpoint returned HTTP 200"

    # Test 1.2: Response body check
    print_info "Test 1.2: Checking response contains 'healthy' text..."

    local response_body
    response_body=$(curl -s "$endpoint" 2>/dev/null || echo "")

    if ! echo "$response_body" | grep -q "healthy"; then
        print_error "Health endpoint response does not contain 'healthy'"
        echo ""
        echo "Actual response:"
        echo "  $response_body"
        echo ""
        echo "Troubleshooting:"
        echo "  1. Check nginx.conf health endpoint configuration"
        echo "  2. Verify health endpoint returns correct response"
        exit 1
    fi

    print_success "Health endpoint contains 'healthy' text"
    echo ""
    echo "Response preview:"
    echo "  $response_body"
    echo ""
    print_success "✓ Health endpoint test PASSED"
    echo ""
}

test_root_endpoint() {
    local endpoint="http://localhost:${PORT}/"

    print_header "Test 2: Application Root Endpoint"
    print_info "Testing endpoint: $endpoint"
    echo ""

    # Test 2.1: HTTP status code check
    print_info "Test 2.1: Checking HTTP status code..."

    local http_status
    http_status=$(curl -s -o /dev/null -w "%{http_code}" "$endpoint" 2>/dev/null || echo "000")

    if [ "$http_status" != "200" ]; then
        print_error "Root endpoint returned HTTP $http_status (expected 200)"
        echo ""
        echo "Troubleshooting:"
        echo "  1. Check container logs: docker logs $CONTAINER_NAME"
        echo "  2. Verify dist/index.html exists in container"
        echo "  3. Check nginx root directory configuration"
        echo "  4. Verify file permissions on /usr/share/nginx/html"
        exit 2
    fi

    print_success "Root endpoint returned HTTP 200"

    # Test 2.2: DOCTYPE declaration check
    print_info "Test 2.2: Checking for valid HTML with DOCTYPE..."

    local response_body
    response_body=$(curl -s "$endpoint" 2>/dev/null || echo "")

    if ! echo "$response_body" | grep -qi "<!DOCTYPE html>"; then
        print_error "Root endpoint response does not contain '<!DOCTYPE html>'"
        echo ""
        echo "Response preview (first 500 chars):"
        echo "$response_body" | head -c 500
        echo ""
        echo ""
        echo "Troubleshooting:"
        echo "  1. Verify Vite build completed successfully"
        echo "  2. Check that dist/index.html was copied to container"
        echo "  3. Inspect container contents: docker exec $CONTAINER_NAME ls -la /usr/share/nginx/html"
        echo "  4. View file in container: docker exec $CONTAINER_NAME cat /usr/share/nginx/html/index.html"
        exit 2
    fi

    print_success "Response contains valid HTML with DOCTYPE"

    # Test 2.3: React app div check
    print_info "Test 2.3: Checking for React app root div (id=\"root\")..."

    if ! echo "$response_body" | grep -q 'id="root"'; then
        print_error "Root endpoint response does not contain React app div (id=\"root\")"
        echo ""
        echo "Response preview (first 1000 chars):"
        echo "$response_body" | head -c 1000
        echo ""
        echo ""
        echo "Troubleshooting:"
        echo "  1. Verify index.html template includes <div id=\"root\"></div>"
        echo "  2. Check Vite build output for errors"
        echo "  3. Ensure correct index.html is being served"
        exit 3
    fi

    print_success "Response contains React app div (id=\"root\")"
    echo ""
    echo "HTML structure preview:"
    echo "$response_body" | grep -o '<[^>]*id="root"[^>]*>' | head -1
    echo ""
    print_success "✓ Root endpoint test PASSED"
    echo ""
}

#==============================================================================
# Main Test Execution
#==============================================================================

main() {
    print_header "Docker Container Endpoint Regression Tests"

    echo "Configuration:"
    echo "  Container Name: $CONTAINER_NAME"
    echo "  Port:           $PORT"
    echo "  Max Wait:       ${MAX_WAIT_TIME}s"
    echo ""

    # Validate dependencies
    validate_dependencies

    # Validate container is running
    validate_container_running

    # Run tests
    test_health_endpoint
    test_root_endpoint

    # Final summary
    print_header "Test Summary"
    print_success "All endpoint tests PASSED ✓"
    echo ""
    echo "Tests completed:"
    echo "  ✓ Health endpoint returns 200 and contains 'healthy'"
    echo "  ✓ Root endpoint returns 200 with valid HTML"
    echo "  ✓ Root endpoint contains React app div (id=\"root\")"
    echo ""
    print_success "Container is serving content correctly!"
    echo ""

    exit 0
}

# Execute main function
main
