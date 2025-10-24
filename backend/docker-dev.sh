#!/bin/bash

# =============================================================================
# Docker Development Helper Script
# =============================================================================
# This script provides convenient commands for managing Docker development
# environment for the backend application.
#
# Usage:
#   ./docker-dev.sh start       - Start all services
#   ./docker-dev.sh stop        - Stop all services
#   ./docker-dev.sh restart     - Restart all services
#   ./docker-dev.sh build       - Rebuild containers
#   ./docker-dev.sh logs        - View logs
#   ./docker-dev.sh shell       - Open shell in backend container
#   ./docker-dev.sh migrate     - Run database migrations
#   ./docker-dev.sh test        - Run tests
#   ./docker-dev.sh clean       - Remove all containers and volumes
#   ./docker-dev.sh status      - Show service status
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Function to print colored messages
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Function to check if .env.docker exists
check_env() {
    if [ ! -f .env.docker ]; then
        print_error ".env.docker file not found!"
        print_info "Creating .env.docker from template..."
        # The file should already exist, but this is a safety check
        exit 1
    fi
}

# Command handlers
cmd_start() {
    print_info "Starting Docker services..."
    check_docker
    check_env

    docker compose up -d

    print_success "Services started!"
    print_info "Waiting for services to be healthy..."
    sleep 5

    docker compose ps

    echo ""
    print_success "Backend API is available at: http://localhost:8000"
    print_info "API Documentation: http://localhost:8000/api/v1/docs/"
    print_info "View logs: ./docker-dev.sh logs"
}

cmd_stop() {
    print_info "Stopping Docker services..."
    check_docker

    docker compose down

    print_success "Services stopped!"
}

cmd_restart() {
    print_info "Restarting Docker services..."
    cmd_stop
    sleep 2
    cmd_start
}

cmd_build() {
    print_info "Building Docker images..."
    check_docker
    check_env

    docker compose build --no-cache

    print_success "Build complete!"
}

cmd_logs() {
    check_docker

    if [ -n "$2" ]; then
        # Show logs for specific service
        docker compose logs -f "$2"
    else
        # Show logs for all services
        docker compose logs -f
    fi
}

cmd_shell() {
    print_info "Opening shell in backend container..."
    check_docker

    docker compose exec backend bash
}

cmd_migrate() {
    print_info "Running database migrations..."
    check_docker

    docker compose exec backend python manage.py migrate

    print_success "Migrations complete!"
}

cmd_makemigrations() {
    print_info "Creating new migrations..."
    check_docker

    docker compose exec backend python manage.py makemigrations

    print_success "Migrations created!"
}

cmd_test() {
    print_info "Running tests..."
    check_docker

    docker compose exec backend pytest "${@:2}"

    print_success "Tests complete!"
}

cmd_clean() {
    print_warning "This will remove all containers, networks, and volumes!"
    read -p "Are you sure? (y/N) " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Cleaning up Docker resources..."
        docker compose down -v
        print_success "Cleanup complete!"
    else
        print_info "Cleanup cancelled."
    fi
}

cmd_status() {
    print_info "Service status:"
    check_docker

    docker compose ps

    echo ""
    print_info "Checking service health..."

    # Check backend health
    if curl -sf http://localhost:8000/api/v1/health/ > /dev/null 2>&1; then
        print_success "Backend API is healthy"
    else
        print_error "Backend API is not responding"
    fi

    # Check database
    if docker compose exec -T db pg_isready -U postgres -d backend_db > /dev/null 2>&1; then
        print_success "Database is healthy"
    else
        print_error "Database is not healthy"
    fi

    # Check Redis
    if docker compose exec -T redis redis-cli ping > /dev/null 2>&1; then
        print_success "Redis is healthy"
    else
        print_error "Redis is not healthy"
    fi
}

cmd_createsuperuser() {
    print_info "Creating Django superuser..."
    check_docker

    docker compose exec backend python manage.py createsuperuser
}

cmd_help() {
    cat << EOF
Docker Development Helper Script

Usage: ./docker-dev.sh <command> [options]

Commands:
    start               Start all services in background
    stop                Stop all services
    restart             Restart all services
    build               Rebuild Docker images
    logs [service]      View logs (optionally for specific service)
    shell               Open bash shell in backend container
    migrate             Run database migrations
    makemigrations      Create new migrations
    test [args]         Run tests (with optional pytest arguments)
    clean               Remove all containers and volumes
    status              Show service status and health
    createsuperuser     Create Django superuser
    help                Show this help message

Examples:
    ./docker-dev.sh start
    ./docker-dev.sh logs backend
    ./docker-dev.sh test tests/unit
    ./docker-dev.sh shell

For more information, see DOCKER.md
EOF
}

# Main command dispatcher
case "${1:-}" in
    start)
        cmd_start
        ;;
    stop)
        cmd_stop
        ;;
    restart)
        cmd_restart
        ;;
    build)
        cmd_build
        ;;
    logs)
        cmd_logs "$@"
        ;;
    shell)
        cmd_shell
        ;;
    migrate)
        cmd_migrate
        ;;
    makemigrations)
        cmd_makemigrations
        ;;
    test)
        cmd_test "$@"
        ;;
    clean)
        cmd_clean
        ;;
    status)
        cmd_status
        ;;
    createsuperuser)
        cmd_createsuperuser
        ;;
    help|--help|-h)
        cmd_help
        ;;
    "")
        print_error "No command specified"
        echo ""
        cmd_help
        exit 1
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        cmd_help
        exit 1
        ;;
esac
