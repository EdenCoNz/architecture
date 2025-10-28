# Container Health Monitoring

**Last Updated**: 2025-10-24
**Feature**: Story 8.8 - Container Health Monitoring
**Status**: Implemented

## Overview

This document describes the container health monitoring implementation for the application stack. All containers include comprehensive health checks that enable automatic failure detection and container restart capabilities.

## Health Check Implementation

### Backend Application

**Container**: `app-backend`
**Health Endpoint**: `/api/v1/health/`
**Check Interval**: 30 seconds
**Check Timeout**: 3 seconds
**Start Period**: 40 seconds
**Retries**: 3

#### Health Check Configuration

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health/"]
  interval: 30s
  timeout: 3s
  retries: 3
  start_period: 40s
```

#### Health Endpoints

The backend provides multiple health check endpoints for different purposes:

1. **Basic Health Check** - `/api/v1/health/`
   - Returns: 200 if healthy, 503 if unhealthy
   - Checks: Application responsiveness, database connectivity
   - Use: Docker health checks, load balancers

2. **Detailed Status** - `/api/v1/status/`
   - Returns: Always 200 (even if unhealthy)
   - Checks: Version info, uptime, memory, database status
   - Use: Monitoring dashboards, troubleshooting

3. **Readiness Probe** - `/api/v1/health/ready/`
   - Returns: 200 if ready, 503 if not ready
   - Checks: Database connectivity, service dependencies
   - Use: Kubernetes readiness probes, traffic routing

4. **Liveness Probe** - `/api/v1/health/live/`
   - Returns: Always 200 if server is running
   - Checks: Application process only (no dependencies)
   - Use: Kubernetes liveness probes, container restart decisions

#### Health Check Response Examples

**Healthy Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-24T12:00:00Z",
  "database": {
    "status": "connected",
    "response_time_ms": 15.5,
    "engine": "postgresql"
  }
}
```

**Unhealthy Response** (HTTP 503):
```json
{
  "status": "unhealthy",
  "timestamp": "2025-10-24T12:00:00Z",
  "database": {
    "status": "disconnected",
    "error": "connection refused"
  }
}
```

#### What the Backend Health Check Verifies

- Application server is responding to HTTP requests
- Database connection is established and responsive
- Database queries complete within acceptable time
- Application can access critical dependencies

### Frontend Application

**Container**: `app-frontend` (development)
**Health Check**: HTTP request to Vite dev server
**Check Interval**: 30 seconds
**Check Timeout**: 3 seconds
**Start Period**: 30 seconds
**Retries**: 3

#### Development Health Check Configuration

```yaml
healthcheck:
  test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:5173"]
  interval: 30s
  timeout: 3s
  retries: 3
  start_period: 30s
```

#### Production Health Check Configuration

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost/health || exit 1
```

**Production Health Endpoint**: `/health`
- Returns: 200 with "healthy" text
- Configured in nginx
- Simple text response for minimal overhead

#### What the Frontend Health Check Verifies

- Web server is responding to HTTP requests
- Development server (Vite) or production server (nginx) is running
- Static assets can be served

### Database (PostgreSQL)

**Container**: `app-db`
**Health Check**: `pg_isready` command
**Check Interval**: 10 seconds
**Check Timeout**: 5 seconds
**Start Period**: 10 seconds
**Retries**: 5

#### Health Check Configuration

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U postgres -d backend_db"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 10s
```

#### What the Database Health Check Verifies

- PostgreSQL server is running
- Database is accepting connections
- Database is ready to execute queries

### Cache (Redis)

**Container**: `app-redis`
**Health Check**: `redis-cli ping` command
**Check Interval**: 10 seconds
**Check Timeout**: 3 seconds
**Start Period**: 10 seconds
**Retries**: 5

#### Health Check Configuration

```yaml
healthcheck:
  test: ["CMD", "redis-cli", "ping"]
  interval: 10s
  timeout: 3s
  retries: 5
  start_period: 10s
```

#### What the Redis Health Check Verifies

- Redis server is running
- Redis is accepting commands
- Cache is operational

## Health Check Parameters Explained

### Interval
Time between health check executions. Shorter intervals detect failures faster but increase resource usage.

**Recommendations**:
- Critical services (database, cache): 10-15 seconds
- Application services: 30 seconds
- Frontend/static servers: 30-60 seconds

### Timeout
Maximum time to wait for health check to complete. Should be shorter than interval.

**Recommendations**:
- Database/cache checks: 3-5 seconds
- HTTP endpoint checks: 3-5 seconds
- Complex health checks: 10 seconds

### Start Period
Grace period after container starts before health checks count toward retries. Allows application initialization time.

**Recommendations**:
- Simple services (nginx, Redis): 10-15 seconds
- Application servers (Django, Node): 30-60 seconds
- Services with migrations/startup tasks: 60-120 seconds

### Retries
Number of consecutive failures before marking container as unhealthy.

**Recommendations**:
- Production services: 3-5 retries
- Development services: 2-3 retries
- Avoid setting too high (delays failure detection)

## Monitoring Container Health

### View Health Status

```bash
# View all container health status
docker compose ps

# View detailed health information
docker inspect --format='{{.State.Health.Status}}' app-backend

# View health check logs
docker inspect --format='{{range .State.Health.Log}}{{.Output}}{{end}}' app-backend
```

### Run Health Check Validation

```bash
# Validate all services
./scripts/validate-health-checks.sh

# Validate backend only
./scripts/validate-health-checks.sh --backend

# Validate with verbose output
./scripts/validate-health-checks.sh --verbose
```

### Manual Health Endpoint Testing

```bash
# Test backend health endpoint
curl http://localhost:8000/api/v1/health/

# Test backend status endpoint (detailed)
curl http://localhost:8000/api/v1/status/

# Test backend readiness
curl http://localhost:8000/api/v1/health/ready/

# Test backend liveness
curl http://localhost:8000/api/v1/health/live/

# Test frontend (development)
curl http://localhost:5173

# Test frontend health (production)
curl http://localhost/health
```

### Watch Health Status in Real-Time

```bash
# Watch container status
watch -n 2 'docker compose ps'

# Watch health status for all containers
watch -n 2 'docker ps --format "table {{.Names}}\t{{.Status}}"'

# Stream health check events
docker events --filter 'event=health_status'
```

## Automatic Container Restart

### How It Works

1. **Initial State**: Container starts, enters "starting" health state
2. **Start Period**: Health checks run but failures don't count toward retries
3. **Healthy State**: After successful health check, container marked as "healthy"
4. **Failure Detection**: If health check fails, retry counter increments
5. **Unhealthy State**: After configured retries, container marked as "unhealthy"
6. **Restart**: Docker automatically restarts unhealthy containers (with restart policy)

### Restart Policies

**Development** (`docker-compose.yml`):
```yaml
restart: unless-stopped
```
- Containers restart automatically unless explicitly stopped
- Health check failures trigger restarts
- Good for development and testing

**Production** (`docker-compose.production.yml`):
```yaml
restart: always
```
- Containers always restart on failure
- Restarts even after system reboot
- Required for production resilience

### Testing Automatic Restart

#### Test Backend Restart on Database Failure

```bash
# Stop database to trigger health check failure
docker compose stop db

# Watch backend health status (will become unhealthy after ~90 seconds)
docker inspect --format='{{.State.Health.Status}}' app-backend

# Backend will restart automatically when marked unhealthy
docker compose logs -f backend

# Restart database
docker compose start db

# Backend should recover and become healthy again
```

#### Test Frontend Restart on Application Crash

```bash
# Kill the frontend process inside container
docker compose exec frontend pkill node

# Container will restart automatically
docker compose ps

# Verify it becomes healthy again
docker inspect --format='{{.State.Health.Status}}' app-frontend
```

## Troubleshooting

### Container Stuck in "starting" State

**Possible Causes**:
- Application takes longer than `start_period` to initialize
- Health check endpoint not accessible
- Dependencies not ready

**Solutions**:
```bash
# Check container logs
docker compose logs backend

# Increase start_period in docker-compose.yml
healthcheck:
  start_period: 60s  # Increase from 40s

# Verify dependencies are healthy
docker compose ps
```

### Container Marked as "unhealthy"

**Possible Causes**:
- Application crashed or became unresponsive
- Database connection lost
- Health endpoint returning errors

**Solutions**:
```bash
# Check health check output
docker inspect --format='{{range .State.Health.Log}}{{.Output}}{{end}}' app-backend

# Check application logs
docker compose logs backend

# Test health endpoint manually
curl -v http://localhost:8000/api/v1/health/

# Restart the container
docker compose restart backend
```

### Health Checks Passing but Application Not Working

**Possible Causes**:
- Health check too simplistic (not checking critical functionality)
- Health endpoint cached or bypassing application logic
- Race condition between health check and actual requests

**Solutions**:
- Enhance health check to verify critical dependencies
- Add database connectivity check to health endpoint
- Test application functionality separately from health checks

### False Positives During Startup

**Possible Causes**:
- `start_period` too short for application initialization
- Database migrations running during startup
- External service dependencies slow to respond

**Solutions**:
```yaml
# Increase start_period
healthcheck:
  start_period: 90s  # Allow more time for migrations

# Ensure dependencies start first
depends_on:
  db:
    condition: service_healthy
```

## Best Practices

### Health Check Design

1. **Keep It Simple**: Health checks should be fast (<3 seconds)
2. **Check Critical Paths**: Verify database, cache, essential services
3. **Avoid Side Effects**: Health checks should not modify data
4. **Return Quickly**: Don't wait for slow operations
5. **Be Specific**: Return meaningful error messages

### Health Check Configuration

1. **Set Appropriate Intervals**: Balance detection speed vs. resource usage
2. **Allow Startup Time**: Set `start_period` longer than initialization
3. **Configure Retries**: 3-5 retries prevents false positives
4. **Use Short Timeouts**: Force quick failures instead of hanging

### Production Considerations

1. **Monitor Health Status**: Alert on unhealthy containers
2. **Log Health Failures**: Capture health check output for debugging
3. **Test Failure Scenarios**: Verify restart behavior works correctly
4. **Document Dependencies**: Track what each health check verifies
5. **Review Regularly**: Update health checks as application evolves

## Integration with Orchestration

### Docker Compose

Health checks integrate with `depends_on` conditions:

```yaml
backend:
  depends_on:
    db:
      condition: service_healthy  # Wait for db to be healthy
    redis:
      condition: service_healthy  # Wait for redis to be healthy
```

### Kubernetes

The health endpoints support Kubernetes probes:

```yaml
livenessProbe:
  httpGet:
    path: /api/v1/health/live/
    port: 8000
  initialDelaySeconds: 40
  periodSeconds: 30

readinessProbe:
  httpGet:
    path: /api/v1/health/ready/
    port: 8000
  initialDelaySeconds: 20
  periodSeconds: 10
```

### Load Balancers

Health endpoints can be used by load balancers:

- **HAProxy**: `option httpchk GET /api/v1/health/`
- **Nginx**: `health_check uri=/api/v1/health/`
- **AWS ALB**: Use `/api/v1/health/` as target health check path

## Metrics and Monitoring

### Key Metrics to Track

1. **Health Check Success Rate**: Percentage of successful health checks
2. **Time to Healthy**: Duration from container start to healthy state
3. **Restart Count**: Number of automatic restarts per container
4. **Health Check Duration**: Time taken to complete health checks
5. **Unhealthy Duration**: Time spent in unhealthy state before restart

### Recommended Monitoring Setup

```bash
# Export health status to monitoring system
docker inspect --format='{{.State.Health.Status}}' app-backend | \
  prometheus_pushgateway

# Alert on unhealthy containers
docker events --filter 'event=health_status: unhealthy' | \
  monitoring_alert_system
```

## Acceptance Criteria Validation

### ✓ Criterion 1: Report Health Status
- All containers have health checks configured
- Health status visible via `docker ps` and `docker inspect`
- Backend provides detailed health information via API endpoints

### ✓ Criterion 2: Detect Unresponsive Applications
- Health checks verify actual application functionality
- Database connectivity checked in backend health endpoint
- Failed health checks mark container as unhealthy

### ✓ Criterion 3: Automatic Restart
- Unhealthy containers restart automatically with `restart: unless-stopped`
- Production uses `restart: always` for maximum resilience
- Restart behavior tested and verified

### ✓ Criterion 4: Clear Health Results
- Health status displayed in `docker compose ps`
- Detailed health logs available via `docker inspect`
- Validation script provides comprehensive health summary
- Health endpoints return structured, informative responses

## References

- Docker Health Check Documentation: https://docs.docker.com/engine/reference/builder/#healthcheck
- Docker Compose Health Check: https://docs.docker.com/compose/compose-file/compose-file-v3/#healthcheck
- Backend Health Views: `/backend/apps/api/health_views.py`
- Docker Compose Configuration: `/docker-compose.yml`
- Validation Script: `/scripts/validate-health-checks.sh`
