#!/bin/bash
# =============================================================================
# Docker Environment Manager Script
# =============================================================================
# This script manages Docker Compose deployment across different environments
# (local, staging, production) with proper configuration validation.
#
# Usage:
#   ./docker-env.sh <environment> <command> [options]
#
# Environments:
#   local      - Local development (default compose.override.yml)
#   staging    - Staging environment (compose.staging.yml)
#   production - Production environment (compose.production.yml)
#
# Commands:
#   start      - Start services
#   stop       - Stop services
#   restart    - Restart services
#   down       - Stop and remove containers
#   logs       - View logs
#   ps         - Show running services
#   validate   - Validate configuration
#   config     - Show merged configuration
#   pull       - Pull images from registry
#   build      - Build images
#
# Examples:
#   ./docker-env.sh local start
#   ./docker-env.sh staging logs backend
#   ./docker-env.sh production validate
# =============================================================================

set -e  # Exit on error

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_COMPOSE_FILE="${SCRIPT_DIR}/docker-compose.yml"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------

print_header() {
    echo -e "${BLUE}================================================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}================================================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# -----------------------------------------------------------------------------
# Validation Functions
# -----------------------------------------------------------------------------

validate_environment() {
    local env=$1

    case $env in
        local|staging|production)
            return 0
            ;;
        *)
            print_error "Invalid environment: $env"
            echo "Valid environments: local, staging, production"
            return 1
            ;;
    esac
}

validate_env_file() {
    local env=$1
    local env_file=$2

    if [ ! -f "$env_file" ]; then
        print_warning "Environment file not found: $env_file"

        if [ "$env" = "local" ]; then
            print_info "Using default .env file or docker-compose.yml defaults"
            return 0
        else
            print_error "Environment file required for $env environment"
            print_info "Copy from example: cp ${env_file}.example ${env_file}"
            return 1
        fi
    fi

    # Check for CHANGE_ME values in staging/production
    if [ "$env" != "local" ]; then
        if grep -q "CHANGE_ME" "$env_file" 2>/dev/null; then
            print_error "Environment file contains CHANGE_ME placeholders"
            print_info "Please update all CHANGE_ME values in: $env_file"
            return 1
        fi

        # Check for minimum password length (basic validation)
        if [ "$env" = "production" ]; then
            local db_pass=$(grep "^DB_PASSWORD=" "$env_file" | cut -d'=' -f2)
            if [ ${#db_pass} -lt 20 ]; then
                print_warning "DB_PASSWORD may be too short for production (recommend 32+ characters)"
            fi
        fi
    fi

    print_success "Environment file validated: $env_file"
    return 0
}

validate_compose_files() {
    local env=$1
    shift
    local compose_files=("$@")

    print_info "Validating Docker Compose configuration..."

    # Build docker compose command
    local compose_cmd="docker compose"
    for file in "${compose_files[@]}"; do
        compose_cmd="$compose_cmd -f $file"
    done

    # Validate configuration
    if eval "$compose_cmd config --quiet"; then
        print_success "Docker Compose configuration is valid"
        return 0
    else
        print_error "Docker Compose configuration is invalid"
        print_info "Run: $compose_cmd config"
        return 1
    fi
}

check_prerequisites() {
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        return 1
    fi

    # Check if Docker Compose is available
    if ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not available"
        return 1
    fi

    # Check if base compose file exists
    if [ ! -f "$BASE_COMPOSE_FILE" ]; then
        print_error "Base compose file not found: $BASE_COMPOSE_FILE"
        return 1
    fi

    return 0
}

# -----------------------------------------------------------------------------
# Environment Configuration
# -----------------------------------------------------------------------------

get_compose_files() {
    local env=$1
    local files=("$BASE_COMPOSE_FILE")

    case $env in
        local)
            if [ -f "${SCRIPT_DIR}/compose.override.yml" ]; then
                files+=("${SCRIPT_DIR}/compose.override.yml")
            fi
            ;;
        staging)
            files+=("${SCRIPT_DIR}/compose.staging.yml")
            ;;
        production)
            files+=("${SCRIPT_DIR}/compose.production.yml")
            ;;
    esac

    echo "${files[@]}"
}

get_env_file() {
    local env=$1

    case $env in
        local)
            # Try .env.local, then .env, then none
            if [ -f "${SCRIPT_DIR}/.env.local" ]; then
                echo "${SCRIPT_DIR}/.env.local"
            elif [ -f "${SCRIPT_DIR}/.env" ]; then
                echo "${SCRIPT_DIR}/.env"
            else
                echo ""
            fi
            ;;
        staging)
            echo "${SCRIPT_DIR}/.env.staging"
            ;;
        production)
            echo "${SCRIPT_DIR}/.env.production"
            ;;
    esac
}

# -----------------------------------------------------------------------------
# Docker Compose Command Builder
# -----------------------------------------------------------------------------

build_docker_compose_cmd() {
    local env=$1
    shift

    local compose_files=($(get_compose_files "$env"))
    local env_file=$(get_env_file "$env")

    local cmd="docker compose"

    # Add compose files
    for file in "${compose_files[@]}"; do
        cmd="$cmd -f $file"
    done

    # Add env file if exists
    if [ -n "$env_file" ] && [ -f "$env_file" ]; then
        cmd="$cmd --env-file $env_file"
    fi

    # Add remaining arguments
    cmd="$cmd $@"

    echo "$cmd"
}

# -----------------------------------------------------------------------------
# Command Implementations
# -----------------------------------------------------------------------------

cmd_start() {
    local env=$1
    shift

    print_header "Starting $env environment"

    local cmd=$(build_docker_compose_cmd "$env" up -d "$@")
    print_info "Command: $cmd"
    eval $cmd

    print_success "Services started in $env environment"
    print_info "Access the application at: http://localhost/"

    if [ "$env" = "local" ]; then
        print_info "Direct service access:"
        print_info "  - Frontend: http://localhost:5173"
        print_info "  - Backend: http://localhost:8000"
        print_info "  - Backend API Docs: http://localhost:8000/api/v1/docs/"
    fi
}

cmd_stop() {
    local env=$1
    shift

    print_header "Stopping $env environment"

    local cmd=$(build_docker_compose_cmd "$env" stop "$@")
    print_info "Command: $cmd"
    eval $cmd

    print_success "Services stopped in $env environment"
}

cmd_restart() {
    local env=$1
    shift

    print_header "Restarting $env environment"

    cmd_stop "$env" "$@"
    sleep 2
    cmd_start "$env" "$@"
}

cmd_down() {
    local env=$1
    shift

    print_header "Stopping and removing containers in $env environment"
    print_warning "This will stop and remove all containers"

    local cmd=$(build_docker_compose_cmd "$env" down "$@")
    print_info "Command: $cmd"
    eval $cmd

    print_success "Containers stopped and removed in $env environment"
}

cmd_logs() {
    local env=$1
    shift

    print_header "Viewing logs for $env environment"

    local cmd=$(build_docker_compose_cmd "$env" logs -f "$@")
    print_info "Command: $cmd"
    print_info "Press Ctrl+C to exit"
    eval $cmd
}

cmd_ps() {
    local env=$1
    shift

    print_header "Services status in $env environment"

    local cmd=$(build_docker_compose_cmd "$env" ps "$@")
    eval $cmd
}

cmd_validate() {
    local env=$1

    print_header "Validating $env environment configuration"

    local env_file=$(get_env_file "$env")
    local compose_files=($(get_compose_files "$env"))

    # Validate environment file
    if [ -n "$env_file" ]; then
        validate_env_file "$env" "$env_file" || return 1
    fi

    # Validate compose configuration
    validate_compose_files "$env" "${compose_files[@]}" || return 1

    print_success "All validations passed for $env environment"
}

cmd_config() {
    local env=$1
    shift

    print_header "Merged Docker Compose configuration for $env environment"

    local cmd=$(build_docker_compose_cmd "$env" config "$@")
    eval $cmd
}

cmd_pull() {
    local env=$1
    shift

    print_header "Pulling images for $env environment"

    if [ "$env" = "local" ]; then
        print_warning "Local environment uses locally built images"
        print_info "Use 'build' command instead"
        return 0
    fi

    local cmd=$(build_docker_compose_cmd "$env" pull "$@")
    print_info "Command: $cmd"
    eval $cmd

    print_success "Images pulled for $env environment"
}

cmd_build() {
    local env=$1
    shift

    print_header "Building images for $env environment"

    local cmd=$(build_docker_compose_cmd "$env" build "$@")
    print_info "Command: $cmd"
    eval $cmd

    print_success "Images built for $env environment"
}

cmd_exec() {
    local env=$1
    local service=$2
    shift 2

    print_header "Executing command in $service ($env environment)"

    local cmd=$(build_docker_compose_cmd "$env" exec "$service" "$@")
    print_info "Command: $cmd"
    eval $cmd
}

# -----------------------------------------------------------------------------
# Help Function
# -----------------------------------------------------------------------------

show_help() {
    cat << EOF
Docker Environment Manager

Usage:
  $0 <environment> <command> [options]

Environments:
  local       Local development (compose.override.yml)
  staging     Staging environment (compose.staging.yml)
  production  Production environment (compose.production.yml)

Commands:
  start       Start services
  stop        Stop services
  restart     Restart services
  down        Stop and remove containers
  logs        View logs (follow mode)
  ps          Show running services
  validate    Validate configuration
  config      Show merged configuration
  pull        Pull images from registry
  build       Build images
  exec        Execute command in service

Examples:
  # Start local development environment
  $0 local start

  # View logs for staging backend
  $0 staging logs backend

  # Validate production configuration
  $0 production validate

  # Stop all staging services
  $0 staging down

  # Execute shell in local backend
  $0 local exec backend bash

  # Show merged staging configuration
  $0 staging config

Environment Files:
  local:      .env.local (or .env)
  staging:    .env.staging (required)
  production: .env.production (required)

Setup:
  # Create environment files from examples
  cp .env.local.example .env.local
  cp .env.staging.example .env.staging
  cp .env.production.example .env.production

  # Edit environment files with appropriate values
  # For staging/production, replace all CHANGE_ME values

Configuration Files:
  Base:       docker-compose.yml
  Local:      compose.override.yml (automatically loaded)
  Staging:    compose.staging.yml
  Production: compose.production.yml

For more information, see docs/features/12/
EOF
}

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

main() {
    # Check prerequisites
    check_prerequisites || exit 1

    # Parse arguments
    if [ $# -lt 1 ]; then
        show_help
        exit 1
    fi

    local environment=$1
    shift

    # Validate environment
    if [ "$environment" = "help" ] || [ "$environment" = "-h" ] || [ "$environment" = "--help" ]; then
        show_help
        exit 0
    fi

    validate_environment "$environment" || exit 1

    # Get command
    if [ $# -lt 1 ]; then
        print_error "No command specified"
        show_help
        exit 1
    fi

    local command=$1
    shift

    # Execute command
    case $command in
        start)
            cmd_start "$environment" "$@"
            ;;
        stop)
            cmd_stop "$environment" "$@"
            ;;
        restart)
            cmd_restart "$environment" "$@"
            ;;
        down)
            cmd_down "$environment" "$@"
            ;;
        logs)
            cmd_logs "$environment" "$@"
            ;;
        ps)
            cmd_ps "$environment" "$@"
            ;;
        validate)
            cmd_validate "$environment"
            ;;
        config)
            cmd_config "$environment" "$@"
            ;;
        pull)
            cmd_pull "$environment" "$@"
            ;;
        build)
            cmd_build "$environment" "$@"
            ;;
        exec)
            cmd_exec "$environment" "$@"
            ;;
        help|-h|--help)
            show_help
            ;;
        *)
            print_error "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
