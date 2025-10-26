# Docker Compose Unified - Quick Start Guide

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
cp .env.unified.example .env

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
docker compose -f docker-compose.unified.yml up -d

# View logs
docker compose -f docker-compose.unified.yml logs -f

# Check status
docker compose -f docker-compose.unified.yml ps
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
docker compose -f docker-compose.unified.yml up -d

# Stop services
docker compose -f docker-compose.unified.yml down

# View logs
docker compose -f docker-compose.unified.yml logs -f

# Restart a service
docker compose -f docker-compose.unified.yml restart backend

# Rebuild and restart
docker compose -f docker-compose.unified.yml up -d --build

# Remove everything including volumes (CAUTION!)
docker compose -f docker-compose.unified.yml down -v
```

---

## Switching Environments

```bash
# Edit .env
nano .env

# Change ENVIRONMENT variable
ENVIRONMENT=staging  # was: local

# Restart services
docker compose -f docker-compose.unified.yml restart
```

---

## Troubleshooting

### Services won't start
```bash
# Check configuration
docker compose -f docker-compose.unified.yml config

# View service logs
docker compose -f docker-compose.unified.yml logs [service-name]
```

### Port already in use
```bash
# Check what's using the port
sudo lsof -i :80

# Or use different project name
COMPOSE_PROJECT_NAME=app-test docker compose -f docker-compose.unified.yml up -d
```

### Need help?
See `DOCKER_COMPOSE_MIGRATION_GUIDE.md` for detailed troubleshooting.

---

## What Makes This Different?

**Old Way (5 files):**
```bash
docker compose -f docker-compose.yml -f compose.override.yml up    # Local
docker compose -f docker-compose.yml -f compose.staging.yml up     # Staging
docker compose -f docker-compose.yml -f compose.production.yml up  # Production
```

**New Way (1 file):**
```bash
docker compose -f docker-compose.unified.yml up -d   # All environments!
```

Just change `ENVIRONMENT` in `.env` to switch. That's it!

---

## Key Features

✅ **One File:** Single docker-compose.unified.yml for everything
✅ **Consistent Ports:** Same ports across all environments
✅ **Simple Switching:** Change one variable to switch environments
✅ **No Conflicts:** Run multiple environments simultaneously
✅ **Fully Validated:** Automated testing ensures it works

---

## Need More Details?

- **Full Guide:** `DOCKER_COMPOSE_MIGRATION_GUIDE.md`
- **Complete Summary:** `DOCKER_COMPOSE_UNIFIED_SUMMARY.md`
- **Environment Variables:** `.env.unified.example` (comprehensive docs)
- **Validation:** `./validate-environments.sh [environment]`

---

**Ready to go!** 🚀
