# Docker Development Setup

This guide covers running the backend application in Docker containers for local development.

> **Production Deployment**: For production container setup, see [DOCKER_PRODUCTION.md](./DOCKER_PRODUCTION.md)

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Common Commands](#common-commands)
- [Development Workflow](#development-workflow)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Advanced Usage](#advanced-usage)
- [Production Deployment](#production-deployment)

## Prerequisites

### Required Software

- **Docker Engine 23.0+**: [Install Docker](https://docs.docker.com/get-docker/)
- **Docker Compose V2**: Usually included with Docker Desktop
- **Docker BuildKit**: Enabled by default in Docker Engine 23.0+

### Verify Installation

```bash
# Check Docker version
docker --version
# Expected: Docker version 23.0 or higher

# Check Docker Compose version
docker compose version
# Expected: Docker Compose version v2.x.x

# Verify Docker is running
docker ps
# Should show running containers (or empty list if none running)
```

## Quick Start

### 1. Start All Services

```bash
# Navigate to backend directory
cd backend/

# Start all services (PostgreSQL, Redis, Backend)
docker compose up

# Or run in background (detached mode)
docker compose up -d

# View logs
docker compose logs -f backend
```

The backend API will be available at: http://localhost:8000/

### 2. Verify Services

```bash
# Check all services are running
docker compose ps

# Check backend health
curl http://localhost:8000/api/v1/health/

# Check backend detailed status
curl http://localhost:8000/api/v1/health/status/
```

### 3. Stop Services

```bash
# Stop all services (preserves data)
docker compose down

# Stop and remove volumes (deletes database data)
docker compose down -v
```

## Architecture

### Services

The Docker Compose setup includes three services:

#### 1. PostgreSQL Database (db)
- **Image**: postgres:15-alpine
- **Port**: 5432
- **Data**: Persistent volume (backend-postgres-data)
- **Health Check**: pg_isready command every 10s

#### 2. Redis Cache (redis)
- **Image**: redis:7-alpine
- **Port**: 6379
- **Data**: Persistent volume (backend-redis-data)
- **Health Check**: redis-cli ping every 10s

#### 3. Backend Application (backend)
- **Image**: Built from Dockerfile (development stage)
- **Port**: 8000
- **Code**: Live-mounted from host (hot reload enabled)
- **Health Check**: HTTP request to /api/v1/health/

#### 4. Celery Worker (celery) - Optional
- **Image**: Same as backend
- **Purpose**: Background task processing
- **Start**: `docker compose --profile with-celery up`

### Network

All services communicate over a bridge network called `backend-network`. Services can reach each other using their service names:
- Database: `db:5432`
- Redis: `redis:6379`
- Backend: `backend:8000`

### Volumes

Persistent data is stored in named volumes:

| Volume | Purpose | Persists |
|--------|---------|----------|
| `backend-postgres-data` | Database data | Yes |
| `backend-redis-data` | Redis cache data | Yes |
| `backend-media-data` | User-uploaded media files | Yes |
| `backend-static-data` | Collected static files | Yes |

## Common Commands

### Service Management

```bash
# Start all services
docker compose up

# Start specific service
docker compose up backend

# Start in background
docker compose up -d

# Stop all services
docker compose down

# Stop and remove volumes
docker compose down -v

# Restart a service
docker compose restart backend

# View service status
docker compose ps
```

### Logs

```bash
# View logs from all services
docker compose logs

# Follow logs in real-time
docker compose logs -f

# View logs from specific service
docker compose logs backend

# View last 100 lines
docker compose logs --tail=100 backend

# View logs with timestamps
docker compose logs -t backend
```

### Building and Rebuilding

```bash
# Build images
docker compose build

# Build with no cache (clean build)
docker compose build --no-cache

# Rebuild and restart
docker compose up --build

# Pull latest base images
docker compose pull
```

### Executing Commands in Containers

```bash
# Open shell in backend container
docker compose exec backend bash

# Run Django management commands
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
docker compose exec backend python manage.py shell

# Run as specific user
docker compose exec -u django backend bash

# Check database connectivity
docker compose exec backend python manage.py check_database
```

## Development Workflow

### Starting Development

1. **Initial Setup** (first time only):
   ```bash
   # Start containers
   docker compose up -d

   # Wait for services to be healthy
   docker compose ps

   # Verify backend is running
   curl http://localhost:8000/api/v1/health/
   ```

2. **Create Superuser** (optional):
   ```bash
   docker compose exec backend python manage.py createsuperuser
   ```

3. **Access Services**:
   - Backend API: http://localhost:8000/
   - API Documentation: http://localhost:8000/api/v1/docs/
   - Django Admin: http://localhost:8000/admin/

### Making Code Changes

The backend service uses volume mounts for live code reloading:

1. Edit Python files on your host machine
2. Django development server automatically detects changes
3. Server reloads with your new code
4. No need to rebuild containers for code changes

**Important**: If you change dependencies (requirements/*.txt), you must rebuild:
```bash
docker compose up --build backend
```

### Running Database Migrations

```bash
# Create new migrations
docker compose exec backend python manage.py makemigrations

# Apply migrations
docker compose exec backend python manage.py migrate

# Show migration status
docker compose exec backend python manage.py showmigrations

# Rollback migration
docker compose exec backend python manage.py migrate app_name migration_name
```

### Running Tests

```bash
# Run all tests
docker compose exec backend pytest

# Run with coverage
docker compose exec backend pytest --cov=apps --cov-report=html

# Run specific test file
docker compose exec backend pytest tests/unit/test_models.py

# Run in parallel
docker compose exec backend pytest -n auto
```

### Database Operations

```bash
# Connect to PostgreSQL
docker compose exec db psql -U postgres -d backend_db

# Create database backup
docker compose exec db pg_dump -U postgres backend_db > backup.sql

# Restore database
docker compose exec -T db psql -U postgres backend_db < backup.sql

# View database size
docker compose exec db psql -U postgres -d backend_db -c "\l+"

# View table sizes
docker compose exec db psql -U postgres -d backend_db -c "\dt+"
```

### Redis Operations

```bash
# Connect to Redis CLI
docker compose exec redis redis-cli

# View cache keys
docker compose exec redis redis-cli KEYS '*'

# Clear all cache
docker compose exec redis redis-cli FLUSHALL

# Monitor Redis commands in real-time
docker compose exec redis redis-cli MONITOR
```

## Configuration

### Environment Variables

Configuration is managed through `.env.docker` file. Key variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_NAME` | backend_db | Database name |
| `DB_USER` | postgres | Database user |
| `DB_PASSWORD` | postgres | Database password |
| `SECRET_KEY` | (generated) | Django secret key |
| `DEBUG` | True | Debug mode |
| `ALLOWED_HOSTS` | localhost,127.0.0.1 | Allowed hosts |

### Customizing Ports

Edit `docker-compose.yml` to change port mappings:

```yaml
services:
  backend:
    ports:
      - "8001:8000"  # Host port 8001 -> Container port 8000
```

Or use environment variables in `.env.docker`:
```bash
DEV_PORT=8001
```

### Resource Limits

Resource limits are defined in `docker-compose.yml`:

```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 1G
    reservations:
      cpus: '0.5'
      memory: 512M
```

Adjust based on your machine's capabilities.

## Troubleshooting

### Common Issues

#### 1. Port Already in Use

**Error**: `Bind for 0.0.0.0:8000 failed: port is already allocated`

**Solution**:
```bash
# Find process using the port
sudo lsof -i :8000

# Kill the process
sudo kill -9 <PID>

# Or change port in docker-compose.yml
```

#### 2. Database Connection Refused

**Error**: `FATAL: password authentication failed`

**Solution**:
```bash
# Check database is running
docker compose ps db

# Check database logs
docker compose logs db

# Restart database
docker compose restart db

# Verify environment variables
docker compose exec backend env | grep DB_
```

#### 3. Container Won't Start

**Error**: Container exits immediately

**Solution**:
```bash
# Check logs for error messages
docker compose logs backend

# Try running interactively
docker compose run --rm backend bash

# Rebuild image
docker compose build --no-cache backend
```

#### 4. Permission Denied Errors

**Error**: `Permission denied` when accessing files

**Solution**:
```bash
# Fix ownership of logs directory
sudo chown -R $USER:$USER logs/

# Or run as root (not recommended for production)
docker compose exec -u root backend bash
```

#### 5. Out of Disk Space

**Error**: `no space left on device`

**Solution**:
```bash
# Remove unused containers
docker container prune

# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Remove everything (be careful!)
docker system prune -a --volumes
```

### Health Check Failures

If health checks fail:

```bash
# Check backend health manually
docker compose exec backend curl http://localhost:8000/api/v1/health/

# Check database health
docker compose exec db pg_isready -U postgres -d backend_db

# Check Redis health
docker compose exec redis redis-cli ping

# View health status
docker compose ps
```

### Debugging Tips

1. **View container logs**:
   ```bash
   docker compose logs -f backend
   ```

2. **Check resource usage**:
   ```bash
   docker stats
   ```

3. **Inspect container**:
   ```bash
   docker compose exec backend bash
   ```

4. **Validate configuration**:
   ```bash
   docker compose config
   ```

5. **Test database connectivity**:
   ```bash
   docker compose exec backend python manage.py check_database
   ```

## Advanced Usage

### Using Celery for Background Tasks

Start services with Celery worker:

```bash
# Start with Celery profile
docker compose --profile with-celery up -d

# View Celery logs
docker compose logs -f celery

# Access Celery shell
docker compose exec celery celery -A config shell
```

### Multi-Stage Builds

The Dockerfile includes multiple stages:

- **base**: Common dependencies
- **development**: Full development environment
- **builder**: Production dependency builder
- **production**: Minimal production runtime

Build specific stage:
```bash
# Build production image
docker build --target production -t backend-prod:latest .

# Run production container
docker run -p 8000:8000 backend-prod:latest
```

### Docker BuildKit Features

The Dockerfile uses BuildKit features for faster builds:

```bash
# Enable BuildKit (if not default)
export DOCKER_BUILDKIT=1

# Build with cache
docker compose build

# Build with inline cache
docker buildx build --cache-to=type=inline --tag backend-dev:latest .
```

### Connecting External Tools

#### Database Tools (DBeaver, pgAdmin)

Connect to PostgreSQL using:
- Host: `localhost`
- Port: `5432`
- Database: `backend_db`
- User: `postgres`
- Password: `postgres`

#### Redis Clients (RedisInsight)

Connect to Redis using:
- Host: `localhost`
- Port: `6379`

### Production Deployment

For production, use the production stage:

```bash
# Build production image
docker build --target production -t backend:latest .

# Run with production settings
docker run -d \
  -e DJANGO_SETTINGS_MODULE=config.settings.production \
  -e SECRET_KEY=<secure-key> \
  -e DB_HOST=<production-db> \
  -p 8000:8000 \
  backend:latest
```

**Note**: For production orchestration, consider Kubernetes, Docker Swarm, or managed container services.

## Best Practices

1. **Never commit secrets**: Use `.env.docker` for development, environment injection for production
2. **Use volumes for data**: Database and media files should be in volumes
3. **Rebuild after dependency changes**: New packages require image rebuild
4. **Monitor resource usage**: Use `docker stats` to track container resources
5. **Clean up regularly**: Remove unused images and volumes with `docker system prune`
6. **Keep images updated**: Pull latest base images periodically
7. **Use health checks**: Ensure services are healthy before depending on them
8. **Review logs**: Check logs regularly for errors and warnings

## Production Deployment

This guide covers **development setup only**. For production deployment:

### Production Container

The production container setup includes:
- **Minimal Image**: Multi-stage build (~200MB vs ~400MB dev)
- **Production Server**: Gunicorn WSGI server with 4 workers
- **Security Hardened**: Non-root user, HTTPS enforcement, secure cookies
- **Auto-Migrations**: Database migrations applied on startup
- **Structured Logging**: JSON-formatted logs for aggregation
- **Health Checks**: Built-in monitoring for orchestration

### Production Documentation

See **[DOCKER_PRODUCTION.md](./DOCKER_PRODUCTION.md)** for:
- Production container build and deployment
- Security configuration and best practices
- Performance optimization and tuning
- Monitoring, logging, and maintenance
- Troubleshooting production issues
- Database backups and disaster recovery

### Quick Production Start

```bash
# 1. Create production environment file
cp .env.production.example .env.production
nano .env.production  # Fill in production values

# 2. Build and start production containers
docker compose -f docker-compose.production.yml up --build -d

# 3. Verify deployment
curl http://localhost:8000/api/v1/health/
```

### Development vs Production

| Aspect | Development | Production |
|--------|-------------|------------|
| Dockerfile Target | `development` | `production` |
| Server | Django runserver | Gunicorn (4 workers) |
| Image Size | ~400MB | ~200MB |
| Hot Reload | Enabled | Disabled |
| Debug Mode | True | False |
| Logging | Console (verbose) | JSON (structured) |
| Security | Relaxed | Hardened |

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Django on Docker Best Practices](https://docs.docker.com/samples/django/)
- [Production Deployment Guide](./DOCKER_PRODUCTION.md)
- [Backend README](README.md)

## Support

For issues or questions:
1. Check logs: `docker compose logs -f`
2. Review [Troubleshooting](#troubleshooting) section
3. Verify configuration: `docker compose config`
4. For production issues, see [DOCKER_PRODUCTION.md](./DOCKER_PRODUCTION.md)
5. Open an issue on the repository
