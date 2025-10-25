#!/bin/bash
# =============================================================================
# Docker Setup Pre-Flight Validation Script
# =============================================================================
# This script validates the Docker development environment setup before
# starting containers, preventing common issues that cause startup failures.
#
# Usage:
#   ./scripts/preflight-check.sh              # Run all checks
#   ./scripts/preflight-check.sh --fix        # Run checks and auto-fix issues
#   ./scripts/preflight-check.sh --verbose    # Run with detailed output
#
# Exit codes:
#   0 - All checks passed
#   1 - One or more checks failed (or validation errors found)
#
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
VERBOSE=false
AUTO_FIX=false
ERRORS=0
WARNINGS=0

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --fix|-f)
            AUTO_FIX=true
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --help|-h)
            cat << EOF
${CYAN}Docker Setup Pre-Flight Validation Script${NC}

${YELLOW}Usage:${NC}
  ./scripts/preflight-check.sh [options]

${YELLOW}Options:${NC}
  --fix, -f         Auto-fix issues where possible
  --verbose, -v     Show detailed output
  --help, -h        Show this help message

${YELLOW}Checks Performed:${NC}
  ✓ Docker and Docker Compose installation
  ✓ Required files and directories exist
  ✓ Entrypoint script exists and is executable
  ✓ Log directory exists with correct permissions
  ✓ Environment files exist
  ✓ Docker daemon is running
  ✓ Port availability (80, 5432, 6379, 5173, 8000)

${YELLOW}Exit Codes:${NC}
  0 - All checks passed
  1 - One or more checks failed

${YELLOW}Examples:${NC}
  ./scripts/preflight-check.sh           # Run validation only
  ./scripts/preflight-check.sh --fix     # Run and auto-fix issues
  ./scripts/preflight-check.sh --verbose # Run with detailed output

EOF
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Helper functions
print_header() {
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
}

print_check() {
    echo -e "${BLUE}[CHECK]${NC} $1"
}

print_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

print_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((ERRORS++))
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
    ((WARNINGS++))
}

print_info() {
    if [ "$VERBOSE" = true ]; then
        echo -e "${CYAN}[INFO]${NC} $1"
    fi
}

print_fix() {
    echo -e "${GREEN}[FIX]${NC} $1"
}

# Check functions
check_docker_installed() {
    print_check "Checking if Docker is installed..."
    if command -v docker &> /dev/null; then
        local docker_version=$(docker --version)
        print_pass "Docker is installed: $docker_version"
        print_info "Docker client path: $(which docker)"
        return 0
    else
        print_fail "Docker is not installed or not in PATH"
        echo "  → Install Docker: https://docs.docker.com/get-docker/"
        return 1
    fi
}

check_docker_compose_installed() {
    print_check "Checking if Docker Compose is installed..."
    if docker compose version &> /dev/null; then
        local compose_version=$(docker compose version)
        print_pass "Docker Compose is available: $compose_version"
        return 0
    else
        print_fail "Docker Compose is not available"
        echo "  → Install Docker Compose: https://docs.docker.com/compose/install/"
        return 1
    fi
}

check_docker_daemon_running() {
    print_check "Checking if Docker daemon is running..."
    if docker info &> /dev/null; then
        print_pass "Docker daemon is running"
        if [ "$VERBOSE" = true ]; then
            local containers=$(docker ps -q | wc -l)
            print_info "Currently running containers: $containers"
        fi
        return 0
    else
        print_fail "Docker daemon is not running"
        echo "  → Start Docker daemon: sudo systemctl start docker (Linux)"
        echo "  → Or open Docker Desktop (macOS/Windows)"
        return 1
    fi
}

check_entrypoint_script() {
    print_check "Checking backend entrypoint script..."
    local entrypoint="$BACKEND_DIR/docker-entrypoint-dev.sh"

    if [ ! -f "$entrypoint" ]; then
        print_fail "Entrypoint script not found: $entrypoint"
        echo "  → The entrypoint script should exist in the repository"
        echo "  → If missing, restore it from version control"
        return 1
    fi

    print_pass "Entrypoint script exists: $entrypoint"

    # Check if executable
    if [ ! -x "$entrypoint" ]; then
        if [ "$AUTO_FIX" = true ]; then
            print_fix "Making entrypoint script executable..."
            chmod +x "$entrypoint"
            print_pass "Entrypoint script is now executable"
        else
            print_warning "Entrypoint script is not executable"
            echo "  → Run with --fix to auto-fix, or manually: chmod +x $entrypoint"
        fi
    else
        print_pass "Entrypoint script is executable"
    fi

    print_info "Entrypoint script permissions: $(stat -c '%a' "$entrypoint" 2>/dev/null || stat -f '%A' "$entrypoint" 2>/dev/null)"
    return 0
}

check_log_directory() {
    print_check "Checking backend log directory..."
    local log_dir="$BACKEND_DIR/logs"

    if [ ! -d "$log_dir" ]; then
        if [ "$AUTO_FIX" = true ]; then
            print_fix "Creating log directory..."
            mkdir -p "$log_dir"
            print_pass "Log directory created: $log_dir"
        else
            print_warning "Log directory does not exist: $log_dir"
            echo "  → Run with --fix to auto-fix, or manually: mkdir -p $log_dir"
            return 0
        fi
    else
        print_pass "Log directory exists: $log_dir"
    fi

    # Check for log files and their permissions
    local log_files=$(find "$log_dir" -type f -name "*.log" 2>/dev/null)
    if [ -n "$log_files" ]; then
        print_info "Found existing log files"

        # Check if log files are writable
        local readonly_logs=$(find "$log_dir" -type f -name "*.log" ! -writable 2>/dev/null)
        if [ -n "$readonly_logs" ]; then
            if [ "$AUTO_FIX" = true ]; then
                print_fix "Fixing log file permissions (making world-writable for container access)..."
                find "$log_dir" -type f -name "*.log" -exec chmod 666 {} \; 2>/dev/null
                print_pass "Log file permissions fixed"
            else
                print_warning "Some log files are not writable by the container user (UID 1001)"
                echo "  → Run with --fix to auto-fix, or manually: chmod 666 $log_dir/*.log"
                echo "  → Note: Entrypoint script will also attempt to fix permissions on startup"
            fi
        else
            print_pass "Log files have correct permissions"
        fi
    else
        print_info "No existing log files (will be created on first run)"
    fi

    return 0
}

check_env_files() {
    print_check "Checking environment files..."
    local backend_env="$BACKEND_DIR/.env.docker"
    local frontend_env="$FRONTEND_DIR/.env.docker"
    local all_ok=true

    # Backend .env.docker
    if [ -f "$backend_env" ]; then
        print_pass "Backend environment file exists: .env.docker"
        print_info "Backend .env.docker path: $backend_env"
    else
        print_warning "Backend environment file not found: $backend_env"
        echo "  → Create from example: cp $BACKEND_DIR/.env.example $backend_env"
        all_ok=false
    fi

    # Frontend .env.docker
    if [ -f "$frontend_env" ]; then
        print_pass "Frontend environment file exists: .env.docker"
        print_info "Frontend .env.docker path: $frontend_env"
    else
        print_warning "Frontend environment file not found: $frontend_env"
        echo "  → Create from example: cp $FRONTEND_DIR/.env.example $frontend_env"
        all_ok=false
    fi

    [ "$all_ok" = true ] && return 0 || return 0  # Don't fail, just warn
}

check_required_files() {
    print_check "Checking required files..."
    local all_ok=true

    local required_files=(
        "$PROJECT_ROOT/docker-compose.yml"
        "$BACKEND_DIR/Dockerfile"
        "$FRONTEND_DIR/Dockerfile"
        "$BACKEND_DIR/requirements/base.txt"
        "$BACKEND_DIR/requirements/dev.txt"
        "$FRONTEND_DIR/package.json"
    )

    for file in "${required_files[@]}"; do
        if [ -f "$file" ]; then
            print_info "✓ $(basename $file)"
        else
            print_fail "Missing required file: $file"
            all_ok=false
        fi
    done

    [ "$all_ok" = true ] && print_pass "All required files exist" && return 0 || return 1
}

check_port_availability() {
    print_check "Checking port availability..."

    # Ports used by services
    local ports=(80 5432 6379 5173 8000)
    local port_names=("Proxy" "PostgreSQL" "Redis" "Frontend" "Backend")
    local conflicts=()

    for i in "${!ports[@]}"; do
        local port="${ports[$i]}"
        local name="${port_names[$i]}"

        # Check if port is in use
        if command -v lsof &> /dev/null; then
            if lsof -i ":$port" -sTCP:LISTEN -t &> /dev/null; then
                print_warning "Port $port ($name) is already in use"
                if [ "$VERBOSE" = true ]; then
                    lsof -i ":$port" -sTCP:LISTEN
                fi
                conflicts+=("$port ($name)")
            else
                print_info "✓ Port $port ($name) is available"
            fi
        elif command -v netstat &> /dev/null; then
            if netstat -tuln | grep -q ":$port "; then
                print_warning "Port $port ($name) is already in use"
                conflicts+=("$port ($name)")
            else
                print_info "✓ Port $port ($name) is available"
            fi
        else
            print_info "Cannot check port $port (lsof/netstat not available)"
        fi
    done

    if [ ${#conflicts[@]} -eq 0 ]; then
        print_pass "All required ports are available"
        return 0
    else
        print_warning "Some ports are in use: ${conflicts[*]}"
        echo "  → Stop conflicting services or Docker containers using these ports"
        echo "  → Run: docker compose down (if previous containers are still running)"
        return 0  # Don't fail, just warn
    fi
}

check_disk_space() {
    print_check "Checking available disk space..."

    # Check available space in project directory
    local available=$(df -h "$PROJECT_ROOT" | awk 'NR==2 {print $4}')
    local available_bytes=$(df "$PROJECT_ROOT" | awk 'NR==2 {print $4}')

    print_info "Available disk space: $available"

    # Warn if less than 5GB available
    if [ "$available_bytes" -lt 5242880 ]; then  # 5GB in KB
        print_warning "Low disk space: $available (recommend at least 5GB for Docker images)"
        echo "  → Free up disk space or run: docker system prune -a"
    else
        print_pass "Sufficient disk space available: $available"
    fi

    return 0
}

check_docker_compose_syntax() {
    print_check "Validating docker-compose.yml syntax..."

    if docker compose config &> /dev/null; then
        print_pass "docker-compose.yml syntax is valid"
        return 0
    else
        print_fail "docker-compose.yml has syntax errors"
        echo "  → Run: docker compose config (to see detailed errors)"
        return 1
    fi
}

# Main execution
main() {
    print_header "Docker Setup Pre-Flight Validation"
    echo ""
    echo "Project root: $PROJECT_ROOT"
    if [ "$AUTO_FIX" = true ]; then
        echo -e "${GREEN}Auto-fix mode enabled${NC}"
    fi
    if [ "$VERBOSE" = true ]; then
        echo -e "${CYAN}Verbose mode enabled${NC}"
    fi

    # Run all checks
    check_docker_installed
    check_docker_compose_installed
    check_docker_daemon_running
    check_required_files
    check_entrypoint_script
    check_log_directory
    check_env_files
    check_port_availability
    check_disk_space
    check_docker_compose_syntax

    # Summary
    print_header "Validation Summary"
    echo ""

    if [ $ERRORS -eq 0 ]; then
        echo -e "${GREEN}✓ All critical checks passed${NC}"
    else
        echo -e "${RED}✗ $ERRORS critical check(s) failed${NC}"
    fi

    if [ $WARNINGS -gt 0 ]; then
        echo -e "${YELLOW}⚠ $WARNINGS warning(s) found${NC}"
    fi

    echo ""

    if [ $ERRORS -eq 0 ]; then
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${GREEN}  Environment is ready for Docker Compose${NC}"
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        echo "Next steps:"
        echo "  1. Start services: docker compose up -d"
        echo "  2. View logs: docker compose logs -f"
        echo "  3. Check status: docker compose ps"
        echo ""
        echo "Or use the helper script:"
        echo "  ./docker-dev.sh start"
        echo ""
        exit 0
    else
        echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${RED}  Please fix the errors above before starting containers${NC}"
        echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        if [ "$AUTO_FIX" = false ]; then
            echo "Tip: Run with --fix to automatically fix some issues:"
            echo "  ./scripts/preflight-check.sh --fix"
            echo ""
        fi
        exit 1
    fi
}

# Run main function
main
