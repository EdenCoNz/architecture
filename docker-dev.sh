#!/bin/bash
# =============================================================================
# Docker Development Helper Script
# =============================================================================
# Convenient wrapper around docker compose commands for the full application
# stack (frontend, backend, database, redis).
#
# Usage: ./docker-dev.sh <command> [options]
#
# Commands:
#   start                Start all services
#   stop                 Stop all services
#   restart              Restart all services
#   build                Build/rebuild all containers
#   rebuild              Rebuild and restart all services
#   logs [service]       View logs (optionally for specific service)
#   shell <service>      Open shell in service container
#   exec <service> <cmd> Execute command in service container
#   ps                   Show service status
#   clean                Remove containers and volumes (DESTRUCTIVE)
#   status               Show detailed service status
#   backend-shell        Open Django shell
#   backend-migrate      Run database migrations
#   backend-makemigrations Create new migrations
#   frontend-shell       Open shell in frontend container
#   db-shell             Open PostgreSQL shell
#   redis-cli            Open Redis CLI
#   help                 Show this help message
#
# Examples:
#   ./docker-dev.sh start
#   ./docker-dev.sh logs backend
#   ./docker-dev.sh rebuild
#   ./docker-dev.sh backend-shell
#
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Helper functions
print_info() {
    echo -e "${BLUE}INFO:${NC} $1"
}

print_success() {
    echo -e "${GREEN}SUCCESS:${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}WARNING:${NC} $1"
}

print_error() {
    echo -e "${RED}ERROR:${NC} $1"
}

print_header() {
    echo -e "${MAGENTA}=== $1 ===${NC}"
}

# Check if docker compose is available
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed or not in PATH"
        exit 1
    fi

    if ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not available. Please install Docker Compose."
        exit 1
    fi
}

# Main commands
cmd_start() {
    print_header "Starting all services"
    docker compose up -d
    print_success "All services started"
    echo ""
    cmd_status
}

cmd_stop() {
    print_header "Stopping all services"
    docker compose down
    print_success "All services stopped"
}

cmd_restart() {
    print_header "Restarting all services"
    docker compose restart
    print_success "All services restarted"
    echo ""
    cmd_status
}

cmd_build() {
    print_header "Building all containers"
    docker compose build --no-cache
    print_success "All containers built"
}

cmd_rebuild() {
    print_header "Rebuilding and restarting all services"
    docker compose down
    docker compose build
    docker compose up -d
    print_success "All services rebuilt and restarted"
    echo ""
    cmd_status
}

cmd_logs() {
    local service=$1
    if [ -z "$service" ]; then
        print_header "Viewing logs for all services"
        docker compose logs -f
    else
        print_header "Viewing logs for $service"
        docker compose logs -f "$service"
    fi
}

cmd_shell() {
    local service=$1
    if [ -z "$service" ]; then
        print_error "Please specify a service name"
        echo "Available services: frontend, backend, db, redis, celery"
        exit 1
    fi

    print_header "Opening shell in $service"
    docker compose exec "$service" /bin/sh
}

cmd_exec() {
    local service=$1
    shift
    local command=$@

    if [ -z "$service" ] || [ -z "$command" ]; then
        print_error "Usage: ./docker-dev.sh exec <service> <command>"
        exit 1
    fi

    print_header "Executing command in $service"
    docker compose exec "$service" $command
}

cmd_ps() {
    print_header "Service status"
    docker compose ps
}

cmd_clean() {
    print_warning "This will remove all containers and volumes (including database data)"
    read -p "Are you sure? (yes/no): " -r
    echo
    if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        print_header "Cleaning up containers and volumes"
        docker compose down -v
        print_success "Cleanup complete"
    else
        print_info "Cleanup cancelled"
    fi
}

cmd_status() {
    print_header "Detailed service status"
    docker compose ps
    echo ""

    # Check health status
    print_info "Health checks:"
    for service in db redis backend frontend; do
        health=$(docker inspect --format='{{.State.Health.Status}}' "app-$service" 2>/dev/null || echo "not running")
        if [ "$health" = "healthy" ]; then
            echo -e "  $service: ${GREEN}healthy${NC}"
        elif [ "$health" = "starting" ]; then
            echo -e "  $service: ${YELLOW}starting${NC}"
        elif [ "$health" = "unhealthy" ]; then
            echo -e "  $service: ${RED}unhealthy${NC}"
        else
            echo -e "  $service: ${RED}$health${NC}"
        fi
    done
    echo ""

    # Show URLs
    print_info "Application URLs:"
    echo "  Frontend: http://localhost:5173"
    echo "  Backend API: http://localhost:8000"
    echo "  Backend Admin: http://localhost:8000/admin"
    echo "  Backend Health: http://localhost:8000/api/v1/health/"
    echo ""

    print_info "Database connection:"
    echo "  Host: localhost"
    echo "  Port: 5432"
    echo "  Database: backend_db"
    echo "  User: postgres"
    echo "  Password: postgres"
    echo ""

    print_info "Redis connection:"
    echo "  Host: localhost"
    echo "  Port: 6379"
}

cmd_backend_shell() {
    print_header "Opening Django shell"
    docker compose exec backend python manage.py shell
}

cmd_backend_migrate() {
    print_header "Running database migrations"
    docker compose exec backend python manage.py migrate
    print_success "Migrations complete"
}

cmd_backend_makemigrations() {
    print_header "Creating new migrations"
    docker compose exec backend python manage.py makemigrations
    print_success "Migrations created"
}

cmd_frontend_shell() {
    print_header "Opening shell in frontend container"
    docker compose exec frontend /bin/sh
}

cmd_db_shell() {
    print_header "Opening PostgreSQL shell"
    docker compose exec db psql -U postgres -d backend_db
}

cmd_redis_cli() {
    print_header "Opening Redis CLI"
    docker compose exec redis redis-cli
}

cmd_help() {
    cat << EOF
${CYAN}Docker Development Helper Script${NC}

${YELLOW}Usage:${NC} ./docker-dev.sh <command> [options]

${YELLOW}Commands:${NC}
  ${GREEN}start${NC}                         Start all services
  ${GREEN}stop${NC}                          Stop all services
  ${GREEN}restart${NC}                       Restart all services
  ${GREEN}build${NC}                         Build/rebuild all containers
  ${GREEN}rebuild${NC}                       Rebuild and restart all services
  ${GREEN}logs${NC} [service]                View logs (optionally for specific service)
  ${GREEN}shell${NC} <service>               Open shell in service container
  ${GREEN}exec${NC} <service> <cmd>          Execute command in service container
  ${GREEN}ps${NC}                            Show service status
  ${GREEN}clean${NC}                         Remove containers and volumes (DESTRUCTIVE)
  ${GREEN}status${NC}                        Show detailed service status
  ${GREEN}backend-shell${NC}                 Open Django shell
  ${GREEN}backend-migrate${NC}               Run database migrations
  ${GREEN}backend-makemigrations${NC}        Create new migrations
  ${GREEN}frontend-shell${NC}                Open shell in frontend container
  ${GREEN}db-shell${NC}                      Open PostgreSQL shell
  ${GREEN}redis-cli${NC}                     Open Redis CLI
  ${GREEN}help${NC}                          Show this help message

${YELLOW}Examples:${NC}
  ./docker-dev.sh start
  ./docker-dev.sh logs backend
  ./docker-dev.sh rebuild
  ./docker-dev.sh backend-shell
  ./docker-dev.sh exec backend python manage.py createsuperuser

${YELLOW}Available services:${NC}
  - frontend  (React/Vite application)
  - backend   (Django REST API)
  - db        (PostgreSQL database)
  - redis     (Redis cache)
  - celery    (Background task worker - optional)

${YELLOW}Application URLs:${NC}
  Frontend:      http://localhost:5173
  Backend API:   http://localhost:8000
  Backend Admin: http://localhost:8000/admin

EOF
}

# Main script
main() {
    check_docker

    local command=${1:-help}
    shift || true

    case "$command" in
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
        rebuild)
            cmd_rebuild
            ;;
        logs)
            cmd_logs "$@"
            ;;
        shell)
            cmd_shell "$@"
            ;;
        exec)
            cmd_exec "$@"
            ;;
        ps)
            cmd_ps
            ;;
        clean)
            cmd_clean
            ;;
        status)
            cmd_status
            ;;
        backend-shell)
            cmd_backend_shell
            ;;
        backend-migrate)
            cmd_backend_migrate
            ;;
        backend-makemigrations)
            cmd_backend_makemigrations
            ;;
        frontend-shell)
            cmd_frontend_shell
            ;;
        db-shell)
            cmd_db_shell
            ;;
        redis-cli)
            cmd_redis_cli
            ;;
        help|--help|-h)
            cmd_help
            ;;
        *)
            print_error "Unknown command: $command"
            echo ""
            cmd_help
            exit 1
            ;;
    esac
}

main "$@"
