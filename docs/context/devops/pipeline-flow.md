# CI/CD Pipeline - Flow Documentation

## Overview

Unified CI/CD pipeline with sequential stages: Build → Test → Stage → E2E → Production

**Trigger**: Push to `main` or `feature/**` branches, Pull Requests to `main`

### Deployment Strategy

- **Feature branches (`feature/*`)**: Deploy to staging for testing and validation
  - Pipeline: Build → Test → **Deploy to Staging** → E2E Test
  - Allows developers to test features in staging environment before merging
  - No production deployment from feature branches

- **Main branch (`main`)**: Full deployment pipeline including production
  - Pipeline: Build → Test → Deploy to Staging → E2E Test → **Deploy to Production**
  - Production deployment only after all tests pass

- **Pull Requests**: Build and test only, no deployments
  - Pipeline: Build → Test
  - Ensures code quality before merge

---

## Pipeline Flow

### Stage 1: Build and Test (45 min timeout)

#### Build Phase
1. **Checkout code** from repository
2. **Extract versions** from:
   - Backend: `backend/config/__init__.py`
   - Frontend: `frontend/package.json`
3. **Build development containers**:
   - Backend: `backend-dev:version`
   - Frontend: `frontend-dev:version`
   - Uses GitHub Actions cache for layer optimization
4. **Clean up** existing containers (mandatory protocol)

#### Test Phase
5. **Backend tests**:
   - Start dependencies: PostgreSQL + Redis
   - Wait for service health checks
   - Run pytest with coverage (`-n auto` for parallel execution)
   - Tests use: `config.settings.testing`, PostgreSQL test database

6. **Frontend tests**:
   - Run unit/integration tests: `npm run test:run`

7. **Code quality checks**:
   - Backend: `black`, `isort`, `flake8`
   - Frontend: `npm run lint`

#### Publish Phase
8. **Build production containers**:
   - Target: `production` stage in Dockerfiles
   - Push to GitHub Container Registry (`ghcr.io`)
   - Tags: `version`, `version-sha`, `latest`, `branch-name`

---

### Stage 2: Deploy to Staging (20 min timeout)

**Condition**: On `main` branch OR `feature/*` branches push, after successful build

1. **Connect to server** via Tailscale VPN
2. **Setup SSH** authentication
3. **Prepare environment files**:
   - `.env.docker` (base configuration)
   - `.env.staging` (staging-specific settings)
   - Root `.env` (docker-compose variables)
4. **Transfer files** via SCP:
   - `docker-compose.yml`, `compose.staging.yml`
   - Environment files
5. **Deploy on server**:
   - Login to container registry
   - Pull SHA-tagged images (immutable)
   - Stop existing containers
   - Start services with `--force-recreate`
   - Wait for health checks (max 120s)
6. **Verify deployment**:
   - Poll `/api/v1/status/` endpoint
   - Max 12 retries × 5s interval

**Target**: `https://staging.edenco.online`

---

### Stage 3: E2E Testing (30 min timeout)

**Condition**: After successful staging deployment (from main or feature branches)

1. **Connect to staging** via Tailscale
2. **Create test config** pointing to staging server
3. **Build test runner** container
4. **Run E2E tests**:
   - Execute Playwright tests against staging
   - Reporters: HTML, JSON, list
5. **Upload test artifacts** (30 day retention)
6. **Block production** if tests fail

---

### Stage 4: Deploy to Production (20 min timeout)

**Condition**: ONLY from `main` branch, after successful staging deploy AND E2E tests pass

1. **Connect to production server** via Tailscale
2. **Setup SSH** authentication
3. **Prepare environment files**:
   - `.env.docker` (production settings)
   - `.env.production` (production-specific)
   - Root `.env` with production database credentials
4. **Transfer configuration** files via SCP
5. **Deploy on production server**:
   - Login to container registry
   - Pull same SHA-tagged images from staging
   - Stop existing containers
   - Start services with `--force-recreate`
   - Wait for health checks (max 120s)
6. **Verify production deployment**:
   - Poll `/api/v1/status/` endpoint
   - Max 12 retries × 5s interval

**Target**: `https://yourdomain.com`

---

## Failure Handling

**Automated Issue Creation** runs if any stage fails:
- Detects failed stage
- Creates GitHub issue with:
  - Failed stage name
  - Run number, branch, commit
  - Full pipeline status
  - Link to workflow logs
- Labels: `bug`
- Auto-closes when fixed with "Fix issue #N" commit message

---

## Docker Compose Architecture

### Development Stack
```
docker-compose.yml (base)
├── db (PostgreSQL)
├── redis (Redis)
├── backend (Django)
├── frontend (React/Vite)
├── proxy (Nginx reverse proxy - ONLY exposed port)
└── celery (optional, profile: with-celery)
```

### Test Environment
```
docker-compose.yml + compose.test.yml
├── Separate test database/redis instances
├── Test ports: db:5433, redis:6380, backend:8001, frontend:5174
└── test-runner (Playwright E2E tests)
```

### Staging/Production
```
docker-compose.yml + compose.{staging|production}.yml
├── Pulls pre-built images from registry
├── Production-optimized settings
├── Network isolation (only proxy exposed)
└── Resource limits configured
```

---

## Key Features

### Container Registry
- **Default**: GitHub Container Registry (`ghcr.io`)
- **Images**: Tagged with version + SHA for immutability
- **Authentication**: Automatic via `GITHUB_TOKEN`

### Caching Strategy
Multi-level fallback:
1. Version + branch specific
2. Version + main branch
3. Branch fallback
4. Main branch fallback
5. General cache

### Network Security
- **Development**: All ports exposed for debugging
- **Production**: ONLY reverse proxy port exposed
- **Service isolation**: Internal docker network only
- **VPN**: All deployments via Tailscale encrypted tunnel

### Health Checks
All services have healthcheck configurations:
- **Database**: `pg_isready` + query execution
- **Redis**: `PING` command
- **Backend**: `/api/v1/health/` endpoint
- **Frontend**: Vite dev server check
- **Proxy**: nginx status

---

## Quick Commands

### Local Development
```bash
docker compose up                    # Start all services
docker compose up -d                 # Background mode
docker compose down                  # Stop all services
docker compose logs -f SERVICE       # View logs
./docker-dev.sh start               # Helper script
```

### Testing Locally
```bash
docker compose -f docker-compose.yml -f compose.test.yml up -d
./testing/run-tests.sh              # Run all tests
./testing/run-tests.sh --suite e2e  # E2E tests only
```

### Manual Deployment (Server)
```bash
cd ~/deployments/app-staging
docker compose -f docker-compose.yml -f compose.staging.yml pull
docker compose -f docker-compose.yml -f compose.staging.yml up -d
docker compose ps                   # Check status
```

---

## Environment Variables

### Build Stage
- `BACKEND_VERSION`: Extracted from `config/__init__.py`
- `FRONTEND_VERSION`: Extracted from `package.json`

### Deployment Stage
- `CONTAINER_REGISTRY`: Container registry URL (default: `ghcr.io`)
- `REPOSITORY_OWNER`: GitHub org/user (lowercase)
- `BACKEND_IMAGE`: Full image path with SHA tag
- `FRONTEND_IMAGE`: Full image path with SHA tag
- `DB_PASSWORD`: Database password (from secrets)
- `REDIS_PASSWORD`: Redis password (from secrets)

### GitHub Secrets Required
- `TS_OAUTH_CLIENT_ID`: Tailscale OAuth client
- `TS_OAUTH_SECRET`: Tailscale OAuth secret
- `SSH_PRIVATE_KEY`: SSH key for server access
- `SERVER_HOST`: Tailscale IP of deployment server
- `SERVER_USER`: SSH username on server
- `DB_PASSWORD`: Production database password
- `REDIS_PASSWORD`: Production Redis password

---

## Service Dependencies

**Layer 1** (No dependencies):
- db, redis

**Layer 2** (Depends on Layer 1):
- backend (requires: db, redis healthy)

**Layer 3** (Depends on Layer 2):
- frontend (requires: backend healthy)

**Layer 4** (Depends on Layers 2+3):
- proxy (requires: frontend, backend healthy)

**Optional**:
- celery (requires: db, redis healthy)

---

## Concurrency Control

- **Cancel in-progress**: Enabled per branch/PR
- **Group**: `${{ github.workflow }}-${{ github.ref }}`
- **Prevents**: Multiple deployments of same branch

---

## Summary

1. **Code Change** → Push to repository
2. **Build** → Extract versions, build dev containers, run in parallel
3. **Test** → Backend (pytest) + Frontend (vitest) + Linting (all parallel)
4. **Publish** → Build production images, push to registry
5. **Deploy Staging** → Pull images, deploy via SSH, verify health
6. **E2E Test** → Playwright tests against staging
7. **Deploy Production** → Pull same images, deploy, verify health
8. **Monitor** → Auto-create issue on failure

**Total Pipeline Time**: ~1.5-2 hours for full main branch deploy
**Safety**: E2E validation before production, immutable image tags
