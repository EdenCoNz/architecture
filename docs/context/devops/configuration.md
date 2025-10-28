# Global Configuration

Configuration requirements for all services across environments.

**Related Documentation:**
- CI/CD Pipeline: [CICD.md](./CICD.md)
- Container Health Monitoring: [container-health-monitoring.md](./container-health-monitoring.md)
- Pipeline Flow: [pipeline-flow.md](./pipeline-flow.md)

---

## Frontend

**Location:** `/frontend/`
**Tech:** React + Vite + TypeScript

### Environment Files
- `.env.example` - Development template
- `.env.production.example` - Production template
- `.env.staging.example` - Staging template
- `.env.local.example` - Local override template
- `.env.test` - Test environment
- `.env.docker` - Docker environment

### Required Variables
```bash
VITE_API_URL=http://localhost:8000  # Backend API URL
VITE_NODE_ENV=development           # Environment type
```

### Optional Variables
```bash
# API
VITE_API_TIMEOUT=30000              # Request timeout (ms)
VITE_API_ENABLE_LOGGING=true        # API logging

# Application
VITE_APP_NAME=App                   # Application name
VITE_APP_TITLE=App                  # Browser tab title
VITE_APP_VERSION=1.0.0              # Version
VITE_DEBUG=true                     # Debug mode

# Features
VITE_ENABLE_ANALYTICS=false         # Analytics
VITE_ENABLE_ERROR_REPORTING=false   # Error reporting
VITE_ENABLE_SERVICE_WORKER=false    # Offline support/caching

# Security
VITE_SECURITY_ENABLE_CSP=false      # Content Security Policy
VITE_SECURITY_MAX_LOGIN_ATTEMPTS=5  # Login attempt limit
```

### Ports
- Dev: `5173`
- Test: `5174`
- Prod: `80/443` (via nginx)

### Config Files
- `vite.config.ts` - Build & dev server
- `tsconfig.json` - TypeScript
- `eslint.config.js` - Linting
- `.prettierrc` - Formatting

---

## Backend

**Location:** `/backend/`
**Tech:** Django + DRF + PostgreSQL + Redis

### Environment Files
- `.env.example` - Development template
- `.env.production.example` - Production template
- `.env.staging.example` - Staging template
- `.env.docker` - Docker environment

### Required Variables
```bash
# Django Core
SECRET_KEY=your-secret-key          # Min 50 chars in prod
DJANGO_SETTINGS_MODULE=config.settings.development
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=backend_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost                    # "db" in Docker
DB_PORT=5432

# Redis
REDIS_URL=redis://127.0.0.1:6379/1
REDIS_PASSWORD=                      # Required in prod

# CORS/CSRF
CORS_ALLOWED_ORIGINS=http://localhost:5173
CSRF_TRUSTED_ORIGINS=http://localhost:5173
```

### Optional Variables
```bash
# Email
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=noreply@example.com

# JWT
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=15
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7

# Security (Production)
SECURE_SSL_REDIRECT=False            # True in prod
SESSION_COOKIE_SECURE=False          # True in prod
CSRF_COOKIE_SECURE=False             # True in prod
RATELIMIT_ENABLE=True
PASSWORD_MIN_LENGTH=12

# Logging
LOG_LEVEL=INFO
SLOW_REQUEST_THRESHOLD_MS=1000

# Gunicorn (Production)
GUNICORN_WORKERS=4
GUNICORN_TIMEOUT=30
GUNICORN_MAX_REQUESTS=1000

# Celery
CELERY_BROKER_URL=redis://127.0.0.1:6379/0
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/0
CELERY_WORKER_CONCURRENCY=4

# External Services
SENTRY_DSN=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
USE_S3=False

# Frontend Runtime Configuration (Feature #12)
# Backend serves these to frontend at /api/v1/config/frontend/
FRONTEND_API_URL=http://localhost
FRONTEND_API_TIMEOUT=30000
FRONTEND_API_ENABLE_LOGGING=true
FRONTEND_APP_NAME=Application
FRONTEND_APP_TITLE=Application
FRONTEND_APP_VERSION=1.0.0
FRONTEND_ENABLE_ANALYTICS=false
FRONTEND_ENABLE_DEBUG=true

# Docker-Specific Settings
PYTHONUNBUFFERED=1                   # Important for Docker logs
PYTHONDONTWRITEBYTECODE=1            # Prevent .pyc files
```

### Ports
- Dev: `8000`
- Test: `8001`
- Prod: `8000` (via Gunicorn behind nginx)

### Config Files
- `config/settings/` - Django settings (base, development, production, staging, testing)
- `pytest.ini` - Testing
- `pyproject.toml` - Project metadata
- `.flake8` - Linting
- `requirements/` - Dependencies (base, dev, prod)

---

## Testing

**Location:** `/testing/`
**Types:** E2E (Playwright), Visual Regression, Integration (Pytest), Performance (Locust), Unit Tests

### Environment File
- `.env.test` - Test environment

### Required Variables
```bash
# Database
TEST_DB_NAME=backend_test_db
TEST_DB_USER=postgres
TEST_DB_PASSWORD=postgres
TEST_DB_HOST=db
TEST_DB_PORT=5432

# Service URLs
FRONTEND_URL=http://frontend:5173
BACKEND_URL=http://backend:8000
PROXY_URL=http://proxy:80
TEST_BASE_URL=http://localhost:5174
TEST_API_URL=http://localhost:8001
```

### Optional Variables
```bash
# Playwright
PLAYWRIGHT_HEADLESS=true
PLAYWRIGHT_SLOWMO=0
PLAYWRIGHT_TIMEOUT=30000
CI=false

# Visual Regression
VISUAL_REGRESSION_THRESHOLD=0.1
VISUAL_UPDATE_BASELINE=false

# Performance
PERFORMANCE_DURATION=60
PERFORMANCE_USERS=10
PERFORMANCE_SPAWN_RATE=2

# Test Data
LOAD_FIXTURES=true
GENERATE_TEST_DATA=true
TEST_USERS_COUNT=10
TEST_ASSESSMENTS_COUNT=20

# Artifacts
TEST_REPORTS_DIR=/testing/reports
TEST_REPORT_FORMAT=html,json
```

### Ports
- Frontend: `5174`
- Backend: `8001`
- Database: `5433`
- Redis: `6380`
- Proxy: `80` (note: may conflict with dev environment)

### Config Files
- `e2e/playwright.config.ts` - E2E tests
- `visual/playwright.config.ts` - Visual regression
- `pytest.ini` - Integration tests
- `performance/locustfile.py` - Load tests

---

## Infrastructure Services

### PostgreSQL
```bash
POSTGRES_DB=backend_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
# Production tuning
POSTGRES_SHARED_BUFFERS=256MB
POSTGRES_EFFECTIVE_CACHE_SIZE=1GB
POSTGRES_MAX_CONNECTIONS=100
```
**Port:** `5432` (dev), `5433` (test)

### Redis
```bash
REDIS_PASSWORD=                      # Required in prod
REDIS_MAXMEMORY=256mb               # 512mb staging, 1gb prod
```
**Port:** `6379` (dev), `6380` (test)

### Nginx
**Port:** `80` (HTTP), `443` (HTTPS)
**Config:** `/nginx/nginx.conf`
**Routes:**
- `/` → Frontend
- `/api/` → Backend
- `/admin/` → Django Admin
- `/static/` → Static files
- `/media/` → Media files

---

## Root Orchestration

### Docker Compose Files

**Consolidated Structure (Feature #15)** - All compose files are located at the project root:

- `docker-compose.yml` - Base orchestration for all services and environments
- `compose.override.yml` - Local dev overrides (automatically loaded)
- `compose.production.yml` - Production environment overrides
- `compose.staging.yml` - Staging environment overrides
- `compose.test.yml` - Test environment

**Files Removed in Feature #15:**
- ❌ `docker-compose.unified.yml` - Was duplicate of docker-compose.yml
- ❌ `backend/docker-compose.yml` - Backend services moved to root
- ❌ `backend/docker-compose.production.yml` - Production config moved to root
- ❌ `frontend/docker-compose.yml` - Frontend service moved to root
- ❌ `frontend/docker-compose.prod.yml` - Production config moved to root

All redundant service-specific compose files have been consolidated into the root compose files for simplified maintenance and consistency.

### Root Variables
```bash
ENVIRONMENT=local                    # local/staging/production/test
COMPOSE_PROJECT_NAME=app
APP_VERSION=1.0.0
```

---

## Environment Summary

| Setting | Local | Staging | Production | Test |
|---------|-------|---------|------------|------|
| Debug | ✓ | ✓ | ✗ | ✓ |
| HTTPS | ✗ | ✓ | ✓ | ✗ |
| Exposed Ports | All | Proxy only | Proxy only | All (alt) |
| Security | Relaxed | Strict | Strict | Relaxed |
| External Services | ✗ | ✓ | ✓ | ✗ |
| Logging | Verbose | Info | Warning | Debug |
| Hot Reload | ✓ | ✗ | ✗ | ✗ |

---

## Quick Reference

### Start Services
```bash
# Local development
docker compose up

# With Celery
docker compose --profile with-celery up

# Staging
docker compose -f docker-compose.yml -f compose.staging.yml up

# Production
docker compose -f docker-compose.yml -f compose.production.yml up

# Test environment
docker compose -f docker-compose.yml -f compose.test.yml up
```

### Environment Files Priority
1. `.env.{environment}` (local, staging, production)
2. `.env.local` (git-ignored overrides)
3. `.env` (fallback)

---

## Container Registry Configuration

**Default Registry:** GitHub Container Registry (`ghcr.io`)

### Environment Variables
```bash
# Used in CI/CD pipeline
CONTAINER_REGISTRY=ghcr.io           # Container registry URL
REPOSITORY_OWNER=username            # GitHub org/user (lowercase)

# Image versioning
BACKEND_VERSION=1.0.0                # From config/__init__.py
FRONTEND_VERSION=1.0.0               # From package.json
BACKEND_IMAGE=ghcr.io/owner/backend:tag
FRONTEND_IMAGE=ghcr.io/owner/frontend:tag
```

### Image Tagging Strategy
- `version` - Semantic version (e.g., 1.0.0)
- `version-sha` - Version with commit SHA (immutable)
- `latest` - Latest build from main branch
- `branch-name` - Latest build from specific branch

---

## GitHub Actions Secrets

Required secrets for CI/CD deployment:

```bash
# Tailscale VPN
TS_OAUTH_CLIENT_ID=                  # Tailscale OAuth client ID
TS_OAUTH_SECRET=                     # Tailscale OAuth secret

# Server Access
SSH_PRIVATE_KEY=                     # SSH key for server access
SERVER_HOST=                         # Tailscale IP of deployment server
SERVER_USER=                         # SSH username on server

# Production Credentials
DB_PASSWORD=                         # Production database password
REDIS_PASSWORD=                      # Production Redis password
GITHUB_TOKEN=                        # Auto-provided by GitHub Actions
```

**Setup Instructions:** See `.github/workflows/QUICK_START.md`
