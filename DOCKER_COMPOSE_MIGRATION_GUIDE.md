# Docker Compose Migration Guide

**Migration from Multi-File to Unified Single-File Architecture**

**Date:** 2025-10-26
**Status:** Ready for implementation

---

## Table of Contents

1. [Overview](#overview)
2. [What's Changing](#whats-changing)
3. [Benefits](#benefits)
4. [Migration Steps](#migration-steps)
5. [Configuration Mapping](#configuration-mapping)
6. [Testing the Migration](#testing-the-migration)
7. [Rollback Procedure](#rollback-procedure)
8. [Troubleshooting](#troubleshooting)
9. [FAQ](#faq)

---

## Overview

This guide walks you through migrating from the current multi-file Docker Compose setup to a simplified single-file architecture that supports all environments through environment variables.

### Current Architecture (Before)

```
docker-compose.yml              # Base configuration
compose.override.yml            # Local development
compose.test.yml                # Testing
compose.staging.yml             # Staging
compose.production.yml          # Production
.env.local.example
.env.staging.example
.env.production.example
.env.test
```

### New Architecture (After)

```
docker-compose.unified.yml      # Single file for ALL environments
.env.unified.example            # Single environment file template
.env                            # Your active environment configuration
```

---

## What's Changing

### Key Changes

1. **Single Compose File**: One `docker-compose.unified.yml` instead of 5 separate files
2. **Single Environment File**: One `.env` file with environment variable switching
3. **Consistent Ports**: Same port numbers across all environments (80, 443, 8000, 5173, 5432, 6379)
4. **Environment Variable Switching**: Change `ENVIRONMENT=local|staging|production` to switch
5. **Simplified Commands**: Always use same command, environment controlled by `.env`

### What Stays the Same

1. **Service Names**: db, redis, backend, frontend, proxy, celery (unchanged)
2. **Network Architecture**: Still uses reverse proxy with isolated backend/frontend
3. **Dockerfile Targets**: Still uses development/production build targets
4. **Volume Persistence**: Data persists between environments via named volumes
5. **Health Checks**: Same health check endpoints and behavior

---

## Benefits

### 1. Simplified Operations

**Before:**
```bash
# Different commands for each environment
docker compose up                                           # Local
docker compose -f docker-compose.yml -f compose.test.yml up    # Test
docker compose -f docker-compose.yml -f compose.staging.yml up # Staging
docker compose -f docker-compose.yml -f compose.production.yml up # Production
```

**After:**
```bash
# Same command for all environments
docker compose -f docker-compose.unified.yml up -d
# Environment controlled by ENVIRONMENT variable in .env
```

### 2. Eliminated Configuration Drift

- **Before**: Each environment file could diverge, creating subtle bugs
- **After**: Single source of truth, configuration differences explicit and minimal

### 3. Fixed Configuration Discrepancies

Addresses all issues documented in `CONFIGURATION_DISCREPANCIES.md`:

- ✅ Consistent Django settings module path across all environments
- ✅ Standardized API URLs (always through proxy)
- ✅ Uniform health check implementations (127.0.0.1, consistent tools)
- ✅ Consistent CORS configuration across environments
- ✅ No port conflicts between environments

### 4. Easier Environment Switching

**Before:**
```bash
# Manual file juggling
docker compose -f docker-compose.yml -f compose.staging.yml down
docker compose -f docker-compose.yml -f compose.production.yml up
```

**After:**
```bash
# Edit ENVIRONMENT in .env and restart
nano .env  # Change ENVIRONMENT=staging to ENVIRONMENT=production
docker compose -f docker-compose.unified.yml restart
```

### 5. Clear Configuration Differences

The **only** primary configuration that changes between environments:

```bash
# Local
ALLOWED_HOSTS=localhost,127.0.0.1

# Staging
ALLOWED_HOSTS=localhost,staging.yourdomain.com

# Production
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

Everything else (ports, services, architecture) remains consistent.

---

## Migration Steps

### Step 1: Backup Current Configuration

```bash
# Create backup directory
mkdir -p docker-compose-backup

# Backup existing compose files
cp docker-compose.yml docker-compose-backup/
cp compose.*.yml docker-compose-backup/
cp .env* docker-compose-backup/

# Backup current volumes (optional but recommended)
docker compose ps --format json > docker-compose-backup/running-services.json
```

### Step 2: Stop Current Environment

```bash
# Stop whichever environment is currently running
docker compose down

# Or if using override files
docker compose -f docker-compose.yml -f compose.staging.yml down
```

### Step 3: Copy New Configuration Files

```bash
# Copy the unified compose file
cp docker-compose.unified.yml docker-compose.yml

# Create your environment file from template
cp .env.unified.example .env
```

### Step 4: Configure Your Environment

Edit `.env` and:

1. Set the `ENVIRONMENT` variable:
   ```bash
   ENVIRONMENT=local    # or staging, or production
   ```

2. Uncomment the appropriate environment section

3. Fill in environment-specific values:

**For Local Development:**
```bash
ENVIRONMENT=local
COMPOSE_PROJECT_NAME=app
# Keep the LOCAL ENVIRONMENT section as-is
# Comment out STAGING and PRODUCTION sections
```

**For Staging:**
```bash
ENVIRONMENT=staging
COMPOSE_PROJECT_NAME=app-staging

# Comment out LOCAL section
# Uncomment STAGING ENVIRONMENT section
# Fill in:
DB_PASSWORD=your-secure-staging-password
REDIS_PASSWORD=your-secure-staging-password
ALLOWED_HOSTS=localhost,staging.yourdomain.com
CORS_ALLOWED_ORIGINS=https://staging.yourdomain.com
FRONTEND_API_URL=https://staging.yourdomain.com
```

**For Production:**
```bash
ENVIRONMENT=production
COMPOSE_PROJECT_NAME=app-production

# Comment out LOCAL and STAGING sections
# Uncomment PRODUCTION ENVIRONMENT section
# Fill in:
DB_PASSWORD=your-highly-secure-production-password
REDIS_PASSWORD=your-highly-secure-production-password
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
FRONTEND_API_URL=https://yourdomain.com
```

### Step 5: Validate Configuration

```bash
# Check configuration is valid
docker compose -f docker-compose.yml config

# Verify environment variables are loaded
docker compose -f docker-compose.yml config | grep ENVIRONMENT
```

### Step 6: Start New Environment

```bash
# Start with the new unified configuration
docker compose up -d

# Monitor startup
docker compose logs -f
```

### Step 7: Verify Services

```bash
# Check all services are healthy
docker compose ps

# Test health endpoints
curl http://localhost/health              # Proxy
curl http://localhost/api/v1/health/      # Backend
curl http://localhost/                    # Frontend
```

### Step 8: Test Application Functionality

- [ ] Backend API responds correctly
- [ ] Frontend loads and fetches runtime config
- [ ] Database connections work
- [ ] Redis cache operations succeed
- [ ] Proxy routing works correctly
- [ ] Static/media files served properly
- [ ] Authentication flows work
- [ ] Celery tasks execute (if enabled)

### Step 9: Update Scripts and Documentation

Update any deployment scripts to use the new compose file:

```bash
# Update docker-dev.sh or similar scripts
# Old:
# docker compose -f docker-compose.yml -f compose.override.yml up -d

# New:
# docker compose up -d
```

### Step 10: Archive Old Files (Optional)

Once confirmed working:

```bash
# Move old files to archive
mkdir -p archive/docker-compose-old
mv docker-compose-backup/* archive/docker-compose-old/
mv compose.*.yml archive/docker-compose-old/
```

---

## Configuration Mapping

### Environment Variable Mapping

Here's how old environment-specific configurations map to the new unified approach:

#### Local Development

| Old File | Old Setting | New File | New Setting |
|----------|-------------|----------|-------------|
| compose.override.yml | `target: development` | .env | `BUILD_TARGET=development` |
| compose.override.yml | `ports: - "8000:8000"` | .env | `BACKEND_PORT_EXPOSE=8000` |
| compose.override.yml | `DEBUG: True` | .env | `DEBUG=True` |
| .env.local.example | `ENVIRONMENT=local` | .env | `ENVIRONMENT=local` |

#### Staging

| Old File | Old Setting | New File | New Setting |
|----------|-------------|----------|-------------|
| compose.staging.yml | `target: production` | .env | `BUILD_TARGET=production` |
| compose.staging.yml | `ports: []` | .env | `BACKEND_PORT_EXPOSE=` (empty) |
| compose.staging.yml | `DEBUG: False` | .env | `DEBUG=False` |
| .env.staging.example | `ENVIRONMENT=staging` | .env | `ENVIRONMENT=staging` |

#### Production

| Old File | Old Setting | New File | New Setting |
|----------|-------------|----------|-------------|
| compose.production.yml | `target: production` | .env | `BUILD_TARGET=production` |
| compose.production.yml | `ports: []` | .env | `BACKEND_PORT_EXPOSE=` (empty) |
| compose.production.yml | `DEBUG: False` | .env | `DEBUG=False` |
| .env.production.example | `ENVIRONMENT=production` | .env | `ENVIRONMENT=production` |

### Port Consistency

All environments now use **identical internal ports**:

| Service | Port | Exposed In |
|---------|------|------------|
| Proxy (HTTP) | 80 | All environments |
| Proxy (HTTPS) | 443 | Staging, Production only |
| Backend | 8000 | Internal (exposed in local only) |
| Frontend | 5173 | Internal (exposed in local only) |
| PostgreSQL | 5432 | Internal (exposed in local only) |
| Redis | 6379 | Internal (exposed in local only) |

**No more port conflicts** when running multiple environments simultaneously (different project names handle isolation).

---

## Testing the Migration

### Automated Validation

Use the provided validation script:

```bash
# Make script executable
chmod +x validate-environments.sh

# Test local environment
./validate-environments.sh local

# Test staging environment
./validate-environments.sh staging

# Test production environment
./validate-environments.sh production

# Test all environments
./validate-environments.sh all
```

### Manual Validation Checklist

#### Local Environment

```bash
# Set environment
echo "ENVIRONMENT=local" > .env
cat .env.unified.example | grep -A 100 "LOCAL ENVIRONMENT" >> .env

# Start services
docker compose up -d

# Verify
curl http://localhost/health                          # Should return 200
curl http://localhost/api/v1/health/                  # Should return {"status": "healthy"}
curl http://localhost/                                # Should load frontend
docker compose ps | grep healthy                      # All services should be healthy
docker compose logs backend | grep "ALLOWED_HOSTS"    # Should show localhost,127.0.0.1
```

#### Staging Environment

```bash
# Set environment
# Edit .env: ENVIRONMENT=staging
# Uncomment and fill in STAGING section

# Start services
docker compose up -d

# Verify
curl https://staging.yourdomain.com/health            # Should return 200
curl https://staging.yourdomain.com/api/v1/health/    # Should return {"status": "healthy"}
docker compose ps | grep healthy                      # All services should be healthy
docker compose logs backend | grep "ALLOWED_HOSTS"    # Should show staging.yourdomain.com
```

#### Production Environment

```bash
# Set environment
# Edit .env: ENVIRONMENT=production
# Uncomment and fill in PRODUCTION section

# Start services
docker compose up -d

# Verify
curl https://yourdomain.com/health                    # Should return 200
curl https://yourdomain.com/api/v1/health/            # Should return {"status": "healthy"}
docker compose ps | grep healthy                      # All services should be healthy
docker compose logs backend | grep "ALLOWED_HOSTS"    # Should show yourdomain.com
```

---

## Rollback Procedure

If you encounter issues with the new setup:

### Quick Rollback

```bash
# Stop new environment
docker compose down

# Restore old compose files
cp docker-compose-backup/docker-compose.yml .
cp docker-compose-backup/compose.*.yml .
cp docker-compose-backup/.env* .

# Start old environment
docker compose up -d
# Or with override:
# docker compose -f docker-compose.yml -f compose.override.yml up -d
```

### Data Preservation

**Volumes are safe**: Named volumes persist independently of compose file structure. Your data (database, redis, media files) will not be lost during migration or rollback.

```bash
# List volumes to verify data is preserved
docker volume ls | grep app

# If needed, inspect a volume
docker volume inspect app-postgres-data
```

---

## Troubleshooting

### Issue: Services won't start

**Symptoms:**
- `docker compose up` fails immediately
- Errors about missing environment variables

**Solution:**
```bash
# Verify .env file exists and is loaded
cat .env | grep ENVIRONMENT

# Check compose file can be parsed
docker compose config

# Ensure all required variables are set
docker compose config | grep -i "error"
```

### Issue: Port conflicts

**Symptoms:**
- Error: "port is already allocated"
- Cannot bind to 80 or 443

**Solution:**
```bash
# Check what's using the port
sudo lsof -i :80
sudo lsof -i :443

# Stop conflicting service or use different project name
COMPOSE_PROJECT_NAME=app-local docker compose up -d
```

### Issue: Wrong environment configuration loaded

**Symptoms:**
- Staging configuration loading in production
- Debug mode enabled when it shouldn't be

**Solution:**
```bash
# Verify ENVIRONMENT variable
docker compose config | grep ENVIRONMENT

# Check which .env section is active (uncommented)
cat .env | grep -v "^#" | grep -v "^$"

# Ensure only ONE environment section is uncommented in .env
```

### Issue: Container can't connect to database

**Symptoms:**
- Backend health check fails
- "could not connect to server" errors

**Solution:**
```bash
# Check database is healthy
docker compose ps db

# Verify database environment variables
docker compose exec backend env | grep DB_

# Check database logs
docker compose logs db

# Verify ALLOWED_HOSTS includes necessary values
docker compose exec backend python manage.py check --deploy
```

### Issue: Frontend shows old configuration

**Symptoms:**
- Frontend displays old environment settings
- API requests go to wrong URL

**Solution:**
```bash
# Frontend uses runtime config - verify backend provides correct values
curl http://localhost/api/v1/config/frontend/ | jq

# Check backend environment variables
docker compose exec backend env | grep FRONTEND_

# Rebuild frontend if needed (only for development)
docker compose build frontend
docker compose restart frontend
```

### Issue: SSL/TLS not working in staging/production

**Symptoms:**
- HTTPS connections fail
- Certificate errors

**Solution:**
```bash
# Verify SSL is enabled in .env
grep SSL_ENABLED .env

# Check nginx configuration includes SSL config
docker compose exec proxy cat /etc/nginx/nginx.conf | grep ssl

# Verify SSL certificates exist and are mounted
docker compose exec proxy ls -la /etc/nginx/ssl/

# Check nginx logs for SSL errors
docker compose logs proxy | grep -i ssl
```

---

## FAQ

### Q: Can I run multiple environments simultaneously?

**A:** Yes! Use different project names:

```bash
# Terminal 1 - Local
COMPOSE_PROJECT_NAME=app-local docker compose up -d

# Terminal 2 - Staging
COMPOSE_PROJECT_NAME=app-staging docker compose up -d

# They'll have isolated networks and volumes
```

### Q: Do I need to change nginx configuration files?

**A:** No. The same nginx configuration files work across all environments. The unified compose file uses environment variables to select the right config:

- Local: `./nginx/nginx.conf`
- Staging: `./nginx/nginx.staging.conf` (if `NGINX_CONFIG` set)
- Production: `./nginx/nginx.production.conf` (if `NGINX_CONFIG` set)

### Q: What happens to my existing data?

**A:** All data is safe. Volume names include the project name, so:

- `app-postgres-data` (local)
- `app-staging-postgres-data` (staging)
- `app-production-postgres-data` (production)

Each environment has isolated data.

### Q: How do I switch from local to staging quickly?

**A:**

```bash
# Method 1: Edit .env
nano .env
# Change ENVIRONMENT=local to ENVIRONMENT=staging
# Uncomment staging section, comment local section
docker compose restart

# Method 2: Use different .env files
cp .env .env.local
cp .env.unified.example .env
# Configure for staging
docker compose up -d
```

### Q: Can I customize resource limits per environment?

**A:** Yes! Each environment section in `.env.unified.example` has resource limit variables:

```bash
# Local (relaxed)
DB_CPU_LIMIT=2
DB_MEMORY_LIMIT=1G

# Production (strict)
DB_CPU_LIMIT=4
DB_MEMORY_LIMIT=2G
```

### Q: How do I add environment-specific services?

**A:** Use profiles in the compose file:

```yaml
services:
  debug-tool:
    # ... configuration ...
    profiles:
      - ${DEBUG_PROFILE:-debug}
```

Then in `.env`:
```bash
# Local: enable debug profile
DEBUG_PROFILE=debug

# Production: disable by leaving empty
DEBUG_PROFILE=
```

### Q: What if I need different nginx configs per environment?

**A:** Use the `NGINX_CONFIG` variable in `.env`:

```bash
# Local
NGINX_CONFIG=./nginx/nginx.conf

# Staging
NGINX_CONFIG=./nginx/nginx.staging.conf

# Production
NGINX_CONFIG=./nginx/nginx.production.conf
```

### Q: How do I handle secrets in production?

**A:** The `.env` file should **never** be committed with production secrets. Instead:

1. Store `.env` in a secrets manager (AWS Secrets Manager, HashiCorp Vault)
2. Retrieve at deployment time:
   ```bash
   aws secretsmanager get-secret-value --secret-id prod-env > .env
   ```
3. Use CI/CD environment variables
4. Use Docker Swarm/Kubernetes secrets

### Q: Can I still use the old compose files?

**A:** Yes! The old files are compatible and can coexist. However, you should migrate to avoid configuration drift and benefit from fixes documented in `CONFIGURATION_DISCREPANCIES.md`.

### Q: How do I test without affecting my current setup?

**A:** Use a different project name:

```bash
# Test with isolated project
COMPOSE_PROJECT_NAME=app-test docker compose -f docker-compose.unified.yml up -d

# Original environment unaffected
docker compose ps  # Shows original services still running
```

---

## Summary

### Before Migration

- 5 compose files to maintain
- Port conflicts between environments
- Configuration discrepancies (7 critical issues)
- Complex commands for different environments
- Easy to diverge configurations

### After Migration

- 1 compose file for all environments
- Consistent ports across all environments
- All configuration discrepancies fixed
- Simple commands (same for all environments)
- Single source of truth prevents drift
- Only ALLOWED_HOSTS changes between environments

### Next Steps

1. ✅ Complete migration steps above
2. ✅ Run validation script for your environment
3. ✅ Update deployment documentation
4. ✅ Archive old compose files
5. ✅ Monitor for 1-2 weeks to ensure stability
6. ✅ Train team on new simplified approach

---

**Need Help?**

If you encounter issues not covered in this guide:

1. Check `docker compose logs` for service-specific errors
2. Run `docker compose config` to verify configuration parsing
3. Review `CONFIGURATION_DISCREPANCIES.md` for known issues
4. Check Docker and Docker Compose versions: `docker --version`, `docker compose version`

**Minimum Requirements:**
- Docker: 20.10+
- Docker Compose: 2.0+ (v2 CLI required for variable substitution features)
