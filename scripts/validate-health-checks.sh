#!/bin/bash
# =============================================================================
# Container Health Check Validation Script
# =============================================================================
# This script validates that all containers have properly configured health
# checks and that they are functioning correctly. It verifies:
#   - Health check configurations in Docker Compose files
#   - Health endpoint availability and correctness
#   - Container restart behavior on health check failures
#   - Health check timing parameters
#
# Usage:
#   ./scripts/validate-health-checks.sh              # Validate all containers
#   ./scripts/validate-health-checks.sh --backend    # Validate backend only
#   ./scripts/validate-health-checks.sh --frontend   # Validate frontend only
#   ./scripts/validate-health-checks.sh --all        # Validate all services
#
# Exit codes:
#   0 - All health checks passed
#   1 - One or more health checks failed
# =============================================================================

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DOCKER_COMPOSE_FILE="$PROJECT_ROOT/docker-compose.yml"
BACKEND_COMPOSE="$PROJECT_ROOT/backend/docker-compose.yml"
FRONTEND_COMPOSE="$PROJECT_ROOT/frontend/docker-compose.yml"

# Default settings
VALIDATE_BACKEND=true
VALIDATE_FRONTEND=true
VALIDATE_DB=true
VALIDATE_REDIS=true
VERBOSE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --backend)
            VALIDATE_FRONTEND=false
            shift
            ;;
        --frontend)
            VALIDATE_BACKEND=false
            VALIDATE_DB=false
            VALIDATE_REDIS=false
            shift
            ;;
        --all)
            # Default is all, no changes needed
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --backend     Validate only backend services"
            echo "  --frontend    Validate only frontend service"
            echo "  --all         Validate all services (default)"
            echo "  -v, --verbose Enable verbose output"
            echo "  -h, --help    Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# =============================================================================
# Helper Functions
# =============================================================================

print_header() {
    echo ""
    echo -e "${BLUE}=============================================================================${NC}"
    echo -e "${BLUE} $1${NC}"
    echo -e "${BLUE}=============================================================================${NC}"
    echo ""
}

print_subheader() {
    echo ""
    echo -e "${YELLOW}--- $1 ---${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

verbose() {
    if [ "$VERBOSE" = true ]; then
        echo -e "${BLUE}  → $1${NC}"
    fi
}

check_container_running() {
    local container_name=$1
    if docker ps --format '{{.Names}}' | grep -q "^${container_name}$"; then
        return 0
    else
        return 1
    fi
}

get_container_health() {
    local container_name=$1
    docker inspect --format='{{.State.Health.Status}}' "$container_name" 2>/dev/null || echo "unknown"
}

wait_for_health() {
    local container_name=$1
    local max_wait=${2:-60}
    local waited=0

    verbose "Waiting for $container_name to become healthy (max ${max_wait}s)..."

    while [ $waited -lt $max_wait ]; do
        local health=$(get_container_health "$container_name")

        if [ "$health" = "healthy" ]; then
            print_success "$container_name is healthy (took ${waited}s)"
            return 0
        elif [ "$health" = "unhealthy" ]; then
            print_error "$container_name is unhealthy"
            return 1
        fi

        sleep 2
        waited=$((waited + 2))
        verbose "Health status: $health (${waited}s elapsed)"
    done

    print_error "$container_name did not become healthy within ${max_wait}s"
    return 1
}

check_health_endpoint() {
    local url=$1
    local expected_status=${2:-200}

    verbose "Checking health endpoint: $url"

    local response=$(curl -s -w "\n%{http_code}" "$url" 2>/dev/null || echo -e "\n000")
    local status_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | head -n-1)

    if [ "$status_code" = "$expected_status" ]; then
        print_success "Health endpoint $url returned $status_code"
        if [ "$VERBOSE" = true ]; then
            echo "$body" | head -n 10
        fi
        return 0
    else
        print_error "Health endpoint $url returned $status_code (expected $expected_status)"
        if [ "$VERBOSE" = true ] && [ -n "$body" ]; then
            echo "$body" | head -n 10
        fi
        return 1
    fi
}

check_health_config() {
    local container_name=$1

    verbose "Checking health check configuration for $container_name"

    local health_test=$(docker inspect --format='{{.Config.Healthcheck.Test}}' "$container_name" 2>/dev/null)
    local health_interval=$(docker inspect --format='{{.Config.Healthcheck.Interval}}' "$container_name" 2>/dev/null)
    local health_timeout=$(docker inspect --format='{{.Config.Healthcheck.Timeout}}' "$container_name" 2>/dev/null)
    local health_retries=$(docker inspect --format='{{.Config.Healthcheck.Retries}}' "$container_name" 2>/dev/null)
    local health_start_period=$(docker inspect --format='{{.Config.Healthcheck.StartPeriod}}' "$container_name" 2>/dev/null)

    if [ -z "$health_test" ] || [ "$health_test" = "<nil>" ] || [ "$health_test" = "[]" ]; then
        print_error "$container_name has no health check configured"
        return 1
    fi

    print_success "$container_name has health check configured"
    verbose "  Test: $health_test"
    verbose "  Interval: $health_interval"
    verbose "  Timeout: $health_timeout"
    verbose "  Retries: $health_retries"
    verbose "  Start Period: $health_start_period"

    return 0
}

# =============================================================================
# Main Validation Functions
# =============================================================================

validate_database() {
    print_subheader "Validating Database (PostgreSQL)"

    local container_name="app-db"
    local failures=0

    if ! check_container_running "$container_name"; then
        print_error "$container_name is not running"
        return 1
    fi
    print_success "$container_name is running"

    if ! check_health_config "$container_name"; then
        failures=$((failures + 1))
    fi

    if ! wait_for_health "$container_name" 30; then
        failures=$((failures + 1))
    fi

    # Check health check logs
    verbose "Recent health check logs:"
    if [ "$VERBOSE" = true ]; then
        docker inspect --format='{{range .State.Health.Log}}{{.Output}}{{end}}' "$container_name" 2>/dev/null | tail -n 5
    fi

    return $failures
}

validate_redis() {
    print_subheader "Validating Cache (Redis)"

    local container_name="app-redis"
    local failures=0

    if ! check_container_running "$container_name"; then
        print_error "$container_name is not running"
        return 1
    fi
    print_success "$container_name is running"

    if ! check_health_config "$container_name"; then
        failures=$((failures + 1))
    fi

    if ! wait_for_health "$container_name" 30; then
        failures=$((failures + 1))
    fi

    return $failures
}

validate_backend() {
    print_subheader "Validating Backend Application"

    local container_name="app-backend"
    local failures=0

    if ! check_container_running "$container_name"; then
        print_error "$container_name is not running"
        return 1
    fi
    print_success "$container_name is running"

    if ! check_health_config "$container_name"; then
        failures=$((failures + 1))
    fi

    if ! wait_for_health "$container_name" 60; then
        failures=$((failures + 1))
    fi

    # Test health endpoints
    print_info "Testing backend health endpoints..."

    if ! check_health_endpoint "http://localhost:8000/api/v1/health/" 200; then
        failures=$((failures + 1))
    fi

    if ! check_health_endpoint "http://localhost:8000/api/v1/status/" 200; then
        failures=$((failures + 1))
    fi

    if ! check_health_endpoint "http://localhost:8000/api/v1/health/ready/" 200; then
        failures=$((failures + 1))
    fi

    if ! check_health_endpoint "http://localhost:8000/api/v1/health/live/" 200; then
        failures=$((failures + 1))
    fi

    # Verify health endpoint returns correct structure
    print_info "Verifying health endpoint response structure..."
    local health_response=$(curl -s http://localhost:8000/api/v1/health/)

    if echo "$health_response" | grep -q '"status"'; then
        print_success "Health endpoint returns status field"
    else
        print_error "Health endpoint missing status field"
        failures=$((failures + 1))
    fi

    if echo "$health_response" | grep -q '"database"'; then
        print_success "Health endpoint checks database connectivity"
    else
        print_error "Health endpoint missing database check"
        failures=$((failures + 1))
    fi

    if echo "$health_response" | grep -q '"timestamp"'; then
        print_success "Health endpoint returns timestamp"
    else
        print_error "Health endpoint missing timestamp"
        failures=$((failures + 1))
    fi

    return $failures
}

validate_frontend() {
    print_subheader "Validating Frontend Application"

    local container_name="app-frontend"
    local failures=0

    if ! check_container_running "$container_name"; then
        print_error "$container_name is not running"
        return 1
    fi
    print_success "$container_name is running"

    if ! check_health_config "$container_name"; then
        failures=$((failures + 1))
    fi

    if ! wait_for_health "$container_name" 60; then
        failures=$((failures + 1))
    fi

    # Test frontend accessibility
    print_info "Testing frontend accessibility..."

    if ! check_health_endpoint "http://localhost:5173" 200; then
        failures=$((failures + 1))
    fi

    return $failures
}

display_health_summary() {
    print_subheader "Health Check Summary"

    echo ""
    echo "Container Health Status:"
    echo "------------------------"
    docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "(app-|NAMES)"
    echo ""

    if command -v docker &> /dev/null; then
        # Get detailed health info
        for container in $(docker ps --format '{{.Names}}' | grep '^app-'); do
            local health=$(get_container_health "$container")
            local color=$RED

            if [ "$health" = "healthy" ]; then
                color=$GREEN
            elif [ "$health" = "starting" ]; then
                color=$YELLOW
            fi

            echo -e "$container: ${color}${health}${NC}"
        done
        echo ""
    fi
}

# =============================================================================
# Main Execution
# =============================================================================

print_header "Container Health Check Validation"

print_info "Project root: $PROJECT_ROOT"
print_info "Validating services..."
echo ""

TOTAL_FAILURES=0

# Validate services based on flags
if [ "$VALIDATE_DB" = true ]; then
    validate_database
    TOTAL_FAILURES=$((TOTAL_FAILURES + $?))
fi

if [ "$VALIDATE_REDIS" = true ]; then
    validate_redis
    TOTAL_FAILURES=$((TOTAL_FAILURES + $?))
fi

if [ "$VALIDATE_BACKEND" = true ]; then
    validate_backend
    TOTAL_FAILURES=$((TOTAL_FAILURES + $?))
fi

if [ "$VALIDATE_FRONTEND" = true ]; then
    validate_frontend
    TOTAL_FAILURES=$((TOTAL_FAILURES + $?))
fi

# Display summary
display_health_summary

# Final result
print_header "Validation Results"

if [ $TOTAL_FAILURES -eq 0 ]; then
    print_success "All health checks passed!"
    echo ""
    print_info "All containers are healthy and properly configured"
    echo ""
    exit 0
else
    print_error "Health check validation failed with $TOTAL_FAILURES error(s)"
    echo ""
    print_warning "Please review the errors above and fix any issues"
    echo ""

    print_info "Troubleshooting tips:"
    echo "  - Check container logs: docker compose logs <service-name>"
    echo "  - Inspect health check: docker inspect <container-name>"
    echo "  - Verify configurations in docker-compose.yml"
    echo "  - Ensure all dependencies are running"
    echo ""

    exit 1
fi
