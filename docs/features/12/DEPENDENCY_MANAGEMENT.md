# Service Dependency Management (Story 12.2)

**Feature**: #12 - Unified Multi-Service Orchestration
**Story**: 12.2 - Service Dependency Management
**Status**: Completed
**Date**: 2025-10-25

## Overview

This document describes the service dependency management system implemented for the unified multi-service orchestration. Services start in the correct order based on their dependencies, with health checks ensuring that dependent services don't fail because required services aren't ready.

## Dependency Architecture

### Service Dependency Layers

The application stack is organized into 4 dependency layers:

```
Layer 1 (Foundation - No Dependencies)
├── db (PostgreSQL)
└── redis (Redis Cache)

Layer 2 (Backend Services)
└── backend (Django API) → depends on: db, redis

Layer 3 (Frontend Services)
└── frontend (React/Vite) → depends on: backend

Layer 4 (Reverse Proxy - Unified Entry Point)
└── proxy (Nginx) → depends on: frontend, backend
```

### Dependency Graph

```
              ┌──────────────────────────────────┐
              │         Unified Entry Point      │
              │                                  │
              │   proxy (nginx:1.27-alpine)     │
              │   Layer 4                        │
              └────────────┬────────────┬────────┘
                          │            │
                   depends on      depends on
                          │            │
              ┌───────────▼────┐   ┌──▼────────────┐
              │  frontend      │   │   backend     │
              │  (React/Vite)  │   │   (Django)    │
              │  Layer 3       │   │   Layer 2     │
              └────────┬───────┘   └──┬──────┬─────┘
                      │               │      │
                 depends on      depends on  │
                      │               │      │
                      └───────────────┼──────┘
                                      │
                              ┌───────▼──────┐
                              │   Layer 1    │
                              │              │
                       ┌──────┴──────┬───────┴──────┐
                       │             │              │
                  ┌────▼─────┐  ┌───▼──────┐       │
                  │    db    │  │  redis   │       │
                  │(postgres)│  │  (cache) │       │
                  └──────────┘  └──────────┘       │
```

## Implementation Details

### 1. Health Check Strategy

Each service implements comprehensive health checks to verify readiness:

#### Database (PostgreSQL)
```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U postgres -d backend_db || exit 1"]
  interval: 5s
  timeout: 3s
  retries: 5
  start_period: 15s
```

**Purpose**: Verifies PostgreSQL is ready to accept connections before backend starts.

#### Redis Cache
```yaml
healthcheck:
  test: ["CMD", "redis-cli", "ping"]
  interval: 5s
  timeout: 3s
  retries: 5
  start_period: 10s
```

**Purpose**: Ensures Redis is responding before backend attempts cache operations.

#### Backend (Django)
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health/"]
  interval: 15s
  timeout: 5s
  retries: 3
  start_period: 45s
```

**Purpose**: Validates Django application is running AND database/redis connections are working.

**Note**: The backend health endpoint internally validates database and redis connectivity, providing deep health verification.

#### Frontend (React/Vite)
```yaml
healthcheck:
  test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:5173"]
  interval: 15s
  timeout: 5s
  retries: 3
  start_period: 35s
```

**Purpose**: Confirms Vite dev server is running and serving content.

#### Reverse Proxy (Nginx)
```yaml
healthcheck:
  test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost/health"]
  interval: 15s
  timeout: 5s
  retries: 3
  start_period: 15s
```

**Purpose**: Verifies nginx is responding and can route to upstream services.

### 2. Dependency Configuration

Services use Docker Compose `depends_on` with health check conditions and restart policies:

#### Backend Dependencies
```yaml
depends_on:
  db:
    condition: service_healthy
    restart: true
  redis:
    condition: service_healthy
    restart: true
```

**Behavior**:
- Backend waits for both `db` and `redis` to report healthy before starting
- If `db` or `redis` becomes unhealthy, backend automatically restarts
- Backend entrypoint script performs additional validation with clear error messages

#### Frontend Dependencies
```yaml
depends_on:
  backend:
    condition: service_healthy
    restart: true
```

**Behavior**:
- Frontend waits for backend health check to pass
- Frontend fetches runtime configuration from `/api/v1/config/frontend/`
- Uses fallback configuration if backend is temporarily unavailable

#### Proxy Dependencies
```yaml
depends_on:
  frontend:
    condition: service_healthy
    restart: true
  backend:
    condition: service_healthy
    restart: true
```

**Behavior**:
- Proxy starts LAST, after both frontend and backend are healthy
- Ensures unified entry point only becomes available when all services are ready
- Routes traffic to healthy upstream services

### 3. Startup Sequence

When you run `docker compose up`, services start in this order:

```
Time  │ Service      │ Action                                    │ Status
──────┼──────────────┼───────────────────────────────────────────┼──────────────
0s    │ db           │ PostgreSQL container starts               │ starting
0s    │ redis        │ Redis container starts                    │ starting
──────┼──────────────┼───────────────────────────────────────────┼──────────────
5s    │ db           │ pg_isready check begins                   │ health: starting
5s    │ redis        │ redis-cli ping check begins               │ health: starting
──────┼──────────────┼───────────────────────────────────────────┼──────────────
15s   │ db           │ Health check passes (5 retries max)       │ healthy
10s   │ redis        │ Health check passes (5 retries max)       │ healthy
──────┼──────────────┼───────────────────────────────────────────┼──────────────
15s   │ backend      │ Container starts (deps satisfied)         │ starting
      │              │ Entrypoint validates db connection        │
      │              │ Runs migrations if needed                 │
──────┼──────────────┼───────────────────────────────────────────┼──────────────
60s   │ backend      │ Health check passes after start_period    │ healthy
──────┼──────────────┼───────────────────────────────────────────┼──────────────
60s   │ frontend     │ Container starts (backend healthy)        │ starting
      │              │ npm install runs                          │
      │              │ Vite dev server starts                    │
──────┼──────────────┼───────────────────────────────────────────┼──────────────
95s   │ frontend     │ Health check passes after start_period    │ healthy
──────┼──────────────┼───────────────────────────────────────────┼──────────────
95s   │ proxy        │ Container starts (frontend & backend OK)  │ starting
      │              │ Nginx configuration loaded                │
      │              │ Upstream health verified                  │
──────┼──────────────┼───────────────────────────────────────────┼──────────────
110s  │ proxy        │ Health check passes                       │ healthy
──────┼──────────────┼───────────────────────────────────────────┼──────────────
110s  │ ALL          │ Complete stack ready                      │ ✓ READY
```

**Total startup time**: ~110 seconds for full stack (cold start)

### 4. Error Handling and Diagnostics

#### Backend Entrypoint Validation

The backend container's entrypoint script (`docker-entrypoint-dev.sh`) performs extensive validation:

```bash
1. Configuration Validation
   ├─ python manage.py check_config --quiet
   └─ Exit on failure with clear error message

2. Database Connectivity Check
   ├─ python manage.py check_database --wait 30
   ├─ Waits up to 30 seconds for database
   ├─ Retries every 2 seconds
   └─ Shows clear error if database unavailable:
      "✗ Database connection failed: could not connect to server"

3. Migration Status Check
   ├─ python manage.py showmigrations
   ├─ Applies pending migrations automatically
   └─ Shows migration status

4. Start Application
   └─ python manage.py runserver 0.0.0.0:8000
```

#### Dependency Validation Script

The project includes a comprehensive dependency checking script:

```bash
./scripts/check-dependencies.sh          # Check all services
./scripts/check-dependencies.sh -v       # Verbose mode with details
./scripts/check-dependencies.sh -w 60    # Wait up to 60s for health
```

**Output Example**:
```
═══════════════════════════════════════════════════════════════
  Service Dependency Health Check
═══════════════════════════════════════════════════════════════

Dependency Order: db redis backend frontend proxy

✓ db is healthy (running since 10:23:15)
✓ redis is healthy (running since 10:23:15)
✓ backend is healthy (running since 10:23:45)
✓ frontend is healthy (running since 10:24:20)
✓ proxy is healthy (running since 10:24:35)

═══════════════════════════════════════════════════════════════
✓ All services are healthy and dependencies are satisfied
```

**Failure Example**:
```
✗ backend is unhealthy - dependency failure detected:
  - db (PostgreSQL Database)
  - redis (Redis Cache)

Troubleshooting:
  1. Check service logs: docker compose logs <service>
  2. Check all logs: docker compose logs
  3. Restart services: docker compose restart
  4. Check service status: docker compose ps
```

## Acceptance Criteria Validation

### AC1: Database Ready Before Backend Connects

**Requirement**: Given I start the orchestration, when services initialize, then the database should be ready before the backend attempts to connect.

**Implementation**:
- ✅ `depends_on: db: condition: service_healthy` ensures backend waits for database
- ✅ `pg_isready` health check validates database accepts connections
- ✅ Backend entrypoint script waits up to 30 seconds with retry logic
- ✅ Clear error messages if database is unavailable

**Validation**:
```bash
docker compose up -d
docker compose logs backend | grep "Database is ready"
# Output: Database is ready!
```

### AC2: Database Accepting Connections

**Requirement**: Given the backend is starting, when it needs the database, then the database should already be accepting connections.

**Implementation**:
- ✅ Database health check: `pg_isready -U postgres -d backend_db`
- ✅ 5-second interval with 5 retries (max 25s to become healthy)
- ✅ 15-second start period allows PostgreSQL initialization
- ✅ Backend validates connection with `check_database --wait 30`

**Validation**:
```bash
docker compose exec backend python manage.py check_database
# Output: ✓ Database connection successful!
```

### AC3: Reverse Proxy Starts After Services Ready

**Requirement**: Given the reverse proxy is starting, when it configures routing, then both frontend and backend services should already be running.

**Implementation**:
- ✅ Proxy depends on both `frontend` and `backend` with `service_healthy` condition
- ✅ Proxy is Layer 4 (last to start)
- ✅ Health checks ensure services are not just running, but fully functional
- ✅ Nginx validates upstream connectivity on startup

**Validation**:
```bash
docker compose up -d
curl http://localhost/health
# Output: healthy (only available when all services ready)
```

### AC4: Clear Dependency Error Messages

**Requirement**: Given a service fails to start, when I check the logs, then I should see clear indication of which dependency was not available.

**Implementation**:
- ✅ Backend entrypoint shows detailed database connection errors
- ✅ Dependency validation script identifies failed dependencies
- ✅ Docker Compose shows dependency wait status
- ✅ Service health checks provide specific failure reasons

**Validation**:

**Scenario 1**: Database not available
```bash
# Stop database
docker compose stop db

# Try to start backend
docker compose up backend
# Output:
# backend  | Waiting for PostgreSQL to be ready...
# backend  | Attempt 1: Connection failed. Retrying in 2s (timeout in 28s)...
# backend  | ✗ Database connection failed after 30s (15 attempts)
# backend  | Error: could not connect to server: Connection refused
```

**Scenario 2**: Using validation script
```bash
./scripts/check-dependencies.sh -v
# Output:
# ✗ backend is unhealthy - dependency failure detected:
#   - db (PostgreSQL Database)
#
# Troubleshooting:
#   1. Check service logs: docker compose logs db
```

## Usage Guide

### Starting Services

```bash
# Start all services with dependency management
docker compose up

# Start in background
docker compose up -d

# Start and watch logs
docker compose up | grep -E "(Database is ready|healthy|unhealthy)"
```

### Checking Service Health

```bash
# Quick status check
docker compose ps

# Detailed health status
./scripts/check-dependencies.sh -v

# Wait for all services to be healthy (with timeout)
./scripts/check-dependencies.sh --wait 120

# Check specific service
docker compose exec backend python manage.py check_database
```

### Troubleshooting Dependency Issues

#### Problem: Backend fails to start

**Symptoms**:
```
backend  | ✗ Database connection failed
backend exited with code 1
```

**Solution**:
```bash
# 1. Check database health
docker compose ps db

# 2. Check database logs
docker compose logs db --tail 50

# 3. Verify database is healthy
docker compose exec db pg_isready -U postgres

# 4. Restart backend
docker compose restart backend
```

#### Problem: Frontend can't reach backend

**Symptoms**:
```
frontend  | Failed to fetch config from /api/v1/config/frontend/
frontend  | Using fallback configuration
```

**Solution**:
```bash
# 1. Verify backend health
./scripts/check-dependencies.sh

# 2. Check backend API
curl http://localhost:8000/api/v1/health/

# 3. Check logs
docker compose logs backend --tail 50
```

#### Problem: Proxy shows 502 Bad Gateway

**Symptoms**:
```
proxy    | [error] upstream timed out
```

**Solution**:
```bash
# 1. Check upstream service health
./scripts/check-dependencies.sh -v

# 2. Verify backend is responding
docker compose exec backend curl http://localhost:8000/api/v1/health/

# 3. Verify frontend is responding
docker compose exec frontend wget -O- http://localhost:5173

# 4. Check nginx configuration
docker compose exec proxy nginx -t
```

### Viewing Dependency Status

```bash
# Service status with health
docker compose ps

# Dependency validation with details
./scripts/check-dependencies.sh --verbose

# Watch services become healthy
watch -n 2 'docker compose ps'

# Monitor logs for health status changes
docker compose logs -f | grep -E "(healthy|unhealthy|starting)"
```

## Best Practices

### 1. Always Use Health Checks

All services should implement health checks that verify actual functionality, not just process existence.

**Good**:
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health/"]
```

**Bad**:
```yaml
healthcheck:
  test: ["CMD", "ps", "aux", "|", "grep", "python"]
```

### 2. Set Appropriate Start Periods

Start periods should account for initialization time:

- Database: 15s (schema initialization)
- Redis: 10s (data loading)
- Backend: 45s (Python startup, migrations)
- Frontend: 35s (npm install, Vite build)
- Proxy: 15s (nginx configuration load)

### 3. Use Restart Policies

Enable automatic restart on dependency failures:

```yaml
depends_on:
  db:
    condition: service_healthy
    restart: true  # Auto-restart if db becomes unhealthy
```

### 4. Validate Configuration Early

Backend entrypoint validates configuration before attempting connections:

```bash
python manage.py check_config --quiet || exit 1
python manage.py check_database --wait 30 || exit 1
```

### 5. Provide Clear Error Messages

Log actionable error messages that help developers diagnose issues:

```bash
echo "✗ Database connection failed: $ERROR"
echo "Troubleshooting:"
echo "  1. Ensure PostgreSQL is running: docker compose ps db"
echo "  2. Check database logs: docker compose logs db"
```

## Monitoring and Observability

### Service Health Dashboard

```bash
# Create a simple health monitoring loop
while true; do
  clear
  echo "Service Health Status - $(date)"
  echo "================================"
  docker compose ps
  echo ""
  echo "Dependency Validation:"
  ./scripts/check-dependencies.sh --quiet
  sleep 5
done
```

### Log Aggregation

All services use structured logging with rotation:

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

View aggregated logs:
```bash
# All services
docker compose logs -f

# Specific services
docker compose logs -f backend frontend

# Dependency-related logs
docker compose logs -f | grep -E "(Database|Redis|healthy|unhealthy)"
```

## Performance Considerations

### Startup Time Optimization

**Current startup times** (cold start):
- Layer 1 (db, redis): ~15 seconds
- Layer 2 (backend): ~45 seconds (includes migrations)
- Layer 3 (frontend): ~35 seconds (includes npm install)
- Layer 4 (proxy): ~10 seconds
- **Total: ~110 seconds**

**Optimization strategies**:

1. **Use cached images**: Pre-built images start in ~30 seconds
2. **Skip migrations**: Set environment flag to skip automatic migrations (-40s)
3. **Persistent node_modules**: Volume mount reduces npm install time (-20s)
4. **Parallel dependencies**: Layer 1 services start simultaneously

**Optimized startup**: ~50 seconds with pre-built images and caching

### Health Check Intervals

Balance between responsiveness and resource usage:

- **Frequent checks** (5s): Layer 1 services (db, redis) - critical dependencies
- **Standard checks** (15s): Application services - balances load and detection
- **Longer timeouts** (30s): Production deployments - reduces false positives

## Security Considerations

### 1. Network Isolation

Services communicate via private Docker network:
```yaml
networks:
  - app-network  # Isolated bridge network
```

External access only through reverse proxy on port 80.

### 2. Health Check Security

Health checks use internal endpoints, not exposed externally:
- Database: `pg_isready` (no external port needed)
- Backend: Internal health endpoint, not routed by proxy
- Frontend: Internal Vite dev server check

### 3. Dependency Validation

Backend validates database credentials before attempting connection, preventing credential leakage in error messages.

## Future Enhancements

### Story 12.9: Service Health Monitoring

Advanced health monitoring features planned:
- Prometheus metrics export
- Grafana dashboards
- Alert notifications
- Health history tracking
- Automatic recovery procedures

### Production Deployment

For production environments (Story 12.8):
- Reduce health check intervals (30s → 60s)
- Increase retry counts for reliability
- Add dependency timeout limits
- Implement circuit breakers
- Enable health-based load balancing

## References

- [Docker Compose depends_on documentation](https://docs.docker.com/compose/compose-file/05-services/#depends_on)
- [Docker Compose healthcheck specification](https://docs.docker.com/compose/compose-file/05-services/#healthcheck)
- [PostgreSQL pg_isready documentation](https://www.postgresql.org/docs/current/app-pg-isready.html)
- [Feature 12 User Stories](/home/ed/Dev/architecture/docs/features/12/user-stories.md)
- [Unified Orchestration Documentation](/home/ed/Dev/architecture/docs/features/12/UNIFIED_ORCHESTRATION.md)

## Summary

Story 12.2 implements robust service dependency management with:

✅ **4-layer dependency architecture** - Clear separation of concerns
✅ **Health-based startup** - Services wait for healthy dependencies
✅ **Automatic restart** - Failed dependencies trigger dependent restarts
✅ **Clear error messages** - Actionable diagnostics for failures
✅ **Validation tooling** - Comprehensive dependency checking script
✅ **Comprehensive documentation** - Usage guides and troubleshooting

All acceptance criteria have been met, with services starting in the correct order and providing clear error messages when dependencies are unavailable.
