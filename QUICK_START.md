# Quick Start Guide - Docker Development Environment

## TL;DR

```bash
# First time setup
./scripts/preflight-check.sh --fix
./docker-dev.sh start

# Daily development
./docker-dev.sh start          # Start all services
./docker-dev.sh logs           # View logs
./docker-dev.sh stop           # Stop when done
```

## Prerequisites

- Docker and Docker Compose installed
- At least 5GB free disk space
- Ports available: 80, 5432, 6379, 5173, 8000

## First Time Setup

1. **Validate Environment**
   ```bash
   ./scripts/preflight-check.sh --fix
   ```
   This checks and auto-fixes:
   - Docker installation
   - File permissions
   - Port availability
   - Environment files

2. **Start Services**
   ```bash
   ./docker-dev.sh start
   ```
   This automatically:
   - Runs pre-flight validation
   - Starts all containers
   - Shows service status

3. **Verify Everything Works**
   ```bash
   # Check services are healthy
   docker compose ps

   # Visit application
   # Frontend: http://localhost/
   # Backend API: http://localhost/api/
   # Admin: http://localhost/admin/
   ```

## Daily Workflow

### Start Development

```bash
./docker-dev.sh start
```

### View Logs

```bash
# All services
./docker-dev.sh logs

# Specific service
./docker-dev.sh logs backend
./docker-dev.sh logs frontend
```

### Run Database Migrations

```bash
./docker-dev.sh backend-migrate
```

### Access Django Shell

```bash
./docker-dev.sh backend-shell
```

### Stop Services

```bash
./docker-dev.sh stop
```

## Troubleshooting

### Services Not Starting?

```bash
# Run validation
./scripts/preflight-check.sh --fix

# Check logs
./docker-dev.sh logs

# Rebuild and restart
./docker-dev.sh rebuild
```

### Permission Errors?

The entrypoint script automatically fixes log permissions on startup. If you see permission errors:

```bash
# Restart container (fixes permissions automatically)
docker compose restart backend
```

### Ports Already in Use?

```bash
# Check what's using ports
./scripts/preflight-check.sh --verbose

# Stop conflicting containers
docker compose down
```

### Need Clean Slate?

```bash
# Stop and remove containers (keeps data)
./docker-dev.sh clean

# Nuclear option: Remove EVERYTHING
./docker-dev.sh clean-all
```

## Common Commands

### Service Management

```bash
./docker-dev.sh start          # Start all services
./docker-dev.sh stop           # Stop all services
./docker-dev.sh restart        # Restart all services
./docker-dev.sh rebuild        # Rebuild and restart
./docker-dev.sh status         # Show detailed status
```

### Development Tools

```bash
./docker-dev.sh backend-shell      # Django shell
./docker-dev.sh backend-migrate    # Run migrations
./docker-dev.sh db-shell           # PostgreSQL shell
./docker-dev.sh redis-cli          # Redis CLI
./docker-dev.sh frontend-shell     # Frontend shell
```

### Data Management

```bash
./docker-dev.sh volumes        # Show volume usage
./docker-dev.sh backup         # Backup all data
./docker-dev.sh backup-db      # Backup database only
./docker-dev.sh clean-logs     # Remove log files
./docker-dev.sh clean-cache    # Remove Redis cache
```

### Validation

```bash
./docker-dev.sh preflight              # Validate setup
./docker-dev.sh preflight --fix        # Validate and auto-fix
./docker-dev.sh validate               # Validate running services
```

## Service URLs

### Unified Entry Point (Reverse Proxy)

- **Frontend:** http://localhost/
- **Backend API:** http://localhost/api/
- **Admin Panel:** http://localhost/admin/
- **Backend Health:** http://localhost/api/v1/health/

### Direct Service Access (for debugging)

- **Frontend Direct:** http://localhost:5173
- **Backend Direct:** http://localhost:8000
- **Database:** localhost:5432 (user: postgres, password: postgres, db: backend_db)
- **Redis:** localhost:6379

## Important Files

- **Main Compose File:** `docker-compose.yml`
- **Backend Dockerfile:** `backend/Dockerfile`
- **Frontend Dockerfile:** `frontend/Dockerfile`
- **Helper Script:** `docker-dev.sh`
- **Pre-Flight Check:** `scripts/preflight-check.sh`
- **Troubleshooting Guide:** `docs/DOCKER_TROUBLESHOOTING.md`

## Need Help?

1. **Check the troubleshooting guide:**
   ```bash
   cat docs/DOCKER_TROUBLESHOOTING.md
   ```

2. **Run validation:**
   ```bash
   ./scripts/preflight-check.sh --verbose
   ```

3. **Check logs:**
   ```bash
   ./docker-dev.sh logs
   ```

4. **View full help:**
   ```bash
   ./docker-dev.sh help
   ```

## Tips

- **Always run pre-flight check** before starting containers
- **Check service status** regularly: `./docker-dev.sh status`
- **Backup before destructive operations**: `./docker-dev.sh backup`
- **Use the helper script** - it validates and handles common issues automatically
- **View logs** when debugging: `./docker-dev.sh logs [service]`

## What's Different Now?

Recent fixes ensure:

✅ **Entrypoint script** - Automatically managed, no missing script errors
✅ **Log permissions** - Automatically fixed on startup, no permission errors
✅ **Healthchecks** - Use IPv4 explicitly, no IPv6 connection failures
✅ **Pre-flight validation** - Catches issues before containers start
✅ **Auto-fix** - Common issues fixed automatically

Just run `./docker-dev.sh start` and everything works!
