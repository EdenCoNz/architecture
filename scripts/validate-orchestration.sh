#!/usr/bin/env bash
# =============================================================================
# Orchestration Testing and Validation Script (Story 12.11)
# =============================================================================
# This script validates that the orchestrated application stack is working
# correctly by verifying:
#   - All services are running and healthy
#   - Frontend can reach backend through reverse proxy
#   - Database connectivity from backend
#   - Reverse proxy routing is correct
#   - Environment configuration is loaded correctly
#
# Usage:
#   ./scripts/validate-orchestration.sh              # Full validation
#   ./scripts/validate-orchestration.sh --quick      # Quick validation (basic checks)
#   ./scripts/validate-orchestration.sh --verbose    # Detailed output
#   ./scripts/validate-orchestration.sh --json       # JSON output for CI/CD
#
# Exit codes:
#   0 - All validations passed
#   1 - One or more validations failed
#   2 - Script error or invalid arguments
# =============================================================================

set -euo pipefail

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m' # No Color

# Configuration
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
readonly COMPOSE_FILE="${PROJECT_ROOT}/docker-compose.yml"

# Default options
VERBOSE=false
QUICK_MODE=false
JSON_OUTPUT=false
WAIT_FOR_SERVICES=true
MAX_WAIT=120

# Test results tracking
declare -a PASSED_TESTS=()
declare -a FAILED_TESTS=()
declare -a WARNINGS=()

# Service definitions
declare -A SERVICES=(
    [db]="PostgreSQL Database"
    [redis]="Redis Cache"
    [backend]="Django Backend API"
    [frontend]="React Frontend"
    [proxy]="Nginx Reverse Proxy"
)

# Expected routes
declare -A PROXY_ROUTES=(
    ["/"]="frontend"
    ["/api/v1/health/"]="backend"
    ["/admin/"]="backend"
    ["/health"]="proxy"
)

# =============================================================================
# Helper Functions
# =============================================================================

log_header() {
    if [ "$JSON_OUTPUT" = false ]; then
        echo ""
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${BLUE}  $1${NC}"
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
    fi
}

log_section() {
    if [ "$JSON_OUTPUT" = false ]; then
        echo ""
        echo -e "${CYAN}▸ $1${NC}"
        echo ""
    fi
}

log_success() {
    if [ "$JSON_OUTPUT" = false ]; then
        echo -e "${GREEN}✓${NC} $1"
    fi
    PASSED_TESTS+=("$1")
}

log_error() {
    if [ "$JSON_OUTPUT" = false ]; then
        echo -e "${RED}✗${NC} $1"
    fi
    FAILED_TESTS+=("$1")
}

log_warning() {
    if [ "$JSON_OUTPUT" = false ]; then
        echo -e "${YELLOW}⚠${NC} $1"
    fi
    WARNINGS+=("$1")
}

log_info() {
    if [ "$JSON_OUTPUT" = false ] && [ "$VERBOSE" = true ]; then
        echo -e "${BLUE}  ℹ${NC} $1"
    fi
}

log_verbose() {
    if [ "$VERBOSE" = true ] && [ "$JSON_OUTPUT" = false ]; then
        echo -e "    $1"
    fi
}

# =============================================================================
# Service Health Validation
# =============================================================================

validate_service_health() {
    log_section "Validating Service Health"

    local all_healthy=true

    for service in "${!SERVICES[@]}"; do
        local description="${SERVICES[$service]}"
        local container_name="app-${service}"

        # Check if container exists and is running
        if ! docker ps --format '{{.Names}}' | grep -q "^${container_name}$"; then
            log_error "Service ${service} (${description}) is not running"
            all_healthy=false
            continue
        fi

        # Check health status
        local health_status
        health_status=$(docker inspect --format='{{.State.Health.Status}}' "${container_name}" 2>/dev/null || echo "no_healthcheck")

        if [ "$health_status" = "healthy" ]; then
            log_success "Service ${service} is healthy"
            log_verbose "Container: ${container_name}"

            if [ "$VERBOSE" = true ]; then
                local uptime
                uptime=$(docker inspect --format='{{.State.Status}} (started {{.State.StartedAt}})' "${container_name}")
                log_verbose "Status: ${uptime}"
            fi
        elif [ "$health_status" = "no_healthcheck" ]; then
            # For services without health checks, just verify they're running
            local state
            state=$(docker inspect --format='{{.State.Status}}' "${container_name}")
            if [ "$state" = "running" ]; then
                log_success "Service ${service} is running (no health check)"
            else
                log_error "Service ${service} is not running (state: ${state})"
                all_healthy=false
            fi
        else
            log_error "Service ${service} is unhealthy (status: ${health_status})"
            all_healthy=false

            # Show recent health check logs
            if [ "$VERBOSE" = true ]; then
                log_verbose "Recent health check output:"
                docker inspect --format='{{range .State.Health.Log}}  {{.Output}}{{end}}' "${container_name}" 2>/dev/null | tail -n 3
            fi
        fi
    done

    return $([ "$all_healthy" = true ] && echo 0 || echo 1)
}

# =============================================================================
# Reverse Proxy Routing Validation
# =============================================================================

validate_proxy_routing() {
    log_section "Validating Reverse Proxy Routing"

    local all_routes_ok=true

    # Check if proxy is accessible
    if ! curl -sf -o /dev/null http://localhost/health; then
        log_error "Reverse proxy is not accessible on http://localhost/"
        return 1
    fi

    log_success "Reverse proxy is accessible"

    # Test each route
    for route in "${!PROXY_ROUTES[@]}"; do
        local expected_service="${PROXY_ROUTES[$route]}"
        local url="http://localhost${route}"

        log_info "Testing route: ${route} -> ${expected_service}"

        # Make request and check status
        local http_code
        http_code=$(curl -sf -o /dev/null -w "%{http_code}" "${url}" 2>/dev/null || echo "000")

        if [ "$http_code" = "200" ] || [ "$http_code" = "301" ] || [ "$http_code" = "302" ]; then
            log_success "Route ${route} returns ${http_code}"

            if [ "$VERBOSE" = true ]; then
                # Get response headers to verify routing
                local headers
                headers=$(curl -sI "${url}" 2>/dev/null | head -n 10)
                log_verbose "Response headers:"
                echo "$headers" | while IFS= read -r line; do
                    log_verbose "  $line"
                done
            fi
        else
            log_error "Route ${route} returned ${http_code} (expected 200/301/302)"
            all_routes_ok=false
        fi
    done

    # Test static file serving (if available)
    log_info "Testing static file serving..."
    local static_code
    static_code=$(curl -sf -o /dev/null -w "%{http_code}" "http://localhost/static/admin/css/base.css" 2>/dev/null || echo "000")

    if [ "$static_code" = "200" ] || [ "$static_code" = "404" ]; then
        log_success "Static file routing is configured (status: ${static_code})"
    else
        log_warning "Static file routing may have issues (status: ${static_code})"
    fi

    return $([ "$all_routes_ok" = true ] && echo 0 || echo 1)
}

# =============================================================================
# Frontend-Backend Connectivity Validation
# =============================================================================

validate_frontend_backend_connectivity() {
    log_section "Validating Frontend-Backend Connectivity Through Proxy"

    local all_ok=true

    # Test backend API through proxy
    log_info "Testing backend API accessibility through proxy..."

    local api_response
    api_response=$(curl -sf http://localhost/api/v1/health/ 2>/dev/null || echo "")

    if [ -n "$api_response" ]; then
        log_success "Backend API is accessible through reverse proxy"

        # Validate response structure
        if echo "$api_response" | grep -q '"status"'; then
            log_success "API health endpoint returns valid JSON with status field"
        else
            log_warning "API health response may be missing expected fields"
        fi

        if [ "$VERBOSE" = true ]; then
            log_verbose "API health response:"
            echo "$api_response" | python3 -m json.tool 2>/dev/null || echo "$api_response"
        fi
    else
        log_error "Backend API is not accessible through reverse proxy"
        all_ok=false
    fi

    # Test CORS headers
    log_info "Testing CORS configuration..."

    local cors_headers
    cors_headers=$(curl -sI -H "Origin: http://localhost" http://localhost/api/v1/health/ 2>/dev/null || echo "")

    if echo "$cors_headers" | grep -qi "access-control-allow"; then
        log_success "CORS headers are configured"

        if [ "$VERBOSE" = true ]; then
            log_verbose "CORS headers:"
            echo "$cors_headers" | grep -i "access-control" | while IFS= read -r line; do
                log_verbose "  $line"
            done
        fi
    else
        log_warning "CORS headers not found (may be ok for same-origin requests)"
    fi

    # Test frontend accessibility
    log_info "Testing frontend accessibility through proxy..."

    local frontend_code
    frontend_code=$(curl -sf -o /dev/null -w "%{http_code}" http://localhost/ 2>/dev/null || echo "000")

    if [ "$frontend_code" = "200" ]; then
        log_success "Frontend is accessible through reverse proxy"
    else
        log_error "Frontend is not accessible through reverse proxy (HTTP ${frontend_code})"
        all_ok=false
    fi

    # Test WebSocket support for Vite HMR (development mode)
    if docker ps --format '{{.Names}}' | grep -q "app-frontend"; then
        log_info "Testing WebSocket support (Vite HMR)..."

        # Check if nginx config supports WebSocket upgrade
        local ws_config
        ws_config=$(docker exec app-proxy cat /etc/nginx/nginx.conf 2>/dev/null | grep -i "upgrade" || echo "")

        if [ -n "$ws_config" ]; then
            log_success "WebSocket upgrade headers configured in nginx"
        else
            log_warning "WebSocket upgrade headers not found (HMR may not work)"
        fi
    fi

    return $([ "$all_ok" = true ] && echo 0 || echo 1)
}

# =============================================================================
# Database Connectivity Validation
# =============================================================================

validate_database_connectivity() {
    log_section "Validating Database Connectivity from Backend"

    local all_ok=true

    # Test database connectivity through backend health endpoint
    log_info "Testing database connectivity through backend health endpoint..."

    local health_response
    health_response=$(curl -sf http://localhost/api/v1/health/ 2>/dev/null || echo "")

    if echo "$health_response" | grep -q '"database"'; then
        local db_status
        db_status=$(echo "$health_response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('database', {}).get('status', 'unknown'))" 2>/dev/null || echo "unknown")

        if [ "$db_status" = "healthy" ] || [ "$db_status" = "connected" ]; then
            log_success "Backend successfully connected to database (status: ${db_status})"
        else
            log_error "Database connection issue detected (status: ${db_status})"
            all_ok=false
        fi
    else
        log_warning "Health endpoint does not include database status"
    fi

    # Direct database health check
    log_info "Testing PostgreSQL health check..."

    if docker exec app-db pg_isready -U postgres >/dev/null 2>&1; then
        log_success "PostgreSQL is accepting connections"
    else
        log_error "PostgreSQL is not accepting connections"
        all_ok=false
    fi

    # Test Redis connectivity
    log_info "Testing Redis connectivity..."

    if docker exec app-redis redis-cli ping 2>/dev/null | grep -q "PONG"; then
        log_success "Redis is responding to commands"
    else
        log_error "Redis is not responding"
        all_ok=false
    fi

    # Check if backend can query database
    if [ "$VERBOSE" = true ]; then
        log_info "Testing backend database query capability..."

        local db_query_test
        db_query_test=$(docker exec app-backend python -c "
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
        print('OK')
except Exception as e:
    print(f'ERROR: {e}')
" 2>/dev/null || echo "ERROR")

        if echo "$db_query_test" | grep -q "OK"; then
            log_success "Backend can execute database queries"
        else
            log_warning "Backend database query test failed"
        fi
    fi

    return $([ "$all_ok" = true ] && echo 0 || echo 1)
}

# =============================================================================
# Environment Configuration Validation
# =============================================================================

validate_environment_config() {
    log_section "Validating Environment Configuration"

    local all_ok=true

    # Check backend environment configuration
    log_info "Checking backend environment configuration..."

    local backend_env
    backend_env=$(docker exec app-backend env 2>/dev/null || echo "")

    # Check critical environment variables
    local required_vars=(
        "DJANGO_SETTINGS_MODULE"
        "DB_HOST"
        "DB_NAME"
        "REDIS_URL"
    )

    for var in "${required_vars[@]}"; do
        if echo "$backend_env" | grep -q "^${var}="; then
            local value
            value=$(echo "$backend_env" | grep "^${var}=" | cut -d= -f2-)
            log_success "Backend env: ${var} is set"

            if [ "$VERBOSE" = true ]; then
                # Mask sensitive values
                if [[ "$var" =~ PASSWORD|SECRET|KEY ]]; then
                    log_verbose "Value: ********"
                else
                    log_verbose "Value: ${value}"
                fi
            fi
        else
            log_error "Backend env: ${var} is not set"
            all_ok=false
        fi
    done

    # Check frontend runtime configuration
    log_info "Checking frontend runtime configuration..."

    local config_endpoint="http://localhost/api/v1/config/frontend/"
    local config_response
    config_response=$(curl -sf "$config_endpoint" 2>/dev/null || echo "")

    if [ -n "$config_response" ]; then
        log_success "Frontend runtime configuration endpoint is accessible"

        if echo "$config_response" | grep -q '"apiUrl"'; then
            log_success "Frontend configuration includes apiUrl"
        else
            log_warning "Frontend configuration may be missing apiUrl"
        fi

        if [ "$VERBOSE" = true ]; then
            log_verbose "Frontend configuration:"
            echo "$config_response" | python3 -m json.tool 2>/dev/null || echo "$config_response"
        fi
    else
        log_error "Frontend runtime configuration endpoint not accessible"
        all_ok=false
    fi

    # Verify network isolation
    log_info "Verifying network isolation..."

    local exposed_ports
    exposed_ports=$(docker ps --format '{{.Names}}\t{{.Ports}}' | grep "^app-" || echo "")

    # Only proxy should expose ports to host
    local non_proxy_exposed
    non_proxy_exposed=$(echo "$exposed_ports" | grep -v "app-proxy" | grep "0.0.0.0" || echo "")

    if [ -z "$non_proxy_exposed" ]; then
        log_success "Network isolation: Only proxy exposes ports to host"
    else
        log_warning "Network isolation: Other services expose ports (development mode?)"

        if [ "$VERBOSE" = true ]; then
            log_verbose "Exposed ports:"
            echo "$non_proxy_exposed" | while IFS= read -r line; do
                log_verbose "  $line"
            done
        fi
    fi

    return $([ "$all_ok" = true ] && echo 0 || echo 1)
}

# =============================================================================
# Performance and Security Checks
# =============================================================================

validate_security_headers() {
    log_section "Validating Security Headers"

    local all_ok=true

    log_info "Checking security headers from reverse proxy..."

    local headers
    headers=$(curl -sI http://localhost/ 2>/dev/null || echo "")

    local expected_headers=(
        "X-Frame-Options"
        "X-Content-Type-Options"
        "X-XSS-Protection"
    )

    for header in "${expected_headers[@]}"; do
        if echo "$headers" | grep -qi "^${header}:"; then
            local value
            value=$(echo "$headers" | grep -i "^${header}:" | cut -d: -f2- | tr -d '\r' | xargs)
            log_success "Security header: ${header} = ${value}"
        else
            log_warning "Security header missing: ${header}"
        fi
    done

    # Check for compression
    log_info "Checking response compression..."

    if echo "$headers" | grep -qi "content-encoding.*gzip"; then
        log_success "Gzip compression is enabled"
    else
        log_warning "Gzip compression not detected (may not be enabled for all responses)"
    fi

    return 0
}

# =============================================================================
# Service Dependency Validation
# =============================================================================

validate_service_dependencies() {
    log_section "Validating Service Dependencies"

    local all_ok=true

    # Verify dependency chain
    log_info "Checking service dependency chain..."

    # Database should have no dependencies
    if docker inspect app-db --format '{{.HostConfig.DependsOn}}' 2>/dev/null | grep -q "null"; then
        log_success "Database has no dependencies (correct)"
    fi

    # Backend should depend on db and redis
    local backend_deps
    backend_deps=$(docker inspect app-backend --format '{{json .HostConfig}}' 2>/dev/null || echo "")

    if [ -n "$backend_deps" ]; then
        log_success "Backend dependency configuration found"
    else
        log_warning "Could not verify backend dependencies"
    fi

    # Check startup order via container start times
    if [ "$VERBOSE" = true ]; then
        log_info "Service startup timeline:"

        for service in db redis backend frontend proxy; do
            local container="app-${service}"
            if docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
                local started
                started=$(docker inspect --format='{{.State.StartedAt}}' "${container}" 2>/dev/null)
                log_verbose "${service}: started at ${started}"
            fi
        done
    fi

    return $([ "$all_ok" = true ] && echo 0 || echo 1)
}

# =============================================================================
# Wait for Services
# =============================================================================

wait_for_services() {
    if [ "$WAIT_FOR_SERVICES" = false ]; then
        return 0
    fi

    log_section "Waiting for Services to Become Healthy"

    local start_time
    start_time=$(date +%s)
    local all_healthy=false

    while true; do
        local current_time
        current_time=$(date +%s)
        local elapsed=$((current_time - start_time))

        if [ $elapsed -ge $MAX_WAIT ]; then
            log_error "Timeout waiting for services (${MAX_WAIT}s elapsed)"
            return 1
        fi

        local unhealthy_count=0

        for service in "${!SERVICES[@]}"; do
            local container_name="app-${service}"

            if ! docker ps --format '{{.Names}}' | grep -q "^${container_name}$"; then
                ((unhealthy_count++))
                continue
            fi

            local health_status
            health_status=$(docker inspect --format='{{.State.Health.Status}}' "${container_name}" 2>/dev/null || echo "no_healthcheck")

            if [ "$health_status" != "healthy" ] && [ "$health_status" != "no_healthcheck" ]; then
                ((unhealthy_count++))
            elif [ "$health_status" = "no_healthcheck" ]; then
                # Check if running
                local state
                state=$(docker inspect --format='{{.State.Status}}' "${container_name}")
                if [ "$state" != "running" ]; then
                    ((unhealthy_count++))
                fi
            fi
        done

        if [ $unhealthy_count -eq 0 ]; then
            all_healthy=true
            break
        fi

        if [ "$JSON_OUTPUT" = false ]; then
            echo -ne "\r  Waiting for services... (${elapsed}s elapsed, ${unhealthy_count} services not ready)    "
        fi

        sleep 2
    done

    if [ "$JSON_OUTPUT" = false ]; then
        echo ""
    fi

    if [ "$all_healthy" = true ]; then
        log_success "All services are healthy"
        return 0
    else
        return 1
    fi
}

# =============================================================================
# JSON Output
# =============================================================================

output_json_results() {
    local status="passed"
    if [ ${#FAILED_TESTS[@]} -gt 0 ]; then
        status="failed"
    fi

    cat <<EOF
{
  "status": "${status}",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "summary": {
    "passed": ${#PASSED_TESTS[@]},
    "failed": ${#FAILED_TESTS[@]},
    "warnings": ${#WARNINGS[@]}
  },
  "passed_tests": $(printf '%s\n' "${PASSED_TESTS[@]}" | jq -R . | jq -s .),
  "failed_tests": $(printf '%s\n' "${FAILED_TESTS[@]}" | jq -R . | jq -s .),
  "warnings": $(printf '%s\n' "${WARNINGS[@]}" | jq -R . | jq -s .)
}
EOF
}

# =============================================================================
# Main Execution
# =============================================================================

show_usage() {
    cat <<EOF
Usage: $0 [OPTIONS]

Validate the orchestrated application stack to ensure all services are
communicating properly and the application is fully functional.

OPTIONS:
    --quick             Quick validation (basic health checks only)
    --verbose           Show detailed output for all checks
    --json              Output results in JSON format (for CI/CD)
    --no-wait           Don't wait for services to become healthy
    --max-wait N        Maximum seconds to wait for services (default: 120)
    -h, --help          Show this help message

EXAMPLES:
    $0                  # Full validation with default settings
    $0 --quick          # Quick validation (health checks only)
    $0 --verbose        # Full validation with detailed output
    $0 --json           # JSON output for CI/CD integration
    $0 --no-wait        # Skip waiting for services

EXIT CODES:
    0 - All validations passed
    1 - One or more validations failed
    2 - Script error or invalid arguments

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --quick)
            QUICK_MODE=true
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --json)
            JSON_OUTPUT=true
            shift
            ;;
        --no-wait)
            WAIT_FOR_SERVICES=false
            shift
            ;;
        --max-wait)
            MAX_WAIT="$2"
            shift 2
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

# Change to project root
cd "$PROJECT_ROOT"

# Start validation
if [ "$JSON_OUTPUT" = false ]; then
    log_header "Orchestration Validation (Story 12.11)"
    echo "Project: $PROJECT_ROOT"
    echo "Mode: $([ "$QUICK_MODE" = true ] && echo "Quick" || echo "Full")"
    echo "Timestamp: $(date)"
fi

# Wait for services if needed
if [ "$WAIT_FOR_SERVICES" = true ]; then
    wait_for_services || {
        if [ "$JSON_OUTPUT" = true ]; then
            output_json_results
        fi
        exit 1
    }
fi

# Run validation checks
VALIDATION_FAILED=false

# Always run service health validation
validate_service_health || VALIDATION_FAILED=true

# Run additional checks in full mode
if [ "$QUICK_MODE" = false ]; then
    validate_proxy_routing || VALIDATION_FAILED=true
    validate_frontend_backend_connectivity || VALIDATION_FAILED=true
    validate_database_connectivity || VALIDATION_FAILED=true
    validate_environment_config || VALIDATION_FAILED=true
    validate_security_headers || true  # Don't fail on security header warnings
    validate_service_dependencies || true  # Don't fail on dependency warnings
fi

# Output results
if [ "$JSON_OUTPUT" = true ]; then
    output_json_results
else
    log_header "Validation Summary"

    echo ""
    echo -e "${GREEN}Passed:${NC}  ${#PASSED_TESTS[@]} tests"
    echo -e "${RED}Failed:${NC}  ${#FAILED_TESTS[@]} tests"
    echo -e "${YELLOW}Warnings:${NC} ${#WARNINGS[@]} warnings"
    echo ""

    if [ ${#FAILED_TESTS[@]} -gt 0 ]; then
        echo -e "${RED}Failed Tests:${NC}"
        for test in "${FAILED_TESTS[@]}"; do
            echo -e "  ${RED}✗${NC} $test"
        done
        echo ""
    fi

    if [ ${#WARNINGS[@]} -gt 0 ] && [ "$VERBOSE" = true ]; then
        echo -e "${YELLOW}Warnings:${NC}"
        for warning in "${WARNINGS[@]}"; do
            echo -e "  ${YELLOW}⚠${NC} $warning"
        done
        echo ""
    fi

    if [ "$VALIDATION_FAILED" = false ]; then
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${GREEN}  ✓ All critical validations passed!${NC}"
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        echo "The orchestrated application stack is working correctly."
        echo ""
    else
        echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${RED}  ✗ Validation failed!${NC}"
        echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        echo "Troubleshooting:"
        echo "  - Check service logs: docker compose logs <service>"
        echo "  - Check service status: docker compose ps"
        echo "  - Run dependency check: ./scripts/check-dependencies.sh"
        echo "  - Run health validation: ./scripts/validate-health-checks.sh"
        echo ""
    fi
fi

# Exit with appropriate code
if [ "$VALIDATION_FAILED" = true ]; then
    exit 1
else
    exit 0
fi
