# Global Configuration

Configuration requirements for all services across environments.

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
VITE_APP_VERSION=1.0.0              # Version
VITE_DEBUG=true                     # Debug mode

# Features
VITE_ENABLE_ANALYTICS=false         # Analytics
VITE_ENABLE_ERROR_REPORTING=false   # Error reporting

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
- `docker-compose.yml` - Base orchestration
- `compose.override.yml` - Local dev overrides
- `compose.production.yml` - Production
- `compose.staging.yml` - Staging
- `compose.test.yml` - Test environment

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
docker compose -f compose.test.yml up
```

### Environment Files Priority
1. `.env.{environment}` (local, staging, production)
2. `.env.local` (git-ignored overrides)
3. `.env` (fallback)
