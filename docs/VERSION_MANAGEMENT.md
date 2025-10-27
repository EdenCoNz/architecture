# Application Version Management Guide

**Last Updated**: 2025-10-28
**Feature**: #16 - Application Version Management

## Overview

This guide provides comprehensive documentation on how to manage application versions across frontend and backend services using semantic versioning. Understanding version management is critical for:

- Controlling Docker build cache invalidation
- Tracking deployments across environments
- Enabling version-aware rollbacks
- Debugging production issues
- Managing release cycles

## Table of Contents

1. [Quick Start](#quick-start)
2. [Semantic Versioning Explained](#semantic-versioning-explained)
3. [How to Update Versions](#how-to-update-versions)
4. [Impact on Docker Builds](#impact-on-docker-builds)
5. [Impact on CI/CD Pipelines](#impact-on-ci-cd-pipelines)
6. [Impact on Deployments](#impact-on-deployments)
7. [Version Exposure and Verification](#version-exposure-and-verification)
8. [Common Workflows](#common-workflows)
9. [Troubleshooting](#troubleshooting)

---

## Quick Start

### For New Team Members

**To increment a version:**

1. **Frontend**: Edit `/frontend/package.json` and change the `version` field
2. **Backend**: Edit `/backend/config/__init__.py` and change the `__version__` constant
3. Commit your changes
4. Push to trigger CI/CD rebuild with new version

**To verify deployed version:**

- **Frontend**: Open browser console or check `window.APP_VERSION`
- **Backend**: Query `GET /api/v1/status/` endpoint

**Quick Reference:**

```bash
# Check current versions
grep '"version"' frontend/package.json
grep '__version__' backend/config/__init__.py

# View version in running containers
docker inspect <container> --format='{{index .Config.Labels "app.version"}}'

# Filter containers by version
docker images --filter "label=app.version=1.0.0"
```

---

## Semantic Versioning Explained

### Format: MAJOR.MINOR.PATCH

Semantic versioning follows the format `X.Y.Z` where:

- **X** = MAJOR version
- **Y** = MINOR version
- **Z** = PATCH version

### Version Increment Rules

#### MAJOR Version (X.0.0)

**When to increment:**
- Breaking changes that require user or API consumer updates
- Fundamental architecture changes
- Database schema changes requiring migration
- API endpoint removals or incompatible modifications
- Changes to authentication/authorization mechanisms

**Examples:**
- `1.5.3 → 2.0.0`: Removed deprecated API endpoints
- `2.1.4 → 3.0.0`: Changed authentication from session-based to JWT-only
- `3.2.1 → 4.0.0`: Migrated database schema with breaking changes

**Impact:**
- Requires coordination with frontend/backend teams
- May require data migrations
- Usually requires updated documentation
- Should be announced to all stakeholders

#### MINOR Version (X.Y.0)

**When to increment:**
- New features added in backward-compatible manner
- New API endpoints that don't break existing ones
- Optional new functionality
- Performance improvements without breaking changes
- New configuration options with sensible defaults

**Examples:**
- `1.2.3 → 1.3.0`: Added new user profile export feature
- `2.5.1 → 2.6.0`: Added optional two-factor authentication
- `3.1.4 → 3.2.0`: Added new analytics dashboard

**Impact:**
- Safe to deploy without coordination
- Existing functionality continues to work
- Users can adopt new features at their own pace
- Should be documented in release notes

#### PATCH Version (X.Y.Z)

**When to increment:**
- Bug fixes that don't change functionality
- Security patches
- Performance improvements
- Documentation updates
- Dependency updates (without breaking changes)
- Internal refactoring

**Examples:**
- `1.2.3 → 1.2.4`: Fixed login form validation error
- `2.5.1 → 2.5.2`: Patched security vulnerability
- `3.1.4 → 3.1.5`: Fixed memory leak in background job

**Impact:**
- Safe to deploy immediately
- No functional changes to existing features
- Usually automated deployment
- Minimal documentation needed

### Pre-release and Build Metadata (Optional)

While not currently implemented in this project, semantic versioning supports:

- **Pre-release**: `1.0.0-alpha`, `1.0.0-beta.1`, `1.0.0-rc.2`
- **Build metadata**: `1.0.0+20130313144700`, `1.0.0-beta+exp.sha.5114f85`

These can be added in the future if needed for release management.

---

## How to Update Versions

### Frontend Version Update

**Location**: `/frontend/package.json`

**Current version format:**
```json
{
  "name": "frontend",
  "version": "1.0.0",
  ...
}
```

**Steps to update:**

1. Open `/frontend/package.json` in your editor
2. Locate the `version` field (typically line 4)
3. Update the version following semantic versioning rules
4. Save the file

**Example changes:**

```json
# Patch update (bug fix)
"version": "1.0.0"  →  "version": "1.0.1"

# Minor update (new feature)
"version": "1.0.1"  →  "version": "1.1.0"

# Major update (breaking change)
"version": "1.1.0"  →  "version": "2.0.0"
```

**Verification:**

```bash
# Check version was updated
grep '"version"' frontend/package.json

# Verify npm recognizes the version
cd frontend && npm version --json

# Test build includes new version
npm run build
grep -r "1.0.1" dist/  # Replace 1.0.1 with your version
```

### Backend Version Update

**Location**: `/backend/config/__init__.py`

**Current version format:**
```python
# Application version using semantic versioning (MAJOR.MINOR.PATCH)
# This version is used by all backend services and can be imported
# from any module: from config import __version__
__version__ = "1.0.0"
```

**Steps to update:**

1. Open `/backend/config/__init__.py` in your editor
2. Locate the `__version__` constant (typically line 17)
3. Update the version string following semantic versioning rules
4. Save the file

**Example changes:**

```python
# Patch update (bug fix)
__version__ = "1.0.0"  →  __version__ = "1.0.1"

# Minor update (new feature)
__version__ = "1.0.1"  →  __version__ = "1.1.0"

# Major update (breaking change)
__version__ = "1.1.0"  →  __version__ = "2.0.0"
```

**Verification:**

```bash
# Check version was updated
grep '__version__' backend/config/__init__.py

# Verify Python can import the version
docker compose run --rm backend python -c "from config import __version__; print(f'Backend version: {__version__}')"

# Run tests to ensure version is accessible
docker compose run --rm backend pytest tests/unit/test_version.py -v
```

### Version Update Checklist

When updating versions, complete this checklist:

- [ ] Determine correct version increment (MAJOR, MINOR, or PATCH)
- [ ] Update frontend version in `/frontend/package.json` (if frontend changes)
- [ ] Update backend version in `/backend/config/__init__.py` (if backend changes)
- [ ] Verify version syntax is correct (X.Y.Z format)
- [ ] Run local tests to ensure version is accessible
- [ ] Update CHANGELOG.md with version changes (if maintained)
- [ ] Commit with clear message: `chore: bump version to X.Y.Z`
- [ ] Push to trigger CI/CD pipeline
- [ ] Verify CI/CD builds with new version
- [ ] Check deployed version in target environment

---

## Impact on Docker Builds

Version changes have significant impact on Docker build caching and performance. Understanding this behavior is critical for efficient development and deployment.

### How Version Affects Docker Cache

**Cache Invalidation Mechanism:**

Both frontend and backend Dockerfiles use version information to control Docker layer caching. When the version changes, Docker invalidates the cache for version-dependent layers and all subsequent layers.

**Frontend Dockerfile** (`/frontend/Dockerfile`):
```dockerfile
# Builder stage - version extraction
FROM node:20-alpine AS builder
WORKDIR /app

# Step 1: Install dependencies (cached independently of version)
COPY package*.json ./
RUN npm ci

# Step 2: Extract and store version (cache invalidates when version changes)
RUN node -p "require('./package.json').version" > /tmp/app-version.txt

# Step 3: Copy source code and build (rebuilds when version or code changes)
COPY . .
RUN npm run build
```

**Backend Dockerfile** (`/backend/Dockerfile`):
```dockerfile
# Development stage - version ARG
FROM python:3.12-slim AS development

# Version ARG (cache invalidates when APP_VERSION build arg changes)
ARG APP_VERSION=1.0.0
LABEL app.version="${APP_VERSION}"

# Install dependencies (cached if version unchanged)
COPY requirements/base.txt requirements/dev.txt ./requirements/
RUN pip install --no-cache-dir -r requirements/dev.txt
```

### Cache Behavior Scenarios

#### Scenario 1: Version Unchanged, Code Changed

**What happens:**
- Version layer: **CACHED** ✓
- Dependency installation: **CACHED** ✓
- Code copy: **REBUILT** (detects change)
- Build step: **REBUILT** (depends on code)

**Build time**: Fast (30-60 seconds)
- Dependencies reused from cache
- Only code and build steps execute

**Example:**
```bash
# First build: version 1.0.0, original code
docker build -f frontend/Dockerfile --target production \
  --build-arg VERSION=1.0.0 -t frontend:1.0.0 frontend
# Build time: 75 seconds

# Modify frontend/src/App.tsx

# Second build: version 1.0.0, modified code
docker build -f frontend/Dockerfile --target production \
  --build-arg VERSION=1.0.0 -t frontend:1.0.0-v2 frontend
# Build time: 35 seconds (dependencies cached)
```

#### Scenario 2: Version Changed, Code Unchanged

**What happens:**
- Version layer: **REBUILT** (version changed)
- Dependency installation: **CACHED** ✓ (npm/pip dependencies unchanged)
- Code copy: **REBUILT** (follows version layer)
- Build step: **REBUILT** (follows code layer)

**Build time**: Medium (60-90 seconds)
- Dependencies reused from cache
- Version extraction, code copy, and build execute

**Example:**
```bash
# First build: version 1.0.0
docker build -f backend/Dockerfile --target production \
  --build-arg APP_VERSION=1.0.0 -t backend:1.0.0 backend
# Build time: 120 seconds

# Change backend/config/__init__.py: __version__ = "1.0.1"

# Second build: version 1.0.1
docker build -f backend/Dockerfile --target production \
  --build-arg APP_VERSION=1.0.1 -t backend:1.0.1 backend
# Build time: 85 seconds (dependencies cached, version layer rebuilt)
```

#### Scenario 3: Version Unchanged, Code Unchanged

**What happens:**
- All layers: **CACHED** ✓
- No rebuilding occurs

**Build time**: Very fast (1-5 seconds)

**Example:**
```bash
# First build
docker build -f frontend/Dockerfile --target production \
  --build-arg VERSION=1.0.0 -t frontend:1.0.0 frontend
# Build time: 75 seconds

# Second build (no changes)
docker build -f frontend/Dockerfile --target production \
  --build-arg VERSION=1.0.0 -t frontend:1.0.0-rebuild frontend
# Build time: 2 seconds (all layers cached)
```

#### Scenario 4: Version Changed, Dependencies Changed

**What happens:**
- Version layer: **REBUILT** (version changed)
- Dependency installation: **REBUILT** (package files changed)
- Code copy: **REBUILT** (follows dependencies)
- Build step: **REBUILT** (follows code)

**Build time**: Slow (120-180 seconds)
- Full rebuild of all layers
- No cache reuse except base image

**Example:**
```bash
# First build: version 1.0.0
# Second build: version 1.1.0 + added new npm packages
# Build time: 150 seconds (no cache reuse)
```

### Strategic Layer Placement

The Dockerfiles are optimized for cache efficiency through strategic layer ordering:

**Optimal order (least to most frequently changed):**

1. **Base image** - Rarely changes
2. **System dependencies** - Changes infrequently
3. **Package files** (`package.json`, `requirements.txt`) - Moderate change frequency
4. **Dependency installation** - Expensive operation, should be cached
5. **Version extraction/ARG** - Changes with each release
6. **Source code** - Changes frequently
7. **Build step** - Depends on code

This ordering ensures:
- Dependencies are cached separately from version changes
- Version changes don't trigger dependency reinstallation
- Code changes don't invalidate dependency cache
- Maximum cache reuse for common development workflows

### Container Labels

All built containers include version labels for inspection:

```bash
# Inspect container version
docker inspect frontend:1.0.0 --format='{{index .Config.Labels "app.version"}}'
# Output: 1.0.0

# View all labels
docker inspect frontend:1.0.0 --format='{{json .Config.Labels}}' | python3 -m json.tool
```

**Frontend labels** (comprehensive OCI-compliant):
- `app.version`: Application version (e.g., "1.0.0")
- `app.component`: Component name (e.g., "frontend")
- `app.type`: Application type (e.g., "web-application")
- `org.opencontainers.image.version`: OCI standard version
- `org.opencontainers.image.created`: Build timestamp
- `org.opencontainers.image.revision`: Git commit SHA
- `org.opencontainers.image.title`: Image title
- `org.opencontainers.image.description`: Image description

**Backend labels**:
- `app.version`: Application version (e.g., "1.0.0")

---

## Impact on CI/CD Pipelines

Version changes trigger specific behaviors in the GitHub Actions CI/CD pipeline, affecting build caching, deployment strategies, and artifact naming.

### Version Extraction in CI/CD

**Workflow**: `.github/workflows/unified-ci-cd.yml`

The pipeline automatically extracts versions from both frontend and backend:

```yaml
# Frontend version extraction
- name: Extract frontend version
  id: frontend_version
  run: |
    VERSION=$(node -p "require('./frontend/package.json').version")
    echo "version=$VERSION" >> $GITHUB_OUTPUT

# Backend version extraction
- name: Extract backend version
  id: backend_version
  run: |
    VERSION=$(grep -E "^__version__\s*=\s*" backend/config/__init__.py | cut -d'"' -f2)
    echo "version=$VERSION" >> $GITHUB_OUTPUT
```

**Usage in subsequent steps:**
- `${{ steps.frontend_version.outputs.version }}`
- `${{ steps.backend_version.outputs.version }}`

### Multi-Level Cache Fallback Strategy

The pipeline uses a sophisticated 5-level cache fallback strategy that incorporates version information:

**Cache scope hierarchy:**

1. **Version + Branch**: `backend-prod-v1.0.0-feature-123`
   - Most specific cache for current version on current branch
   - Highest priority, checked first

2. **Version + Main**: `backend-prod-v1.0.0-main`
   - Version-specific cache from main branch
   - Fallback for feature branches with same version

3. **Branch**: `backend-prod-feature-123`
   - Cross-version cache for current branch
   - Allows some cache reuse when version changes

4. **Main**: `backend-prod-main`
   - Cross-version cache from main branch
   - Stable fallback for all branches

5. **General**: `backend-prod`
   - Last resort fallback
   - Minimal cache reuse

**Implementation example:**

```yaml
- name: Build backend production container
  uses: docker/build-push-action@v5
  with:
    context: backend
    file: backend/Dockerfile
    target: production
    build-args: |
      APP_VERSION=${{ steps.backend_version.outputs.version }}
    cache-from: |
      type=gha,scope=backend-prod-v${{ steps.backend_version.outputs.version }}-${{ github.ref_name }}
      type=gha,scope=backend-prod-v${{ steps.backend_version.outputs.version }}-main
      type=gha,scope=backend-prod-${{ github.ref_name }}
      type=gha,scope=backend-prod-main
      type=gha,scope=backend-prod
    cache-to: type=gha,mode=max,scope=backend-prod-v${{ steps.backend_version.outputs.version }}-${{ github.ref_name }}
```

### Cache Behavior in CI/CD

#### Scenario 1: Feature Branch, Version Unchanged

**Context:**
- Branch: `feature/add-user-profile`
- Version: `1.0.0` (same as main)
- Previous builds exist for version `1.0.0`

**Cache resolution:**
1. Try: `backend-prod-v1.0.0-feature/add-user-profile` → **MISS** (first build on this branch)
2. Try: `backend-prod-v1.0.0-main` → **HIT** ✓
3. Use cache from main branch with same version

**Result**: Fast build using version-specific cache from main

#### Scenario 2: Main Branch, Version Incremented

**Context:**
- Branch: `main`
- Version: `1.0.0 → 1.0.1` (incremented)
- Previous builds exist for version `1.0.0`

**Cache resolution:**
1. Try: `backend-prod-v1.0.1-main` → **MISS** (new version)
2. Try: `backend-prod-v1.0.1-main` → **MISS** (no such cache)
3. Try: `backend-prod-main` → **PARTIAL HIT** (dependency layers only)

**Result**: Rebuild with partial cache reuse (dependencies cached, version+ layers rebuilt)

#### Scenario 3: Multiple Versions in Development

**Context:**
- Branch: `main`
- Versions: `1.0.0`, `1.0.1`, `1.1.0` all actively developed
- Multiple version caches exist

**Cache isolation:**
- `1.0.0` builds: Use `backend-prod-v1.0.0-*` caches
- `1.0.1` builds: Use `backend-prod-v1.0.1-*` caches
- `1.1.0` builds: Use `backend-prod-v1.1.0-*` caches

**Result**: Each version maintains isolated cache, enabling fast rollbacks

### Build Artifacts and Tagging

**Container image tags** include version information:

**Main branch (production deployments):**
```yaml
tags: |
  ghcr.io/${{ github.repository }}/backend:latest
  ghcr.io/${{ github.repository }}/backend:${{ steps.backend_version.outputs.version }}
  ghcr.io/${{ github.repository }}/backend:prod-${{ github.sha }}
  ghcr.io/${{ github.repository }}/backend:prod-${{ steps.backend_version.outputs.version }}-${{ github.sha }}
```

**Feature branches:**
```yaml
tags: |
  ghcr.io/${{ github.repository }}/backend:prod-${{ github.ref_name }}
  ghcr.io/${{ github.repository }}/backend:prod-${{ github.sha }}
  ghcr.io/${{ github.repository }}/backend:prod-${{ steps.backend_version.outputs.version }}-${{ github.sha }}
```

**Tag examples for version 1.0.1:**
- `ghcr.io/org/repo/backend:latest`
- `ghcr.io/org/repo/backend:1.0.1`
- `ghcr.io/org/repo/backend:prod-8ed3c59`
- `ghcr.io/org/repo/backend:prod-1.0.1-8ed3c59`

### Performance Impact

**Typical build times with version-based caching:**

| Scenario | Dependencies | Version Layer | Total Build Time |
|----------|--------------|---------------|------------------|
| No changes | Cached | Cached | 10-15 seconds |
| Code change only | Cached | Cached | 30-60 seconds |
| Version change only | Cached | Rebuilt | 60-90 seconds |
| Dependency change | Rebuilt | Rebuilt | 120-180 seconds |
| Clean build | Rebuilt | Rebuilt | 120-180 seconds |

**Cache storage:**
- GitHub Actions provides 10 GB cache storage per repository
- Cache entries are evicted after 7 days of inactivity
- `mode=max` caches all intermediate layers (recommended)
- `mode=min` caches only final image (not recommended)

### CI/CD Pipeline Stages

**Complete pipeline flow with version awareness:**

```
1. Code Quality (Parallel)
   ├─ Lint
   ├─ Typecheck
   ├─ Unit Tests
   └─ Security Audit

2. Extract Versions
   ├─ Frontend version from package.json
   └─ Backend version from config/__init__.py

3. Build Containers (Parallel)
   ├─ Frontend Dev (with VERSION build arg + version-based cache)
   ├─ Frontend Prod (with VERSION build arg + version-based cache)
   ├─ Backend Dev (with APP_VERSION build arg + version-based cache)
   └─ Backend Prod (with APP_VERSION build arg + version-based cache)

4. Security Scan (Parallel)
   ├─ Frontend container (Trivy scan)
   └─ Backend container (Trivy scan)

5. Functional Tests
   ├─ Container startup validation
   └─ API health checks

6. Publish to Registry
   ├─ Multi-arch builds (linux/amd64, linux/arm64 on main)
   ├─ Version-based tagging
   └─ GHCR publishing

7. Automation
   ├─ Auto-close linked issues
   └─ Failure notifications
```

---

## Impact on Deployments

Version changes affect deployment strategies, rollback procedures, and production monitoring.

### Deployment Environments

**Version tracking by environment:**

| Environment | Version Source | Deployment Method | Update Frequency |
|-------------|----------------|-------------------|------------------|
| **Local Development** | Code checkout | Docker Compose | Continuous |
| **Staging** | Git branch (main) | Docker Compose | On commit to main |
| **Production** | Tagged release | Container registry | Manual/scheduled |
| **Testing** | Feature branches | Docker Compose | On PR |

### Deployment Strategies

#### Blue-Green Deployment

**Using version tags for zero-downtime deployments:**

```bash
# Current production: version 1.0.0
docker compose -f docker-compose.yml -f compose.production.yml up -d

# Deploy new version 1.0.1 alongside 1.0.0
docker pull ghcr.io/org/repo/backend:1.0.1
docker pull ghcr.io/org/repo/frontend:1.0.1

# Test new version (on different ports or internal network)
docker compose -f docker-compose.yml -f compose.production.yml \
  -p app-blue up -d

# Verify new version health
curl http://blue-backend:8000/api/v1/status/
# Response: {"version": "1.0.1", ...}

# Switch traffic to new version (update reverse proxy config)
# Rollback: Switch traffic back to 1.0.0 if issues detected
```

#### Rolling Deployment

**Gradual rollout by version:**

```bash
# Update 1 instance at a time
docker service update --image ghcr.io/org/repo/backend:1.0.1 \
  --update-parallelism 1 --update-delay 30s backend
```

#### Canary Deployment

**Route percentage of traffic to new version:**

```nginx
# Nginx configuration for canary deployment
upstream backend {
    server backend-1.0.0:8000 weight=9;  # 90% traffic
    server backend-1.0.1:8000 weight=1;  # 10% traffic
}
```

### Rollback Procedures

**Quick rollback using version tags:**

```bash
# Method 1: Redeploy previous version
docker compose -f docker-compose.yml -f compose.production.yml down
docker compose -f docker-compose.yml -f compose.production.yml \
  pull ghcr.io/org/repo/backend:1.0.0
docker compose -f docker-compose.yml -f compose.production.yml up -d

# Method 2: Use Git to revert version
git revert <commit-that-bumped-version>
git push  # Triggers CI/CD to rebuild with old version

# Method 3: Pull specific version from registry
docker pull ghcr.io/org/repo/backend:1.0.0
docker tag ghcr.io/org/repo/backend:1.0.0 ghcr.io/org/repo/backend:latest
docker compose up -d backend
```

**Verification after rollback:**

```bash
# Check running version
docker inspect backend --format='{{index .Config.Labels "app.version"}}'
# Expected: 1.0.0

# Query status endpoint
curl http://localhost:8000/api/v1/status/
# Expected: {"version": "1.0.0", ...}

# Check frontend version
curl http://localhost/  # Open browser console
# Expected: window.APP_VERSION === "1.0.0"
```

### Production Monitoring

**Version tracking in monitoring systems:**

```bash
# Prometheus metrics (example)
app_version_info{version="1.0.1", component="backend"} 1

# Grafana dashboard query
avg by (version) (up{job="backend"})

# Log aggregation (ELK, Splunk)
fields @timestamp, version, message
| filter version = "1.0.1"
| stats count() by version
```

**Health check integration:**

```yaml
# docker-compose.yml health check
services:
  backend:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/status/"]
      interval: 30s
      timeout: 3s
      retries: 3
```

### Version-Aware Deployment Checklist

Before deploying a new version:

- [ ] Version increment follows semantic versioning rules
- [ ] CI/CD pipeline completed successfully for new version
- [ ] Security scans passed (Trivy reports no critical vulnerabilities)
- [ ] Functional tests passed in CI/CD
- [ ] Staging environment deployed and tested with new version
- [ ] Database migrations tested (if MAJOR version change)
- [ ] Rollback procedure documented and tested
- [ ] Monitoring dashboards updated to track new version
- [ ] Stakeholders notified (if MAJOR or significant MINOR change)
- [ ] Deployment window scheduled (if high-impact change)

After deploying:

- [ ] Verify version via status endpoint
- [ ] Check container labels match expected version
- [ ] Monitor error rates and performance metrics
- [ ] Confirm health checks passing
- [ ] Document deployment in change log
- [ ] Update tracking systems (Jira, etc.)

---

## Version Exposure and Verification

### Frontend Version Verification

**Browser Console:**

Open browser developer tools console, you'll see:
```
🚀 Frontend Application v1.0.0
Environment: production
Programmatic access: window.APP_VERSION or window.__APP_INFO__
```

**Programmatic Access:**

```javascript
// Quick version check
console.log(window.APP_VERSION);
// Output: "1.0.0"

// Detailed version info
console.log(window.__APP_INFO__);
// Output: {
//   version: "1.0.0",
//   name: "Frontend Application",
//   environment: "production",
//   buildDate: "2025-10-28T00:00:00Z"
// }
```

**Source Code:**

```javascript
import { getVersion, getVersionInfo } from '@/utils/version';

// Get version string
const version = getVersion();
console.log(version);  // "1.0.0"

// Get detailed info
const info = getVersionInfo();
console.log(info);  // {version, name, environment, buildDate}
```

### Backend Version Verification

**Status Endpoint:**

```bash
# Query status endpoint
curl http://localhost:8000/api/v1/status/

# Response (formatted)
{
  "status": "healthy",
  "timestamp": "2025-10-28T12:00:00Z",
  "version": "1.0.0",
  "api_version": "v1",
  "environment": "production",
  "uptime_seconds": 3600,
  "database": {
    "status": "connected",
    "latency_ms": 5
  }
}
```

**Python Code:**

```python
from config import __version__

print(f"Backend version: {__version__}")
# Output: Backend version: 1.0.0
```

**Django Management Command:**

```bash
# From Django shell
docker compose exec backend python manage.py shell
>>> from config import __version__
>>> print(__version__)
1.0.0
```

### Container Version Verification

**Docker Inspect:**

```bash
# Check container version label
docker inspect backend --format='{{index .Config.Labels "app.version"}}'
# Output: 1.0.0

# View all labels
docker inspect backend --format='{{json .Config.Labels}}' | python3 -m json.tool

# Check frontend OCI labels
docker inspect frontend --format='{{index .Config.Labels "org.opencontainers.image.version"}}'
# Output: 1.0.0
```

**List Containers by Version:**

```bash
# Find all containers with version 1.0.0
docker ps --filter "label=app.version=1.0.0" --format "table {{.Names}}\t{{.Image}}\t{{.Status}}"

# List all images with version label
docker images --filter "label=app.version=1.0.0" --format "table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.CreatedSince}}"
```

**Compare Versions:**

```bash
# List all versions in registry
docker images --format "{{.Repository}}:{{.Tag}}" | grep backend | sort

# Find newest version
docker images backend --format "{{.Tag}}" | grep -E "^[0-9]+\.[0-9]+\.[0-9]+$" | sort -V -r | head -1
# Output: 1.0.1
```

### Multi-Environment Verification

**Check versions across environments:**

```bash
#!/bin/bash
# check-versions.sh

echo "=== Version Verification Across Environments ==="

# Local
echo -e "\nLocal Development:"
grep '"version"' frontend/package.json
grep '__version__' backend/config/__init__.py

# Staging
echo -e "\nStaging:"
curl -s https://staging.example.com/api/v1/status/ | jq -r '.version'

# Production
echo -e "\nProduction:"
curl -s https://api.example.com/api/v1/status/ | jq -r '.version'

# Container Registry
echo -e "\nContainer Registry (Latest Tags):"
docker pull ghcr.io/org/repo/backend:latest -q
docker inspect ghcr.io/org/repo/backend:latest --format='{{index .Config.Labels "app.version"}}'
```

---

## Common Workflows

### Workflow 1: Release a Patch Version (Bug Fix)

**Scenario**: Fix a bug in production without adding new features.

**Steps:**

1. **Create fix branch:**
   ```bash
   git checkout -b fix/user-login-validation
   ```

2. **Implement fix** in code

3. **Update version** (PATCH increment):
   ```bash
   # Frontend (if frontend bug)
   # Edit frontend/package.json: "1.0.0" → "1.0.1"

   # Backend (if backend bug)
   # Edit backend/config/__init__.py: "1.0.0" → "1.0.1"
   ```

4. **Test locally:**
   ```bash
   # Build and test with new version
   docker compose down -v
   docker compose up --build

   # Verify version
   curl http://localhost:8000/api/v1/status/ | jq '.version'
   # Expected: "1.0.1"
   ```

5. **Commit and push:**
   ```bash
   git add frontend/package.json backend/config/__init__.py
   git commit -m "chore: bump version to 1.0.1 for login validation fix"
   git push origin fix/user-login-validation
   ```

6. **Create PR** and wait for CI/CD to pass

7. **Merge to main** and deploy:
   ```bash
   # CI/CD automatically builds version 1.0.1
   # Deploy to staging first, then production
   ```

8. **Verify deployment:**
   ```bash
   # Staging
   curl https://staging.example.com/api/v1/status/ | jq '.version'

   # Production
   curl https://api.example.com/api/v1/status/ | jq '.version'
   ```

### Workflow 2: Release a Minor Version (New Feature)

**Scenario**: Add a new feature that doesn't break existing functionality.

**Steps:**

1. **Create feature branch:**
   ```bash
   git checkout -b feature/user-profile-export
   ```

2. **Implement feature** with tests

3. **Update version** (MINOR increment):
   ```bash
   # Frontend (if frontend feature)
   # Edit frontend/package.json: "1.0.1" → "1.1.0"

   # Backend (if backend feature)
   # Edit backend/config/__init__.py: "1.0.1" → "1.1.0"
   ```

4. **Update documentation** for new feature

5. **Test thoroughly:**
   ```bash
   # Run full test suite
   docker compose run --rm frontend npm test
   docker compose run --rm backend pytest

   # Test in isolated environment
   docker compose -f docker-compose.yml -f compose.staging.yml up
   ```

6. **Commit and push:**
   ```bash
   git add .
   git commit -m "feat: add user profile export feature (v1.1.0)"
   git push origin feature/user-profile-export
   ```

7. **Create PR**, get code review, merge

8. **Tag release** in Git:
   ```bash
   git tag -a v1.1.0 -m "Release version 1.1.0: User profile export"
   git push origin v1.1.0
   ```

9. **Deploy** with announcement to users

### Workflow 3: Release a Major Version (Breaking Change)

**Scenario**: Make breaking API changes that require coordination.

**Steps:**

1. **Plan breaking changes** with team

2. **Create release branch:**
   ```bash
   git checkout -b release/2.0.0
   ```

3. **Implement breaking changes** with migration plan

4. **Update version** (MAJOR increment):
   ```bash
   # Both frontend and backend typically change for major release
   # Edit frontend/package.json: "1.5.2" → "2.0.0"
   # Edit backend/config/__init__.py: "1.5.2" → "2.0.0"
   ```

5. **Update documentation:**
   - Migration guide for users
   - Breaking changes documentation
   - Updated API documentation
   - CHANGELOG.md with comprehensive notes

6. **Test migration path:**
   ```bash
   # Test upgrade from 1.5.2 to 2.0.0
   # Test database migrations
   # Test API compatibility layer (if applicable)
   ```

7. **Coordinate with stakeholders:**
   - Notify users of upcoming breaking changes
   - Schedule deployment window
   - Prepare rollback plan

8. **Deploy to staging** for extended testing:
   ```bash
   docker compose -f docker-compose.yml -f compose.staging.yml pull
   docker compose -f docker-compose.yml -f compose.staging.yml up -d
   ```

9. **Deploy to production** during scheduled window

10. **Monitor closely** post-deployment:
    ```bash
    # Watch logs
    docker compose logs -f backend frontend

    # Monitor error rates
    # Check user reports
    # Verify metrics dashboards
    ```

### Workflow 4: Hotfix Production Issue

**Scenario**: Critical bug in production requires immediate fix.

**Steps:**

1. **Create hotfix branch from production tag:**
   ```bash
   git checkout -b hotfix/critical-security-patch v1.0.1
   ```

2. **Implement minimal fix** (no feature changes)

3. **Update version** (PATCH increment):
   ```bash
   # Edit backend/config/__init__.py: "1.0.1" → "1.0.2"
   ```

4. **Test fix:**
   ```bash
   docker compose run --rm backend pytest -k test_security
   ```

5. **Fast-track through CI/CD:**
   ```bash
   git commit -m "fix: critical security patch (v1.0.2)"
   git push origin hotfix/critical-security-patch
   ```

6. **Emergency deployment:**
   ```bash
   # Skip staging if critical
   # Deploy directly to production
   # Notify team immediately
   ```

7. **Merge hotfix to both main and release branches:**
   ```bash
   git checkout main
   git merge hotfix/critical-security-patch
   git push origin main
   ```

### Workflow 5: Rollback Failed Deployment

**Scenario**: Version 1.1.0 deployed but causing issues, need to rollback to 1.0.2.

**Steps:**

1. **Identify issues** in monitoring/logs

2. **Quick rollback using container tags:**
   ```bash
   # Pull previous version
   docker pull ghcr.io/org/repo/backend:1.0.2
   docker pull ghcr.io/org/repo/frontend:1.0.2

   # Stop current deployment
   docker compose -f docker-compose.yml -f compose.production.yml down

   # Update tags to previous version
   docker tag ghcr.io/org/repo/backend:1.0.2 ghcr.io/org/repo/backend:latest
   docker tag ghcr.io/org/repo/frontend:1.0.2 ghcr.io/org/repo/frontend:latest

   # Restart with previous version
   docker compose -f docker-compose.yml -f compose.production.yml up -d
   ```

3. **Verify rollback:**
   ```bash
   curl http://localhost:8000/api/v1/status/ | jq '.version'
   # Expected: "1.0.2"

   docker inspect backend --format='{{index .Config.Labels "app.version"}}'
   # Expected: 1.0.2
   ```

4. **Investigate issue** in version 1.1.0

5. **Fix issue** and re-release as 1.1.1

---

## Troubleshooting

### Issue 1: Version Mismatch Between Frontend and Backend

**Symptoms:**
- Frontend shows version 1.0.1
- Backend shows version 1.0.0
- API compatibility issues

**Diagnosis:**
```bash
# Check frontend version
grep '"version"' frontend/package.json

# Check backend version
grep '__version__' backend/config/__init__.py

# Check deployed versions
curl http://localhost/  # Browser console: window.APP_VERSION
curl http://localhost:8000/api/v1/status/ | jq '.version'
```

**Resolution:**
```bash
# Option 1: Update both to same version
# Edit both files to match (e.g., both 1.0.1)

# Option 2: Understand intentional mismatch
# Frontend and backend can have different versions if they change independently
# Ensure API compatibility is maintained
```

**Prevention:**
- Consider synchronized versioning for major releases
- Document version compatibility matrix
- Use API versioning (`/api/v1/`, `/api/v2/`) for breaking changes

### Issue 2: Docker Cache Not Invalidating on Version Change

**Symptoms:**
- Changed version from 1.0.0 to 1.0.1
- Docker build shows all layers CACHED
- Built container still shows version 1.0.0

**Diagnosis:**
```bash
# Check if version ARG is being passed
docker build --target production --build-arg APP_VERSION=1.0.1 \
  -t backend:test backend

# Verify build args in Dockerfile
grep "ARG APP_VERSION" backend/Dockerfile
```

**Resolution:**
```bash
# Ensure build args are passed correctly
docker build --target production \
  --build-arg APP_VERSION=1.0.1 \
  --build-arg VERSION=1.0.1 \
  --no-cache \  # Force rebuild if needed
  -t backend:1.0.1 backend

# Verify version in built image
docker inspect backend:1.0.1 --format='{{index .Config.Labels "app.version"}}'
```

**Root Cause:**
- Build arg not passed to docker build command
- ARG declared after it's used in Dockerfile
- BuildKit cache mode issue

**Prevention:**
- Always pass version as build arg in local builds
- CI/CD automatically passes version args
- Use `--no-cache` flag for troubleshooting

### Issue 3: CI/CD Build Fails After Version Change

**Symptoms:**
- Version changed from 1.0.0 to 1.0.1
- CI/CD pipeline fails with cache-related errors
- Error: "cache import failed"

**Diagnosis:**
```bash
# Check GitHub Actions logs
# Look for cache-related errors in build steps

# Verify version extraction succeeded
# Check "Extract version" step output
```

**Resolution:**
```bash
# Option 1: Clear GitHub Actions cache
# Settings → Actions → Caches → Delete cache for branch

# Option 2: Rebuild without cache
# Add --no-cache flag to build step temporarily

# Option 3: Fix version format
# Ensure version follows X.Y.Z format (no prefix, suffix, or invalid chars)
```

**Root Cause:**
- Corrupted cache in GitHub Actions
- Invalid version format breaking cache scope naming
- Network issues during cache retrieval

**Prevention:**
- Validate version format in pre-commit hook
- Monitor GitHub Actions cache usage
- Use fallback cache levels (already implemented)

### Issue 4: Version Not Visible in Production

**Symptoms:**
- Version updated in code
- CI/CD passed
- Deployed to production
- Status endpoint shows old version

**Diagnosis:**
```bash
# Check what's running in production
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}"

# Check image version
docker inspect <container> --format='{{index .Config.Labels "app.version"}}'

# Query status endpoint
curl https://api.example.com/api/v1/status/ | jq '.version'

# Check if deployment actually happened
docker images backend --format "table {{.Repository}}\t{{.Tag}}\t{{.CreatedAt}}"
```

**Resolution:**
```bash
# Pull latest image
docker compose -f docker-compose.yml -f compose.production.yml pull

# Recreate containers
docker compose -f docker-compose.yml -f compose.production.yml up -d --force-recreate

# Verify new version
curl https://api.example.com/api/v1/status/ | jq '.version'
```

**Root Cause:**
- Deployment didn't pull latest image
- Container restart didn't happen
- Wrong image tag deployed
- Cache serving old image

**Prevention:**
- Use `docker compose pull` before `docker compose up`
- Use `--force-recreate` flag to ensure fresh containers
- Verify version immediately after deployment
- Implement deployment verification in CI/CD

### Issue 5: Version Format Validation Fails

**Symptoms:**
- Tests fail with version format errors
- Version doesn't match semantic versioning pattern
- CI/CD rejects version string

**Diagnosis:**
```bash
# Check current version format
grep '"version"' frontend/package.json
grep '__version__' backend/config/__init__.py

# Validate format manually
echo "1.0.0" | grep -E "^[0-9]+\.[0-9]+\.[0-9]+$"  # Should match
echo "v1.0.0" | grep -E "^[0-9]+\.[0-9]+\.[0-9]+$"  # No match (has prefix)
```

**Resolution:**
```bash
# Fix version format to match X.Y.Z
# Remove prefixes (v1.0.0 → 1.0.0)
# Remove suffixes (1.0.0-beta → 1.0.0 or use 1.0.0 for release)
# Ensure three parts separated by dots

# Valid:   1.0.0, 2.5.13, 10.0.1
# Invalid: v1.0.0, 1.0, 1.0.0-beta, 1.0.0.0
```

**Root Cause:**
- Incorrect version format
- Confusion about semantic versioning syntax
- Copy-paste from other projects with different conventions

**Prevention:**
- Document version format clearly (this guide)
- Add pre-commit hook to validate version format
- Include version format tests in test suite

### Issue 6: Build Time Unexpectedly Slow

**Symptoms:**
- Version change should use cached dependencies
- Build takes 120+ seconds instead of expected 60-90 seconds
- All layers being rebuilt

**Diagnosis:**
```bash
# Check build logs for cache status
docker build -f backend/Dockerfile --target production \
  --build-arg APP_VERSION=1.0.1 -t backend:test backend 2>&1 | grep -i cache

# Check if cache mounts are working
docker build -f backend/Dockerfile --target production \
  --build-arg APP_VERSION=1.0.1 -t backend:test backend 2>&1 | grep "mount=type=cache"
```

**Resolution:**
```bash
# Ensure BuildKit is enabled
export DOCKER_BUILDKIT=1

# Check Docker version (BuildKit default in 23.0+)
docker version | grep Version

# Rebuild with verbose output
docker build --progress=plain -f backend/Dockerfile --target production \
  --build-arg APP_VERSION=1.0.1 -t backend:test backend

# Check cache mount permissions
# Ensure build context has correct permissions
```

**Root Cause:**
- BuildKit not enabled
- Cache mounts not working
- Docker version too old
- Permission issues preventing cache reuse

**Prevention:**
- Use Docker Engine 23.0+ (BuildKit default)
- Set DOCKER_BUILDKIT=1 in environment
- Monitor build times in CI/CD metrics

---

## Best Practices Summary

### For Developers

1. **Always follow semantic versioning rules**
   - MAJOR for breaking changes
   - MINOR for new features
   - PATCH for bug fixes

2. **Update versions in both frontend and backend** when needed
   - Frontend: `/frontend/package.json`
   - Backend: `/backend/config/__init__.py`

3. **Test version changes locally before pushing**
   - Build containers with new version
   - Verify version labels
   - Check status endpoints

4. **Use clear commit messages for version bumps**
   - `chore: bump version to 1.0.1`
   - `feat: version 1.1.0 - add user export`
   - `fix: hotfix version 1.0.2`

5. **Verify CI/CD passes before merging**
   - Check all pipeline stages
   - Review build times for anomalies
   - Confirm security scans pass

### For DevOps

1. **Monitor version-based cache performance**
   - Track build times in CI/CD
   - Review cache hit rates
   - Clean up old cache entries

2. **Maintain version compatibility matrix**
   - Document which frontend versions work with which backend versions
   - Plan coordinated releases for breaking changes

3. **Implement version verification in deployments**
   - Check version after deployment
   - Monitor version mismatches across services
   - Alert on unexpected version changes

4. **Use version labels for troubleshooting**
   - Filter containers by version
   - Compare versions across environments
   - Track version history in logs

5. **Plan rollback procedures**
   - Keep previous version images available
   - Document rollback steps
   - Test rollback in staging

### For Release Management

1. **Coordinate major version releases**
   - Plan breaking changes with team
   - Notify stakeholders in advance
   - Schedule deployment windows

2. **Document version changes**
   - Maintain CHANGELOG.md
   - Update release notes
   - Communicate to users

3. **Tag releases in Git**
   - Use annotated tags: `git tag -a v1.0.0`
   - Push tags to remote
   - Link tags to release notes

4. **Track version deployment status**
   - Which version is in which environment
   - When was each version deployed
   - Who approved the deployment

---

## Additional Resources

### Internal Documentation

- **Configuration Reference**: `/docs/configuration.md`
- **Docker Best Practices**: `/context/devops/docker.md`
- **GitHub Actions Guide**: `/context/devops/github-actions.md`
- **Feature #16 User Stories**: `/docs/features/16/user-stories.md`
- **Implementation Log**: `/docs/features/16/implementation-log.json`

### External Resources

- [Semantic Versioning Specification](https://semver.org/)
- [Docker BuildKit Documentation](https://docs.docker.com/build/buildkit/)
- [OCI Image Spec Annotations](https://github.com/opencontainers/image-spec/blob/main/annotations.md)
- [GitHub Actions Cache](https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows)

### Quick Command Reference

```bash
# View current versions
grep '"version"' frontend/package.json
grep '__version__' backend/config/__init__.py

# Build with specific version
docker build -f frontend/Dockerfile --target production \
  --build-arg VERSION=1.0.1 -t frontend:1.0.1 frontend

docker build -f backend/Dockerfile --target production \
  --build-arg APP_VERSION=1.0.1 -t backend:1.0.1 backend

# Inspect container version
docker inspect <container> --format='{{index .Config.Labels "app.version"}}'

# Query backend version
curl http://localhost:8000/api/v1/status/ | jq '.version'

# Filter containers by version
docker images --filter "label=app.version=1.0.0"

# Find newest version
docker images backend --format "{{.Tag}}" | \
  grep -E "^[0-9]+\.[0-9]+\.[0-9]+$" | sort -V -r | head -1
```

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-10-28 | DevOps Team | Initial version management documentation for Feature #16 |

---

**For questions or issues with version management, please:**
1. Consult this documentation first
2. Check the troubleshooting section
3. Review Feature #16 implementation log for technical details
4. Contact the DevOps team if issues persist
