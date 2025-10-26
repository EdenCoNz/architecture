# Docker Compose - Quick Start Guide

**5-Minute Setup for Any Environment**

---

## Step 1: Choose Your Environment

```bash
# Local Development
ENVIRONMENT=local

# Staging
ENVIRONMENT=staging

# Production
ENVIRONMENT=production
```

---

## Step 2: Create Your .env File

```bash
# Copy template
cp .env.example .env

# Edit and set ENVIRONMENT variable
nano .env
```

**Edit this one line:**
```bash
ENVIRONMENT=local    # Change to: local, staging, or production
```

**For staging/production, also set:**
```bash
# Secure passwords (generate with: openssl rand -base64 32)
DB_PASSWORD=your-secure-password
REDIS_PASSWORD=your-secure-redis-password

# Your domain
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

---

## Step 3: Start Services

```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f

# Check status
docker compose ps
```

---

## Step 4: Access Your Application

### Local Development
```
Frontend:         http://localhost/
Backend API:      http://localhost/api/
Django Admin:     http://localhost/admin/

Development-only direct access:
Backend:          http://localhost:8000
Frontend:         http://localhost:5173
Database:         localhost:5432
Redis:            localhost:6379
```

### Staging
```
All Access:       https://staging.yourdomain.com/
(No direct service access - secure by default)
```

### Production
```
All Access:       https://yourdomain.com/
(No direct service access - maximum security)
```

---

## Step 5: Verify Everything Works

```bash
# Run automated validation
chmod +x validate-environments.sh
./validate-environments.sh local    # or staging, or production

# Or manually test
curl http://localhost/health                 # Proxy health
curl http://localhost/api/v1/health/         # Backend health
curl http://localhost/                       # Frontend loads
```

---

## Common Commands

```bash
# Start services
docker compose up -d

# Stop services
docker compose down

# View logs
docker compose logs -f

# Restart a service
docker compose restart backend

# Rebuild and restart
docker compose up -d --build

# Remove everything including volumes (CAUTION!)
docker compose down -v
```

---

## Switching Environments

```bash
# Edit .env
nano .env

# Change ENVIRONMENT variable
ENVIRONMENT=staging  # was: local

# Restart services
docker compose restart
```

---

## Troubleshooting

### Services won't start
```bash
# Check configuration
docker compose config

# View service logs
docker compose logs [service-name]
```

### Port already in use
```bash
# Check what's using the port
sudo lsof -i :80

# Or use different project name
COMPOSE_PROJECT_NAME=app-test docker compose up -d
```

### Need help?
See `TROUBLESHOOTING.md` for detailed troubleshooting.

---

## Rollback Procedures

If you encounter issues with the consolidated compose file structure:

### Quick Rollback

The previous configuration has been preserved in a backup branch:

```bash
# Switch to backup branch
git checkout backup/pre-docker-simplification-phase1

# Start services using old configuration
docker compose up -d
```

### File-Level Restore

Individual files are available in timestamped backup:

```bash
# List available backups
ls -la backups/

# Restore from specific backup
cp backups/docker-config-20251027_071855/<filename> .
```

### Return to Current Version

```bash
# Return to main branch
git checkout main

# Restart services with consolidated configuration
docker compose up -d
```

**Note**: The consolidation (Feature #15) removed redundant compose files while maintaining full functionality. The current setup uses:
- `docker-compose.yml` - Base configuration
- `compose.override.yml` - Local dev overrides (auto-loaded)
- `compose.staging.yml` - Staging environment
- `compose.production.yml` - Production environment
- `compose.test.yml` - Testing environment

---

## What Makes This Different?

**Simplified Approach:**
```bash
# Local development (uses compose.override.yml automatically)
docker compose up -d

# Staging
docker compose -f docker-compose.yml -f compose.staging.yml up -d

# Production
docker compose -f docker-compose.yml -f compose.production.yml up -d
```

The base `docker-compose.yml` works for all environments!

---

## Key Features

✅ **Simplified:** Base compose file with environment-specific overlays
✅ **Consistent Ports:** Same ports across all environments
✅ **Standard Pattern:** Uses Docker Compose overlay pattern
✅ **No Conflicts:** Run multiple environments simultaneously
✅ **Fully Validated:** Automated testing ensures it works

---

## Need More Details?

- **Configuration Reference:** `docs/configuration.md`
- **Environment Variables:** `.env.example` (comprehensive docs)
- **Validation:** `./validate-environments.sh [environment]`
- **README:** Project root README for detailed instructions

---

**Ready to go!** 🚀
