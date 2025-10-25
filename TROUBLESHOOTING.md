# Troubleshooting Guide

This guide provides solutions to common problems you may encounter when working with the unified multi-service orchestration setup.

## Table of Contents

- [Quick Diagnostics](#quick-diagnostics)
- [Service Startup Issues](#service-startup-issues)
- [Network and Connectivity](#network-and-connectivity)
- [Database Problems](#database-problems)
- [Redis Issues](#redis-issues)
- [Frontend Issues](#frontend-issues)
- [Backend Issues](#backend-issues)
- [Reverse Proxy Issues](#reverse-proxy-issues)
- [Performance Problems](#performance-problems)
- [Data and Volume Issues](#data-and-volume-issues)
- [Environment-Specific Issues](#environment-specific-issues)
- [Docker and System Issues](#docker-and-system-issues)

---

## Quick Diagnostics

**When something goes wrong, start here:**

```bash
# 1. Check service status
./docker-dev.sh status

# 2. View logs for all services
./docker-dev.sh logs

# 3. Validate orchestration
./scripts/validate-orchestration.sh

# 4. Check health of all services
./scripts/validate-health-checks.sh
```

**Most common fix**: Rebuild and restart
```bash
./docker-dev.sh rebuild
./docker-dev.sh start
```

---

## Service Startup Issues

### Problem: Services Won't Start

**Symptoms**: Services fail to start or immediately exit

**Diagnosis**:
```bash
# Check what failed
docker compose ps

# View detailed logs
./docker-dev.sh logs <service-name>

# Check for port conflicts
sudo netstat -tlnp | grep -E ":(80|8000|5173|5432|6379)"
```

**Solutions**:

1. **Port Conflicts**:
   ```bash
   # Stop conflicting services
   sudo systemctl stop nginx    # If nginx is running on host
   sudo systemctl stop apache2  # If apache is running on host

   # Or change ports in .env file
   export PROXY_PORT=8080
   export BACKEND_PORT=8001
   export FRONTEND_PORT=5174
   ./docker-dev.sh start
   ```

2. **Insufficient Resources**:
   ```bash
   # Check available resources
   docker system df

   # Clean up unused resources
   docker system prune -a --volumes

   # Increase Docker Desktop resources
   # Docker Desktop → Settings → Resources
   # Set Memory: 8GB, CPUs: 4
   ```

3. **Configuration Errors**:
   ```bash
   # Validate Docker Compose configuration
   docker compose config --quiet

   # If errors found, check for:
   # - Invalid YAML syntax
   # - Missing environment variables
   # - Incorrect file paths
   ```

### Problem: Service Stuck in "Starting" State

**Symptoms**: Service shows as "starting" and never becomes healthy

**Diagnosis**:
```bash
# Check health check logs
docker inspect --format='{{json .State.Health}}' app-<service-name> | jq

# View service logs
./docker-dev.sh logs <service-name>

# Check dependencies
./scripts/check-dependencies.sh
```

**Solutions**:

1. **Health Check Timeout Too Short**:
   - Edit `docker-compose.yml`
   - Increase `start_period` for the service
   - Increase `timeout` value

2. **Dependencies Not Ready**:
   ```bash
   # Check dependency health
   docker compose ps

   # Restart in correct order
   ./docker-dev.sh stop
   ./docker-dev.sh start
   ```

3. **Application Startup Failure**:
   ```bash
   # View full startup logs
   docker compose logs <service-name> | head -100

   # Common issues:
   # - Missing dependencies
   # - Configuration errors
   # - Database connection failures
   ```

### Problem: Service Exits Immediately After Starting

**Symptoms**: Container starts then stops with exit code 0 or 1

**Diagnosis**:
```bash
# View exit reason
docker compose ps

# View full logs including exit
docker compose logs <service-name> --tail=100

# Check last container state
docker inspect app-<service-name> | grep -A 20 "State"
```

**Solutions**:

1. **Missing Entry Point**:
   - Check `Dockerfile` has correct `CMD` or `ENTRYPOINT`
   - Verify entry point script is executable

2. **Configuration Error**:
   ```bash
   # Check environment variables
   docker compose config | grep -A 20 "<service-name>"

   # Validate .env files
   cat .env.local    # or .env.staging, .env.production
   ```

3. **Application Crash**:
   ```bash
   # Run service in debug mode
   docker compose run --rm <service-name> /bin/bash

   # Try starting application manually
   # For backend:
   python manage.py runserver 0.0.0.0:8000

   # For frontend:
   npm run dev
   ```

---

## Network and Connectivity

### Problem: Can't Access Application at http://localhost/

**Symptoms**: Browser shows "Connection refused" or "Can't reach this page"

**Diagnosis**:
```bash
# Check proxy is running
docker compose ps proxy

# Test proxy health endpoint
curl http://localhost/health

# Check port binding
docker port app-proxy
```

**Solutions**:

1. **Proxy Not Running**:
   ```bash
   # Start proxy
   docker compose up -d proxy

   # Check proxy logs
   docker compose logs proxy
   ```

2. **Port Not Exposed**:
   ```bash
   # Check port mapping
   docker compose ps proxy

   # Should show: 0.0.0.0:80->80/tcp

   # If not, check docker-compose.yml
   # ports section for proxy service
   ```

3. **Firewall Blocking Connection**:
   ```bash
   # Check firewall (Linux)
   sudo ufw status
   sudo ufw allow 80/tcp

   # Check firewall (macOS)
   sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate
   ```

### Problem: Frontend Can't Reach Backend API

**Symptoms**: Frontend shows "Network Error" or API calls fail

**Diagnosis**:
```bash
# Check backend health
curl http://localhost/api/v1/health/

# Check CORS configuration
docker compose exec backend python manage.py shell
>>> from django.conf import settings
>>> print(settings.CORS_ALLOWED_ORIGINS)

# Check proxy routing
docker compose logs proxy | grep -i error
```

**Solutions**:

1. **Backend Not Healthy**:
   ```bash
   # Check backend status
   docker compose ps backend

   # View backend logs
   ./docker-dev.sh logs backend

   # Restart backend
   docker compose restart backend
   ```

2. **CORS Configuration Issue**:
   ```bash
   # Check backend environment variables
   docker compose exec backend env | grep CORS

   # Should include:
   # CORS_ALLOWED_ORIGINS=http://localhost,http://localhost:5173

   # Update backend/.env.docker if needed
   ```

3. **Proxy Routing Misconfigured**:
   ```bash
   # Test backend directly (if port exposed)
   curl http://localhost:8000/api/v1/health/

   # Test through proxy
   curl http://localhost/api/v1/health/

   # Compare responses
   ```

### Problem: WebSocket Connection Failed (Frontend HMR)

**Symptoms**: Hot Module Replacement not working, console shows WebSocket errors

**Diagnosis**:
```bash
# Check frontend logs
docker compose logs frontend | grep -i websocket

# Check browser console for WebSocket errors
# Should show: [vite] connected.

# Check nginx WebSocket configuration
docker compose exec proxy cat /etc/nginx/nginx.conf | grep -A 5 "location /ws"
```

**Solutions**:

1. **WebSocket Not Proxied Correctly**:
   - Check `nginx/nginx.conf` has WebSocket upgrade headers
   - Restart proxy: `docker compose restart proxy`

2. **Frontend Not Accessible**:
   ```bash
   # Test frontend directly
   curl http://localhost:5173

   # Restart frontend
   docker compose restart frontend
   ```

---

## Database Problems

### Problem: Database Connection Refused

**Symptoms**: Backend can't connect to database, errors in logs

**Diagnosis**:
```bash
# Check database is running
docker compose ps db

# Test database connectivity
docker compose exec db pg_isready -U postgres

# Check database logs
docker compose logs db | tail -50

# Check backend can reach database
docker compose exec backend python manage.py check_database
```

**Solutions**:

1. **Database Not Ready**:
   ```bash
   # Wait for database to be healthy
   docker compose ps db

   # Should show: healthy

   # If starting, wait 10-15 seconds
   ```

2. **Wrong Database Credentials**:
   ```bash
   # Check environment variables
   docker compose exec backend env | grep DB_

   # Should show:
   # DB_HOST=db
   # DB_PORT=5432
   # DB_NAME=backend_db
   # DB_USER=postgres
   # DB_PASSWORD=postgres

   # Update backend/.env.docker if incorrect
   ```

3. **Database Not Initialized**:
   ```bash
   # Check database exists
   docker compose exec db psql -U postgres -c "\l"

   # Should list backend_db

   # If missing, recreate database
   ./docker-dev.sh clean
   ./docker-dev.sh start
   ```

### Problem: Database Migration Failures

**Symptoms**: Migrations fail with errors

**Diagnosis**:
```bash
# Check migration status
docker compose exec backend python manage.py showmigrations

# Try running migrations with verbose output
docker compose exec backend python manage.py migrate --verbosity 3
```

**Solutions**:

1. **Migration Conflicts**:
   ```bash
   # Check for conflicting migrations
   docker compose exec backend python manage.py showmigrations | grep "\[ \]"

   # Resolve conflicts by creating merge migration
   docker compose exec backend python manage.py makemigrations --merge
   ```

2. **Database Schema Out of Sync**:
   ```bash
   # Backup data first!
   ./docker-dev.sh backup-db

   # Drop and recreate database (DESTRUCTIVE)
   docker compose down
   docker volume rm app-postgres-data
   ./docker-dev.sh start
   ./docker-dev.sh backend-migrate
   ```

3. **Permission Issues**:
   ```bash
   # Check database user permissions
   docker compose exec db psql -U postgres -d backend_db

   # Grant permissions
   GRANT ALL PRIVILEGES ON DATABASE backend_db TO postgres;
   GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
   ```

### Problem: Database Data Lost After Restart

**Symptoms**: Data disappears when containers restart

**Diagnosis**:
```bash
# Check volumes exist
docker volume ls | grep postgres

# Check volume mount
docker inspect app-db | grep -A 10 "Mounts"
```

**Solutions**:

1. **Volume Not Mounted**:
   - Check `docker-compose.yml` has volume definition for `db` service
   - Ensure volume is listed in `volumes:` section at bottom

2. **Volume Was Deleted**:
   ```bash
   # Don't use: docker compose down -v (deletes volumes!)

   # Correct usage:
   docker compose down           # Stops but preserves volumes
   docker compose stop           # Stops without removing containers
   ```

3. **Data in Wrong Location**:
   ```bash
   # Check where database stores data
   docker compose exec db psql -U postgres -c "SHOW data_directory;"

   # Should be: /var/lib/postgresql/data
   ```

---

## Redis Issues

### Problem: Redis Connection Refused

**Symptoms**: Backend can't connect to Redis

**Diagnosis**:
```bash
# Check Redis is running
docker compose ps redis

# Test Redis connectivity
docker compose exec redis redis-cli ping

# Should return: PONG

# Check backend can reach Redis
docker compose exec backend python -c "import redis; r = redis.from_url('redis://redis:6379/1'); print(r.ping())"
```

**Solutions**:

1. **Redis Not Ready**:
   ```bash
   # Wait for Redis to be healthy
   docker compose ps redis

   # Restart if needed
   docker compose restart redis
   ```

2. **Wrong Redis URL**:
   ```bash
   # Check environment variable
   docker compose exec backend env | grep REDIS_URL

   # Should be: redis://redis:6379/1

   # Update backend/.env.docker if incorrect
   ```

3. **Redis Password Required (Production)**:
   ```bash
   # Check if Redis requires password
   docker compose exec redis redis-cli ping

   # If returns: NOAUTH Authentication required
   # Update REDIS_URL to include password:
   # redis://:password@redis:6379/1
   ```

### Problem: Redis Memory Issues

**Symptoms**: Redis crashes or evicts data unexpectedly

**Diagnosis**:
```bash
# Check Redis memory usage
docker compose exec redis redis-cli INFO memory

# Check maxmemory setting
docker compose exec redis redis-cli CONFIG GET maxmemory
```

**Solutions**:

1. **Memory Limit Too Low**:
   - Edit `docker-compose.yml`
   - Increase `maxmemory` in Redis command
   - Default is 256MB, increase to 512MB or 1GB

2. **Memory Policy Wrong**:
   ```bash
   # Check eviction policy
   docker compose exec redis redis-cli CONFIG GET maxmemory-policy

   # Should be: allkeys-lru (evicts least recently used keys)
   ```

---

## Frontend Issues

### Problem: Frontend Shows White Screen

**Symptoms**: Browser shows blank page, no content

**Diagnosis**:
```bash
# Check browser console for errors (F12)

# Check frontend logs
docker compose logs frontend | tail -50

# Check frontend is serving content
curl http://localhost:5173
```

**Solutions**:

1. **Frontend Build Failed**:
   ```bash
   # Rebuild frontend
   ./docker-dev.sh rebuild frontend
   ./docker-dev.sh start

   # Check build output for errors
   docker compose logs frontend | grep -i error
   ```

2. **JavaScript Error**:
   - Check browser console (F12) for JavaScript errors
   - Check recent code changes
   - Rollback recent changes if needed

3. **API Not Responding**:
   ```bash
   # Check frontend can reach backend
   curl http://localhost/api/v1/health/

   # Check browser Network tab (F12) for failed API calls
   ```

### Problem: Hot Module Replacement Not Working

**Symptoms**: Changes to frontend code don't reload browser automatically

**Diagnosis**:
```bash
# Check browser console for HMR messages
# Should show: [vite] connected.

# Check frontend logs for file watching
docker compose logs frontend | grep -i "file change detected"

# Check WebSocket connection
# Browser DevTools → Network → WS tab
```

**Solutions**:

1. **File Watching Not Working**:
   - Check `vite.config.ts` has polling enabled
   - Restart frontend: `docker compose restart frontend`

2. **WebSocket Not Connected**:
   ```bash
   # Check WebSocket proxy configuration
   docker compose exec proxy cat /etc/nginx/nginx.conf | grep -A 5 "/ws"

   # Restart proxy
   docker compose restart proxy
   ```

3. **Volume Mount Issue**:
   ```bash
   # Check source code is mounted
   docker compose exec frontend ls -la /app/src

   # Should show your source files

   # If empty, check docker-compose.yml volumes section
   ```

### Problem: npm Install Fails

**Symptoms**: Can't install npm packages

**Diagnosis**:
```bash
# Check npm logs
docker compose exec frontend npm install --loglevel verbose

# Check disk space
docker exec app-frontend df -h

# Check network connectivity
docker compose exec frontend ping -c 3 registry.npmjs.org
```

**Solutions**:

1. **Network Issues**:
   ```bash
   # Try again with proxy (if behind corporate firewall)
   docker compose exec frontend npm config set proxy http://proxy.company.com:8080
   docker compose exec frontend npm install
   ```

2. **Corrupted node_modules**:
   ```bash
   # Remove and rebuild node_modules
   docker compose down
   docker volume rm app-frontend-node-modules
   ./docker-dev.sh rebuild frontend
   ./docker-dev.sh start
   ```

3. **Insufficient Disk Space**:
   ```bash
   # Clean up Docker resources
   docker system prune -a --volumes

   # Increase Docker Desktop disk space
   # Docker Desktop → Settings → Resources → Disk image size
   ```

---

## Backend Issues

### Problem: Backend 500 Internal Server Error

**Symptoms**: API requests return 500 errors

**Diagnosis**:
```bash
# Check backend logs
docker compose logs backend | tail -100

# Check Django debug mode
docker compose exec backend python manage.py shell
>>> from django.conf import settings
>>> print(settings.DEBUG)

# Test backend health endpoint
curl http://localhost/api/v1/health/
```

**Solutions**:

1. **Check Recent Code Changes**:
   - Review recent commits: `git log --oneline -10`
   - Check for syntax errors in Python code
   - Rollback if needed: `git revert <commit>`

2. **Database Connection Issues**:
   ```bash
   # Test database connection
   docker compose exec backend python manage.py check_database

   # Check migrations
   docker compose exec backend python manage.py showmigrations
   ```

3. **Missing Environment Variables**:
   ```bash
   # Check all required variables are set
   docker compose exec backend python manage.py check

   # Review backend/.env.docker
   ```

### Problem: Django Auto-Reload Not Working

**Symptoms**: Backend code changes don't take effect

**Diagnosis**:
```bash
# Check if watchdog is installed
docker compose exec backend pip list | grep watchdog

# Check source code is mounted
docker compose exec backend ls -la /app

# Check logs for reload messages
docker compose logs backend | grep -i "reload"
```

**Solutions**:

1. **Source Code Not Mounted**:
   - Check `docker-compose.yml` has backend volume mount
   - Should have: `./backend:/app`
   - Restart services: `./docker-dev.sh restart`

2. **Watchdog Not Installed**:
   ```bash
   # Install watchdog
   docker compose exec backend pip install watchdog

   # Restart backend
   docker compose restart backend
   ```

3. **Python Bytecode Caching**:
   ```bash
   # Clear Python cache
   docker compose exec backend find /app -type d -name __pycache__ -exec rm -rf {} +
   docker compose exec backend find /app -type f -name "*.pyc" -delete

   # Restart backend
   docker compose restart backend
   ```

### Problem: pip Install Fails

**Symptoms**: Can't install Python packages

**Diagnosis**:
```bash
# Check pip logs
docker compose exec backend pip install <package> --verbose

# Check disk space
docker exec app-backend df -h

# Check network connectivity
docker compose exec backend ping -c 3 pypi.org
```

**Solutions**:

1. **Permission Issues**:
   ```bash
   # Install as non-root user
   docker compose exec backend pip install --user <package>

   # Or rebuild container with package in requirements
   echo "<package>==<version>" >> backend/requirements/dev.txt
   ./docker-dev.sh rebuild backend
   ```

2. **Incompatible Dependencies**:
   ```bash
   # Check for conflicts
   docker compose exec backend pip check

   # Install specific version
   docker compose exec backend pip install "<package>==<version>"
   ```

---

## Reverse Proxy Issues

### Problem: 502 Bad Gateway

**Symptoms**: Nginx returns 502 Bad Gateway error

**Diagnosis**:
```bash
# Check backend and frontend are running
docker compose ps backend frontend

# Check proxy logs
docker compose logs proxy | grep -i error

# Test upstream services
curl http://localhost:8000/api/v1/health/   # Backend (if port exposed)
curl http://localhost:5173                   # Frontend (if port exposed)
```

**Solutions**:

1. **Upstream Service Down**:
   ```bash
   # Check which service is down
   ./docker-dev.sh status

   # Restart failed service
   docker compose restart <service-name>
   ```

2. **Upstream Service Not Ready**:
   ```bash
   # Wait for services to be healthy
   docker compose ps

   # All should show: healthy

   # If starting, wait 1-2 minutes
   ```

3. **Proxy Can't Reach Upstream**:
   ```bash
   # Check network connectivity
   docker compose exec proxy ping -c 3 backend
   docker compose exec proxy ping -c 3 frontend

   # Check DNS resolution
   docker compose exec proxy nslookup backend
   docker compose exec proxy nslookup frontend
   ```

### Problem: 404 Not Found for API Endpoints

**Symptoms**: API requests return 404

**Diagnosis**:
```bash
# Check nginx configuration
docker compose exec proxy cat /etc/nginx/nginx.conf | grep -A 10 "location /api"

# Test backend directly
curl http://localhost:8000/api/v1/health/

# Check proxy access logs
docker compose exec proxy tail -f /var/log/nginx/access.log
```

**Solutions**:

1. **Incorrect Proxy Configuration**:
   - Check `nginx/nginx.conf` has correct location blocks
   - Verify `proxy_pass` directives point to correct services
   - Restart proxy: `docker compose restart proxy`

2. **Backend URL Wrong**:
   ```bash
   # Test different URL patterns
   curl -v http://localhost/api/v1/health/
   curl -v http://localhost/api/

   # Check which returns data
   ```

---

## Performance Problems

### Problem: Application Slow to Start

**Symptoms**: Services take a long time to become healthy

**Diagnosis**:
```bash
# Monitor startup process
./docker-dev.sh start
./docker-dev.sh status

# Check resource usage
docker stats
```

**Solutions**:

1. **Insufficient Resources**:
   - Increase Docker Desktop resources
   - Docker Desktop → Settings → Resources
   - Set: Memory 8GB, CPUs 4+

2. **Slow Image Pulls**:
   ```bash
   # Use pre-built images if available
   docker compose pull

   # Or build locally once
   ./docker-dev.sh rebuild
   ```

3. **Slow Health Checks**:
   - Edit `docker-compose.yml`
   - Increase `start_period` for services
   - This gives services more time to initialize

### Problem: Frontend Build Very Slow

**Symptoms**: Frontend takes minutes to build/rebuild

**Diagnosis**:
```bash
# Check build time
time docker compose build frontend

# Check disk I/O
docker stats app-frontend
```

**Solutions**:

1. **Use Volume for node_modules**:
   - Already configured in `docker-compose.yml`
   - Ensure volume mount is working: `docker volume ls | grep node_modules`

2. **Enable BuildKit Cache**:
   ```bash
   # Set environment variable
   export DOCKER_BUILDKIT=1
   export COMPOSE_DOCKER_CLI_BUILD=1

   # Rebuild
   ./docker-dev.sh rebuild frontend
   ```

### Problem: Backend Response Time Slow

**Symptoms**: API requests take several seconds

**Diagnosis**:
```bash
# Time a request
time curl http://localhost/api/v1/health/

# Check backend CPU/memory usage
docker stats app-backend

# Check database queries (if slow query logging enabled)
docker compose logs backend | grep "slow query"
```

**Solutions**:

1. **Database Query Optimization**:
   ```bash
   # Enable query logging
   docker compose exec backend python manage.py shell
   >>> from django.db import connection
   >>> connection.queries  # View executed queries

   # Add database indexes if needed
   ```

2. **Increase Backend Resources**:
   - Edit `docker-compose.yml`
   - Increase backend resource limits (CPU, memory)
   - Restart: `./docker-dev.sh restart`

3. **Enable Redis Caching**:
   - Verify Redis is running: `docker compose ps redis`
   - Check cache is configured in Django settings
   - Clear cache if stale: `docker compose exec redis redis-cli FLUSHALL`

---

## Data and Volume Issues

### Problem: Can't Remove Volume (Volume in Use)

**Symptoms**: `docker volume rm` fails with "volume in use" error

**Diagnosis**:
```bash
# Check which containers use volume
docker ps -a --filter volume=<volume-name>

# Check volume details
docker volume inspect <volume-name>
```

**Solutions**:

```bash
# Stop all containers using volume
docker compose down

# Verify no containers running
docker ps -a

# Remove volume
docker volume rm <volume-name>

# Or remove all unused volumes
docker volume prune
```

### Problem: Volume Data Corrupted

**Symptoms**: Services fail with data corruption errors

**Diagnosis**:
```bash
# Check volume exists
docker volume ls | grep app-

# Inspect volume
docker volume inspect <volume-name>

# Check container logs for corruption messages
docker compose logs db | grep -i corrupt
```

**Solutions**:

```bash
# Backup data first!
./docker-dev.sh backup

# Remove corrupted volume (DESTRUCTIVE)
docker compose down
docker volume rm <volume-name>

# Restart (creates new empty volume)
./docker-dev.sh start

# Restore from backup if available
```

---

## Environment-Specific Issues

### Problem: Environment File Not Found

**Symptoms**: Error loading environment file

**Diagnosis**:
```bash
# Check file exists
ls -la .env.*

# Validate file has no CHANGE_ME placeholders (staging/production)
grep -n "CHANGE_ME" .env.staging
grep -n "CHANGE_ME" .env.production
```

**Solutions**:

```bash
# Create from example
cp .env.staging.example .env.staging

# Edit and replace CHANGE_ME values
nano .env.staging

# Validate
./docker-env.sh staging validate
```

### Problem: Production Images Not Found

**Symptoms**: Can't pull production images from registry

**Diagnosis**:
```bash
# Check image exists in registry
docker pull ghcr.io/<org>/<image>:latest

# Check authentication
docker login ghcr.io
```

**Solutions**:

```bash
# Authenticate to GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Pull images
./docker-env.sh production pull

# Or build locally
docker compose -f docker-compose.yml -f compose.production.yml build
```

---

## Docker and System Issues

### Problem: Docker Daemon Not Running

**Symptoms**: "Cannot connect to Docker daemon" error

**Solutions**:

```bash
# Linux: Start Docker
sudo systemctl start docker
sudo systemctl enable docker

# macOS: Start Docker Desktop
open -a Docker

# Windows: Start Docker Desktop
# Start menu → Docker Desktop
```

### Problem: Disk Space Issues

**Symptoms**: "No space left on device" errors

**Diagnosis**:
```bash
# Check disk usage
docker system df

# Check host disk space
df -h
```

**Solutions**:

```bash
# Clean up Docker resources
docker system prune -a --volumes

# Remove old images
docker image prune -a

# Remove unused volumes
docker volume prune

# Remove build cache
docker builder prune
```

### Problem: Permission Denied Errors

**Symptoms**: Permission errors when running Docker commands

**Solutions**:

```bash
# Linux: Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Or run with sudo
sudo docker compose up

# macOS/Windows: Usually not needed (Docker Desktop handles this)
```

---

## Advanced Troubleshooting

### Debugging Containers

```bash
# Start container with shell (override entrypoint)
docker compose run --rm --entrypoint /bin/bash backend

# Execute commands inside running container
docker compose exec backend /bin/bash

# View container details
docker inspect app-backend

# View container processes
docker compose top backend
```

### Network Debugging

```bash
# Check Docker networks
docker network ls

# Inspect network
docker network inspect architecture_app-network

# Test connectivity between containers
docker compose exec backend ping -c 3 db
docker compose exec frontend ping -c 3 backend
```

### Log Debugging

```bash
# View logs with timestamps
docker compose logs -t backend

# View logs since specific time
docker compose logs --since 2025-10-25T10:00:00 backend

# View logs until specific time
docker compose logs --until 2025-10-25T11:00:00 backend

# Follow logs from multiple services
docker compose logs -f backend frontend proxy
```

---

## Getting Additional Help

### Collecting Diagnostic Information

When asking for help, include:

```bash
# 1. Service status
./docker-dev.sh status

# 2. Recent logs
./docker-dev.sh logs | tail -500 > logs-output.txt

# 3. Docker info
docker --version
docker compose version
docker system df

# 4. Environment
uname -a
cat .env.local  # Redact sensitive information!

# 5. Validation results
./scripts/validate-orchestration.sh
```

### Where to Get Help

1. **Documentation**: Check relevant docs in `docs/features/12/`
2. **GitHub Issues**: Search for similar issues or create new one
3. **Logs**: Always check service logs first
4. **Validation**: Run `./scripts/validate-orchestration.sh`
5. **Community**: Reach out on project communication channels

---

## Quick Reference: Most Common Fixes

```bash
# 1. Nothing works - full rebuild
./docker-dev.sh clean
./docker-dev.sh rebuild
./docker-dev.sh start

# 2. Port conflict
export PROXY_PORT=8080
./docker-dev.sh start

# 3. Service won't start
./docker-dev.sh logs <service>
./docker-dev.sh rebuild <service>

# 4. Database issues
./docker-dev.sh backup-db
docker compose down
docker volume rm app-postgres-data
./docker-dev.sh start

# 5. Out of disk space
docker system prune -a --volumes

# 6. Permission errors (Linux)
sudo usermod -aG docker $USER
newgrp docker

# 7. Slow performance
# Increase Docker Desktop resources
# Settings → Resources → Memory: 8GB, CPUs: 4

# 8. Can't access application
curl http://localhost/health
./docker-dev.sh status
docker compose restart proxy
```

---

**Remember**: When in doubt, check the logs first!

```bash
./docker-dev.sh logs
```

Most issues can be resolved by reviewing service logs and following the diagnostic steps in this guide.
