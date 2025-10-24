#!/bin/bash

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Frontend Container Functional Testing Script
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
# This script performs comprehensive functional testing of the frontend container
# to verify that it starts correctly, serves the application, and responds to
# requests as expected.
#
# Usage:
#   ./test-container-functional.sh <container-image> <container-port> [test-port]
#
# Arguments:
#   container-image: The Docker image to test (e.g., frontend:prod-abc123)
#   container-port: The internal container port (80 for production, 5173 for dev)
#   test-port: Optional external port to bind (default: 8080 for prod, 5173 for dev)
#
# Examples:
#   ./test-container-functional.sh frontend:prod-abc123 80 8080
#   ./test-container-functional.sh frontend:dev-abc123 5173
#
# Exit codes:
#   0: All tests passed
#   1: Container startup failed
#   2: Health check failed
#   3: Application endpoint failed
#   4: Content verification failed
#   5: Critical functionality failed
#
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

set -e  # Exit on error
set -o pipefail  # Catch errors in pipes

# ============================================================================
# Configuration
# ============================================================================

CONTAINER_IMAGE="${1:-}"
CONTAINER_PORT="${2:-80}"
TEST_PORT="${3:-8080}"

# Auto-detect test port based on container port if not specified
if [ "$#" -lt 3 ]; then
  if [ "$CONTAINER_PORT" = "5173" ]; then
    TEST_PORT="5173"
  fi
fi

# Test configuration
STARTUP_WAIT_TIME=15      # Seconds to wait for container startup
HEALTH_CHECK_TIMEOUT=5    # Seconds to wait for health check
MAX_RETRIES=5             # Maximum retries for endpoint checks
RETRY_DELAY=2             # Seconds between retries

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test results
TESTS_PASSED=0
TESTS_FAILED=0
CONTAINER_ID=""

# ============================================================================
# Utility Functions
# ============================================================================

log_info() {
  echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
  echo -e "${GREEN}[SUCCESS]${NC} $1"
  TESTS_PASSED=$((TESTS_PASSED + 1))
}

log_error() {
  echo -e "${RED}[ERROR]${NC} $1"
  TESTS_FAILED=$((TESTS_FAILED + 1))
}

log_warning() {
  echo -e "${YELLOW}[WARNING]${NC} $1"
}

cleanup() {
  if [ -n "$CONTAINER_ID" ]; then
    log_info "Cleaning up container: $CONTAINER_ID"
    docker stop "$CONTAINER_ID" >/dev/null 2>&1 || true
    docker rm "$CONTAINER_ID" >/dev/null 2>&1 || true
  fi
}

# Cleanup on script exit
trap cleanup EXIT

# ============================================================================
# Validation
# ============================================================================

if [ -z "$CONTAINER_IMAGE" ]; then
  echo "Usage: $0 <container-image> <container-port> [test-port]"
  echo ""
  echo "Examples:"
  echo "  $0 frontend:prod-abc123 80 8080"
  echo "  $0 frontend:dev-abc123 5173"
  exit 1
fi

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
  log_error "Docker is not running or not accessible"
  exit 1
fi

# Check if image exists
if ! docker image inspect "$CONTAINER_IMAGE" >/dev/null 2>&1; then
  log_error "Container image '$CONTAINER_IMAGE' not found"
  exit 1
fi

# ============================================================================
# Test Execution
# ============================================================================

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Frontend Container Functional Testing"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Configuration:"
echo "  Image:          $CONTAINER_IMAGE"
echo "  Container Port: $CONTAINER_PORT"
echo "  Test Port:      $TEST_PORT"
echo "  Startup Wait:   ${STARTUP_WAIT_TIME}s"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ============================================================================
# Test 1: Container Startup
# ============================================================================

echo "Test 1: Container Startup"
echo "─────────────────────────────────────────────────────────────────────────"

log_info "Starting container..."
CONTAINER_ID=$(docker run -d -p "${TEST_PORT}:${CONTAINER_PORT}" "$CONTAINER_IMAGE")

if [ -z "$CONTAINER_ID" ]; then
  log_error "Failed to start container"
  exit 1
fi

log_success "Container started: $CONTAINER_ID"
echo ""

# ============================================================================
# Test 2: Container Running State
# ============================================================================

echo "Test 2: Container Running State"
echo "─────────────────────────────────────────────────────────────────────────"

log_info "Waiting ${STARTUP_WAIT_TIME}s for container to initialize..."
sleep "$STARTUP_WAIT_TIME"

if docker ps | grep -q "$CONTAINER_ID"; then
  log_success "Container is running"
else
  log_error "Container is not running"
  echo ""
  echo "Container logs:"
  docker logs "$CONTAINER_ID" 2>&1
  exit 1
fi
echo ""

# ============================================================================
# Test 3: Container Health Status
# ============================================================================

echo "Test 3: Container Health Status"
echo "─────────────────────────────────────────────────────────────────────────"

HEALTH_STATUS=$(docker inspect --format='{{.State.Health.Status}}' "$CONTAINER_ID" 2>/dev/null || echo "no-healthcheck")

if [ "$HEALTH_STATUS" = "healthy" ]; then
  log_success "Container health check: healthy"
elif [ "$HEALTH_STATUS" = "no-healthcheck" ]; then
  log_warning "Container has no health check configured (expected for dev containers)"
else
  log_error "Container health check failed: $HEALTH_STATUS"
  echo ""
  echo "Container logs:"
  docker logs "$CONTAINER_ID" 2>&1 | tail -50
  exit 2
fi
echo ""

# ============================================================================
# Test 4: Health Endpoint (Production containers only)
# ============================================================================

if [ "$CONTAINER_PORT" = "80" ]; then
  echo "Test 4: Health Endpoint"
  echo "─────────────────────────────────────────────────────────────────────────"

  log_info "Testing health endpoint at http://localhost:${TEST_PORT}/health"

  HEALTH_RESPONSE=$(curl -s -w "\n%{http_code}" "http://localhost:${TEST_PORT}/health" 2>&1 || echo "")
  HEALTH_HTTP_CODE=$(echo "$HEALTH_RESPONSE" | tail -1)
  HEALTH_BODY=$(echo "$HEALTH_RESPONSE" | head -n -1)

  if [ "$HEALTH_HTTP_CODE" = "200" ]; then
    log_success "Health endpoint responding with HTTP 200"
    log_info "Health response: $HEALTH_BODY"
  else
    log_error "Health endpoint failed with HTTP $HEALTH_HTTP_CODE"
    exit 2
  fi
  echo ""
fi

# ============================================================================
# Test 5: Application Endpoint
# ============================================================================

echo "Test 5: Application Endpoint"
echo "─────────────────────────────────────────────────────────────────────────"

log_info "Testing application endpoint at http://localhost:${TEST_PORT}/"

for i in $(seq 1 $MAX_RETRIES); do
  log_info "Attempt $i/$MAX_RETRIES..."

  RESPONSE=$(curl -s -w "\n%{http_code}" "http://localhost:${TEST_PORT}/" 2>&1 || echo "")
  HTTP_CODE=$(echo "$RESPONSE" | tail -1)

  if [ "$HTTP_CODE" = "200" ]; then
    log_success "Application endpoint responding with HTTP 200"
    break
  else
    if [ "$i" -eq "$MAX_RETRIES" ]; then
      log_error "Application endpoint failed after $MAX_RETRIES attempts (HTTP $HTTP_CODE)"
      echo ""
      echo "Container logs:"
      docker logs "$CONTAINER_ID" 2>&1 | tail -50
      exit 3
    else
      log_warning "Attempt $i failed with HTTP $HTTP_CODE, retrying in ${RETRY_DELAY}s..."
      sleep "$RETRY_DELAY"
    fi
  fi
done
echo ""

# ============================================================================
# Test 6: Content Verification
# ============================================================================

echo "Test 6: Content Verification"
echo "─────────────────────────────────────────────────────────────────────────"

log_info "Verifying application content..."

PAGE_CONTENT=$(curl -s "http://localhost:${TEST_PORT}/" 2>&1)

# Check for HTML structure
if echo "$PAGE_CONTENT" | grep -q "<!DOCTYPE html>"; then
  log_success "HTML DOCTYPE declaration found"
else
  log_error "HTML DOCTYPE declaration not found"
  exit 4
fi

# Check for root element
if echo "$PAGE_CONTENT" | grep -q "<div id=\"root\">"; then
  log_success "React root element found"
else
  log_error "React root element not found"
  exit 4
fi

# Check for script tags (bundled JavaScript)
if echo "$PAGE_CONTENT" | grep -q "<script"; then
  log_success "JavaScript bundle references found"
else
  log_error "JavaScript bundle references not found"
  exit 4
fi
echo ""

# ============================================================================
# Test 7: Static Assets
# ============================================================================

echo "Test 7: Static Assets"
echo "─────────────────────────────────────────────────────────────────────────"

log_info "Testing static asset delivery..."

# Test favicon or any static file
FAVICON_RESPONSE=$(curl -s -w "\n%{http_code}" "http://localhost:${TEST_PORT}/vite.svg" 2>&1 || echo "")
FAVICON_HTTP_CODE=$(echo "$FAVICON_RESPONSE" | tail -1)

if [ "$FAVICON_HTTP_CODE" = "200" ]; then
  log_success "Static assets accessible (HTTP 200)"
else
  log_warning "Static asset test returned HTTP $FAVICON_HTTP_CODE (may be expected if file doesn't exist)"
fi
echo ""

# ============================================================================
# Test 8: Response Headers (Production containers only)
# ============================================================================

if [ "$CONTAINER_PORT" = "80" ]; then
  echo "Test 8: Security Headers"
  echo "─────────────────────────────────────────────────────────────────────────"

  log_info "Checking security headers..."

  HEADERS=$(curl -s -I "http://localhost:${TEST_PORT}/" 2>&1)

  # Check for security headers
  if echo "$HEADERS" | grep -qi "X-Frame-Options"; then
    log_success "X-Frame-Options header present"
  else
    log_warning "X-Frame-Options header not found"
  fi

  if echo "$HEADERS" | grep -qi "X-Content-Type-Options"; then
    log_success "X-Content-Type-Options header present"
  else
    log_warning "X-Content-Type-Options header not found"
  fi

  if echo "$HEADERS" | grep -qi "X-XSS-Protection"; then
    log_success "X-XSS-Protection header present"
  else
    log_warning "X-XSS-Protection header not found"
  fi
  echo ""
fi

# ============================================================================
# Test 9: Container Logs
# ============================================================================

echo "Test 9: Container Logs Analysis"
echo "─────────────────────────────────────────────────────────────────────────"

log_info "Analyzing container logs for errors..."

CONTAINER_LOGS=$(docker logs "$CONTAINER_ID" 2>&1)

# Check for common error patterns
ERROR_COUNT=$(echo "$CONTAINER_LOGS" | grep -iE "error|exception|failed|fatal" | wc -l)

if [ "$ERROR_COUNT" -eq 0 ]; then
  log_success "No errors found in container logs"
else
  log_warning "Found $ERROR_COUNT potential error messages in logs"
  echo ""
  echo "Error messages:"
  echo "$CONTAINER_LOGS" | grep -iE "error|exception|failed|fatal" | head -10
fi
echo ""

# ============================================================================
# Test 10: Container Resource Usage
# ============================================================================

echo "Test 10: Container Resource Usage"
echo "─────────────────────────────────────────────────────────────────────────"

log_info "Checking container resource usage..."

CONTAINER_STATS=$(docker stats "$CONTAINER_ID" --no-stream --format "CPU: {{.CPUPerc}} | Memory: {{.MemUsage}}")

log_success "Container resource usage: $CONTAINER_STATS"
echo ""

# ============================================================================
# Test Summary
# ============================================================================

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Container Image: $CONTAINER_IMAGE"
echo "  Container ID:    $CONTAINER_ID"
echo ""
echo "  Tests Passed:    $TESTS_PASSED"
echo "  Tests Failed:    $TESTS_FAILED"
echo ""

if [ "$TESTS_FAILED" -eq 0 ]; then
  log_success "All functional tests passed!"
  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  exit 0
else
  log_error "Some tests failed. Please review the output above."
  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  exit 5
fi
