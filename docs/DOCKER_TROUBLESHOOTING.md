# Docker Setup Troubleshooting Guide

This guide documents common Docker setup issues and their permanent solutions.

## Quick Start - Pre-Flight Check

**Always run the pre-flight check before starting containers:**

```bash
# Run validation
./scripts/preflight-check.sh

# Run with auto-fix
./scripts/preflight-check.sh --fix

# Run with verbose output
./scripts/preflight-check.sh --verbose
```

This script validates:
- Docker and Docker Compose installation
- Required files and directories
- Entrypoint script permissions
- Log directory permissions
- Environment files
- Port availability
- Disk space
- docker-compose.yml syntax

## Common Issues and Solutions

### Issue 1: Missing Entrypoint Script

**Symptom:**
```
backend-1  | /bin/sh: /app/docker-entrypoint-dev.sh: not found
```

**Root Cause:**
The entrypoint script is maintained in the repository but was being overridden by the Dockerfile's inline creation. Volume mounts then override the container's version with the host filesystem.

**Permanent Solution:**
The entrypoint script is now maintained in the repository at:
```
backend/docker-entrypoint-dev.sh
```

The Dockerfile has been updated to:
1. Copy the script from the repository during build
2. Set correct permissions (executable, owned by django user)
3. NOT create the script inline (which would be overridden by volume mount)

**Verification:**
```bash
# Check script exists and is executable
ls -lah backend/docker-entrypoint-dev.sh
# Should show: -rwxrwxr-x (executable)

# Run pre-flight check
./scripts/preflight-check.sh
```

**Manual Fix (if needed):**
```bash
# Ensure script is executable
chmod +x backend/docker-entrypoint-dev.sh

# Or use auto-fix
./scripts/preflight-check.sh --fix
```

---

### Issue 2: Log File Permission Errors

**Symptom:**
```
PermissionError: [Errno 13] Permission denied: '/app/logs/general.log'
```

**Root Cause:**
- Backend container runs as `django` user (UID 1001)
- Log files created on host are owned by host user (typically UID 1000)
- Container cannot write to files it doesn't own

**Permanent Solution:**
The entrypoint script now fixes log file permissions on every container startup:

```bash
# From backend/docker-entrypoint-dev.sh (lines 6-21)
# Fix log file permissions
if [ -d "/app/logs" ]; then
    mkdir -p /app/logs
    find /app/logs -type f -name "*.log" -exec chmod 666 {} \; 2>/dev/null || true
    chmod 755 /app/logs 2>/dev/null || true
fi
```

This ensures:
- Log directory exists with correct permissions (755)
- All log files are world-writable (666) so container can write
- Works for both new and existing log files
- Runs automatically on every container start

**Verification:**
```bash
# Check log file permissions
ls -lah backend/logs/
# Should show: -rw-rw-rw- for .log files

# Check in running container
docker compose exec backend ls -lah /app/logs/
```

**Manual Fix (if needed):**
```bash
# Fix existing log files
chmod 666 backend/logs/*.log

# Or use auto-fix
./scripts/preflight-check.sh --fix

# Or restart container (entrypoint will fix automatically)
docker compose restart backend
```

**Why chmod 666?**
- The container user (UID 1001) needs write access
- The host user (UID 1000) needs read access for viewing logs
- World-writable (666) allows both users to access files
- Alternative: Use Docker volumes for logs (isolates from host filesystem)

---

### Issue 3: Healthcheck IPv6 Errors

**Symptom:**
```
curl: (7) Failed to connect to localhost port 8000 after 0 ms: Connection refused
```

Or healthcheck shows unhealthy even though service is running:
```bash
docker compose ps
# backend    unhealthy (even though curl http://127.0.0.1:8000/api/v1/health/ works)
```

**Root Cause:**
- `localhost` resolves to IPv6 (::1) first on many systems
- Django and Vite bind to `0.0.0.0` which is IPv4 only
- Healthcheck tries IPv6, fails, and marks service as unhealthy

**Permanent Solution:**
All healthchecks now use `127.0.0.1` instead of `localhost` to force IPv4:

```dockerfile
# Backend Dockerfile (development stage)
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD curl -f http://127.0.0.1:8000/api/v1/health/ || exit 1

# Backend Dockerfile (production stage)
HEALTHCHECK --interval=30s --timeout=3s --start-period=60s --retries=3 \
    CMD curl -f http://127.0.0.1:8000/api/v1/health/ || exit 1
```

```yaml
# docker-compose.yml (backend service)
healthcheck:
  test: ["CMD", "curl", "-f", "http://127.0.0.1:8000/api/v1/health/"]

# docker-compose.yml (frontend service)
healthcheck:
  test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://127.0.0.1:5173"]

# docker-compose.yml (proxy service)
healthcheck:
  test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://127.0.0.1/health"]
```

**Verification:**
```bash
# Check healthchecks are passing
docker compose ps
# All services should show "healthy"

# Test manually inside container
docker compose exec backend curl -f http://127.0.0.1:8000/api/v1/health/
# Should return: {"status": "healthy", ...}

# Check health from host
curl http://localhost:8000/api/v1/health/
# Should work (localhost is fine from outside container)
```

**Why This Matters:**
- Inside containers, services bind to `0.0.0.0` (all IPv4 interfaces)
- `localhost` can resolve to IPv6 `::1`, which nothing is listening on
- `127.0.0.1` explicitly forces IPv4, ensuring connection to the service
- From outside the container, both `localhost` and `127.0.0.1` work

---

## Validation and Testing

### Pre-Flight Validation

Before starting containers, always run:

```bash
# Basic validation
./scripts/preflight-check.sh

# With auto-fix enabled
./scripts/preflight-check.sh --fix

# With verbose output
./scripts/preflight-check.sh --verbose
```

The script checks:
1. ✓ Docker and Docker Compose installed
2. ✓ Docker daemon running
3. ✓ Required files exist (Dockerfiles, docker-compose.yml, etc.)
4. ✓ Entrypoint script exists and is executable
5. ✓ Log directory exists with correct permissions
6. ✓ Environment files exist (.env.docker)
7. ✓ Ports are available (80, 5432, 6379, 5173, 8000)
8. ✓ Sufficient disk space (>5GB recommended)
9. ✓ docker-compose.yml syntax is valid

### Starting Containers

```bash
# Option 1: Using docker-dev.sh helper script (recommended)
./docker-dev.sh start

# Option 2: Using docker compose directly
docker compose up -d

# View logs
./docker-dev.sh logs
# or
docker compose logs -f

# Check service status
./docker-dev.sh status
# or
docker compose ps
```

### Verifying Everything Works

```bash
# 1. Check all containers are healthy
docker compose ps
# All services should show "Up" and "healthy"

# 2. Test backend API
curl http://localhost/api/v1/health/
# Should return: {"status": "healthy", ...}

# 3. Test frontend
curl http://localhost/
# Should return HTML

# 4. Check logs for errors
docker compose logs backend | grep -i error
# Should be empty or show only expected errors

# 5. Verify log files are being written
ls -lah backend/logs/
# Should see *.log files with recent timestamps
```

### Troubleshooting Failed Startup

If containers fail to start:

```bash
# 1. Check logs for specific service
docker compose logs backend
docker compose logs frontend
docker compose logs db

# 2. Check container status
docker compose ps

# 3. Inspect unhealthy service
docker compose exec backend curl http://127.0.0.1:8000/api/v1/health/

# 4. Check dependencies
docker compose exec backend python manage.py check_database
docker compose exec backend python manage.py check_config

# 5. Rebuild if needed
./docker-dev.sh rebuild
```

## Architecture Decisions

### Why Entrypoint Script in Repository?

**Decision:** Maintain `docker-entrypoint-dev.sh` in repository, not inline in Dockerfile.

**Rationale:**
1. **Version Control:** Entrypoint script changes are tracked in git
2. **Volume Mount Compatibility:** Script is accessible via volume mount in development
3. **Maintainability:** Easier to edit than inline Dockerfile `RUN echo` commands
4. **Consistency:** Same pattern as production (different script, same approach)

**Trade-offs:**
- ✓ Pro: Easy to modify without rebuilding image
- ✓ Pro: Works with development volume mounts
- ✓ Pro: Better for complex startup logic
- ✗ Con: Must ensure script exists in repository (checked by pre-flight)

### Why Fix Log Permissions in Entrypoint?

**Decision:** Fix log file permissions in entrypoint script on every startup.

**Rationale:**
1. **Resilience:** Works even if host creates files with wrong permissions
2. **Developer Experience:** No manual permission fixing required
3. **Cross-platform:** Works on Linux, macOS, Windows (with WSL2)
4. **Startup Cost:** Minimal performance impact (runs once per start)

**Alternatives Considered:**
1. **Docker Volume for Logs** - Isolates logs from host, but harder to view/tail
2. **User Namespace Mapping** - Complex setup, not portable
3. **Host-side Scripts** - Requires manual execution, fragile
4. **Manual `chmod`** - Not permanent, forgotten easily

### Why 127.0.0.1 Instead of localhost?

**Decision:** Use `127.0.0.1` in all Docker healthchecks.

**Rationale:**
1. **IPv4 Explicit:** Forces IPv4 connection, no IPv6 ambiguity
2. **Service Binding:** Django/Vite bind to `0.0.0.0` (IPv4 only by default)
3. **Reliability:** Eliminates IPv6-related healthcheck failures
4. **Standard Practice:** Common pattern in Docker healthchecks

**Note:** From outside containers (host browser), both `localhost` and `127.0.0.1` work fine.

## Best Practices

### Before Every Start

1. **Run Pre-Flight Check:**
   ```bash
   ./scripts/preflight-check.sh --fix
   ```

2. **Check for Updates:**
   ```bash
   git pull
   docker compose pull  # Update base images
   ```

3. **Clean Up Old Resources (if issues):**
   ```bash
   ./docker-dev.sh clean
   docker system prune -f
   ```

### Development Workflow

1. **First Time Setup:**
   ```bash
   ./scripts/preflight-check.sh --fix
   ./docker-dev.sh start
   ```

2. **Daily Development:**
   ```bash
   # Start containers
   ./docker-dev.sh start

   # View logs
   ./docker-dev.sh logs

   # Run migrations
   ./docker-dev.sh backend-migrate

   # Access Django shell
   ./docker-dev.sh backend-shell
   ```

3. **After Dependency Changes:**
   ```bash
   # Rebuild containers
   ./docker-dev.sh rebuild
   ```

4. **Shutdown:**
   ```bash
   ./docker-dev.sh stop
   ```

### Monitoring Health

```bash
# Check all services
docker compose ps

# Continuous health monitoring
watch -n 2 'docker compose ps'

# Check specific service health
docker inspect app-backend --format='{{.State.Health.Status}}'

# View healthcheck logs
docker inspect app-backend --format='{{json .State.Health}}' | jq
```

## Additional Resources

- **Docker Compose Reference:** `/home/ed/Dev/architecture/docker-compose.yml`
- **Backend Dockerfile:** `/home/ed/Dev/architecture/backend/Dockerfile`
- **Frontend Dockerfile:** `/home/ed/Dev/architecture/frontend/Dockerfile`
- **Entrypoint Script:** `/home/ed/Dev/architecture/backend/docker-entrypoint-dev.sh`
- **Helper Script:** `/home/ed/Dev/architecture/docker-dev.sh`
- **Pre-flight Check:** `/home/ed/Dev/architecture/scripts/preflight-check.sh`

## Getting Help

If you encounter issues not covered here:

1. **Check logs:**
   ```bash
   ./docker-dev.sh logs [service-name]
   ```

2. **Run validation:**
   ```bash
   ./scripts/preflight-check.sh --verbose
   ```

3. **Clean restart:**
   ```bash
   ./docker-dev.sh stop
   ./docker-dev.sh clean
   ./docker-dev.sh start
   ```

4. **Check GitHub issues:**
   Search for similar problems in repository issues

5. **Create detailed issue:**
   Include logs, `docker compose ps` output, and system info
