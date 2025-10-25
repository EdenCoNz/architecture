#!/bin/bash
# =============================================================================
# Production Configuration Validation Script
# =============================================================================
# This script validates the production environment configuration before
# deployment to ensure all acceptance criteria for Story 12.8 are met.
#
# Usage:
#   ./scripts/validate-production-config.sh
#   ./scripts/validate-production-config.sh --verbose
#
# Exit codes:
#   0 - All checks passed
#   1 - One or more checks failed
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

VERBOSE=0
if [[ "$1" == "--verbose" ]] || [[ "$1" == "-v" ]]; then
    VERBOSE=1
fi

FAILED_CHECKS=0
PASSED_CHECKS=0
WARNING_CHECKS=0

# Helper functions
print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASSED_CHECKS++))
}

print_failure() {
    echo -e "${RED}✗${NC} $1"
    ((FAILED_CHECKS++))
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((WARNING_CHECKS++))
}

print_info() {
    if [[ $VERBOSE -eq 1 ]]; then
        echo -e "  ℹ $1"
    fi
}

# =============================================================================
# Check 1: YAML Syntax Validation
# =============================================================================
check_yaml_syntax() {
    print_header "Check 1: YAML Syntax Validation"

    local files=(
        "docker-compose.yml"
        "compose.production.yml"
        "compose.staging.yml"
        "compose.override.yml"
    )

    for file in "${files[@]}"; do
        if [[ -f "$file" ]]; then
            if python3 -c "import yaml; yaml.safe_load(open('$file'))" 2>/dev/null; then
                print_success "$file has valid YAML syntax"
            else
                print_failure "$file has invalid YAML syntax"
            fi
        else
            print_warning "$file not found"
        fi
    done
    echo
}

# =============================================================================
# Check 2: Production Docker Compose Configuration
# =============================================================================
check_compose_config() {
    print_header "Check 2: Docker Compose Production Configuration"

    if docker compose -f docker-compose.yml -f compose.production.yml config > /dev/null 2>&1; then
        print_success "Production compose configuration is valid"
    else
        print_failure "Production compose configuration has errors"
        if [[ $VERBOSE -eq 1 ]]; then
            docker compose -f docker-compose.yml -f compose.production.yml config 2>&1 | tail -20
        fi
    fi
    echo
}

# =============================================================================
# Check 3: Production Dockerfile Targets
# =============================================================================
check_dockerfile_targets() {
    print_header "Check 3: Production Dockerfile Targets"

    # Check backend
    if grep -q "FROM.*AS production" backend/Dockerfile; then
        print_success "Backend Dockerfile has production stage"
        print_info "Backend base: $(grep 'FROM.*AS production' backend/Dockerfile | cut -d' ' -f2)"
    else
        print_failure "Backend Dockerfile missing production stage"
    fi

    # Check frontend
    if grep -q "FROM.*AS production" frontend/Dockerfile; then
        print_success "Frontend Dockerfile has production stage"
        print_info "Frontend base: $(grep 'FROM.*AS production' frontend/Dockerfile | cut -d' ' -f2)"
    else
        print_failure "Frontend Dockerfile missing production stage"
    fi
    echo
}

# =============================================================================
# Check 4: Non-Root Users
# =============================================================================
check_nonroot_users() {
    print_header "Check 4: Non-Root User Configuration"

    # Check backend
    if grep -q "USER django" backend/Dockerfile; then
        local uid=$(grep -E "useradd.*-u [0-9]+" backend/Dockerfile | grep -oP "(?<=-u )[0-9]+")
        if [[ "$uid" -gt 0 ]]; then
            print_success "Backend runs as non-root user 'django' (UID: $uid)"
        else
            print_failure "Backend user has root UID"
        fi
    else
        print_failure "Backend Dockerfile doesn't set non-root user"
    fi

    # Check frontend
    if grep -q "USER nginx" frontend/Dockerfile; then
        print_success "Frontend runs as non-root user 'nginx'"
    else
        print_failure "Frontend Dockerfile doesn't set non-root user"
    fi
    echo
}

# =============================================================================
# Check 5: Resource Limits
# =============================================================================
check_resource_limits() {
    print_header "Check 5: Resource Limits Configuration"

    local services=("backend" "frontend" "db" "redis" "proxy")

    for service in "${services[@]}"; do
        # Extract resource limits from compose.production.yml
        local cpu_limit=$(grep -A 20 "^  $service:" compose.production.yml | grep -A 3 "limits:" | grep "cpus:" | head -1 | awk '{print $2}' | tr -d "'\"")
        local mem_limit=$(grep -A 20 "^  $service:" compose.production.yml | grep -A 3 "limits:" | grep "memory:" | head -1 | awk '{print $2}')

        if [[ -n "$cpu_limit" ]] && [[ -n "$mem_limit" ]]; then
            print_success "$service has resource limits (CPU: $cpu_limit, Memory: $mem_limit)"
        else
            print_warning "$service missing resource limits"
        fi
    done
    echo
}

# =============================================================================
# Check 6: Development Features Disabled
# =============================================================================
check_debug_disabled() {
    print_header "Check 6: Development Features Disabled"

    # Check DEBUG=False
    if grep -q "DEBUG=False" compose.production.yml; then
        print_success "DEBUG mode is disabled (DEBUG=False)"
    else
        print_failure "DEBUG mode not explicitly disabled in production"
    fi

    # Check LOG_LEVEL
    if grep -q "LOG_LEVEL=WARNING" compose.production.yml; then
        print_success "Log level set to WARNING (production-appropriate)"
    else
        print_warning "LOG_LEVEL not set to WARNING"
    fi

    # Check no source code bind mounts
    local backend_volumes=$(grep -A 10 "^  backend:" compose.production.yml | grep -A 5 "volumes:" | grep -c "\./backend:/app" || true)
    if [[ "$backend_volumes" -eq 0 ]]; then
        print_success "Backend has no source code bind mounts"
    else
        print_failure "Backend has source code bind mounts in production"
    fi

    local frontend_volumes=$(grep -A 10 "^  frontend:" compose.production.yml | grep -A 5 "volumes:" | grep "volumes: \[\]" || true)
    if [[ -n "$frontend_volumes" ]]; then
        print_success "Frontend has no volumes (static content baked into image)"
    else
        print_warning "Frontend may have unnecessary volumes"
    fi
    echo
}

# =============================================================================
# Check 7: Network Isolation
# =============================================================================
check_network_isolation() {
    print_header "Check 7: Network Isolation (Port Exposure)"

    # Services that should NOT expose ports in production
    local isolated_services=("backend" "frontend" "db" "redis")

    for service in "${isolated_services[@]}"; do
        local ports=$(grep -A 10 "^  $service:" compose.production.yml | grep "ports: \[\]" || true)
        if [[ -n "$ports" ]]; then
            print_success "$service has no exposed ports (isolated)"
        else
            local port_count=$(grep -A 10 "^  $service:" compose.production.yml | grep -A 5 "ports:" | grep -c "\".*:.*\"" || true)
            if [[ "$port_count" -eq 0 ]]; then
                print_success "$service has no exposed ports"
            else
                print_warning "$service exposes $port_count port(s) - verify this is intentional"
            fi
        fi
    done

    # Proxy should expose ports
    local proxy_ports=$(grep -A 10 "^  proxy:" compose.production.yml | grep -A 5 "ports:" | grep -c "\".*:.*\"" || true)
    if [[ "$proxy_ports" -gt 0 ]]; then
        print_success "Proxy exposes $proxy_ports port(s) (required for external access)"
    else
        print_failure "Proxy doesn't expose any ports"
    fi
    echo
}

# =============================================================================
# Check 8: Security Configuration
# =============================================================================
check_security_config() {
    print_header "Check 8: Security Configuration"

    # Check SSL/TLS enforcement
    if grep -q "SECURE_SSL_REDIRECT=True" compose.production.yml; then
        print_success "SSL redirect enabled"
    else
        print_warning "SSL redirect not enabled"
    fi

    if grep -q "SESSION_COOKIE_SECURE=True" compose.production.yml; then
        print_success "Secure session cookies enabled"
    else
        print_warning "Secure session cookies not enabled"
    fi

    if grep -q "SECURE_HSTS_SECONDS=31536000" compose.production.yml; then
        print_success "HSTS enabled (1 year)"
    else
        print_warning "HSTS not configured"
    fi

    # Check restart policy
    local restart_count=$(grep -c "restart: always" compose.production.yml || true)
    if [[ "$restart_count" -gt 0 ]]; then
        print_success "Production services use 'restart: always' policy ($restart_count services)"
    else
        print_warning "No services configured with 'restart: always'"
    fi
    echo
}

# =============================================================================
# Check 9: Environment Files
# =============================================================================
check_env_files() {
    print_header "Check 9: Environment Configuration Files"

    # Check backend
    if [[ -f "backend/.env.production.example" ]]; then
        print_success "backend/.env.production.example exists"
    else
        print_warning "backend/.env.production.example not found"
    fi

    if [[ -f "backend/.env.production" ]]; then
        print_info "backend/.env.production exists (not tracked in git)"
    else
        print_warning "backend/.env.production not found (needs to be created from .example)"
    fi

    # Check frontend
    if [[ -f "frontend/.env.production.example" ]]; then
        print_success "frontend/.env.production.example exists"
    else
        print_warning "frontend/.env.production.example not found"
    fi

    if [[ -f "frontend/.env.production" ]]; then
        print_info "frontend/.env.production exists (not tracked in git)"
    else
        print_warning "frontend/.env.production not found (needs to be created from .example)"
    fi
    echo
}

# =============================================================================
# Check 10: Documentation
# =============================================================================
check_documentation() {
    print_header "Check 10: Production Documentation"

    if [[ -f "docs/features/12/production-optimizations.md" ]]; then
        print_success "Production optimizations documentation exists"
        local doc_size=$(wc -l < docs/features/12/production-optimizations.md)
        print_info "Documentation: $doc_size lines"
    else
        print_warning "Production optimizations documentation not found"
    fi
    echo
}

# =============================================================================
# Main Execution
# =============================================================================
main() {
    echo -e "${BLUE}"
    echo "╔═══════════════════════════════════════════════════════════════════╗"
    echo "║   Production Configuration Validation (Story 12.8)               ║"
    echo "║   Feature #12: Unified Multi-Service Orchestration               ║"
    echo "╚═══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo

    # Run all checks
    check_yaml_syntax
    check_compose_config
    check_dockerfile_targets
    check_nonroot_users
    check_resource_limits
    check_debug_disabled
    check_network_isolation
    check_security_config
    check_env_files
    check_documentation

    # Summary
    print_header "Validation Summary"
    echo -e "${GREEN}Passed:  $PASSED_CHECKS${NC}"
    echo -e "${YELLOW}Warnings: $WARNING_CHECKS${NC}"
    echo -e "${RED}Failed:   $FAILED_CHECKS${NC}"
    echo

    if [[ $FAILED_CHECKS -eq 0 ]]; then
        echo -e "${GREEN}✓ All critical checks passed!${NC}"
        echo -e "${GREEN}Production configuration is ready for deployment.${NC}"
        exit 0
    else
        echo -e "${RED}✗ $FAILED_CHECKS critical check(s) failed.${NC}"
        echo -e "${RED}Fix the failures before deploying to production.${NC}"
        exit 1
    fi
}

# Run main function
main "$@"
