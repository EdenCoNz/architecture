# Backend Production Container Deployment Guide

**Last Updated**: 2025-10-24
**Story**: Feature #8.4 - Backend Production Container

This guide covers deploying the backend application in production using Docker containers with optimized configurations, security best practices, and proper production server setup.

---

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Prerequisites](#prerequisites)
- [Production Architecture](#production-architecture)
- [Configuration](#configuration)
- [Container Build](#container-build)
- [Deployment](#deployment)
- [Production Checklist](#production-checklist)
- [Monitoring & Logs](#monitoring--logs)
- [Security Considerations](#security-considerations)
- [Performance Optimization](#performance-optimization)
- [Troubleshooting](#troubleshooting)
- [Maintenance](#maintenance)

---

## Overview

The production container setup provides:

- **Minimal Image Size**: Multi-stage build excludes dev tools (200MB vs 400MB+ dev)
- **Production Server**: Gunicorn WSGI server with 4 workers
- **Security Hardened**: Non-root user, no debug mode, HTTPS enforcement
- **Structured Logging**: JSON-formatted logs for aggregation
- **Auto-Migration**: Database migrations applied automatically on startup
- **Health Checks**: Built-in health monitoring for container orchestration
- **Resource Limits**: CPU and memory constraints prevent resource exhaustion
- **Persistent Storage**: Separate volumes for database, cache, media, and static files

---

## Quick Start

```bash
# 1. Copy production environment template
cd backend
cp .env.production.example .env.production

# 2. Edit .env.production with your production values
nano .env.production

# 3. Build and start production containers
docker compose -f docker-compose.production.yml up --build -d

# 4. Check logs
docker compose -f docker-compose.production.yml logs -f backend

# 5. Verify health status
curl http://localhost:8000/api/v1/health/
```

---

## Prerequisites

### System Requirements

- **Docker Engine**: 23.0+ (with BuildKit enabled)
- **Docker Compose**: 2.20+
- **Server Resources**:
  - Minimum: 2 CPU cores, 4GB RAM, 20GB disk
  - Recommended: 4 CPU cores, 8GB RAM, 50GB disk
- **Operating System**: Linux (Ubuntu 22.04 LTS, Debian 12, or similar)

### Network Requirements

- **Port 8000**: Backend application (should be behind reverse proxy)
- **HTTPS**: SSL/TLS certificates (handled by reverse proxy)
- **DNS**: Domain name configured and pointing to server

### External Services

- **Database**: PostgreSQL 15+ (included in compose or external)
- **Cache**: Redis 7+ (included in compose or external)
- **Reverse Proxy**: Nginx, Traefik, or Caddy (for HTTPS termination)
- **Email**: SMTP server for notifications
- **Monitoring**: Sentry (recommended for error tracking)

---

## Production Architecture

### Container Structure

```
┌─────────────────────────────────────────────────────┐
│                  Reverse Proxy                      │
│            (Nginx/Traefik/Caddy)                    │
│         HTTPS Termination, Load Balancing           │
└─────────────────────────────────────────────────────┘
                       │ HTTP
                       ▼
┌─────────────────────────────────────────────────────┐
│              Backend Container (Gunicorn)            │
│  - Python 3.12-slim                                 │
│  - Non-root user (django:1001)                      │
│  - 4 Gunicorn workers                               │
│  - Health checks enabled                            │
│  - Resource limits: 4 CPU, 2GB RAM                  │
└─────────────────────────────────────────────────────┘
              │                        │
              │ PostgreSQL             │ Redis
              ▼                        ▼
┌───────────────────────┐    ┌──────────────────────┐
│  Database Container   │    │   Cache Container    │
│  - PostgreSQL 15      │    │   - Redis 7          │
│  - Persistent volume  │    │   - Password auth    │
│  - Health checks      │    │   - Persistent AOF   │
│  - 2 CPU, 2GB RAM     │    │   - 1 CPU, 512MB RAM │
└───────────────────────┘    └──────────────────────┘
```

### Dockerfile Stages

The Dockerfile uses multi-stage builds for optimization:

1. **Base Stage**: Common dependencies (Python 3.12-slim, PostgreSQL client, build tools)
2. **Builder Stage**: Installs production Python packages to `/root/.local`
3. **Production Stage**: Minimal runtime with only necessary files and dependencies

**Development vs Production**:

| Aspect | Development | Production |
|--------|-------------|------------|
| Base Image | python:3.12-slim + build tools | python:3.12-slim (minimal) |
| Dependencies | base.txt + dev.txt (pytest, black, mypy) | base.txt + prod.txt (gunicorn, sentry) |
| Server | Django runserver (hot reload) | Gunicorn WSGI (4 workers) |
| Image Size | ~400MB | ~200MB |
| User | django (non-root) | django (non-root) |
| Logging | Console (verbose) | JSON (structured) |
| Security | Relaxed | Hardened (HTTPS, HSTS, etc.) |
| Code Mount | Volume (live editing) | Copied (immutable) |

---

## Configuration

### Environment Variables

Create `.env.production` from template:

```bash
cp .env.production.example .env.production
```

**Critical Settings**:

```bash
# MUST be changed for security
SECRET_KEY=<generate-with-secrets.token_urlsafe(50)>
DB_PASSWORD=<strong-database-password>
REDIS_PASSWORD=<strong-redis-password>

# MUST match your domain
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,api.yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Production values
DEBUG=False
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

**Generate Secure Keys**:

```bash
# SECRET_KEY (50+ characters)
python -c "import secrets; print(secrets.token_urlsafe(50))"

# Database/Redis passwords (32 bytes base64)
openssl rand -base64 32
```

### Django Settings

The production container uses `config.settings.production` which includes:

- `DEBUG = False` (enforced)
- HTTPS enforcement (HSTS, secure cookies)
- Strict CORS and CSRF policies
- Production logging (JSON format)
- WhiteNoise for static files
- Database connection pooling
- Enhanced security headers

### Gunicorn Configuration

Configured via environment variables:

```bash
# Number of worker processes (formula: 2-4 x num_cores)
GUNICORN_WORKERS=4

# Request timeout (30s default)
GUNICORN_TIMEOUT=30

# Worker restart after N requests (memory leak protection)
GUNICORN_MAX_REQUESTS=1000
GUNICORN_MAX_REQUESTS_JITTER=100
```

**Worker Calculation**:
- 1 CPU core: 2-4 workers
- 2 CPU cores: 4-8 workers
- 4 CPU cores: 8-16 workers

---

## Container Build

### Building Production Image

```bash
# Build production image with BuildKit cache
docker buildx build \
  --target production \
  --tag backend-prod:latest \
  --tag backend-prod:$(git rev-parse --short HEAD) \
  --cache-from backend-prod:latest \
  --cache-to type=inline \
  .

# Inspect image size
docker images backend-prod:latest

# Scan for vulnerabilities (recommended)
docker scout cves backend-prod:latest
# OR
trivy image backend-prod:latest
```

### Multi-Stage Build Details

```dockerfile
# Stage 1: Base (common dependencies)
FROM python:3.12-slim AS base
# Install system packages: postgresql-client, libpq-dev, gcc, curl

# Stage 2: Builder (install Python packages)
FROM base AS builder
COPY requirements/base.txt requirements/prod.txt
RUN pip install --user -r requirements/prod.txt
# Packages installed to /root/.local

# Stage 3: Production (minimal runtime)
FROM python:3.12-slim AS production
# Copy only Python packages from builder
COPY --from=builder /root/.local /home/django/.local
# Copy application code
# Run as non-root user (django:1001)
# Entrypoint handles migrations, collectstatic, health checks
# Default command: gunicorn with 4 workers
```

**Size Optimization**:
- No development tools (pytest, black, mypy, etc.)
- No build dependencies (gcc, g++, make)
- No source control files (.git, .github)
- No test files or documentation
- Slim Python base (122MB vs 1GB+ full Python)

---

## Deployment

### First-Time Deployment

```bash
# 1. Clone repository on server
git clone https://github.com/yourorg/yourrepo.git
cd yourrepo/backend

# 2. Configure environment
cp .env.production.example .env.production
nano .env.production  # Fill in all values

# 3. Build and start services
docker compose -f docker-compose.production.yml up --build -d

# 4. Wait for services to be healthy
docker compose -f docker-compose.production.yml ps

# 5. Verify application is running
curl http://localhost:8000/api/v1/health/

# 6. Check logs for any issues
docker compose -f docker-compose.production.yml logs -f

# 7. Create superuser (optional)
docker compose -f docker-compose.production.yml exec backend \
  python manage.py createsuperuser
```

### Updating Deployment

```bash
# 1. Pull latest code
git pull origin main

# 2. Rebuild containers
docker compose -f docker-compose.production.yml up --build -d

# 3. Check logs
docker compose -f docker-compose.production.yml logs -f backend
```

### Zero-Downtime Deployment

For production, use rolling updates with container orchestration:

```bash
# Option 1: Docker Compose with scale
docker compose -f docker-compose.production.yml up -d --scale backend=4 --no-recreate
docker compose -f docker-compose.production.yml up -d --scale backend=2

# Option 2: Blue-Green Deployment
# 1. Build new image with tag
docker build -t backend-prod:v2 --target production .

# 2. Update docker-compose.production.yml to use v2
# 3. Start new containers alongside old
docker compose -f docker-compose.production.yml up -d --no-deps backend

# 4. Switch traffic at reverse proxy
# 5. Stop old containers
```

### Rollback Procedure

```bash
# 1. Check available image versions
docker images | grep backend-prod

# 2. Edit docker-compose.production.yml to use previous tag
# image: backend-prod:previous-version

# 3. Restart with previous version
docker compose -f docker-compose.production.yml up -d

# 4. Verify rollback
curl http://localhost:8000/api/v1/health/
```

---

## Production Checklist

### Pre-Deployment

- [ ] `.env.production` configured with strong passwords
- [ ] `ALLOWED_HOSTS` set to actual domains (no `*`)
- [ ] `CORS_ALLOWED_ORIGINS` configured with frontend URLs
- [ ] `SECRET_KEY` is 50+ characters and unique
- [ ] `DEBUG=False` in `.env.production`
- [ ] SSL/TLS certificates configured in reverse proxy
- [ ] Database backups configured
- [ ] Email service configured (SMTP)
- [ ] Sentry DSN configured for error tracking
- [ ] Firewall rules configured (only reverse proxy can access port 8000)
- [ ] DNS records pointing to server

### Post-Deployment

- [ ] Health check endpoint returns 200: `curl http://localhost:8000/api/v1/health/`
- [ ] Static files served correctly
- [ ] Database migrations applied successfully
- [ ] Admin interface accessible (if needed)
- [ ] Email notifications working
- [ ] HTTPS working via reverse proxy
- [ ] Rate limiting active
- [ ] Logging configured and accessible
- [ ] Monitoring dashboards set up
- [ ] Backup restore tested

### Django Deployment Checks

Run Django's built-in deployment checks:

```bash
docker compose -f docker-compose.production.yml exec backend \
  python manage.py check --deploy --fail-level WARNING
```

This validates:
- `DEBUG=False`
- `SECRET_KEY` not using default
- `ALLOWED_HOSTS` configured
- Security middleware enabled
- HTTPS settings correct
- Cookie security configured

---

## Monitoring & Logs

### Health Checks

The production container includes comprehensive health checks:

```bash
# Container health status
docker compose -f docker-compose.production.yml ps

# Manual health check
curl http://localhost:8000/api/v1/health/
```

**Health Check Endpoint** (`/api/v1/health/`):
- Application responsiveness
- Database connectivity
- Cache availability (Redis)
- Disk space
- Memory usage

### Log Access

```bash
# View all logs
docker compose -f docker-compose.production.yml logs -f

# View specific service logs
docker compose -f docker-compose.production.yml logs -f backend
docker compose -f docker-compose.production.yml logs -f db
docker compose -f docker-compose.production.yml logs -f redis

# Follow last 100 lines
docker compose -f docker-compose.production.yml logs -f --tail=100 backend

# Export logs to file
docker compose -f docker-compose.production.yml logs --no-color > backend-logs.txt
```

### Structured Logging

Production logs use JSON format for easy parsing:

```json
{
  "timestamp": "2025-10-24T12:34:56.789Z",
  "level": "INFO",
  "logger": "django.request",
  "message": "GET /api/v1/users/ 200",
  "request_id": "abc123",
  "user_id": 42,
  "duration_ms": 45
}
```

**Log Aggregation**:
- Logs written to `stdout/stderr` (captured by Docker)
- JSON format compatible with ELK Stack, Loki, Datadog
- Rotation configured: 50MB max size, 5 files retained
- Location inside container: `/app/logs/`

### Resource Monitoring

```bash
# Real-time container stats
docker stats

# Specific container stats
docker stats backend-app-prod

# One-time stats snapshot
docker stats --no-stream backend-app-prod

# Detailed inspection
docker inspect backend-app-prod
```

**Key Metrics to Monitor**:
- CPU usage (should be < 80% average)
- Memory usage (should have headroom)
- Network I/O
- Disk I/O
- Container restart count
- Health check failures
- Request latency (target: < 200ms p95)
- Error rate (target: < 1%)

---

## Security Considerations

### Container Security

**Non-Root User**:
- All processes run as `django` user (UID 1001)
- No root privileges inside container
- Limits damage from container escape vulnerabilities

**Image Security**:
```bash
# Scan for vulnerabilities before deployment
trivy image backend-prod:latest --severity HIGH,CRITICAL

# Docker Scout scanning
docker scout cves backend-prod:latest

# Grype scanning
grype backend-prod:latest
```

**Network Security**:
- Database and Redis NOT exposed to host (internal network only)
- Backend exposed only to reverse proxy
- Custom bridge network isolates containers
- No privileged ports (<1024) used

### Application Security

**Django Security Settings** (enforced in production):
- `DEBUG=False` (no debug information leaked)
- `SECRET_KEY` must be 50+ characters
- `ALLOWED_HOSTS` whitelist only
- HTTPS enforcement (`SECURE_SSL_REDIRECT=True`)
- HSTS enabled (31536000 seconds = 1 year)
- Secure cookies (`SESSION_COOKIE_SECURE=True`)
- CSRF protection with trusted origins
- Strict CORS policy
- Content Security Policy headers
- X-Frame-Options, X-Content-Type-Options set

**Secrets Management**:
- Never commit `.env.production` to version control
- Use environment variables for all secrets
- Rotate secrets regularly (every 90 days)
- Use strong passwords (32+ characters random)
- Consider external secret managers (HashiCorp Vault, AWS Secrets Manager)

### Reverse Proxy Configuration

**Nginx Example**:

```nginx
upstream backend {
    server localhost:8000 fail_timeout=0;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/ssl/certs/your-cert.pem;
    ssl_certificate_key /etc/ssl/private/your-key.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Proxy to backend
    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    # Static files (if served by nginx)
    location /static/ {
        alias /var/www/backend/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Media files (if served by nginx)
    location /media/ {
        alias /var/www/backend/media/;
        expires 30d;
        add_header Cache-Control "public";
    }
}
```

---

## Performance Optimization

### Gunicorn Tuning

**Worker Count**:
```
workers = (2 x num_cores) + 1
```

For 4 cores: `GUNICORN_WORKERS=9`

**Worker Class**:
- `sync`: Default, works for most applications
- `gevent`: Asynchronous, better for I/O-bound workloads
- `uvicorn.workers.UvicornWorker`: ASGI support

**Timeout**:
- Default: 30 seconds
- Increase for long-running requests
- Monitor slow requests and optimize database queries

**Max Requests**:
- Restart workers after N requests (prevents memory leaks)
- `GUNICORN_MAX_REQUESTS=1000` (default)
- Add jitter to prevent simultaneous restarts

### Database Optimization

**Connection Pooling**:
```python
# config/settings/production.py
DATABASES['default']['CONN_MAX_AGE'] = 600  # 10 minutes
```

**PostgreSQL Tuning** (docker-compose.production.yml):
```bash
POSTGRES_SHARED_BUFFERS=256MB     # 25% of RAM
POSTGRES_EFFECTIVE_CACHE_SIZE=1GB # 50-75% of RAM
POSTGRES_MAX_CONNECTIONS=100      # Adjust based on workers
```

**Indexing**:
- Add database indexes for frequently queried fields
- Use `django-extensions` to find missing indexes
- Monitor slow queries with `pg_stat_statements`

### Caching Strategy

**Redis Configuration**:
```bash
# LRU eviction when memory limit reached
maxmemory-policy: allkeys-lru
maxmemory: 512mb

# Persistence
appendonly: yes
appendfsync: everysec
```

**Django Cache Settings**:
```python
# Cache database queries
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis:6379/1',
        'TIMEOUT': 900,  # 15 minutes
    }
}
```

### Static File Serving

**WhiteNoise** (included in production):
- Serves static files with compression
- Sets far-future cache headers
- No need for separate web server for static files

**External CDN** (recommended):
- Use AWS CloudFront, Cloudflare, or similar
- Offload static file serving from application server
- Reduce bandwidth costs
- Improve global performance

---

## Troubleshooting

### Container Won't Start

**Symptoms**: Container exits immediately or restarts continuously

**Diagnosis**:
```bash
# Check container status
docker compose -f docker-compose.production.yml ps

# View container logs
docker compose -f docker-compose.production.yml logs backend

# Check last 50 lines
docker compose -f docker-compose.production.yml logs --tail=50 backend

# Inspect container
docker inspect backend-app-prod
```

**Common Causes**:
1. **Database connection failed**
   - Verify `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
   - Check if database container is healthy
   - Solution: `docker compose -f docker-compose.production.yml restart db`

2. **Missing environment variables**
   - Check `.env.production` exists
   - Verify all required variables are set
   - Solution: Review `.env.production.example` for required fields

3. **Port already in use**
   - Check if port 8000 is already bound
   - Solution: `sudo lsof -i :8000` and kill process or change `BACKEND_PORT`

4. **Migrations failed**
   - Check migration logs in container output
   - Solution: Run migrations manually: `docker compose -f docker-compose.production.yml exec backend python manage.py migrate`

### Health Check Failures

**Symptoms**: Container status shows "unhealthy"

**Diagnosis**:
```bash
# Check health status
docker compose -f docker-compose.production.yml ps

# Test health endpoint manually
curl -v http://localhost:8000/api/v1/health/

# Check container logs
docker compose -f docker-compose.production.yml logs backend
```

**Common Causes**:
1. **Application not fully started**
   - Wait for start_period (60s)
   - Check logs for initialization errors

2. **Database connectivity issues**
   - Health check tests database connection
   - Verify database container is healthy

3. **Redis connectivity issues**
   - Health check tests cache connection
   - Verify Redis container is healthy

### High Memory Usage

**Symptoms**: Container using more memory than expected

**Diagnosis**:
```bash
# Check memory usage
docker stats backend-app-prod

# View memory limit
docker inspect backend-app-prod | grep -A 10 Memory
```

**Solutions**:
1. **Reduce Gunicorn workers**
   - Each worker uses ~100-200MB
   - Lower `GUNICORN_WORKERS` in `.env.production`

2. **Enable max_requests worker recycling**
   - Prevents memory leaks from accumulating
   - `GUNICORN_MAX_REQUESTS=1000` (already set)

3. **Increase container memory limit**
   - Edit `docker-compose.production.yml`
   - Increase `deploy.resources.limits.memory`

### Slow Response Times

**Symptoms**: Requests taking > 1 second to complete

**Diagnosis**:
```bash
# Check request logs (includes duration_ms)
docker compose -f docker-compose.production.yml logs backend | grep duration_ms

# Check database query performance
docker compose -f docker-compose.production.yml exec backend \
  python manage.py shell
>>> from django.db import connection
>>> print(connection.queries)
```

**Solutions**:
1. **Database query optimization**
   - Add indexes to frequently queried fields
   - Use `select_related()` and `prefetch_related()`
   - Enable query logging to find slow queries

2. **Increase Gunicorn workers**
   - More workers = more concurrent requests
   - `GUNICORN_WORKERS=8` (for 4 cores)

3. **Enable caching**
   - Cache database queries with Redis
   - Cache API responses for frequently accessed data

### Permission Errors

**Symptoms**: "Permission denied" errors in logs

**Diagnosis**:
```bash
# Check file permissions
docker compose -f docker-compose.production.yml exec backend ls -la /app

# Check user
docker compose -f docker-compose.production.yml exec backend whoami
# Should output: django
```

**Solutions**:
1. **Volume permissions**
   - Ensure volume directories are writable
   - Fix: `docker compose -f docker-compose.production.yml exec backend chown -R django:django /app/logs`

2. **Media files**
   - Check media volume permissions
   - Fix: `docker compose -f docker-compose.production.yml exec backend chown -R django:django /app/media`

### Static Files Not Loading

**Symptoms**: 404 errors for static files, admin CSS missing

**Diagnosis**:
```bash
# Check if static files collected
docker compose -f docker-compose.production.yml exec backend ls -la /app/staticfiles

# Manually run collectstatic
docker compose -f docker-compose.production.yml exec backend \
  python manage.py collectstatic --noinput
```

**Solutions**:
1. **Collectstatic not run**
   - Entrypoint script runs it automatically
   - Run manually if needed (command above)

2. **WhiteNoise not configured**
   - Already configured in production settings
   - Verify `STATICFILES_STORAGE` is set

3. **Reverse proxy not forwarding**
   - Check nginx/traefik configuration
   - Ensure `/static/` location is configured

---

## Maintenance

### Database Backups

**Manual Backup**:
```bash
# Backup database to file
docker compose -f docker-compose.production.yml exec db \
  pg_dump -U ${DB_USER} ${DB_NAME} > backup-$(date +%Y%m%d-%H%M%S).sql

# Backup with compression
docker compose -f docker-compose.production.yml exec db \
  pg_dump -U ${DB_USER} ${DB_NAME} | gzip > backup-$(date +%Y%m%d-%H%M%S).sql.gz
```

**Restore Database**:
```bash
# Restore from backup
cat backup-20251024-120000.sql | \
  docker compose -f docker-compose.production.yml exec -T db \
  psql -U ${DB_USER} ${DB_NAME}

# Restore from compressed backup
gunzip -c backup-20251024-120000.sql.gz | \
  docker compose -f docker-compose.production.yml exec -T db \
  psql -U ${DB_USER} ${DB_NAME}
```

**Automated Backups**:
```bash
# Add to crontab: daily backup at 2 AM
0 2 * * * cd /path/to/backend && docker compose -f docker-compose.production.yml exec -T db pg_dump -U ${DB_USER} ${DB_NAME} | gzip > /backups/backup-$(date +\%Y\%m\%d).sql.gz

# Cleanup old backups (keep 30 days)
0 3 * * * find /backups -name "backup-*.sql.gz" -mtime +30 -delete
```

### Log Rotation

Logs are automatically rotated by Docker:
- Max size: 50MB per log file
- Max files: 5 files retained
- Total max: 250MB per container

**Manual Log Cleanup**:
```bash
# Clear all logs (WARNING: irreversible)
docker compose -f docker-compose.production.yml down
docker system prune -a --volumes
```

### Container Updates

**Update Base Images**:
```bash
# Pull latest base images
docker pull python:3.12-slim
docker pull postgres:15-alpine
docker pull redis:7-alpine

# Rebuild with latest base images
docker compose -f docker-compose.production.yml build --pull
docker compose -f docker-compose.production.yml up -d
```

**Update Application**:
```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker compose -f docker-compose.production.yml up --build -d

# Check logs for issues
docker compose -f docker-compose.production.yml logs -f backend
```

### Cleanup

**Remove Unused Resources**:
```bash
# Remove stopped containers
docker container prune -f

# Remove unused images
docker image prune -a -f

# Remove unused volumes (WARNING: data loss if volumes not in use)
docker volume prune -f

# Full cleanup (WARNING: removes everything not in use)
docker system prune -a --volumes -f
```

**Remove Production Stack**:
```bash
# Stop and remove containers
docker compose -f docker-compose.production.yml down

# Stop and remove containers + volumes (WARNING: deletes data)
docker compose -f docker-compose.production.yml down -v
```

---

## Additional Resources

- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/)
- [Gunicorn Settings](https://docs.gunicorn.org/en/stable/settings.html)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [PostgreSQL Tuning](https://wiki.postgresql.org/wiki/Tuning_Your_PostgreSQL_Server)
- [Redis Production Deployment](https://redis.io/docs/management/admin/)

---

## Support

For issues or questions:
1. Check this documentation and troubleshooting section
2. Review container logs: `docker compose -f docker-compose.production.yml logs -f`
3. Run Django deployment checks: `python manage.py check --deploy`
4. Check GitHub issues or create a new one

---

**Last Updated**: 2025-10-24
**Maintained By**: DevOps Team
**Story**: Feature #8.4 - Backend Production Container
