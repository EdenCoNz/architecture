# Docker Version Tagging Strategy

**Last Updated:** 2025-10-28
**Status:** Implemented ✅

---

## Overview

This document describes the automated version tagging strategy for Docker images used across all environments (local development, staging, production). The strategy ensures that Docker images are always tagged with semantic versions derived from application source files, eliminating reliance on the problematic `:latest` tag.

## Goals

1. **Eliminate `:latest` tag dependency** - Use explicit version tags for all Docker images
2. **Automatic version derivation** - Read versions directly from application source files
3. **Consistency across environments** - Same versioning approach for local, staging, and production
4. **CI/CD integration** - Automated version extraction and tagging in deployment pipelines
5. **Traceability** - Clear mapping between deployed images and source code versions

## Version Sources

### Backend (Django)
- **Source File:** `/backend/config/__init__.py`
- **Variable:** `__version__`
- **Format:** Semantic versioning (e.g., `1.0.0`)
- **Extraction Command:**
  ```bash
  grep -E "^__version__\s*=\s*" backend/config/__init__.py | cut -d'"' -f2
  ```

### Frontend (React + Vite)
- **Source File:** `/frontend/package.json`
- **Variable:** `version`
- **Format:** Semantic versioning (e.g., `1.0.0`)
- **Extraction Command:**
  ```bash
  node -p "require('./frontend/package.json').version"
  ```

## Tagging Strategy

### Development Images (Local)

Built and used for local development with hot module reloading.

**Backend:**
- Primary Tag: `backend-dev:${BACKEND_VERSION}` (e.g., `backend-dev:1.0.0`)
- Fallback Tag: `backend-dev:latest` (for cache compatibility)

**Frontend:**
- Primary Tag: `frontend-dev:${FRONTEND_VERSION}` (e.g., `frontend-dev:1.0.0`)
- Fallback Tag: `frontend-dev:latest` (for cache compatibility)

**Usage:**
```bash
# Version variables are read from .env file
docker compose up

# Images will be tagged as backend-dev:1.0.0 and frontend-dev:1.0.0
```

### Production Images (Staging & Production)

Production-optimized images built in CI/CD and deployed to staging/production.

**Backend:**
- Version Tag: `backend-prod:${BACKEND_VERSION}` (e.g., `backend-prod:1.0.0`)
- Version+SHA Tag: `backend-prod:${BACKEND_VERSION}-${GIT_SHA}` (e.g., `backend-prod:1.0.0-abc1234`)
- Compatibility Tag: `backend-prod:latest` (for backward compatibility)

**Frontend:**
- Version Tag: `frontend-prod:${FRONTEND_VERSION}` (e.g., `frontend-prod:1.0.0`)
- Version+SHA Tag: `frontend-prod:${FRONTEND_VERSION}-${GIT_SHA}` (e.g., `frontend-prod:1.0.0-abc1234`)
- Compatibility Tag: `frontend-prod:latest` (for backward compatibility)

**Staging Environment:**
- Uses version-tagged images with `-staging` suffix
- Example: `ghcr.io/edenconz/backend:1.0.0-staging`

**Production Environment:**
- Uses version-tagged images without suffix
- Example: `ghcr.io/edenconz/backend:1.0.0`

## Implementation Details

### Docker Compose Configuration

#### Base Configuration (`docker-compose.yml`)

Services reference version-tagged images with environment variable substitution:

```yaml
services:
  backend:
    build:
      cache_from:
        - backend-dev:${BACKEND_VERSION:-1.0.0}
        - backend-dev:latest
    image: backend-dev:${BACKEND_VERSION:-1.0.0}

  frontend:
    build:
      cache_from:
        - frontend-dev:${FRONTEND_VERSION:-1.0.0}
        - frontend-dev:latest
    image: frontend-dev:${FRONTEND_VERSION:-1.0.0}
```

#### Production Configuration (`compose.production.yml`)

```yaml
services:
  backend:
    image: ${BACKEND_IMAGE:-ghcr.io/edenconz/backend:${BACKEND_VERSION:-1.0.0}}
    build:
      cache_from:
        - ghcr.io/edenconz/backend:${BACKEND_VERSION:-1.0.0}
        - ghcr.io/edenconz/backend:latest

  frontend:
    image: ${FRONTEND_IMAGE:-ghcr.io/edenconz/frontend:${FRONTEND_VERSION:-1.0.0}}
    build:
      cache_from:
        - ghcr.io/edenconz/frontend:${FRONTEND_VERSION:-1.0.0}
        - ghcr.io/edenconz/frontend:latest
```

#### Staging Configuration (`compose.staging.yml`)

```yaml
services:
  backend:
    image: ${BACKEND_IMAGE:-ghcr.io/edenconz/backend:${BACKEND_VERSION:-1.0.0}-staging}
    build:
      cache_from:
        - ghcr.io/edenconz/backend:${BACKEND_VERSION:-1.0.0}-staging
        - ghcr.io/edenconz/backend:${BACKEND_VERSION:-1.0.0}
        - ghcr.io/edenconz/backend:latest

  frontend:
    image: ${FRONTEND_IMAGE:-ghcr.io/edenconz/frontend:${FRONTEND_VERSION:-1.0.0}-staging}
    build:
      cache_from:
        - ghcr.io/edenconz/frontend:${FRONTEND_VERSION:-1.0.0}-staging
        - ghcr.io/edenconz/frontend:${FRONTEND_VERSION:-1.0.0}
        - ghcr.io/edenconz/frontend:latest
```

### Environment Configuration

Version variables are set in `.env` files for each environment:

#### `.env` (Local Development)
```bash
# Application Versions (Automatically read from source files)
BACKEND_VERSION=1.0.0
FRONTEND_VERSION=1.0.0
```

#### `.env.staging.example` (Staging)
```bash
# Application Versions (Set by CI/CD pipeline)
BACKEND_VERSION=1.0.0
FRONTEND_VERSION=1.0.0
```

#### `.env.production.example` (Production)
```bash
# Application Versions (Set by CI/CD pipeline)
BACKEND_VERSION=1.0.0
FRONTEND_VERSION=1.0.0
```

### CI/CD Pipeline Configuration

The unified CI/CD workflow (`unified-ci-cd.yml`) implements version extraction and tagging:

#### Version Extraction (Build Job)

```yaml
- name: Extract backend version from config/__init__.py
  id: backend_version
  run: |
    BACKEND_VERSION=$(grep -E "^__version__\s*=\s*" backend/config/__init__.py | cut -d'"' -f2)
    echo "version=$BACKEND_VERSION" >> $GITHUB_OUTPUT
    echo "Backend version: $BACKEND_VERSION" >> $GITHUB_STEP_SUMMARY

- name: Extract frontend version from package.json
  id: frontend_version
  run: |
    FRONTEND_VERSION=$(node -p "require('./frontend/package.json').version")
    echo "version=$FRONTEND_VERSION" >> $GITHUB_OUTPUT
    echo "Frontend version: $FRONTEND_VERSION" >> $GITHUB_STEP_SUMMARY
```

#### Multi-Tag Build (Development)

```yaml
- name: Build backend container
  uses: docker/build-push-action@v5
  with:
    tags: |
      backend-dev:${{ steps.backend_version.outputs.version }}
      backend-dev:latest
    build-args: |
      APP_VERSION=${{ steps.backend_version.outputs.version }}
```

#### Multi-Tag Build (Production)

```yaml
- name: Build backend production container
  uses: docker/build-push-action@v5
  with:
    tags: |
      backend-prod:${{ steps.backend_version.outputs.version }}
      backend-prod:${{ steps.backend_version.outputs.version }}-${{ github.sha }}
      backend-prod:latest
    build-args: |
      APP_VERSION=${{ steps.backend_version.outputs.version }}
```

#### Deployment Configuration

During deployment, the CI/CD pipeline creates `.env` files with extracted versions:

```yaml
# Create root-level .env file for docker-compose variable substitution
cat > /tmp/docker-artifacts/.env << 'ENV_EOF'
# Application versions (extracted from source files)
BACKEND_VERSION=${{ steps.backend_version.outputs.version }}
FRONTEND_VERSION=${{ steps.frontend_version.outputs.version }}

# Backend image (using versioned production image)
BACKEND_IMAGE=backend-prod:${{ steps.backend_version.outputs.version }}

# Frontend image (using versioned production image)
FRONTEND_IMAGE=frontend-prod:${{ steps.frontend_version.outputs.version }}
ENV_EOF
```

## Cache Strategy

### Multi-Level Cache Fallback

Docker builds use a sophisticated multi-level cache strategy to maximize cache hits:

```yaml
cache-from: |
  type=gha,scope=backend-dev-v${{ steps.backend_version.outputs.version }}-${{ github.ref_name }}
  type=gha,scope=backend-dev-v${{ steps.backend_version.outputs.version }}-main
  type=gha,scope=backend-dev-${{ github.ref_name }}
  type=gha,scope=backend-dev-main
  type=gha,scope=backend-dev
cache-to: type=gha,mode=max,scope=backend-dev-v${{ steps.backend_version.outputs.version }}-${{ github.ref_name }}
```

**Fallback Order:**
1. **Version+Branch Cache:** Current version on current branch (most specific)
2. **Version+Main Cache:** Current version on main branch (shared version layers)
3. **Branch Cache:** Any version on current branch (cross-version fallback)
4. **Main Branch Cache:** Any version on main branch (shared layers)
5. **General Cache:** Any version, any branch (last resort)

This ensures:
- Fast builds when working on the same version
- Reasonable cache hits when version changes
- Maximum cache reuse across branches

## Usage Examples

### Local Development

```bash
# Set versions in .env or let defaults apply
export BACKEND_VERSION=1.0.0
export FRONTEND_VERSION=1.0.0

# Build and start services
docker compose up

# Images are tagged as:
#   - backend-dev:1.0.0
#   - frontend-dev:1.0.0
```

### Staging Deployment

```bash
# Extract versions from source files
BACKEND_VERSION=$(grep -E "^__version__\s*=\s*" backend/config/__init__.py | cut -d'"' -f2)
FRONTEND_VERSION=$(node -p "require('./frontend/package.json').version")

# Export for docker-compose
export BACKEND_VERSION
export FRONTEND_VERSION

# Deploy to staging
docker compose -f docker-compose.yml -f compose.staging.yml up -d

# Images are tagged as:
#   - ghcr.io/edenconz/backend:1.0.0-staging
#   - ghcr.io/edenconz/frontend:1.0.0-staging
```

### Production Deployment

```bash
# Extract versions from source files
BACKEND_VERSION=$(grep -E "^__version__\s*=\s*" backend/config/__init__.py | cut -d'"' -f2)
FRONTEND_VERSION=$(node -p "require('./frontend/package.json').version")

# Export for docker-compose
export BACKEND_VERSION
export FRONTEND_VERSION

# Deploy to production
docker compose -f docker-compose.yml -f compose.production.yml up -d

# Images are tagged as:
#   - ghcr.io/edenconz/backend:1.0.0
#   - ghcr.io/edenconz/frontend:1.0.0
```

### Inspecting Image Versions

```bash
# View local images with versions
docker images | grep -E "(backend-|frontend-)"

# Check container labels
docker inspect backend-dev:1.0.0 --format='{{json .Config.Labels}}'

# Filter images by version label
docker images --filter "label=app.version=1.0.0"
```

## Version Updates

To update application versions:

### Backend Version Update

1. Edit `/backend/config/__init__.py`:
   ```python
   __version__ = "1.1.0"  # Update this line
   ```

2. Commit and push:
   ```bash
   git add backend/config/__init__.py
   git commit -m "Bump backend version to 1.1.0"
   git push
   ```

3. CI/CD automatically extracts and uses the new version

### Frontend Version Update

1. Edit `/frontend/package.json`:
   ```json
   {
     "version": "1.1.0"
   }
   ```

2. Commit and push:
   ```bash
   git add frontend/package.json
   git commit -m "Bump frontend version to 1.1.0"
   git push
   ```

3. CI/CD automatically extracts and uses the new version

## Migration from `:latest`

### Before (Using `:latest`)

```yaml
services:
  backend:
    image: backend-dev:latest  # ❌ Ambiguous, non-reproducible
  frontend:
    image: frontend-dev:latest  # ❌ Ambiguous, non-reproducible
```

### After (Using Versions)

```yaml
services:
  backend:
    image: backend-dev:${BACKEND_VERSION:-1.0.0}  # ✅ Explicit version
  frontend:
    image: frontend-dev:${FRONTEND_VERSION:-1.0.0}  # ✅ Explicit version
```

## Benefits

1. **Reproducibility:** Exact same image can be rebuilt from tagged version
2. **Traceability:** Clear mapping between deployed images and source versions
3. **Rollback Support:** Easy to deploy previous versions by specifying version tag
4. **Cache Efficiency:** Version-based cache scopes improve build performance
5. **Environment Consistency:** Same versioning approach across all environments
6. **No Ambiguity:** No confusion about which `:latest` is deployed where
7. **Audit Trail:** Version tags provide clear deployment history

## Troubleshooting

### Problem: Version variable not set

**Symptom:**
```
Error: invalid reference format
```

**Solution:**
```bash
# Check if version variables are set
echo $BACKEND_VERSION
echo $FRONTEND_VERSION

# Set them explicitly if needed
export BACKEND_VERSION=1.0.0
export FRONTEND_VERSION=1.0.0
```

### Problem: Old :latest images still present

**Symptom:**
```
Multiple images with different tags but same ID
```

**Solution:**
```bash
# Clean up old :latest tags
docker rmi backend-dev:latest frontend-dev:latest

# Rebuild with version tags
docker compose build
```

### Problem: CI/CD using wrong version

**Symptom:**
Deployed image has incorrect version tag

**Solution:**
1. Verify version in source file (`config/__init__.py` or `package.json`)
2. Check CI/CD logs for extracted version
3. Ensure version extraction commands are correct
4. Re-run CI/CD pipeline

## Related Documentation

- [Configuration Documentation](/home/ed/Dev/architecture/docs/configuration.md) - Overall configuration architecture
- [Runtime Configuration](/home/ed/Dev/architecture/docs/RUNTIME_CONFIG_IMPLEMENTATION.md) - Frontend runtime config strategy
- [Docker Compose Files](/home/ed/Dev/architecture/docker-compose.yml) - Base orchestration configuration
- [CI/CD Workflow](/home/ed/Dev/architecture/.github/workflows/unified-ci-cd.yml) - Automated deployment pipeline

## Maintenance

### Regular Tasks

- **Version Updates:** Update `__version__` and `package.json` version before each release
- **Tag Cleanup:** Periodically remove unused old version tags from registry
- **Documentation Sync:** Keep this document updated when versioning strategy changes

### Version Numbering Guidelines

Follow semantic versioning (SemVer):
- **MAJOR.MINOR.PATCH** (e.g., `1.2.3`)
- **MAJOR:** Breaking changes (e.g., `1.0.0` → `2.0.0`)
- **MINOR:** New features, backward-compatible (e.g., `1.0.0` → `1.1.0`)
- **PATCH:** Bug fixes, backward-compatible (e.g., `1.0.0` → `1.0.1`)

---

**Implementation Date:** 2025-10-28
**Implemented By:** DevOps Agent (Claude Code)
**Status:** ✅ Complete and Validated
