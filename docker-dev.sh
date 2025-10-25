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
#   status               Show detailed service status
#   validate [--quick] [--verbose] Validate orchestration is working correctly
#   clean                Remove containers and volumes (DESTRUCTIVE)
#   clean-containers     Remove only containers, preserve data
#   clean-logs           Remove only log files
#   clean-cache          Remove only Redis cache data
#   clean-all            Remove everything including persistent data
#   status               Show detailed service status
#   volumes              Show volume information and disk usage
#   backup               Backup all persistent data
#   backup-db            Backup database only
#   restore <file>       Restore from backup file
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

    # Run pre-flight check first (with auto-fix)
    if [ -f "./scripts/preflight-check.sh" ]; then
        print_info "Running pre-flight validation..."
        if ./scripts/preflight-check.sh --fix; then
            echo ""
        else
            print_error "Pre-flight validation failed. Please fix errors above."
            exit 1
        fi
    else
        print_warning "Pre-flight check script not found, skipping validation"
        echo ""
    fi

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
    print_warning "This will remove containers but preserve all data volumes"
    print_info "For complete cleanup including data, use: ./docker-dev.sh clean-all"
    read -p "Continue? (yes/no): " -r
    echo
    if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        print_header "Cleaning up containers"
        docker compose down
        print_success "Containers removed, data volumes preserved"
    else
        print_info "Cleanup cancelled"
    fi
}

cmd_clean_containers() {
    print_header "Removing containers only"
    docker compose down
    print_success "Containers removed, all data preserved"
}

cmd_clean_logs() {
    print_warning "This will remove log files and proxy logs volume"
    read -p "Continue? (yes/no): " -r
    echo
    if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        print_header "Cleaning log files"
        # Remove backend logs directory
        if [ -d "./backend/logs" ]; then
            rm -rf ./backend/logs/*
            print_success "Backend log files removed"
        fi
        # Remove proxy logs volume
        docker volume rm app-proxy-logs 2>/dev/null || true
        print_success "Log cleanup complete"
    else
        print_info "Cleanup cancelled"
    fi
}

cmd_clean_cache() {
    print_warning "This will remove Redis cache data"
    read -p "Continue? (yes/no): " -r
    echo
    if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        print_header "Cleaning Redis cache"
        docker compose stop redis
        docker volume rm app-redis-data 2>/dev/null || true
        print_success "Cache data removed"
        print_info "Run './docker-dev.sh start' to recreate Redis with empty cache"
    else
        print_info "Cleanup cancelled"
    fi
}

cmd_clean_all() {
    print_error "╔════════════════════════════════════════════════════════════╗"
    print_error "║                    DESTRUCTIVE ACTION                      ║"
    print_error "╚════════════════════════════════════════════════════════════╝"
    print_warning "This will permanently remove:"
    echo "  - All containers"
    echo "  - All volumes (database, uploads, cache, logs)"
    echo "  - All persistent data"
    echo ""
    print_warning "You will lose:"
    echo "  - Database records"
    echo "  - Uploaded files and media"
    echo "  - Redis cache data"
    echo "  - Application logs"
    echo ""
    print_info "Consider backing up first: ./docker-dev.sh backup"
    echo ""
    read -p "Type 'DELETE EVERYTHING' to confirm: " -r
    echo
    if [[ $REPLY == "DELETE EVERYTHING" ]]; then
        print_header "Removing all containers and volumes"
        docker compose down -v
        print_success "Complete cleanup finished"
        print_info "All data has been permanently deleted"
    else
        print_info "Cleanup cancelled (confirmation did not match)"
    fi
}

cmd_status() {
    print_header "Detailed service status"
    docker compose ps
    echo ""

    # Check health status
    print_info "Health checks:"
    for service in db redis backend frontend proxy; do
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
    print_info "Application URLs (Unified Entry Point):"
    echo "  Application: http://localhost/"
    echo "  Frontend: http://localhost/"
    echo "  Backend API: http://localhost/api/"
    echo "  Admin Panel: http://localhost/admin/"
    echo "  Backend Health: http://localhost/api/v1/health/"
    echo "  Proxy Health: http://localhost/health"
    echo ""
    print_info "Direct Service Access (for debugging):"
    echo "  Frontend Direct: http://localhost:5173"
    echo "  Backend Direct: http://localhost:8000"
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

cmd_validate() {
    print_header "Running orchestration validation"

    local verbose_flag=""
    local quick_flag=""

    # Parse optional flags
    while [[ $# -gt 0 ]]; do
        case $1 in
            --verbose|-v)
                verbose_flag="--verbose"
                shift
                ;;
            --quick)
                quick_flag="--quick"
                shift
                ;;
            *)
                shift
                ;;
        esac
    done

    # Check if validation script exists
    if [ ! -f "./scripts/validate-orchestration.sh" ]; then
        print_error "Validation script not found at ./scripts/validate-orchestration.sh"
        exit 1
    fi

    # Run validation
    ./scripts/validate-orchestration.sh $verbose_flag $quick_flag
}

cmd_volumes() {
    print_header "Volume information and disk usage"
    echo ""

    print_info "Persistent volumes:"
    docker volume ls --filter "name=app-" --format "table {{.Name}}\t{{.Driver}}\t{{.Mountpoint}}"
    echo ""

    print_info "Volume sizes:"
    for volume in postgres-data redis-data backend-media backend-static frontend-node-modules proxy-logs; do
        if docker volume inspect "app-$volume" &>/dev/null; then
            size=$(docker run --rm -v "app-$volume:/data" alpine du -sh /data 2>/dev/null | cut -f1)
            echo "  app-$volume: $size"
        fi
    done
    echo ""

    print_info "Volume details:"
    echo "  📊 app-postgres-data     - Database records (PostgreSQL data)"
    echo "  📊 app-redis-data        - Cache and queue data (Redis persistence)"
    echo "  📁 app-backend-media     - User uploaded files and media"
    echo "  📁 app-backend-static    - Collected static files (CSS, JS, images)"
    echo "  📦 app-frontend-node-modules - Frontend dependencies (npm packages)"
    echo "  📝 app-proxy-logs        - Nginx access and error logs"
    echo ""

    print_info "Data persistence locations:"
    echo "  Database:        /var/lib/postgresql/data (in container)"
    echo "  Redis:           /data (in container)"
    echo "  Media files:     /app/media (in container)"
    echo "  Static files:    /app/staticfiles (in container)"
    echo "  Node modules:    /app/node_modules (in container)"
    echo "  Proxy logs:      /var/log/nginx (in container)"
}

cmd_backup() {
    local backup_dir="./backups"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="$backup_dir/full_backup_$timestamp.tar.gz"

    print_header "Creating full backup"

    # Create backup directory
    mkdir -p "$backup_dir"

    print_info "Backing up database..."
    docker compose exec -T db pg_dump -U postgres backend_db > "$backup_dir/db_backup_$timestamp.sql"

    print_info "Backing up media files..."
    docker run --rm -v app-backend-media:/data -v "$(pwd)/$backup_dir:/backup" alpine \
        tar czf "/backup/media_backup_$timestamp.tar.gz" -C /data .

    print_info "Backing up static files..."
    docker run --rm -v app-backend-static:/data -v "$(pwd)/$backup_dir:/backup" alpine \
        tar czf "/backup/static_backup_$timestamp.tar.gz" -C /data .

    print_info "Creating combined backup archive..."
    tar czf "$backup_file" -C "$backup_dir" \
        "db_backup_$timestamp.sql" \
        "media_backup_$timestamp.tar.gz" \
        "static_backup_$timestamp.tar.gz"

    # Clean up individual backup files
    rm "$backup_dir/db_backup_$timestamp.sql"
    rm "$backup_dir/media_backup_$timestamp.tar.gz"
    rm "$backup_dir/static_backup_$timestamp.tar.gz"

    print_success "Backup created: $backup_file"

    local backup_size=$(du -h "$backup_file" | cut -f1)
    print_info "Backup size: $backup_size"
}

cmd_backup_db() {
    local backup_dir="./backups"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="$backup_dir/db_backup_$timestamp.sql"

    print_header "Creating database backup"

    # Create backup directory
    mkdir -p "$backup_dir"

    print_info "Backing up database..."
    docker compose exec -T db pg_dump -U postgres backend_db > "$backup_file"

    print_success "Database backup created: $backup_file"

    local backup_size=$(du -h "$backup_file" | cut -f1)
    print_info "Backup size: $backup_size"
}

cmd_restore() {
    local backup_file=$1

    if [ -z "$backup_file" ]; then
        print_error "Please specify a backup file"
        echo "Usage: ./docker-dev.sh restore <backup_file>"
        echo ""
        print_info "Available backups:"
        ls -lh ./backups/ 2>/dev/null || echo "  No backups found"
        exit 1
    fi

    if [ ! -f "$backup_file" ]; then
        print_error "Backup file not found: $backup_file"
        exit 1
    fi

    print_warning "This will restore data from: $backup_file"
    print_warning "Current data will be overwritten!"
    read -p "Continue? (yes/no): " -r
    echo

    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        print_info "Restore cancelled"
        exit 0
    fi

    print_header "Restoring from backup"

    # Extract backup
    local temp_dir=$(mktemp -d)
    tar xzf "$backup_file" -C "$temp_dir"

    # Find SQL file
    local sql_file=$(find "$temp_dir" -name "*.sql" | head -1)
    if [ -n "$sql_file" ]; then
        print_info "Restoring database..."
        docker compose exec -T db psql -U postgres backend_db < "$sql_file"
    fi

    # Find media backup
    local media_file=$(find "$temp_dir" -name "media_backup_*.tar.gz" | head -1)
    if [ -n "$media_file" ]; then
        print_info "Restoring media files..."
        docker run --rm -v app-backend-media:/data -v "$temp_dir:/backup" alpine \
            sh -c "rm -rf /data/* && tar xzf /backup/$(basename $media_file) -C /data"
    fi

    # Find static backup
    local static_file=$(find "$temp_dir" -name "static_backup_*.tar.gz" | head -1)
    if [ -n "$static_file" ]; then
        print_info "Restoring static files..."
        docker run --rm -v app-backend-static:/data -v "$temp_dir:/backup" alpine \
            sh -c "rm -rf /data/* && tar xzf /backup/$(basename $static_file) -C /data"
    fi

    # Clean up
    rm -rf "$temp_dir"

    print_success "Restore complete"
    print_info "Restart services to apply changes: ./docker-dev.sh restart"
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

cmd_preflight() {
    print_header "Running pre-flight validation"

    if [ ! -f "./scripts/preflight-check.sh" ]; then
        print_error "Pre-flight check script not found at ./scripts/preflight-check.sh"
        exit 1
    fi

    # Pass through arguments
    ./scripts/preflight-check.sh "$@"
}

cmd_help() {
    cat << EOF
${CYAN}Docker Development Helper Script${NC}

${YELLOW}Usage:${NC} ./docker-dev.sh <command> [options]

${YELLOW}Service Management:${NC}
  ${GREEN}start${NC}                         Start all services (with pre-flight check)
  ${GREEN}stop${NC}                          Stop all services
  ${GREEN}restart${NC}                       Restart all services
  ${GREEN}build${NC}                         Build/rebuild all containers
  ${GREEN}rebuild${NC}                       Rebuild and restart all services
  ${GREEN}ps${NC}                            Show service status
  ${GREEN}status${NC}                        Show detailed service status
  ${GREEN}preflight${NC} [--fix] [--verbose]  Run pre-flight validation checks
  ${GREEN}validate${NC} [--quick] [--verbose] Validate orchestration is working correctly
  ${GREEN}logs${NC} [service]                View logs (optionally for specific service)

${YELLOW}Data Management:${NC}
  ${GREEN}volumes${NC}                       Show volume information and disk usage
  ${GREEN}backup${NC}                        Backup all persistent data
  ${GREEN}backup-db${NC}                     Backup database only
  ${GREEN}restore${NC} <file>                Restore from backup file
  ${GREEN}clean${NC}                         Remove containers (preserve data)
  ${GREEN}clean-containers${NC}              Remove only containers
  ${GREEN}clean-logs${NC}                    Remove only log files
  ${GREEN}clean-cache${NC}                   Remove only Redis cache
  ${GREEN}clean-all${NC}                     Remove EVERYTHING (DESTRUCTIVE)

${YELLOW}Service Access:${NC}
  ${GREEN}shell${NC} <service>               Open shell in service container
  ${GREEN}exec${NC} <service> <cmd>          Execute command in service container
  ${GREEN}backend-shell${NC}                 Open Django shell
  ${GREEN}backend-migrate${NC}               Run database migrations
  ${GREEN}backend-makemigrations${NC}        Create new migrations
  ${GREEN}frontend-shell${NC}                Open shell in frontend container
  ${GREEN}db-shell${NC}                      Open PostgreSQL shell
  ${GREEN}redis-cli${NC}                     Open Redis CLI
  ${GREEN}help${NC}                          Show this help message

${YELLOW}Examples:${NC}
  ./docker-dev.sh preflight               # Check setup before starting
  ./docker-dev.sh preflight --fix         # Check and auto-fix issues
  ./docker-dev.sh start                   # Start (runs preflight automatically)
  ./docker-dev.sh validate                # Validate running services
  ./docker-dev.sh validate --verbose
  ./docker-dev.sh logs backend
  ./docker-dev.sh volumes
  ./docker-dev.sh backup
  ./docker-dev.sh clean-cache
  ./docker-dev.sh restore ./backups/full_backup_20251025_120000.tar.gz
  ./docker-dev.sh backend-shell
  ./docker-dev.sh exec backend python manage.py createsuperuser

${YELLOW}Available services:${NC}
  - frontend  (React/Vite application)
  - backend   (Django REST API)
  - db        (PostgreSQL database)
  - redis     (Redis cache)
  - celery    (Background task worker - optional)

${YELLOW}Application URLs (Unified Entry Point):${NC}
  Application:   http://localhost/
  Frontend:      http://localhost/
  Backend API:   http://localhost/api/
  Admin Panel:   http://localhost/admin/

${YELLOW}Direct Service Access (for debugging):${NC}
  Frontend:      http://localhost:5173
  Backend:       http://localhost:8000

${YELLOW}Data Persistence:${NC}
  All application data persists between restarts in named volumes:
  - Database records (PostgreSQL)
  - Uploaded files and media
  - Static files
  - Redis cache data
  - Frontend dependencies
  - Nginx logs

  Use 'volumes' command to inspect disk usage
  Use 'backup' command to create backups before destructive operations
  Use 'clean-all' to reset environment (requires confirmation)

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
        preflight)
            cmd_preflight "$@"
            ;;
        clean)
            cmd_clean
            ;;
        clean-containers)
            cmd_clean_containers
            ;;
        clean-logs)
            cmd_clean_logs
            ;;
        clean-cache)
            cmd_clean_cache
            ;;
        clean-all)
            cmd_clean_all
            ;;
        status)
            cmd_status
            ;;
        validate)
            cmd_validate "$@"
            ;;
        volumes)
            cmd_volumes
            ;;
        backup)
            cmd_backup
            ;;
        backup-db)
            cmd_backup_db
            ;;
        restore)
            cmd_restore "$@"
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
