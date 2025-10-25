# Unified Multi-Service Orchestration - Story 12.1

**Feature**: #12 - Unified Multi-Service Orchestration
**Story**: 12.1 - Unified Service Orchestration Configuration
**Status**: ✅ Completed
**Date**: 2025-10-25

---

## Overview

Story 12.1 implements a unified service orchestration configuration that allows developers to start the complete application stack (frontend, backend, database, web server, reverse proxy) with a single command. All services are accessible through a single entry point on port 80, eliminating the need to remember multiple URLs or manage complex networking requirements.

## Architecture

### Service Stack

```
┌─────────────────────────────────────────────────────────────┐
│                                                               │
│  User Browser → http://localhost/                            │
│                                                               │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Nginx Reverse Proxy (app-proxy)                             │
│  - Port 80 (UNIFIED ENTRY POINT)                             │
│  - Routes traffic based on path                              │
└────┬────────────────────────────────────────────────────┬───┘
     │                                                     │
     │  /                                                  │  /api/*, /admin/*, /static/*, /media/
     │  /@vite/*                                          │
     │  /ws (WebSocket HMR)                               │
     ▼                                                     ▼
┌─────────────────────────┐              ┌──────────────────────────┐
│  Frontend (app-frontend)│              │  Backend (app-backend)   │
│  - React/Vite SPA       │              │  - Django REST API       │
│  - Port 5173 (internal) │              │  - Port 8000 (internal)  │
│  - Hot Module Reload    │              │  - Auto migrations       │
└─────────────────────────┘              └─────────┬────────────────┘
                                                    │
                                    ┌───────────────┴────────────────┐
                                    │                                 │
                                    ▼                                 ▼
                        ┌─────────────────────┐      ┌─────────────────────┐
                        │  PostgreSQL (app-db)│      │  Redis (app-redis)  │
                        │  - Port 5432        │      │  - Port 6379        │
                        │  - Persistent data  │      │  - Cache/Queue      │
                        └─────────────────────┘      └─────────────────────┘
```

### Network Routing

The reverse proxy (nginx) routes requests based on URL paths:

| URL Path | Destination | Purpose |
|----------|------------|---------|
| `/` | Frontend (5173) | React SPA application |
| `/api/*` | Backend (8000) | REST API endpoints |
| `/admin/*` | Backend (8000) | Django admin interface |
| `/static/*` | Backend (8000) | Django static files |
| `/media/*` | Backend (8000) | User-uploaded media |
| `/ws` | Frontend (5173) | Vite HMR WebSocket |
| `/@vite/*` | Frontend (5173) | Vite dev server assets |
| `/health` | Proxy | Reverse proxy health check |

## Acceptance Criteria Validation

### ✅ AC1: Single Command Startup

**Requirement**: Given I run the orchestration start command, when all services initialize, then I should be able to access the complete application through a single entry point.

**Implementation**:
```bash
# Single command starts all services
./docker-dev.sh start

# Or using docker compose directly
docker compose up -d
```

**Result**: All 6 services (db, redis, backend, frontend, proxy, celery) start automatically with proper dependency ordering. The application is accessible at `http://localhost/`.

**Validation**:
```bash
# Check all services are running
docker compose ps

# Verify health checks
docker compose ps | grep healthy

# Access unified entry point
curl http://localhost/
curl http://localhost/api/
curl http://localhost/health
```

### ✅ AC2: Frontend-Backend Communication Through Proxy

**Requirement**: Given all services are running, when I access the application, then the frontend should successfully communicate with the backend through the reverse proxy.

**Implementation**:
- Frontend accesses backend via relative paths: `/api/*`
- Both services on same origin: `http://localhost`
- No CORS issues (same-origin policy satisfied)
- Runtime configuration loaded from `/api/v1/config/frontend/`

**Result**: Frontend makes API requests to `/api/v1/...` which are automatically routed through the reverse proxy to `backend:8000/api/v1/...`

**Validation**:
```bash
# Test frontend can reach backend through proxy
curl http://localhost/api/v1/health/

# Test frontend configuration endpoint
curl http://localhost/api/v1/config/frontend/

# Check reverse proxy routing in logs
docker logs app-proxy | tail -20
```

### ✅ AC3: Clean Service Shutdown

**Requirement**: Given I stop the orchestration, when I run the stop command, then all services should stop cleanly and release resources.

**Implementation**:
```bash
# Stop all services cleanly
./docker-dev.sh stop

# Or using docker compose directly
docker compose down
```

**Result**: All containers stop in reverse dependency order, connections close gracefully, ports are released.

**Validation**:
```bash
# Verify all containers stopped
docker compose ps

# Verify ports released
sudo netstat -tlnp | grep -E ":(80|8000|5173|5432|6379)"
```

### ✅ AC4: Data Persistence Across Restarts

**Requirement**: Given I restart the orchestration, when services start again, then all data and state should be preserved from the previous session.

**Implementation**:
- Named volumes for persistent data:
  - `app-postgres-data`: PostgreSQL database
  - `app-redis-data`: Redis cache
  - `app-backend-media`: Uploaded media files
  - `app-backend-static`: Static files
  - `app-frontend-node-modules`: Node.js dependencies
  - `app-proxy-logs`: Nginx access/error logs

**Result**: Data survives container restarts. Database records, user uploads, and application state persist.

**Validation**:
```bash
# List volumes
docker volume ls | grep app-

# Inspect volume
docker volume inspect app-postgres-data

# Test data persistence
# 1. Start services
./docker-dev.sh start

# 2. Create data (e.g., Django admin user)
docker compose exec backend python manage.py createsuperuser

# 3. Stop services
./docker-dev.sh stop

# 4. Start services again
./docker-dev.sh start

# 5. Verify data persists
docker compose exec backend python manage.py shell
# >>> from django.contrib.auth.models import User
# >>> User.objects.all()
```

## Quick Start Guide

### Prerequisites

- Docker Engine 23.0+ (with BuildKit)
- Docker Compose v2.0+
- 8GB RAM minimum
- 20GB disk space

### Starting the Stack

```bash
# Start all services (recommended)
./docker-dev.sh start

# View status
./docker-dev.sh status

# View logs
./docker-dev.sh logs

# Stop services
./docker-dev.sh stop
```

### Accessing the Application

**Unified Entry Point**:
- Application: http://localhost/
- API: http://localhost/api/
- Admin: http://localhost/admin/
- Health: http://localhost/health

**Direct Service Access** (for debugging):
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- Database: localhost:5432
- Redis: localhost:6379

## Service Dependencies

Services start in the following order to ensure dependencies are met:

1. **PostgreSQL** (db) - Database must be ready first
   - Health check: `pg_isready`
   - Start period: 10s

2. **Redis** (redis) - Cache/queue must be ready
   - Health check: `redis-cli ping`
   - Start period: 10s

3. **Backend** (backend) - Waits for db and redis
   - Health check: `curl http://localhost:8000/api/v1/health/`
   - Start period: 40s
   - Runs migrations automatically on startup

4. **Frontend** (frontend) - Waits for backend
   - Health check: `wget http://localhost:5173`
   - Start period: 30s

5. **Reverse Proxy** (proxy) - Waits for frontend and backend
   - Health check: `wget http://localhost/health`
   - Start period: 10s

6. **Celery** (celery, optional) - Waits for db and redis
   - Profile: `with-celery` (only starts when explicitly requested)

## Configuration

### Environment Variables

The stack supports environment variable configuration:

```bash
# Port configuration
export PROXY_PORT=80          # Reverse proxy port
export BACKEND_PORT=8000      # Backend direct access port
export FRONTEND_PORT=5173     # Frontend direct access port
export DB_PORT=5432           # PostgreSQL port
export REDIS_PORT=6379        # Redis port

# Database configuration
export DB_NAME=backend_db
export DB_USER=postgres
export DB_PASSWORD=postgres

# Start services with custom configuration
docker compose up -d
```

### Runtime Configuration

Frontend configuration is loaded at runtime from the backend API:
- Endpoint: `/api/v1/config/frontend/`
- See: `RUNTIME_CONFIG_IMPLEMENTATION.md`

Backend environment variables control frontend behavior:
```bash
FRONTEND_API_URL=http://localhost
FRONTEND_APP_NAME=Application (Docker Dev)
FRONTEND_ENABLE_DEBUG=true
```

## Networking

### Private Network

All services communicate through a private bridge network (`app-network`):
- Internal DNS resolution: Services can reference each other by name (e.g., `backend:8000`)
- Network isolation: Services cannot be accessed from outside except through exposed ports
- Automatic service discovery: No need to configure IP addresses

### Port Exposure

Only the following ports are exposed to the host:

| Port | Service | Purpose |
|------|---------|---------|
| 80 | Reverse Proxy | **UNIFIED ENTRY POINT** |
| 5432 | PostgreSQL | Database tools (optional) |
| 6379 | Redis | Redis clients (optional) |
| 5173 | Frontend | Direct debugging (optional) |
| 8000 | Backend | Direct debugging (optional) |

**Note**: In production, only port 80 (or 443 for HTTPS) should be exposed.

## Resource Limits

Each service has defined resource limits to prevent exhaustion:

| Service | CPU Limit | Memory Limit | CPU Reservation | Memory Reservation |
|---------|-----------|--------------|-----------------|-------------------|
| PostgreSQL | 1 CPU | 512M | 0.5 CPU | 256M |
| Redis | 0.5 CPU | 256M | 0.25 CPU | 128M |
| Backend | 2 CPUs | 1G | 0.5 CPU | 512M |
| Frontend | 2 CPUs | 2G | 1 CPU | 512M |
| Proxy | 0.5 CPU | 256M | 0.25 CPU | 128M |
| Celery | 1 CPU | 512M | 0.25 CPU | 256M |

**Total Stack Requirements**:
- CPU: 7 CPUs (limit), 2.75 CPUs (reservation)
- Memory: 4.5GB (limit), 1.75GB (reservation)

## Monitoring

### Health Checks

All services implement health checks:

```bash
# Check service health
./docker-dev.sh status

# Or inspect individually
docker inspect --format='{{.State.Health.Status}}' app-proxy
docker inspect --format='{{.State.Health.Status}}' app-backend
docker inspect --format='{{.State.Health.Status}}' app-frontend
docker inspect --format='{{.State.Health.Status}}' app-db
docker inspect --format='{{.State.Health.Status}}' app-redis
```

### Logs

All services log to stdout/stderr with JSON formatting:

```bash
# View all logs
./docker-dev.sh logs

# View specific service
./docker-dev.sh logs backend

# Follow logs in real-time
docker compose logs -f backend

# View proxy access logs
docker compose exec proxy tail -f /var/log/nginx/access.log
```

### Restart Policies

All services (except celery) use `restart: unless-stopped`:
- Automatically restart on failure
- Don't restart if manually stopped
- Restart after host reboot (if Docker auto-starts)

## Troubleshooting

### Service Won't Start

```bash
# Check service status
docker compose ps

# Check logs for errors
./docker-dev.sh logs <service-name>

# Rebuild service
docker compose build <service-name>
docker compose up -d <service-name>
```

### Can't Access Application

```bash
# Verify proxy is running
curl http://localhost/health

# Check backend health
curl http://localhost/api/v1/health/

# Check proxy routing
docker logs app-proxy | tail -50
```

### Frontend Can't Reach Backend

```bash
# Check CORS configuration
docker compose exec backend python manage.py shell
# >>> from django.conf import settings
# >>> settings.CORS_ALLOWED_ORIGINS

# Check reverse proxy config
docker compose exec proxy cat /etc/nginx/nginx.conf | grep -A 10 "location /api"
```

### Database Connection Issues

```bash
# Check database is ready
docker compose exec db pg_isready -U postgres

# Check backend can connect
docker compose exec backend python manage.py check_database

# View database logs
docker compose logs db | tail -50
```

### Port Already in Use

```bash
# Find what's using port 80
sudo netstat -tlnp | grep :80

# Use different port
export PROXY_PORT=8080
docker compose up -d proxy
```

## File Structure

```
/home/ed/Dev/architecture/
├── docker-compose.yml              # Main orchestration file
├── docker-dev.sh                   # Helper script
├── nginx/
│   └── nginx.conf                  # Reverse proxy configuration
├── backend/
│   ├── Dockerfile                  # Backend container
│   └── .env.docker                 # Backend environment
├── frontend/
│   ├── Dockerfile                  # Frontend container
│   └── .env.docker                 # Frontend environment
└── docs/features/12/
    ├── user-stories.md             # Feature stories
    ├── implementation-log.json     # Implementation tracking
    └── UNIFIED_ORCHESTRATION.md    # This document
```

## Next Steps

Story 12.1 provides the foundation for subsequent stories:

- **Story 12.2**: Service Dependency Management - Enhanced dependency handling
- **Story 12.3**: Reverse Proxy Configuration - Advanced routing and security
- **Story 12.4**: Environment-Specific Configuration - Dev/staging/prod configs
- **Story 12.5**: Service Isolation and Networking - Enhanced network security
- **Story 12.6**: Persistent Data Management - Backup and restore strategies

## References

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Nginx Reverse Proxy Guide](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/)
- [Feature #8 Implementation](../8/implementation-summary.md)
- [Runtime Configuration Guide](/RUNTIME_CONFIG_IMPLEMENTATION.md)
- [Docker Best Practices](/context/devops/docker.md)

## Success Metrics

✅ **Single Command Deployment**: Start entire stack with `./docker-dev.sh start`
✅ **Unified Entry Point**: All access through `http://localhost/`
✅ **Zero Configuration**: Works out of the box with sensible defaults
✅ **Data Persistence**: All data survives restarts
✅ **Health Monitoring**: All services have health checks
✅ **Resource Management**: CPU and memory limits defined
✅ **Clean Shutdown**: Graceful service termination

---

**Status**: Story 12.1 is complete and all acceptance criteria are met.
