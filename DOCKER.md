# Docker Multi-Container Development Environment

Complete guide for running the entire application stack (frontend, backend, database, redis) using Docker Compose.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Prerequisites](#prerequisites)
- [Architecture](#architecture)
- [Common Commands](#common-commands)
- [Service-Specific Operations](#service-specific-operations)
- [Development Workflow](#development-workflow)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Advanced Usage](#advanced-usage)

## Overview

This Docker Compose configuration orchestrates a complete development environment with:

- **Frontend**: React + Vite development server with hot module replacement (HMR)
- **Backend**: Django REST Framework API with auto-reload
- **Database**: PostgreSQL 15 with persistent data storage
- **Cache**: Redis 7 for caching and session storage
- **Celery**: Optional background task worker (disabled by default)

All services are networked together and can communicate using service names as hostnames.

## Quick Start

1. **Prerequisites**: Install Docker Desktop (macOS/Windows) or Docker Engine + Docker Compose (Linux)

2. **Start the entire stack**:
   ```bash
   ./docker-dev.sh start
   ```

3. **Access the applications**:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - Backend Admin: http://localhost:8000/admin

4. **View logs**:
   ```bash
   ./docker-dev.sh logs
   ```

5. **Stop all services**:
   ```bash
   ./docker-dev.sh stop
   ```

That's it! The helper script handles all the complexity for you.

## Prerequisites

### Required Software

- **Docker Desktop** (macOS/Windows): Version 24.0+ with Docker Compose V2
  - Download: https://www.docker.com/products/docker-desktop
  - Includes Docker Engine and Docker Compose

- **Docker Engine + Docker Compose** (Linux): Docker Engine 24.0+, Docker Compose V2
  ```bash
  # Ubuntu/Debian
  sudo apt-get update
  sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin

  # Verify installation
  docker --version
  docker compose version
  ```

### System Requirements

- **CPU**: 4 cores recommended (minimum 2 cores)
- **RAM**: 8GB recommended (minimum 4GB)
- **Disk**: 20GB free space for images and volumes
- **OS**: macOS 11+, Windows 10/11 with WSL2, Linux (kernel 5.0+)

### Port Requirements

Ensure these ports are available on your host:
- 5173 (Frontend - Vite dev server)
- 8000 (Backend - Django dev server)
- 5432 (PostgreSQL database)
- 6379 (Redis cache)

## Architecture

### Services

```
┌─────────────────────────────────────────────────────────────┐
│                        Host Machine                         │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Frontend   │  │   Backend    │  │   Database   │     │
│  │  React/Vite  │  │    Django    │  │  PostgreSQL  │     │
│  │  Port 5173   │◄─┤  Port 8000   │◄─┤  Port 5432   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│         │                 │                                 │
│         │                 │          ┌──────────────┐     │
│         │                 └──────────┤    Redis     │     │
│         │                            │  Port 6379   │     │
│         │                            └──────────────┘     │
│         │                                                  │
│         │          ┌──────────────┐                       │
│         └──────────┤    Celery    │ (Optional)            │
│                    │   Worker     │                       │
│                    └──────────────┘                       │
│                                                             │
│                    app-network (bridge)                    │
└─────────────────────────────────────────────────────────────┘
```

### Network

All services are connected via a custom bridge network named `app-network`. This enables:
- **DNS resolution**: Services can reach each other using service names (e.g., `http://backend:8000`)
- **Isolation**: Network is isolated from other Docker networks
- **Communication**: All services can communicate without exposing ports to host (except where explicitly mapped)

### Volumes

Persistent data storage:
- `app-postgres-data`: PostgreSQL database files
- `app-redis-data`: Redis persistence files
- `app-backend-media`: Uploaded media files
- `app-backend-static`: Collected static files
- `app-frontend-node-modules`: npm packages

Bind mounts (for live code editing):
- `./backend` → `/app` (backend source code)
- `./frontend/src` → `/app/src` (frontend source code)
- Configuration files for both services

## Common Commands

### Using the Helper Script (Recommended)

The `docker-dev.sh` script provides convenient commands for common operations:

```bash
# Start all services
./docker-dev.sh start

# Stop all services
./docker-dev.sh stop

# Restart all services
./docker-dev.sh restart

# Rebuild containers and restart
./docker-dev.sh rebuild

# View logs (all services)
./docker-dev.sh logs

# View logs for specific service
./docker-dev.sh logs backend
./docker-dev.sh logs frontend

# Check service status
./docker-dev.sh status

# Clean up (removes volumes - DESTRUCTIVE)
./docker-dev.sh clean

# Show help
./docker-dev.sh help
```

### Using Docker Compose Directly

You can also use Docker Compose commands directly:

```bash
# Start all services
docker compose up -d

# Start and view logs
docker compose up

# Stop all services
docker compose down

# Rebuild specific service
docker compose build backend

# Restart specific service
docker compose restart frontend

# View service status
docker compose ps

# View logs
docker compose logs -f
docker compose logs -f backend

# Stop and remove volumes (DESTRUCTIVE)
docker compose down -v
```

## Service-Specific Operations

### Frontend

```bash
# Access frontend shell
./docker-dev.sh frontend-shell
# Or: docker compose exec frontend /bin/sh

# Install npm package
docker compose exec frontend npm install <package-name>

# Run frontend tests
docker compose exec frontend npm test

# Build production assets
docker compose exec frontend npm run build

# View frontend logs
./docker-dev.sh logs frontend
```

### Backend

```bash
# Access Django shell
./docker-dev.sh backend-shell
# Or: docker compose exec backend python manage.py shell

# Run migrations
./docker-dev.sh backend-migrate
# Or: docker compose exec backend python manage.py migrate

# Create migrations
./docker-dev.sh backend-makemigrations
# Or: docker compose exec backend python manage.py makemigrations

# Create superuser
docker compose exec backend python manage.py createsuperuser

# Run tests
docker compose exec backend pytest

# Run specific test file
docker compose exec backend pytest apps/core/tests/test_models.py

# Access backend shell (bash)
docker compose exec backend /bin/bash

# View backend logs
./docker-dev.sh logs backend
```

### Database

```bash
# Access PostgreSQL shell
./docker-dev.sh db-shell
# Or: docker compose exec db psql -U postgres -d backend_db

# Backup database
docker compose exec db pg_dump -U postgres backend_db > backup.sql

# Restore database
cat backup.sql | docker compose exec -T db psql -U postgres backend_db

# View database logs
./docker-dev.sh logs db
```

### Redis

```bash
# Access Redis CLI
./docker-dev.sh redis-cli
# Or: docker compose exec redis redis-cli

# Monitor Redis commands
docker compose exec redis redis-cli monitor

# Get Redis info
docker compose exec redis redis-cli info

# Clear all Redis data
docker compose exec redis redis-cli flushall

# View Redis logs
./docker-dev.sh logs redis
```

### Celery (Optional)

The Celery worker is disabled by default. To enable it:

```bash
# Start with Celery worker
docker compose --profile with-celery up -d

# View Celery logs
docker compose logs -f celery

# Access Celery container shell
docker compose exec celery /bin/bash

# Stop Celery
docker compose --profile with-celery down
```

## Development Workflow

### 1. Initial Setup

**First-time setup for new developers**:

```bash
# 1. Clone the repository (if not already done)
git clone <repository-url>
cd architecture

# 2. Set up environment configuration files (optional - defaults work for local dev)
# Backend: Copy and customize if needed
cp backend/.env.example backend/.env.local

# Frontend: Copy and customize if needed
cp frontend/.env.example frontend/.env.local

# Note: .env.docker files are pre-configured for Docker and should work out of the box

# 3. Start the entire stack (this may take 3-5 minutes on first run)
./docker-dev.sh start

# 4. Wait for all services to be healthy (30-60 seconds)
# Watch for green "healthy" status for all services
./docker-dev.sh status

# 5. Create Django superuser (for accessing admin interface)
docker compose exec backend python manage.py createsuperuser
# Follow prompts to set username, email, and password

# 6. Verify everything is working
# - Open frontend: http://localhost:5173 (should see application)
# - Open backend API: http://localhost:8000/api/v1/health/ (should see {"status":"healthy"})
# - Open admin: http://localhost:8000/admin (login with superuser credentials)

# 7. You're ready to develop!
```

**What happens during first start:**
- Docker downloads base images (Node, Python, PostgreSQL, Redis) - ~2GB
- Backend and frontend images are built with all dependencies
- Database is initialized with schema migrations
- All services start and connect to each other
- Health checks verify everything is working

### 2. Daily Development

```bash
# Start services in the morning
./docker-dev.sh start

# Make code changes
# - Frontend: Edit files in frontend/src/ - changes auto-reload via HMR
# - Backend: Edit files in backend/ - Django auto-reloads on save

# View logs while developing
./docker-dev.sh logs backend
./docker-dev.sh logs frontend

# Run tests
docker compose exec backend pytest
docker compose exec frontend npm test

# Stop services at end of day
./docker-dev.sh stop
```

### 3. Database Migrations

```bash
# After modifying Django models
./docker-dev.sh backend-makemigrations

# Apply migrations
./docker-dev.sh backend-migrate

# Or combine both
docker compose exec backend python manage.py makemigrations
docker compose exec backend python manage.py migrate
```

### 4. Installing Dependencies

**Frontend (npm packages)**:
```bash
# Install new package
docker compose exec frontend npm install <package-name>

# Package.json is bind-mounted, so changes are saved to host
# node_modules is in a volume, so no rebuild needed

# If you update package.json manually, run:
docker compose exec frontend npm install

# Example: Installing axios
docker compose exec frontend npm install axios
```

**Backend (Python packages)**:
```bash
# 1. Add package to appropriate requirements file:
#    - requirements/base.txt (for packages needed in all environments)
#    - requirements/dev.txt (for development-only packages like pytest)
#    - requirements/prod.txt (for production-only packages like gunicorn)

# 2. Rebuild backend container to install the new package
docker compose build backend

# 3. Restart backend with new image
docker compose up -d backend

# Example: Installing requests library
# Edit requirements/base.txt and add: requests==2.31.0
# Then run:
docker compose build backend
docker compose up -d backend
```

### 5. Debugging

**Frontend debugging**:
- Browser DevTools work normally with HMR
- Source maps are available in development
- Console logs appear in browser console
- Container logs: `./docker-dev.sh logs frontend`

**Backend debugging**:
- Use `import pdb; pdb.set_trace()` or `breakpoint()` in code
- Attach to container with `docker compose exec backend python manage.py shell`
- Django Debug Toolbar available in development (http://localhost:8000/__debug__/)
- Container logs: `./docker-dev.sh logs backend`

### 6. Running Tests in Containers

**Backend tests (pytest)**:
```bash
# Run all tests
docker compose exec backend pytest

# Run specific test file
docker compose exec backend pytest apps/core/tests/test_models.py

# Run tests with coverage report
docker compose exec backend pytest --cov=apps --cov-report=html

# Run tests matching a keyword
docker compose exec backend pytest -k "test_user"

# Run tests with verbose output
docker compose exec backend pytest -v

# Run tests and stop on first failure
docker compose exec backend pytest -x
```

**Frontend tests (Vitest)**:
```bash
# Run all tests
docker compose exec frontend npm test

# Run tests in watch mode (auto-rerun on changes)
docker compose exec frontend npm test -- --watch

# Run specific test file
docker compose exec frontend npm test -- src/components/Button.test.tsx

# Run tests with coverage
docker compose exec frontend npm run test:coverage

# Run tests in UI mode (interactive)
docker compose exec frontend npm test -- --ui
```

**Running tests during CI/CD**:
The same test commands work in CI/CD pipelines. Tests run in isolated containers with fresh databases, ensuring consistent results.

**Test database management**:
```bash
# Backend tests automatically use a separate test database
# No special configuration needed - Django handles this

# To reset test data between test runs, tests use transactions
# that are rolled back after each test

# View test database logs if needed
docker compose logs backend | grep test
```

### 7. Resetting the Environment

**Soft reset** (keeps data):
```bash
./docker-dev.sh restart
```

**Hard reset** (removes containers, keeps volumes):
```bash
docker compose down
docker compose up -d
```

**Complete reset** (removes everything including database):
```bash
./docker-dev.sh clean
./docker-dev.sh start
# Re-run migrations and create superuser
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
```

## Configuration

### Environment Variables

The application uses environment files for configuration:

**Backend**: `backend/.env.docker`
- Database connection (DB_HOST, DB_NAME, DB_USER, DB_PASSWORD)
- Redis connection (REDIS_URL, CELERY_BROKER_URL)
- Django settings (SECRET_KEY, DEBUG, ALLOWED_HOSTS)
- CORS configuration (CORS_ALLOWED_ORIGINS)

**Frontend**: `frontend/.env.docker`
- API URL (VITE_API_URL)
- App configuration (VITE_APP_NAME, VITE_APP_VERSION)
- Feature flags (VITE_ENABLE_ANALYTICS, etc.)

### Customizing Configuration

Create `.env.local` files for personal overrides (not committed to git):

**Backend** (`backend/.env.local`):
```bash
# Override specific variables
DB_PASSWORD=my_secure_password
LOG_LEVEL=DEBUG
```

**Frontend** (`frontend/.env.local`):
```bash
# Override specific variables
VITE_API_URL=http://localhost:8000
VITE_DEBUG=true
```

### Port Customization

Set environment variables before starting:

```bash
# Use custom ports
export FRONTEND_PORT=3000
export BACKEND_PORT=8080
export DB_PORT=5433

./docker-dev.sh start
```

Or edit `docker-compose.yml` directly.

## Troubleshooting

### Services Won't Start

**Check Docker is running**:
```bash
docker info
```

**Check port conflicts**:
```bash
# Check if ports are in use
lsof -i :5173  # Frontend
lsof -i :8000  # Backend
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis

# Kill conflicting processes or change ports
```

**Check logs for errors**:
```bash
./docker-dev.sh logs
./docker-dev.sh logs backend
```

### Database Connection Errors

**Symptoms**: Backend logs show "Connection refused" or "could not connect to server"

**Solutions**:
```bash
# Check database health
docker compose ps db

# View database logs
./docker-dev.sh logs db

# Restart database
docker compose restart db

# Wait for database to be healthy
./docker-dev.sh status

# If database is corrupted, reset it
docker compose down -v db
docker compose up -d db
docker compose exec backend python manage.py migrate
```

### Frontend Can't Reach Backend

**Symptoms**: Frontend shows "Network Error" or API requests fail

**Solutions**:
```bash
# Verify backend is running
curl http://localhost:8000/api/v1/health/

# Check backend logs
./docker-dev.sh logs backend

# Verify CORS configuration
# backend/.env.docker should include:
# CORS_ALLOWED_ORIGINS=http://localhost:5173,...

# Restart backend
docker compose restart backend
```

### Changes Not Reflecting

**Frontend changes not appearing**:
```bash
# Check volume mounts
docker compose exec frontend ls -la /app/src

# Verify file is bind-mounted
docker compose config | grep -A 10 frontend

# Hard refresh browser (Cmd+Shift+R or Ctrl+Shift+R)

# Restart frontend if needed
docker compose restart frontend
```

**Backend changes not appearing**:
```bash
# Check if Django auto-reload is working
./docker-dev.sh logs backend

# Verify source is mounted
docker compose exec backend ls -la /app

# Restart backend
docker compose restart backend
```

### Slow Performance

**macOS/Windows (Docker Desktop)**:
- File I/O is slower on macOS/Windows due to virtualization
- Use named volumes for node_modules (already configured)
- Consider using Docker Desktop with VirtioFS (enabled by default in recent versions)
- Allocate more resources in Docker Desktop settings (4GB+ RAM, 2+ CPUs)

**Linux**:
- Performance should be native speed
- Check disk space: `df -h`
- Check resource usage: `docker stats`

### Out of Disk Space

```bash
# Check Docker disk usage
docker system df

# Clean up unused resources
docker system prune -a

# Remove specific volumes (DESTRUCTIVE)
docker volume rm app-postgres-data
docker volume rm app-redis-data

# Complete cleanup
./docker-dev.sh clean
docker system prune -a --volumes
```

### Permission Errors

**Linux users** may encounter permission issues:

```bash
# Fix backend logs directory
sudo chown -R $USER:$USER ./backend/logs

# Fix frontend node_modules
docker compose exec -u root frontend chown -R nodejs:nodejs /app/node_modules

# If problems persist, run containers as your user
# Edit docker-compose.yml and add:
# user: "${UID}:${GID}"
```

## Advanced Usage

### Running Specific Services

Start only the services you need:

```bash
# Frontend and its dependencies (nothing - frontend can run standalone)
docker compose up frontend

# Backend and its dependencies (db, redis)
docker compose up backend

# Just the database
docker compose up db
```

### Multiple Environments

Run development and production side-by-side:

```bash
# Development (current setup)
docker compose up -d

# Production (separate compose file)
docker compose -f docker-compose.production.yml up -d

# Use different ports to avoid conflicts
```

### Custom Docker Compose Files

Create `docker-compose.override.yml` for personal customizations:

```yaml
# docker-compose.override.yml
services:
  backend:
    ports:
      - "8080:8000"  # Custom port
    environment:
      LOG_LEVEL: DEBUG  # Custom setting
```

This file is automatically loaded and overrides settings in `docker-compose.yml`.

### Scaling Services

Scale specific services (useful for testing):

```bash
# Run multiple backend workers
docker compose up -d --scale backend=3

# Note: You'll need to configure a load balancer for this to be useful
```

### Accessing Services from Other Containers

Services can communicate using service names as hostnames:

```bash
# Backend can access database at:
# postgresql://postgres:postgres@db:5432/backend_db

# Frontend (from browser) accesses backend at:
# http://localhost:8000

# Frontend (from container) would access backend at:
# http://backend:8000
```

### Monitoring Resource Usage

```bash
# Real-time resource stats
docker stats

# Specific service
docker stats app-backend

# Get health status
docker inspect app-backend | grep -A 10 Health
```

### Debugging Container Issues

```bash
# Inspect container configuration
docker inspect app-backend

# View container logs
docker logs app-backend

# Enter container as root (for debugging)
docker compose exec -u root backend /bin/bash

# Check container processes
docker compose exec backend ps aux

# View environment variables
docker compose exec backend env
```

### Backup and Restore

**Database backup**:
```bash
# Backup
docker compose exec db pg_dump -U postgres backend_db > backup_$(date +%Y%m%d).sql

# Restore
cat backup_20241024.sql | docker compose exec -T db psql -U postgres backend_db
```

**Volume backup**:
```bash
# Backup volume to tar
docker run --rm -v app-postgres-data:/data -v $(pwd):/backup \
  alpine tar czf /backup/postgres-backup.tar.gz /data

# Restore volume from tar
docker run --rm -v app-postgres-data:/data -v $(pwd):/backup \
  alpine tar xzf /backup/postgres-backup.tar.gz -C /
```

**Full environment backup**:
```bash
# Stop services
./docker-dev.sh stop

# Backup all volumes
docker run --rm -v app-postgres-data:/postgres \
  -v app-redis-data:/redis -v $(pwd):/backup \
  alpine sh -c "tar czf /backup/full-backup.tar.gz /postgres /redis"

# Restart services
./docker-dev.sh start
```

## Environment Variables Reference

### Backend Environment Variables

**Location**: `backend/.env.docker` (pre-configured for Docker) or `backend/.env.local` (your overrides)

**Required Variables**:
- `SECRET_KEY`: Django secret key (auto-generated for dev, must be set for production)
- `DB_NAME`: Database name (default: `backend_db`)
- `DB_USER`: Database username (default: `postgres`)
- `DB_PASSWORD`: Database password (default: `postgres`)

**Optional Variables**:
- `DB_HOST`: Database host (default: `db` - the service name in Docker)
- `DB_PORT`: Database port (default: `5432`)
- `REDIS_URL`: Redis connection URL (default: `redis://redis:6379/1`)
- `CELERY_BROKER_URL`: Celery broker URL (default: `redis://redis:6379/0`)
- `CORS_ALLOWED_ORIGINS`: Allowed CORS origins (default includes localhost:5173)
- `DEBUG`: Enable debug mode (default: `True` in development)
- `LOG_LEVEL`: Logging level (default: `INFO`)

**How to set variables**:
```bash
# Option 1: Edit .env.docker file directly (not recommended - committed to git)
nano backend/.env.docker

# Option 2: Create .env.local file with overrides (recommended - ignored by git)
cat > backend/.env.local << EOF
DB_PASSWORD=my_secure_password
LOG_LEVEL=DEBUG
EOF

# Option 3: Set in docker-compose.yml environment section (for project-wide changes)
# Option 4: Pass as environment variables when starting
export DB_PASSWORD=my_password
./docker-dev.sh start
```

### Frontend Environment Variables

**Location**: `frontend/.env.docker` (pre-configured for Docker) or `frontend/.env.local` (your overrides)

**Important**: All frontend environment variables must be prefixed with `VITE_` to be accessible in the application.

**Required Variables**:
- `VITE_API_URL`: Backend API URL (default: `http://localhost:8000`)

**Optional Variables**:
- `VITE_API_TIMEOUT`: API request timeout in ms (default: `30000`)
- `VITE_API_ENABLE_LOGGING`: Enable API logging (default: `true`)
- `VITE_APP_NAME`: Application name (default: `Frontend Application`)
- `VITE_APP_VERSION`: Application version (default: `1.0.0`)
- `VITE_DEBUG`: Enable debug mode (default: `true`)
- `VITE_ENABLE_ANALYTICS`: Enable analytics (default: `false`)
- `VITE_ENABLE_ERROR_REPORTING`: Enable error reporting (default: `false`)

**How to set variables**:
```bash
# Option 1: Create .env.local file (recommended)
cat > frontend/.env.local << EOF
VITE_API_URL=http://localhost:8000
VITE_DEBUG=true
EOF

# Option 2: Set in docker-compose.yml environment section
# Note: Frontend variables are embedded at build time, not runtime
# So you need to rebuild after changing them:
docker compose build frontend
docker compose up -d frontend
```

**Security Note**: Frontend environment variables are embedded in the JavaScript bundle and visible to users in the browser. Never store sensitive secrets (API keys, passwords) in frontend environment variables.

## Service-Specific Documentation

For detailed information about individual services:

- **Frontend**: See `frontend/DOCKER.md` (if exists)
- **Backend**: See `backend/DOCKER.md` (if exists)
- **Production deployment**: See production deployment documentation
- **Docker context**: See `context/devops/docker.md` for best practices

## Getting Help

### Quick Troubleshooting Checklist

1. **Check if services are running**: `./docker-dev.sh status`
2. **Check logs for errors**: `./docker-dev.sh logs`
3. **Restart services**: `./docker-dev.sh restart`
4. **Rebuild if code/dependencies changed**: `./docker-dev.sh rebuild`
5. **Reset everything**: `./docker-dev.sh clean && ./docker-dev.sh start`

### Common Error Messages

**"Error: Cannot connect to Docker daemon"**
- Docker is not running. Start Docker Desktop or Docker service.
- On Linux: `sudo systemctl start docker`

**"port is already allocated"**
- Another service is using the required ports (5173, 8000, 5432, 6379)
- Find and stop the conflicting service: `lsof -i :PORT_NUMBER`
- Or change ports in docker-compose.yml

**"database does not exist"**
- Database was not initialized properly
- Solution: `docker compose down -v && ./docker-dev.sh start`

**"relation does not exist"**
- Migrations not applied
- Solution: `docker compose exec backend python manage.py migrate`

**"ModuleNotFoundError" or "npm ERR! Cannot find module"**
- Dependencies not installed or container needs rebuild
- Backend: `docker compose build backend && docker compose up -d backend`
- Frontend: `docker compose exec frontend npm install`

### Resources

- Check logs: `./docker-dev.sh logs`
- Check status: `./docker-dev.sh status`
- View help: `./docker-dev.sh help`
- Docker Compose reference: https://docs.docker.com/compose/
- Docker documentation: https://docs.docker.com/
- Project documentation: `docs/`
- DevOps best practices: `context/devops/docker.md`

## Summary

This Docker Compose setup provides a complete, production-like development environment with:

- ✅ All services running with a single command
- ✅ Hot module replacement for instant feedback
- ✅ Persistent data across restarts
- ✅ Service networking and communication
- ✅ Health checks and auto-restart
- ✅ Resource limits and logging
- ✅ Helper scripts for common tasks

Happy developing! 🚀
