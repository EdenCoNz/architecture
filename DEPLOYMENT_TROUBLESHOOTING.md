# Deployment Troubleshooting Guide

## Backend Container Unhealthy During Staging Deployment

### Problem Summary

The backend container frequently fails health checks during staging deployment with the error:

```
dependency failed to start: container app-backend is unhealthy
```

This happens even though database and redis containers are healthy.

### Root Cause

The issue is a **timing race condition** between:

1. **Backend container startup operations** (migrations, static file collection)
2. **Health check start timing** (`start_period`)
3. **Workflow monitoring timeout**

#### The Startup Sequence

```
Time 0s:      Container starts, entrypoint script begins
Time 0-5s:    Configuration validation (check_config)
Time 5-65s:   Wait for database (check_database --wait 60)
Time 65-75s:  Deployment checks (check --deploy)
Time 75-150s: Database migrations (UNPREDICTABLE - varies based on schema changes)
Time 150-180s: Static file collection (collectstatic)
Time 180s:    Django application server starts
Time 180s+:   Health check endpoint /api/v1/health/ becomes available
```

#### The Health Check Problem

**Before Fix:**
- Health checks started after `start_period: 90s`
- But migrations + collectstatic can take 100-120+ seconds
- Health checks would ping an **unresponsive server** (still running migrations)
- After 3 failed checks, container marked **UNHEALTHY**

### Solution Implemented

#### 1. Extended Health Check Timings

**Changes:**
- `start_period: 90s` → `200s` (3.3 minutes)
- `interval: 45s` → `20s` (more frequent checks after startup)
- `timeout: 5s` → `10s` (allow more time per check)
- `retries: 5` → `3` (fewer retries needed with longer start_period)

**Files Modified:**
- `compose.staging.yml` (line 109-114)
- `compose.production.yml` (line 113-118)

**Rationale:**
```
start_period: 200s  - Allows full startup sequence (DB wait + migrations + collectstatic)
interval: 20s       - Checks every 20s after startup period (faster detection when healthy)
timeout: 10s        - Generous timeout for slow network/server
retries: 3          - Fewer retries needed with generous start_period
```

**Total time before failure:**
```
200s (start_period) + (3 retries × 20s interval) = 260 seconds (4.3 minutes)
```

#### 2. Extended Workflow Monitoring Timeout

**Change:**
- `MAX_WAIT=120` → `600` (10 minutes)

**File Modified:**
- `.github/workflows/unified-ci-cd.yml` (lines 743, 1405)

**Rationale:**
- Workflow must wait for ALL services to become healthy sequentially:
  - Backend: up to 260s (worst case)
  - Frontend: 60s start_period + checks
  - Proxy: 15s start_period + checks
- Total: ~335s minimum + overhead
- 600s (10 minutes) provides generous buffer for system overhead, network latency, and variability

#### 3. Enhanced Entrypoint Logging

**Change:** Added detailed timing and progress logging to `docker-entrypoint-prod.sh`

**Benefits:**
- Shows exactly how long each startup step takes
- Makes bottlenecks visible in deployment logs
- Helps diagnose future timing issues
- Displays total startup time

**Example Output:**
```
╔═══════════════════════════════════════════════════════════════════╗
║          Backend Production Container - Initialization           ║
╚═══════════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[2025-11-01 10:30:00] STEP 1/5: Validating production configuration
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Configuration validation completed in 2s

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[2025-11-01 10:30:02] STEP 2/5: Waiting for PostgreSQL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Database connectivity completed in 5s

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[2025-11-01 10:30:07] STEP 3/5: Running deployment checks
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Deployment checks completed in 3s

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[2025-11-01 10:30:10] STEP 4/5: Applying database migrations
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Database migrations completed in 45s

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[2025-11-01 10:30:55] STEP 5/5: Collecting static files
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Static file collection completed in 15s

╔═══════════════════════════════════════════════════════════════════╗
║            Production Initialization Complete                     ║
╠═══════════════════════════════════════════════════════════════════╣
║  Total startup time: 70s                                          ║
║  Health checks will begin after start_period (200s)               ║
╚═══════════════════════════════════════════════════════════════════╝
```

### How to Monitor Deployments

#### 1. View Container Logs

```bash
# SSH to staging server
ssh user@staging-server

# View backend container logs
cd /home/user/deployments/app-staging
docker compose -f docker-compose.yml -f compose.staging.yml logs -f backend
```

#### 2. Check Container Health Status

```bash
# View all container health status
docker compose -f docker-compose.yml -f compose.staging.yml ps

# Watch health status in real-time
watch -n 2 'docker compose -f docker-compose.yml -f compose.staging.yml ps'
```

#### 3. Debug Health Check Failures

```bash
# Get detailed health check logs
CONTAINER_ID=$(docker compose ps -q backend)
docker inspect $CONTAINER_ID | jq '.[0].State.Health'

# Manually test health endpoint
docker compose exec backend curl -v http://127.0.0.1:8000/api/v1/health/
```

### Future Improvements (Recommended)

#### Option 1: Separate Migrations Job (Best Practice)

Run migrations in a separate container **before** starting the application:

**Pros:**
- Faster application startup
- Follows 12-factor app principles
- Better rollback capabilities
- Cleaner separation of concerns

**Implementation:**
```yaml
# In workflow, add migration job before deployment:
- name: Run database migrations
  run: |
    ssh user@server << EOF
      cd /home/user/deployments/app-staging

      # Run migrations in temporary container
      docker compose run --rm \
        backend \
        python manage.py migrate --noinput

      # Collect static files
      docker compose run --rm \
        backend \
        python manage.py collectstatic --noinput --clear
    EOF

- name: Start application containers
  run: |
    # Now start application (no migrations in entrypoint)
    docker compose up -d
```

**Requires:**
- Remove migrations from `docker-entrypoint-prod.sh`
- Update workflow to run migrations separately
- Consider using shared volume for static files

#### Option 2: Use Liveness/Readiness Probes

Implement Kubernetes-style health checks:

**Liveness Probe** (`/api/v1/health/live/`):
- Just checks if server is running
- **Never fails** during startup
- Only fails if server crashes

**Readiness Probe** (`/api/v1/health/ready/`):
- Checks if server is ready for traffic
- Can fail during startup (migrations)
- Controls traffic routing

**Implementation:**
```yaml
healthcheck:
  # Use liveness endpoint (always returns 200 if server running)
  test: ["CMD", "curl", "-f", "http://127.0.0.1:8000/api/v1/health/live/"]
  interval: 30s
  timeout: 10s
  retries: 5
  start_period: 180s
```

#### Option 3: Pre-baked Database State

For development/staging environments:

- Include database state in Docker image
- Use database snapshots
- Skip migrations on startup
- **Trade-off:** Larger images, but faster startup

### Monitoring Checklist

When deploying to staging/production, verify:

- [ ] Backend logs show "Production Initialization Complete"
- [ ] Total startup time is logged (should be < 180s ideally)
- [ ] Each step completes successfully with timing
- [ ] Health check endpoint returns 200 OK
- [ ] No "UNHEALTHY" status in `docker compose ps`
- [ ] Workflow completes within 6-minute timeout

### Common Issues and Solutions

#### Issue: Migrations Take Too Long (> 60s)

**Solutions:**
1. Run migrations separately before deployment
2. Optimize migration operations (avoid data migrations in schema changes)
3. Consider rolling deployments with blue-green strategy

#### Issue: Static File Collection Slow (> 30s)

**Solutions:**
1. Use CDN for static files
2. Collect static files during image build (pre-bake)
3. Use shared volume between deployments

#### Issue: Database Connection Timeout

**Symptoms:**
```
STEP 2/5: Waiting for PostgreSQL
Database connection timeout after 60s
```

**Solutions:**
1. Check database container is healthy: `docker compose ps db`
2. Verify database credentials in `.env` files
3. Check network connectivity between containers
4. Review database logs: `docker compose logs db`

#### Issue: Health Check Returns 503

**Symptoms:**
```
curl http://127.0.0.1:8000/api/v1/health/
{"status":"unhealthy","database":{"status":"disconnected"}}
```

**Solutions:**
1. Check database connectivity from backend container
2. Verify Django can connect to PostgreSQL
3. Run: `docker compose exec backend python manage.py check_database`

### References

- Docker Compose Health Checks: https://docs.docker.com/compose/compose-file/05-services/#healthcheck
- Django Deployment Checklist: https://docs.djangoproject.com/en/stable/howto/deployment/checklist/
- 12-Factor App Methodology: https://12factor.net/

### Version History

- **2025-11-01**: Initial fix - Extended health check timings and added detailed logging
- **Future**: Plan to separate migrations from container startup

---

**Last Updated:** 2025-11-01
**Status:** ✅ Fixed - Monitoring for stability
