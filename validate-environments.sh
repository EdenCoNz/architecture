#!/bin/bash
# =============================================================================
# Environment Validation Script for Docker Compose
# =============================================================================
# This script validates that all three environments (local, staging, production)
# work correctly with the docker-compose.yml configuration.
#
# Usage:
#   ./validate-environments.sh [environment]
#
#   environment: local, staging, production, or all (default: all)
#
# Examples:
#   ./validate-environments.sh local        # Test local only
#   ./validate-environments.sh staging      # Test staging only
#   ./validate-environments.sh all          # Test all environments
#   ./validate-environments.sh              # Test all (default)
#
# Exit codes:
#   0 - All validations passed
#   1 - One or more validations failed
#   2 - Invalid arguments or setup error
# =============================================================================

set -e  # Exit on error
set -u  # Exit on undefined variable

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
COMPOSE_FILE="docker-compose.yml"
ENV_EXAMPLE=".env.example"
VALIDATION_TIMEOUT=120  # seconds
HEALTHCHECK_RETRIES=30
HEALTHCHECK_INTERVAL=5

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------

print_header() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}"
    echo ""
}

print_section() {
    echo ""
    echo -e "${YELLOW}───────────────────────────────────────────────────────────────────${NC}"
    echo -e "${YELLOW}  $1${NC}"
    echo -e "${YELLOW}───────────────────────────────────────────────────────────────────${NC}"
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
    echo -e "${BLUE}ℹ${NC} $1"
}

run_test() {
    local test_name="$1"
    local test_command="$2"

    TESTS_TOTAL=$((TESTS_TOTAL + 1))

    echo -n "  Testing: $test_name... "

    if eval "$test_command" > /dev/null 2>&1; then
        echo -e "${GREEN}PASS${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}FAIL${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# -----------------------------------------------------------------------------
# Prerequisites Check
# -----------------------------------------------------------------------------

check_prerequisites() {
    print_section "Checking Prerequisites"

    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 2
    fi
    print_success "Docker is installed: $(docker --version)"

    # Check Docker Compose
    if ! docker compose version &> /dev/null; then
        print_error "Docker Compose v2 is not available"
        print_info "Please install Docker Compose v2 (docker compose, not docker-compose)"
        exit 2
    fi
    print_success "Docker Compose is installed: $(docker compose version)"

    # Check compose file exists
    if [[ ! -f "$COMPOSE_FILE" ]]; then
        print_error "Compose file not found: $COMPOSE_FILE"
        exit 2
    fi
    print_success "Compose file found: $COMPOSE_FILE"

    # Check environment example exists
    if [[ ! -f "$ENV_EXAMPLE" ]]; then
        print_error "Environment example not found: $ENV_EXAMPLE"
        exit 2
    fi
    print_success "Environment example found: $ENV_EXAMPLE"

    # Check YAML syntax
    if ! python3 -c "import yaml; yaml.safe_load(open('$COMPOSE_FILE'))" 2>/dev/null; then
        print_error "Invalid YAML syntax in $COMPOSE_FILE"
        exit 2
    fi
    print_success "YAML syntax is valid"

    echo ""
}

# -----------------------------------------------------------------------------
# Environment Creation
# -----------------------------------------------------------------------------

create_test_env() {
    local environment="$1"
    local project_name="app-validate-$environment"

    print_section "Creating Test Environment: $environment"

    # Create temporary .env file for this environment
    local env_file=".env.test.$environment"

    case "$environment" in
        local)
            cat > "$env_file" <<EOF
ENVIRONMENT=local
COMPOSE_PROJECT_NAME=$project_name
DJANGO_SETTINGS_ENV=development
BUILD_TARGET=development
NODE_ENV=development
DEBUG=True
LOG_LEVEL=DEBUG
RESTART_POLICY=no
DB_PORT_EXPOSE=5432
REDIS_PORT_EXPOSE=6379
BACKEND_PORT_EXPOSE=8000
FRONTEND_PORT_EXPOSE=5173
BIND_MOUNT_CODE=
SSL_ENABLED=
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
SECURE_HSTS_SECONDS=0
DB_NAME=backend_db
DB_USER=postgres
DB_PASSWORD=postgres_test
POSTGRES_SHARED_BUFFERS=128MB
POSTGRES_EFFECTIVE_CACHE_SIZE=512MB
POSTGRES_MAX_CONNECTIONS=50
REDIS_PASSWORD=
REDIS_MAXMEMORY=256mb
REDIS_SAVE_CONFIG=
ALLOWED_HOSTS=localhost,127.0.0.1,backend
CORS_ALLOWED_ORIGINS=http://localhost,http://127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost,http://127.0.0.1
FRONTEND_API_URL=http://localhost
FRONTEND_APP_NAME=Application (Validation Test)
FRONTEND_ENABLE_DEBUG=true
FRONTEND_ENABLE_ANALYTICS=false
FRONTEND_API_ENABLE_LOGGING=true
VITE_API_URL=http://localhost
VITE_DEBUG=true
BACKEND_IMAGE=
FRONTEND_IMAGE=
NGINX_CONFIG=./nginx/nginx.conf
CELERY_WORKER_CONCURRENCY=2
CELERY_LOG_LEVEL=info
CELERY_PROFILE=
DB_CPU_LIMIT=1
DB_MEMORY_LIMIT=512M
DB_CPU_RESERVATION=0.5
DB_MEMORY_RESERVATION=256M
REDIS_CPU_LIMIT=0.5
REDIS_MEMORY_LIMIT=256M
REDIS_CPU_RESERVATION=0.25
REDIS_MEMORY_RESERVATION=128M
BACKEND_CPU_LIMIT=1
BACKEND_MEMORY_LIMIT=512M
BACKEND_CPU_RESERVATION=0.5
BACKEND_MEMORY_RESERVATION=256M
FRONTEND_CPU_LIMIT=1
FRONTEND_MEMORY_LIMIT=1G
FRONTEND_CPU_RESERVATION=0.5
FRONTEND_MEMORY_RESERVATION=512M
PROXY_CPU_LIMIT=0.5
PROXY_MEMORY_LIMIT=256M
PROXY_CPU_RESERVATION=0.25
PROXY_MEMORY_RESERVATION=128M
CELERY_CPU_LIMIT=0.5
CELERY_MEMORY_LIMIT=256M
CELERY_CPU_RESERVATION=0.25
CELERY_MEMORY_RESERVATION=128M
HEALTHCHECK_INTERVAL=10s
HEALTHCHECK_START_PERIOD=30s
LOG_MAX_SIZE=10m
LOG_MAX_FILE=3
LOG_COMPRESS=false
PROXY_PORT=8080
PROXY_SSL_PORT=8443
EOF
            ;;

        staging)
            cat > "$env_file" <<EOF
ENVIRONMENT=staging
COMPOSE_PROJECT_NAME=$project_name
DJANGO_SETTINGS_ENV=staging
BUILD_TARGET=production
NODE_ENV=production
DEBUG=False
LOG_LEVEL=INFO
RESTART_POLICY=no
DB_PORT_EXPOSE=
REDIS_PORT_EXPOSE=
BACKEND_PORT_EXPOSE=
FRONTEND_PORT_EXPOSE=
BIND_MOUNT_CODE=
SSL_ENABLED=
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
SECURE_HSTS_SECONDS=0
DB_NAME=backend_staging_db
DB_USER=backend_staging_user
DB_PASSWORD=staging_test_password_123
POSTGRES_SHARED_BUFFERS=256MB
POSTGRES_EFFECTIVE_CACHE_SIZE=1GB
POSTGRES_MAX_CONNECTIONS=100
REDIS_PASSWORD=staging_redis_test_password_123
REDIS_MAXMEMORY=512mb
REDIS_SAVE_CONFIG=--save 900 1
ALLOWED_HOSTS=localhost,staging.example.com
CORS_ALLOWED_ORIGINS=http://localhost
CSRF_TRUSTED_ORIGINS=http://localhost
FRONTEND_API_URL=http://localhost
FRONTEND_APP_NAME=Application (Staging Validation)
FRONTEND_ENABLE_DEBUG=false
FRONTEND_ENABLE_ANALYTICS=false
FRONTEND_API_ENABLE_LOGGING=true
VITE_API_URL=http://localhost
VITE_DEBUG=false
BACKEND_IMAGE=backend-dev:latest
FRONTEND_IMAGE=frontend-dev:latest
NGINX_CONFIG=./nginx/nginx.conf
CELERY_WORKER_CONCURRENCY=4
CELERY_LOG_LEVEL=info
CELERY_PROFILE=
DB_CPU_LIMIT=1
DB_MEMORY_LIMIT=512M
DB_CPU_RESERVATION=0.5
DB_MEMORY_RESERVATION=256M
REDIS_CPU_LIMIT=0.5
REDIS_MEMORY_LIMIT=256M
REDIS_CPU_RESERVATION=0.25
REDIS_MEMORY_RESERVATION=128M
BACKEND_CPU_LIMIT=1
BACKEND_MEMORY_LIMIT=512M
BACKEND_CPU_RESERVATION=0.5
BACKEND_MEMORY_RESERVATION=256M
FRONTEND_CPU_LIMIT=1
FRONTEND_MEMORY_LIMIT=1G
FRONTEND_CPU_RESERVATION=0.5
FRONTEND_MEMORY_RESERVATION=512M
PROXY_CPU_LIMIT=0.5
PROXY_MEMORY_LIMIT=256M
PROXY_CPU_RESERVATION=0.25
PROXY_MEMORY_RESERVATION=128M
CELERY_CPU_LIMIT=0.5
CELERY_MEMORY_LIMIT=256M
CELERY_CPU_RESERVATION=0.25
CELERY_MEMORY_RESERVATION=128M
HEALTHCHECK_INTERVAL=15s
HEALTHCHECK_START_PERIOD=45s
LOG_MAX_SIZE=50m
LOG_MAX_FILE=5
LOG_COMPRESS=true
PROXY_PORT=8081
PROXY_SSL_PORT=8444
EOF
            ;;

        production)
            cat > "$env_file" <<EOF
ENVIRONMENT=production
COMPOSE_PROJECT_NAME=$project_name
DJANGO_SETTINGS_ENV=production
BUILD_TARGET=production
NODE_ENV=production
DEBUG=False
LOG_LEVEL=WARNING
RESTART_POLICY=no
DB_PORT_EXPOSE=
REDIS_PORT_EXPOSE=
BACKEND_PORT_EXPOSE=
FRONTEND_PORT_EXPOSE=
BIND_MOUNT_CODE=
SSL_ENABLED=
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
SECURE_HSTS_SECONDS=0
DB_NAME=backend_prod_db
DB_USER=backend_prod_user
DB_PASSWORD=production_test_password_123
POSTGRES_SHARED_BUFFERS=512MB
POSTGRES_EFFECTIVE_CACHE_SIZE=2GB
POSTGRES_MAX_CONNECTIONS=200
REDIS_PASSWORD=production_redis_test_password_123
REDIS_MAXMEMORY=1gb
REDIS_SAVE_CONFIG=--save 900 1
ALLOWED_HOSTS=example.com,www.example.com
CORS_ALLOWED_ORIGINS=http://localhost
CSRF_TRUSTED_ORIGINS=http://localhost
FRONTEND_API_URL=http://localhost
FRONTEND_APP_NAME=Application (Production Validation)
FRONTEND_ENABLE_DEBUG=false
FRONTEND_ENABLE_ANALYTICS=true
FRONTEND_API_ENABLE_LOGGING=false
VITE_API_URL=http://localhost
VITE_DEBUG=false
BACKEND_IMAGE=backend-dev:latest
FRONTEND_IMAGE=frontend-dev:latest
NGINX_CONFIG=./nginx/nginx.conf
CELERY_WORKER_CONCURRENCY=8
CELERY_LOG_LEVEL=warning
CELERY_PROFILE=
DB_CPU_LIMIT=1
DB_MEMORY_LIMIT=512M
DB_CPU_RESERVATION=0.5
DB_MEMORY_RESERVATION=256M
REDIS_CPU_LIMIT=0.5
REDIS_MEMORY_LIMIT=256M
REDIS_CPU_RESERVATION=0.25
REDIS_MEMORY_RESERVATION=128M
BACKEND_CPU_LIMIT=1
BACKEND_MEMORY_LIMIT=512M
BACKEND_CPU_RESERVATION=0.5
BACKEND_MEMORY_RESERVATION=256M
FRONTEND_CPU_LIMIT=1
FRONTEND_MEMORY_LIMIT=1G
FRONTEND_CPU_RESERVATION=0.5
FRONTEND_MEMORY_RESERVATION=512M
PROXY_CPU_LIMIT=0.5
PROXY_MEMORY_LIMIT=256M
PROXY_CPU_RESERVATION=0.25
PROXY_MEMORY_RESERVATION=128M
CELERY_CPU_LIMIT=0.5
CELERY_MEMORY_LIMIT=256M
CELERY_CPU_RESERVATION=0.25
CELERY_MEMORY_RESERVATION=128M
HEALTHCHECK_INTERVAL=30s
HEALTHCHECK_START_PERIOD=60s
LOG_MAX_SIZE=100m
LOG_MAX_FILE=10
LOG_COMPRESS=true
PROXY_PORT=8082
PROXY_SSL_PORT=8445
EOF
            ;;
    esac

    print_success "Created test environment file: $env_file"
    echo "$env_file"
}

# -----------------------------------------------------------------------------
# Service Validation
# -----------------------------------------------------------------------------

validate_environment() {
    local environment="$1"
    local env_file="$2"

    print_header "Validating Environment: $environment"

    # Configuration validation
    print_section "Configuration Validation"

    run_test "Compose file parses correctly" \
        "docker compose -f $COMPOSE_FILE --env-file $env_file config > /dev/null"

    run_test "Environment variable ENVIRONMENT is set" \
        "grep -q 'ENVIRONMENT=$environment' $env_file"

    run_test "ALLOWED_HOSTS configured correctly" \
        "grep -q 'ALLOWED_HOSTS=' $env_file"

    # Service startup validation
    print_section "Service Startup Validation"

    print_info "Starting services (this may take a few minutes)..."
    if ! docker compose -f "$COMPOSE_FILE" --env-file "$env_file" up -d --build 2>&1 | tee /tmp/compose-up.log; then
        print_error "Failed to start services"
        cat /tmp/compose-up.log
        return 1
    fi
    print_success "Services started"

    # Wait for services to be healthy
    print_section "Health Check Validation"

    local services=("db" "redis" "backend" "frontend" "proxy")

    for service in "${services[@]}"; do
        print_info "Waiting for $service to be healthy..."
        local retries=0
        local healthy=false

        while [[ $retries -lt $HEALTHCHECK_RETRIES ]]; do
            if docker compose -f "$COMPOSE_FILE" --env-file "$env_file" ps "$service" 2>/dev/null | grep -q "healthy"; then
                healthy=true
                break
            fi

            sleep "$HEALTHCHECK_INTERVAL"
            retries=$((retries + 1))
        done

        if [[ "$healthy" == "true" ]]; then
            print_success "$service is healthy"
        else
            print_error "$service failed to become healthy"
            docker compose -f "$COMPOSE_FILE" --env-file "$env_file" logs "$service" | tail -50
            return 1
        fi
    done

    # Endpoint validation
    print_section "Endpoint Validation"

    # Get proxy port from env file
    local proxy_port
    proxy_port=$(grep "^PROXY_PORT=" "$env_file" | cut -d= -f2)

    run_test "Proxy health endpoint responds" \
        "curl -f -s http://localhost:$proxy_port/health"

    run_test "Backend API health endpoint responds" \
        "curl -f -s http://localhost:$proxy_port/api/v1/health/"

    run_test "Frontend loads successfully" \
        "curl -f -s http://localhost:$proxy_port/ | grep -q '<title>'"

    # Configuration discrepancy checks
    print_section "Configuration Discrepancy Checks"

    run_test "Backend uses correct Django settings module" \
        "docker compose -f $COMPOSE_FILE --env-file $env_file exec -T backend env | grep -q 'DJANGO_SETTINGS_MODULE=config.settings'"

    run_test "Health checks use 127.0.0.1 (not localhost)" \
        "docker compose -f $COMPOSE_FILE --env-file $env_file config | grep -q '127.0.0.1'"

    run_test "CORS configuration is set" \
        "docker compose -f $COMPOSE_FILE --env-file $env_file exec -T backend env | grep -q 'CORS_ALLOWED_ORIGINS'"

    # Port consistency checks
    print_section "Port Consistency Checks"

    case "$environment" in
        local)
            run_test "Backend port exposed in local" \
                "docker compose -f $COMPOSE_FILE --env-file $env_file ps backend | grep -q '8000'"

            run_test "Frontend port exposed in local" \
                "docker compose -f $COMPOSE_FILE --env-file $env_file ps frontend | grep -q '5173'"
            ;;

        staging|production)
            run_test "Backend port NOT exposed in $environment" \
                "! docker compose -f $COMPOSE_FILE --env-file $env_file ps backend | grep -q '0.0.0.0:8000'"

            run_test "Frontend port NOT exposed in $environment" \
                "! docker compose -f $COMPOSE_FILE --env-file $env_file ps frontend | grep -q '0.0.0.0:5173'"
            ;;
    esac

    run_test "Proxy port is exposed" \
        "docker compose -f $COMPOSE_FILE --env-file $env_file ps proxy | grep -q '$proxy_port'"

    # Environment-specific validation
    print_section "Environment-Specific Validation"

    case "$environment" in
        local)
            run_test "Debug mode is enabled" \
                "docker compose -f $COMPOSE_FILE --env-file $env_file exec -T backend env | grep -q 'DEBUG=True'"

            run_test "Development Django settings used" \
                "docker compose -f $COMPOSE_FILE --env-file $env_file exec -T backend env | grep -q 'DJANGO_SETTINGS_ENV=development'"
            ;;

        staging)
            run_test "Debug mode is disabled" \
                "docker compose -f $COMPOSE_FILE --env-file $env_file exec -T backend env | grep -q 'DEBUG=False'"

            run_test "Staging Django settings used" \
                "docker compose -f $COMPOSE_FILE --env-file $env_file exec -T backend env | grep -q 'DJANGO_SETTINGS_ENV=staging'"

            run_test "Redis password is set" \
                "docker compose -f $COMPOSE_FILE --env-file $env_file exec -T backend env | grep -q 'REDIS_PASSWORD='"
            ;;

        production)
            run_test "Debug mode is disabled" \
                "docker compose -f $COMPOSE_FILE --env-file $env_file exec -T backend env | grep -q 'DEBUG=False'"

            run_test "Production Django settings used" \
                "docker compose -f $COMPOSE_FILE --env-file $env_file exec -T backend env | grep -q 'DJANGO_SETTINGS_ENV=production'"

            run_test "Redis password is set" \
                "docker compose -f $COMPOSE_FILE --env-file $env_file exec -T backend env | grep -q 'REDIS_PASSWORD='"

            run_test "Analytics enabled" \
                "docker compose -f $COMPOSE_FILE --env-file $env_file exec -T backend env | grep -q 'FRONTEND_ENABLE_ANALYTICS=true'"
            ;;
    esac

    # Cleanup
    print_section "Cleanup"

    print_info "Stopping services..."
    docker compose -f "$COMPOSE_FILE" --env-file "$env_file" down -v > /dev/null 2>&1
    print_success "Services stopped and volumes removed"

    # Remove test env file
    rm -f "$env_file"
    print_success "Test environment file removed"

    echo ""
}

# -----------------------------------------------------------------------------
# Summary Report
# -----------------------------------------------------------------------------

print_summary() {
    print_header "Validation Summary"

    echo "Total tests run: $TESTS_TOTAL"
    echo -e "Tests passed: ${GREEN}$TESTS_PASSED${NC}"
    echo -e "Tests failed: ${RED}$TESTS_FAILED${NC}"
    echo ""

    if [[ $TESTS_FAILED -eq 0 ]]; then
        print_success "All validations passed!"
        echo ""
        echo "✅ The unified Docker Compose configuration is working correctly."
        echo "✅ All three environments (local, staging, production) validated successfully."
        echo "✅ Configuration discrepancies have been fixed."
        echo "✅ Port consistency verified across all environments."
        echo ""
        return 0
    else
        print_error "Some validations failed!"
        echo ""
        echo "⚠️  Please review the errors above and fix the issues."
        echo "⚠️  Check the Docker Compose logs for more details."
        echo ""
        return 1
    fi
}

# -----------------------------------------------------------------------------
# Main Script
# -----------------------------------------------------------------------------

main() {
    local environment="${1:-all}"

    print_header "Docker Compose Environment Validation"

    print_info "Validation target: $environment"
    print_info "Compose file: $COMPOSE_FILE"
    print_info "Timeout: ${VALIDATION_TIMEOUT}s"
    echo ""

    # Check prerequisites
    check_prerequisites

    # Validate environments
    case "$environment" in
        local|staging|production)
            local env_file
            env_file=$(create_test_env "$environment")
            validate_environment "$environment" "$env_file"
            ;;

        all)
            for env in local staging production; do
                local env_file
                env_file=$(create_test_env "$env")
                validate_environment "$env" "$env_file" || true
            done
            ;;

        *)
            print_error "Invalid environment: $environment"
            echo "Usage: $0 [local|staging|production|all]"
            exit 2
            ;;
    esac

    # Print summary
    print_summary
}

# Run main function
main "$@"
