# Quick Start Guide - Unified Application Stack

**One command to rule them all**: `./docker-dev.sh start`

## Prerequisites

- Docker Engine 23.0+
- Docker Compose v2.0+
- 8GB RAM, 20GB disk space

## Getting Started

```bash
# 1. Start all services (database, cache, backend, frontend, reverse proxy)
./docker-dev.sh start

# 2. Wait for services to become healthy (~30-60 seconds)
./docker-dev.sh status

# 3. Access the application
# Open your browser to: http://localhost/
```

**That's it!** The complete stack is now running.

## Access Points

### Unified Entry Point (Recommended)
- **Application**: http://localhost/
- **API**: http://localhost/api/
- **Admin Panel**: http://localhost/admin/
- **Health Check**: http://localhost/health

### Direct Service Access (Debugging)
- **Frontend**: http://localhost:5173
- **Backend**: http://localhost:8000
- **Database**: localhost:5432 (user: postgres, password: postgres)
- **Redis**: localhost:6379

## Common Commands

```bash
# Start services
./docker-dev.sh start

# Stop services
./docker-dev.sh stop

# Restart services
./docker-dev.sh restart

# View logs
./docker-dev.sh logs              # All services
./docker-dev.sh logs backend      # Specific service

# Check status
./docker-dev.sh status

# Rebuild containers (after code changes)
./docker-dev.sh rebuild

# Open Django shell
./docker-dev.sh backend-shell

# Run migrations
./docker-dev.sh backend-migrate

# Access database
./docker-dev.sh db-shell

# Clean up (removes all data!)
./docker-dev.sh clean
```

## What's Running?

| Service | Container Name | Purpose |
|---------|---------------|---------|
| Reverse Proxy | app-proxy | Routes requests to frontend/backend |
| Frontend | app-frontend | React/Vite application |
| Backend | app-backend | Django REST API |
| Database | app-db | PostgreSQL 15 |
| Cache | app-redis | Redis 7 |
| Worker | app-celery | Background tasks (optional) |

## Development Workflow

### Making Changes

**Frontend** (Hot Module Replacement enabled):
```bash
# Edit files in frontend/src/
# Browser automatically reloads - no rebuild needed!
```

**Backend** (Auto-reload enabled):
```bash
# Edit files in backend/
# Django automatically reloads - no rebuild needed!
```

### Database Migrations

```bash
# Create migrations
docker compose exec backend python manage.py makemigrations

# Apply migrations
./docker-dev.sh backend-migrate

# Or let the container do it automatically on startup
./docker-dev.sh restart
```

### Adding Dependencies

**Frontend**:
```bash
# 1. Stop services
./docker-dev.sh stop

# 2. Add package to frontend/package.json

# 3. Rebuild
./docker-dev.sh rebuild
```

**Backend**:
```bash
# 1. Stop services
./docker-dev.sh stop

# 2. Add package to backend/requirements/base.txt or dev.txt

# 3. Rebuild
./docker-dev.sh rebuild
```

## Troubleshooting

### Services Won't Start

```bash
# Check what's wrong
docker compose ps
./docker-dev.sh logs

# Nuclear option: rebuild everything
./docker-dev.sh clean  # WARNING: Deletes all data!
./docker-dev.sh start
```

### Port Conflicts

```bash
# Check what's using port 80
sudo netstat -tlnp | grep :80

# Use different port
export PROXY_PORT=8080
docker compose up -d proxy

# Access at http://localhost:8080/
```

### Can't Access Application

```bash
# Verify proxy is healthy
curl http://localhost/health

# Check backend is responding
curl http://localhost/api/v1/health/

# View proxy logs
docker logs app-proxy | tail -50
```

### Database Issues

```bash
# Check database is ready
docker compose exec db pg_isready -U postgres

# Reset database (WARNING: Deletes all data!)
./docker-dev.sh stop
docker volume rm app-postgres-data
./docker-dev.sh start
```

## Architecture

```
Browser (http://localhost/)
    ↓
Nginx Reverse Proxy (port 80)
    ↓
    ├─→ Frontend (React/Vite) - for routes /
    └─→ Backend (Django API) - for routes /api/*, /admin/*
        ↓
        ├─→ PostgreSQL (database)
        └─→ Redis (cache/queue)
```

## Data Persistence

Your data is safe! These volumes persist across restarts:

- `app-postgres-data` - Database records
- `app-redis-data` - Cache data
- `app-backend-media` - Uploaded files
- `app-backend-static` - Static files
- `app-frontend-node-modules` - NPM packages
- `app-proxy-logs` - Nginx logs

To completely reset (delete all data):
```bash
./docker-dev.sh clean
```

## Resource Usage

Expected resource consumption:

- **Memory**: ~2-3GB (development), ~1.5GB (idle)
- **CPU**: Low (<20% on modern systems)
- **Disk**: ~5GB (images + volumes)

## Next Steps

1. **Create a superuser**:
   ```bash
   docker compose exec backend python manage.py createsuperuser
   ```

2. **Access Django Admin**:
   - Go to http://localhost/admin/
   - Login with superuser credentials

3. **Test the API**:
   ```bash
   # Health check
   curl http://localhost/api/v1/health/

   # Frontend config
   curl http://localhost/api/v1/config/frontend/
   ```

4. **Read full documentation**:
   - `docs/features/12/UNIFIED_ORCHESTRATION.md` - Complete guide
   - `DOCKER.md` - Docker details
   - `RUNTIME_CONFIG_IMPLEMENTATION.md` - Configuration system

## Support

**Common Issues**: See troubleshooting section above

**Logs**: `./docker-dev.sh logs [service-name]`

**Status**: `./docker-dev.sh status`

**Help**: `./docker-dev.sh help`

---

**That's all you need to know!** Start coding! 🚀
