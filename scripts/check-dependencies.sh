#!/usr/bin/env bash
# =============================================================================
# Service Dependency Health Check Script
# =============================================================================
# This script validates that all services in the Docker Compose stack are
# healthy and properly connected, with clear error messages when dependencies
# are not available.
#
# Usage:
#   ./scripts/check-dependencies.sh              # Check all services
#   ./scripts/check-dependencies.sh --verbose    # Show detailed status
#   ./scripts/check-dependencies.sh --wait 60    # Wait up to 60s for services
#
# Exit codes:
#   0 - All services healthy
#   1 - One or more services unhealthy
#   2 - Script error or invalid arguments
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="${PROJECT_ROOT}/docker-compose.yml"

# Default options
VERBOSE=false
WAIT_TIMEOUT=0
QUIET=false

# Service dependency order (from least to most dependent)
declare -a SERVICE_ORDER=(
    "db"
    "redis"
    "backend"
    "frontend"
    "proxy"
)

# Service dependency mapping
declare -A SERVICE_DEPENDENCIES
SERVICE_DEPENDENCIES[db]=""
SERVICE_DEPENDENCIES[redis]=""
SERVICE_DEPENDENCIES[backend]="db redis"
SERVICE_DEPENDENCIES[frontend]="backend"
SERVICE_DEPENDENCIES[proxy]="frontend backend"

# Service descriptions
declare -A SERVICE_DESCRIPTIONS
SERVICE_DESCRIPTIONS[db]="PostgreSQL Database"
SERVICE_DESCRIPTIONS[redis]="Redis Cache"
SERVICE_DESCRIPTIONS[backend]="Django Backend API"
SERVICE_DESCRIPTIONS[frontend]="React Frontend Application"
SERVICE_DESCRIPTIONS[proxy]="Nginx Reverse Proxy"

# Service health check endpoints
declare -A HEALTH_ENDPOINTS
HEALTH_ENDPOINTS[db]="internal"  # Uses pg_isready
HEALTH_ENDPOINTS[redis]="internal"  # Uses redis-cli
HEALTH_ENDPOINTS[backend]="http://localhost:8000/api/v1/health/"
HEALTH_ENDPOINTS[frontend]="http://localhost:5173"
HEALTH_ENDPOINTS[proxy]="http://localhost:80/health"

# =============================================================================
# Helper Functions
# =============================================================================

print_header() {
    if [ "$QUIET" = false ]; then
        echo -e "\n${BLUE}═══════════════════════════════════════════════════════════════${NC}"
        echo -e "${BLUE}  Service Dependency Health Check${NC}"
        echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}\n"
    fi
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    if [ "$VERBOSE" = true ]; then
        echo -e "${BLUE}ℹ${NC} $1"
    fi
}

# =============================================================================
# Service Check Functions
# =============================================================================

check_compose_file() {
    if [ ! -f "$COMPOSE_FILE" ]; then
        print_error "docker-compose.yml not found at: $COMPOSE_FILE"
        exit 2
    fi
    print_info "Using compose file: $COMPOSE_FILE"
}

check_service_running() {
    local service=$1
    local container_name=$(docker compose -f "$COMPOSE_FILE" ps -q "$service" 2>/dev/null)

    if [ -z "$container_name" ]; then
        return 1
    fi

    local state=$(docker inspect -f '{{.State.Status}}' "$container_name" 2>/dev/null)
    if [ "$state" = "running" ]; then
        return 0
    fi

    return 1
}

check_service_health() {
    local service=$1
    local container_name=$(docker compose -f "$COMPOSE_FILE" ps -q "$service" 2>/dev/null)

    if [ -z "$container_name" ]; then
        echo "not_running"
        return 1
    fi

    local health=$(docker inspect -f '{{.State.Health.Status}}' "$container_name" 2>/dev/null)

    # If no health check defined, check if running
    if [ -z "$health" ] || [ "$health" = "<no value>" ]; then
        local state=$(docker inspect -f '{{.State.Status}}' "$container_name" 2>/dev/null)
        if [ "$state" = "running" ]; then
            echo "running"
            return 0
        else
            echo "not_running"
            return 1
        fi
    fi

    echo "$health"

    if [ "$health" = "healthy" ]; then
        return 0
    fi

    return 1
}

get_service_uptime() {
    local service=$1
    local container_name=$(docker compose -f "$COMPOSE_FILE" ps -q "$service" 2>/dev/null)

    if [ -z "$container_name" ]; then
        echo "0s"
        return
    fi

    local started=$(docker inspect -f '{{.State.StartedAt}}' "$container_name" 2>/dev/null)
    if [ -z "$started" ]; then
        echo "0s"
        return
    fi

    # Calculate uptime (simplified - just show started time)
    local uptime=$(docker inspect -f '{{.State.Status}}' "$container_name" 2>/dev/null)
    echo "$uptime since $(date -d "$started" +%H:%M:%S 2>/dev/null || echo 'unknown')"
}

check_dependency_chain() {
    local service=$1
    local dependencies="${SERVICE_DEPENDENCIES[$service]}"

    if [ -z "$dependencies" ]; then
        return 0
    fi

    local all_healthy=true
    local failed_deps=()

    for dep in $dependencies; do
        local dep_health=$(check_service_health "$dep")
        if [ "$dep_health" != "healthy" ] && [ "$dep_health" != "running" ]; then
            all_healthy=false
            failed_deps+=("$dep")
        fi
    done

    if [ "$all_healthy" = false ]; then
        echo "FAILED_DEPENDENCIES"
        for dep in "${failed_deps[@]}"; do
            echo "  - $dep (${SERVICE_DESCRIPTIONS[$dep]})" >&2
        done
        return 1
    fi

    return 0
}

# =============================================================================
# Main Check Logic
# =============================================================================

check_all_services() {
    local all_healthy=true
    local failed_services=()

    print_header

    echo "Dependency Order: ${SERVICE_ORDER[*]}"
    echo ""

    for service in "${SERVICE_ORDER[@]}"; do
        local description="${SERVICE_DESCRIPTIONS[$service]}"

        print_info "Checking $service ($description)..."

        # Check if service is running
        if ! check_service_running "$service"; then
            print_error "$service is not running"
            all_healthy=false
            failed_services+=("$service:not_running")
            continue
        fi

        # Check service health
        local health=$(check_service_health "$service")

        if [ "$health" = "healthy" ] || [ "$health" = "running" ]; then
            local uptime=$(get_service_uptime "$service")
            print_success "$service is healthy ($uptime)"

            # In verbose mode, show dependencies
            if [ "$VERBOSE" = true ]; then
                local deps="${SERVICE_DEPENDENCIES[$service]}"
                if [ -n "$deps" ]; then
                    echo -e "  ${BLUE}├─${NC} Dependencies: $deps"
                fi
                local endpoint="${HEALTH_ENDPOINTS[$service]}"
                if [ "$endpoint" != "internal" ]; then
                    echo -e "  ${BLUE}└─${NC} Health check: $endpoint"
                fi
            fi
        else
            # Check if it's a dependency issue
            local dep_check=$(check_dependency_chain "$service" 2>&1)

            if echo "$dep_check" | grep -q "FAILED_DEPENDENCIES"; then
                print_error "$service is unhealthy - dependency failure detected:"
                echo "$dep_check" | grep -v "FAILED_DEPENDENCIES" | sed 's/^/    /'
            else
                print_error "$service is unhealthy (status: $health)"
            fi

            all_healthy=false
            failed_services+=("$service:$health")
        fi

        echo ""
    done

    # Summary
    if [ "$QUIET" = false ]; then
        echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    fi

    if [ "$all_healthy" = true ]; then
        print_success "All services are healthy and dependencies are satisfied"
        echo ""
        return 0
    else
        print_error "Service health check failed"
        echo ""
        echo "Failed services:"
        for failed in "${failed_services[@]}"; do
            local service_name="${failed%%:*}"
            local status="${failed##*:}"
            echo -e "  ${RED}✗${NC} $service_name (${SERVICE_DESCRIPTIONS[$service_name]}): $status"
        done
        echo ""
        echo "Troubleshooting:"
        echo "  1. Check service logs: docker compose logs <service>"
        echo "  2. Check all logs: docker compose logs"
        echo "  3. Restart services: docker compose restart"
        echo "  4. Check service status: docker compose ps"
        echo ""
        return 1
    fi
}

check_with_wait() {
    local timeout=$1
    local start_time=$(date +%s)
    local attempt=1

    print_header
    echo "Waiting up to ${timeout}s for all services to become healthy..."
    echo ""

    while true; do
        local current_time=$(date +%s)
        local elapsed=$((current_time - start_time))

        if [ $elapsed -ge $timeout ]; then
            print_error "Timeout after ${timeout}s"
            echo ""
            check_all_services
            return 1
        fi

        echo "Attempt $attempt (${elapsed}s elapsed):"

        local all_healthy=true
        for service in "${SERVICE_ORDER[@]}"; do
            local health=$(check_service_health "$service")

            if [ "$health" = "healthy" ] || [ "$health" = "running" ]; then
                print_success "$service"
            else
                print_warning "$service ($health)"
                all_healthy=false
            fi
        done

        if [ "$all_healthy" = true ]; then
            echo ""
            print_success "All services are healthy after ${elapsed}s"
            echo ""
            return 0
        fi

        echo ""
        sleep 2
        attempt=$((attempt + 1))
    done
}

# =============================================================================
# Command Line Parsing
# =============================================================================

show_usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Check the health and dependency status of all Docker Compose services.

OPTIONS:
    -v, --verbose       Show detailed service information
    -w, --wait N        Wait up to N seconds for services to become healthy
    -q, --quiet         Suppress non-essential output
    -h, --help          Show this help message

EXAMPLES:
    $0                  # Check all services once
    $0 --verbose        # Show detailed status
    $0 --wait 60        # Wait up to 60s for services
    $0 -w 30 -v         # Wait 30s with verbose output

EXIT CODES:
    0 - All services healthy
    1 - One or more services unhealthy
    2 - Script error or invalid arguments

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -w|--wait)
            WAIT_TIMEOUT="$2"
            shift 2
            ;;
        -q|--quiet)
            QUIET=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_usage
            exit 2
            ;;
    esac
done

# =============================================================================
# Main Execution
# =============================================================================

# Change to project root
cd "$PROJECT_ROOT"

# Validate compose file exists
check_compose_file

# Run appropriate check
if [ "$WAIT_TIMEOUT" -gt 0 ] 2>/dev/null; then
    check_with_wait "$WAIT_TIMEOUT"
    exit $?
else
    check_all_services
    exit $?
fi
