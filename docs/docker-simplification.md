# Docker Container Setup Simplification Analysis

**Date:** 2025-10-27
**Status:** Phase 1 Complete (Feature #15)
**Impact:** High - 67% reduction in configuration files

**Phase 1 Implementation Status:**
- ✅ Removed docker-compose.unified.yml (Story 15.4 - 2025-10-27)
- ✅ Remove backend compose files (Story 15.5 - 2025-10-26)
- ✅ Remove frontend compose files (Story 15.6 - 2025-10-26)
- ✅ Validate consolidated configuration (Story 15.7 - 2025-10-26)
- ✅ Verify service functionality (Story 15.8 - 2025-10-26)
- ✅ Update documentation (Story 15.9 - 2025-10-27)
- ✅ Communicate changes (Story 15.10 - 2025-10-27)

## Executive Summary

This document analyzes the current Docker container setup and identifies significant complexity and duplication issues. The analysis reveals **30 container-related configuration files** scattered across the repository, with substantial redundancy and inconsistent patterns that create confusion and maintenance burden.

**Key Findings:**
- 10 Docker Compose files (5 are redundant)
- 17 environment files (13 can be consolidated)
- 3 helper scripts (2 can be merged)
- 5+ different ways to start services
- CI/CD workflow doesn't leverage compose configuration

**Recommended Impact:**
- Reduce files from 30 to 10 (67% reduction)
- Consolidate to single entry point
- Eliminate configuration duplication
- Improve developer experience

---

## Current State Inventory

### Docker Compose Files (10 Total)

**Root Directory (6 files):**
```
├── docker-compose.yml                 # 609 lines - Base + all environments
├── docker-compose.unified.yml         # 572 lines - DUPLICATE of above
├── compose.override.yml               # 190 lines - Local dev overrides
├── compose.staging.yml                # 337 lines - Staging overrides
├── compose.production.yml             # 421 lines - Production overrides
└── compose.test.yml                   # Unknown - Testing
```

**Backend Directory (2 files):**
```
backend/
├── docker-compose.yml                 # 274 lines - Backend-only stack
└── docker-compose.production.yml      # Unknown - Backend production
```

**Frontend Directory (2 files):**
```
frontend/
├── docker-compose.yml                 # 93 lines - Frontend-only stack
└── docker-compose.prod.yml            # Unknown - Frontend production
```

### Dockerfiles (3 Total)

```
backend/Dockerfile                     # 192 lines - Multi-stage (dev/prod)
frontend/Dockerfile                    # 200 lines - Multi-stage (dev/prod)
testing/Dockerfile.test-runner         # 105 lines - Test environment
```

### Environment Files (17 Total)

**Root Directory (7 files):**
```
├── .env                               # Active local config
├── .env.local.example                 # Template
├── .env.staging.example               # Template
├── .env.production.example            # Template
├── .env.unified.example               # Template (redundant)
├── .env.test                          # Test config
└── .github/workflows/.env             # CI/CD config
```

**Backend Directory (5 files):**
```
backend/
├── .env.docker                        # Docker-specific
├── .env.example                       # Template
├── .env.staging.example               # Template
└── .env.production.example            # Template
```

**Frontend Directory (5 files):**
```
frontend/
├── .env.docker                        # Docker-specific
├── .env.example                       # Template
├── .env.local.example                 # Template
├── .env.staging.example               # Template
└── .env.production.example            # Template
```

### Helper Scripts (3 Total)

```
├── docker-dev.sh                      # 741 lines - Main helper
├── docker-env.sh                      # Unknown - Environment switcher
└── backend/docker-dev.sh              # Unknown - Backend-specific
└── backend/docker-entrypoint-dev.sh   # Entrypoint script (keep)
```

---

## Critical Problems Identified

### 1. Massive Duplication

**TWO "unified" compose files at root:**
- `docker-compose.yml` (609 lines)
- `docker-compose.unified.yml` (572 lines)

Both files define the complete application stack but with slightly different configurations. This creates:
- Confusion about which file is authoritative
- Risk of diverging configurations
- Wasted maintenance effort updating both files

**Example duplication:**
```yaml
# Both files define the same services:
# - db (PostgreSQL)
# - redis
# - backend (Django)
# - frontend (React)
# - proxy (Nginx)
# - celery (Background tasks)
```

### 2. Scattered Architecture

Container configuration exists in **3 different locations**, creating multiple conflicting entry points:

**From root directory:**
```bash
docker compose up                           # Which compose file?
docker compose -f docker-compose.yml up
docker compose -f docker-compose.unified.yml up
./docker-dev.sh start
./docker-env.sh staging start
```

**From backend directory:**
```bash
cd backend && docker compose up             # Backend-only
cd backend && ./docker-dev.sh start
```

**From frontend directory:**
```bash
cd frontend && docker compose up            # Frontend-only
```

**Result:** 5+ different ways to start services with unclear relationships.

### 3. Inconsistent Naming Conventions

**Mixed naming patterns:**
- `compose.override.yml` (modern convention)
- `docker-compose.yml` (legacy convention)
- `compose.staging.yml` (modern)
- `docker-compose.production.yml` (legacy)
- `docker-compose.prod.yml` (abbreviated)

**Location:** docker-compose.yml:1, compose.override.yml:1, compose.staging.yml:1

### 4. CI/CD Workflow Doesn't Use Compose

**Current implementation (.github/workflows/unified-ci-cd.yml:95-123):**

The workflow manually builds each service using separate `docker/build-push-action` steps:

```yaml
- name: Build backend container
  uses: docker/build-push-action@v5
  with:
    context: ./backend
    file: ./backend/Dockerfile
    target: development
    # ... lots of configuration

- name: Build frontend container
  uses: docker/build-push-action@v5
  with:
    context: ./frontend
    file: ./frontend/Dockerfile
    target: development
    # ... lots of configuration
```

**Problems:**
- Duplicates build configuration already defined in compose files
- Requires maintaining two sources of truth
- Doesn't validate that compose files actually work
- More verbose and error-prone

**What it should be:**
```yaml
- name: Build application stack
  run: docker compose build --parallel
```

### 5. Environment File Chaos

**17 environment files** scattered across 3 directories:

**Overlapping configurations:**
- Root `.env` AND backend `.env.docker` AND frontend `.env.docker`
- Multiple `.env.example` files with different templates
- Unclear inheritance and precedence

**Inconsistent naming:**
- `.env.local.example` vs `.env.example`
- `.env.unified.example` (what makes it "unified"?)
- `.env.staging.example` in root AND backend AND frontend

### 6. Service-Specific Compose Files Are Redundant

**backend/docker-compose.yml duplicates:**
- Database configuration (already in root)
- Redis configuration (already in root)
- Backend service definition (already in root)
- Network configuration (already in root)
- Volume definitions (already in root)

**frontend/docker-compose.yml duplicates:**
- Frontend service definition (already in root)
- Node modules volume (already in root)

**Purpose:** These were likely created for standalone service development, but with the unified architecture (Feature #12), they're now obsolete and confusing.

**Location:** backend/docker-compose.yml:1-274, frontend/docker-compose.yml:1-93

### 7. Unclear Workflow Entry Points

**For developers:**
- Should I use `docker-compose.yml` or `docker-compose.unified.yml`?
- Should I run from root or service directory?
- Should I use `docker compose up` or `./docker-dev.sh start`?
- Which `.env` file is being used?
- How do I switch environments?

**No clear documentation** on the intended workflow or file relationships.

---

## Recommended Simplifications

### Phase 1: Consolidate Compose Files (HIGH IMPACT)

**DELETE these redundant files:**
```
✅ docker-compose.unified.yml          # REMOVED in Story 15.4
✅ backend/docker-compose.yml          # REMOVED in Story 15.5
✅ backend/docker-compose.production.yml # REMOVED in Story 15.5
✅ frontend/docker-compose.yml         # REMOVED in Story 15.6
✅ frontend/docker-compose.prod.yml    # REMOVED in Story 15.6
```

**KEEP only these files:**
```
✅ docker-compose.yml                  # Base configuration for all services
✅ compose.override.yml                # Local dev overrides (auto-loaded)
✅ compose.staging.yml                 # Staging environment overrides
✅ compose.production.yml              # Production environment overrides
✅ compose.test.yml                    # Testing environment
```

**Result:** 10 → 5 files (50% reduction)

**Validation:**
```bash
# Local development (automatic)
docker compose up

# Staging deployment
docker compose -f docker-compose.yml -f compose.staging.yml up -d

# Production deployment
docker compose -f docker-compose.yml -f compose.production.yml up -d

# Testing
docker compose -f compose.test.yml up
```

### Phase 2: Standardize Naming Convention

**Rename for consistency:**
```bash
mv docker-compose.yml compose.yml
```

**Result:** Everything follows `compose.*.yml` pattern
```
✅ compose.yml                         # Base
✅ compose.override.yml                # Local (auto-loaded)
✅ compose.staging.yml                 # Staging
✅ compose.production.yml              # Production
✅ compose.test.yml                    # Testing
```

**Benefits:**
- Follows modern Docker Compose convention
- Crystal clear naming pattern
- Easier to understand at a glance
- Consistent with Docker documentation

**Docker Compose behavior:**
- `docker compose up` automatically uses `compose.yml` + `compose.override.yml`
- Explicit files: `docker compose -f compose.yml -f compose.staging.yml up`

### Phase 3: Simplify Environment Files

**Current chaos (17 files):**
```
Root:      .env, .env.local.example, .env.staging.example,
           .env.production.example, .env.unified.example, .env.test
Backend:   .env.docker, .env.example, .env.staging.example,
           .env.production.example
Frontend:  .env.docker, .env.example, .env.local.example,
           .env.staging.example, .env.production.example
CI/CD:     .github/workflows/.env
```

**Simplified structure (4 files):**
```
✅ .env                               # Local development (gitignored)
✅ .env.example                       # Template for local setup
✅ .env.staging                       # Staging deployment config
✅ .env.production                    # Production deployment config
```

**Key changes:**
1. **Single location:** All environment files at root
2. **Environment-specific:** One file per environment
3. **No service-specific files:** Services reference root env vars
4. **Clear purpose:** Each file has obvious use case

**Migration strategy:**
```bash
# Consolidate backend variables
cat backend/.env.docker >> .env.example
cat backend/.env.staging.example >> .env.staging
cat backend/.env.production.example >> .env.production

# Consolidate frontend variables
cat frontend/.env.docker >> .env.example
cat frontend/.env.staging.example >> .env.staging
cat frontend/.env.production.example >> .env.production

# Remove redundant files
rm backend/.env.*
rm frontend/.env.*
rm .env.local.example .env.unified.example
```

**Compose file references environment:**
```yaml
services:
  backend:
    env_file:
      - .env  # Automatically loaded in dev
    environment:
      - DB_HOST=${DB_HOST:-db}
      - DB_NAME=${DB_NAME}
      # All vars come from root .env
```

**Result:** 17 → 4 files (76% reduction)

### Phase 4: Consolidate Helper Scripts

**DELETE redundant scripts:**
```
❌ backend/docker-dev.sh              # Functionality in root script
❌ docker-env.sh                      # Merge into docker-dev.sh
```

**ENHANCE the single script:**
```
✅ docker-dev.sh                      # Single entry point
```

**Add environment flag support:**
```bash
#!/bin/bash
# Enhanced docker-dev.sh with environment support

ENVIRONMENT=${ENVIRONMENT:-local}

# Parse --env flag
while [[ $# -gt 0 ]]; do
  case $1 in
    --env)
      ENVIRONMENT="$2"
      shift 2
      ;;
    *)
      COMMAND="$1"
      shift
      ;;
  esac
done

# Set compose files based on environment
case "$ENVIRONMENT" in
  local|dev)
    COMPOSE_FILES="-f compose.yml"  # Uses override automatically
    ;;
  staging)
    COMPOSE_FILES="-f compose.yml -f compose.staging.yml"
    ;;
  production)
    COMPOSE_FILES="-f compose.yml -f compose.production.yml"
    ;;
esac

# Execute commands
case "$COMMAND" in
  start)
    docker compose $COMPOSE_FILES up -d
    ;;
  # ... other commands
esac
```

**New usage:**
```bash
./docker-dev.sh start                    # Local (default)
./docker-dev.sh start --env staging      # Staging
./docker-dev.sh start --env production   # Production

./docker-dev.sh logs --env staging       # Staging logs
./docker-dev.sh rebuild --env production # Production rebuild
```

**Result:** 3 → 1 script (67% reduction)

**Benefits:**
- Single source of truth for container operations
- Environment switching built-in
- Consistent interface across all environments
- Easier to maintain and document

### Phase 5: Fix CI/CD Workflow

**Current approach (.github/workflows/unified-ci-cd.yml:95-148):**

Manually builds each service with duplicated configuration:

```yaml
- name: Build backend container
  uses: docker/build-push-action@v5
  with:
    context: ./backend
    file: ./backend/Dockerfile
    target: development
    push: false
    load: true
    tags: backend-dev:latest
    cache-from: |
      type=gha,scope=backend-dev-${{ github.ref_name }}
      type=gha,scope=backend-dev-main
      type=gha,scope=backend-dev
    cache-to: type=gha,mode=max,scope=backend-dev-${{ github.ref_name }}

- name: Build frontend container
  uses: docker/build-push-action@v5
  with:
    context: ./frontend
    file: ./frontend/Dockerfile
    target: development
    push: false
    load: true
    tags: frontend-dev:latest
    cache-from: |
      type=gha,scope=frontend-dev-${{ github.ref_name }}
      type=gha,scope=frontend-dev-main
      type=gha,scope=frontend-dev
    cache-to: type=gha,mode=max,scope=frontend-dev-${{ github.ref_name }}
```

**Problems:**
- 50+ lines of YAML duplicating compose file configuration
- Build context, dockerfile, target all already defined in compose
- If compose file changes, workflow must be manually updated
- Can't test if compose file actually works in CI

**Recommended approach:**

```yaml
- name: Set up Docker Buildx with caching
  uses: docker/setup-buildx-action@v3
  with:
    driver-opts: |
      image=moby/buildkit:latest
      network=host

- name: Build complete application stack
  env:
    DOCKER_BUILDKIT: 1
    COMPOSE_DOCKER_CLI_BUILD: 1
  run: |
    # Build all services in parallel using compose
    docker compose build --parallel

    # Verify images were created
    docker images | grep -E "(backend-dev|frontend-dev)"

- name: Tag images for caching
  run: |
    # Tag with branch for cache scoping
    docker tag backend-dev:latest backend-dev:${{ github.ref_name }}
    docker tag frontend-dev:latest frontend-dev:${{ github.ref_name }}
```

**Benefits:**
- 50+ lines → 15 lines (70% reduction)
- Single source of truth (compose file)
- Automatically validates compose configuration
- Parallel building by default
- Easier to maintain

**For advanced caching (optional):**

If you need GitHub Actions cache backend:

```yaml
- name: Build with Docker Buildx cache
  uses: docker/bake-action@v4
  with:
    files: |
      compose.yml
    targets: backend,frontend
    set: |
      *.cache-from=type=gha,scope=${{ github.ref_name }}
      *.cache-to=type=gha,mode=max,scope=${{ github.ref_name }}
```

**Testing phase (.github/workflows/unified-ci-cd.yml:141-200):**

Also simplify to use compose:

```yaml
- name: Run backend tests
  run: |
    # Start dependencies
    docker compose up -d db redis

    # Run tests using compose
    docker compose run --rm backend pytest --cov

- name: Run frontend tests
  run: docker compose run --rm frontend npm run test:run
```

**Location:** .github/workflows/unified-ci-cd.yml:95-200

---

## Implementation Plan

### Step 1: Backup Current Configuration
```bash
# Create backup branch
git checkout -b backup/pre-docker-simplification
git push origin backup/pre-docker-simplification

# Create backup directory
mkdir -p backups/docker-configs-$(date +%Y%m%d)
cp -r *.yml compose*.yml backend/*.yml frontend/*.yml backups/docker-configs-$(date +%Y%m%d)/
cp -r .env* backend/.env* frontend/.env* backups/docker-configs-$(date +%Y%m%d)/
```

### Step 2: Environment Files (Low Risk)
```bash
# Consolidate environment files
cat backend/.env.docker >> .env.example
cat backend/.env.staging.example >> .env.staging
cat backend/.env.production.example >> .env.production

cat frontend/.env.docker >> .env.example
cat frontend/.env.staging.example >> .env.staging
cat frontend/.env.production.example >> .env.production

# Remove redundant files
rm backend/.env.docker backend/.env.example backend/.env.staging.example backend/.env.production.example
rm frontend/.env.docker frontend/.env.example frontend/.env.local.example frontend/.env.staging.example frontend/.env.production.example
rm .env.local.example .env.unified.example

# Test local environment
docker compose up -d
docker compose ps  # Verify all services healthy
docker compose down
```

### Step 3: Compose Files (Medium Risk)
```bash
# Verify docker-compose.yml is the canonical version
diff docker-compose.yml docker-compose.unified.yml

# If unified has important differences, merge them
# Then delete redundant files
✅ rm docker-compose.unified.yml  # COMPLETED - Story 15.4
✅ rm backend/docker-compose.yml backend/docker-compose.production.yml  # COMPLETED - Story 15.5
✅ rm frontend/docker-compose.yml frontend/docker-compose.prod.yml  # COMPLETED - Story 15.6

# Rename to modern convention
mv docker-compose.yml compose.yml

# Test all environments
docker compose up -d                                              # Local
docker compose -f compose.yml -f compose.staging.yml config       # Validate staging
docker compose -f compose.yml -f compose.production.yml config    # Validate production
```

### Step 4: Helper Scripts (Low Risk)
```bash
# Backup existing scripts
cp docker-dev.sh docker-dev.sh.backup
cp docker-env.sh docker-env.sh.backup

# Enhance docker-dev.sh with environment support
# (Add --env flag logic from Phase 4)

# Test enhanced script
./docker-dev.sh start
./docker-dev.sh start --env staging
./docker-dev.sh status

# Delete redundant scripts
rm docker-env.sh
rm backend/docker-dev.sh
```

### Step 5: CI/CD Workflow (Medium Risk)
```bash
# Update .github/workflows/unified-ci-cd.yml
# Replace manual build steps with compose build

# Test locally first
docker compose build --parallel

# Push changes and monitor CI/CD run
git add .github/workflows/unified-ci-cd.yml
git commit -m "Simplify CI/CD to use docker compose build"
git push
# Monitor workflow run in GitHub Actions
```

### Step 6: Documentation Update
```bash
# Update README.md with new structure
# Update docker-dev.sh help text
# Add migration notes for team members
```

### Step 7: Team Communication
```bash
# Before merging, communicate changes:
# 1. Post in team chat/Slack
# 2. Update onboarding docs
# 3. Record video walkthrough (optional)
# 4. Add migration guide to wiki
```

---

## Expected Benefits

### Developer Experience
- **Single clear workflow:** `./docker-dev.sh start` for all environments
- **Faster onboarding:** Less configuration to understand
- **Fewer errors:** Single source of truth eliminates config drift
- **Easier debugging:** Clear file relationships

### Maintenance
- **67% fewer files to maintain:** 30 → 10 files
- **Single source of truth:** Compose files define all configuration
- **Consistent patterns:** All files follow same naming convention
- **Less duplication:** Configuration defined once, referenced everywhere

### CI/CD
- **Simpler workflows:** `docker compose build` replaces 50+ lines
- **Validated configuration:** CI tests actual compose files used in production
- **Faster builds:** Parallel building by default
- **Easier to modify:** Change compose file, workflow automatically updated

### Metrics

| Area | Before | After | Reduction |
|------|--------|-------|-----------|
| **Compose files** | 10 | 5 | 50% |
| **Environment files** | 17 | 4 | 76% |
| **Helper scripts** | 3 | 1 | 67% |
| **Ways to start services** | 5+ | 2 | 60% |
| **Total config files** | 30 | 10 | **67%** |
| **Lines of workflow YAML** | 50+ | ~15 | 70% |

---

## Recommended File Structure (After Cleanup)

```
architecture/
├── compose.yml                         # Base service definitions
├── compose.override.yml                # Local dev overrides (auto-loaded)
├── compose.staging.yml                 # Staging environment overrides
├── compose.production.yml              # Production environment overrides
├── compose.test.yml                    # Testing environment
│
├── .env                                # Local development config (gitignored)
├── .env.example                        # Template for local setup
├── .env.staging                        # Staging deployment config
├── .env.production                     # Production deployment config
│
├── docker-dev.sh                       # Single helper script with env support
│
├── docs/
│   └── docker-simplification.md        # This document
│
├── backend/
│   ├── Dockerfile                      # Multi-stage build (dev/prod)
│   └── docker-entrypoint-dev.sh        # Dev entrypoint
│
├── frontend/
│   └── Dockerfile                      # Multi-stage build (dev/prod)
│
├── testing/
│   └── Dockerfile.test-runner          # Test environment
│
├── nginx/
│   ├── nginx.conf                      # Local/dev config
│   ├── nginx.staging.conf              # Staging config
│   └── nginx.production.conf           # Production config
│
└── .github/
    └── workflows/
        └── unified-ci-cd.yml           # Simplified to use compose
```

**Total: 10 configuration files** (down from 30)

**Clear patterns:**
- All compose files at root: `compose.*.yml`
- All env files at root: `.env*`
- All service Dockerfiles in service directories
- Single helper script at root
- Environment-specific nginx configs in `nginx/`

---

## Risk Assessment

### Low Risk Changes
✅ Environment file consolidation
✅ Helper script enhancement
✅ Documentation updates

**Why:** No impact on running services, easy to rollback

### Medium Risk Changes
⚠️ Compose file consolidation
⚠️ CI/CD workflow modification

**Why:** Affects how services are built and deployed

**Mitigation:**
- Test thoroughly in local environment first
- Validate compose file configurations with `docker compose config`
- Deploy to staging before production
- Monitor CI/CD pipeline closely on first run
- Keep backup branch for quick rollback

### High Risk Changes
❌ None identified

**Note:** All changes are configuration-only, no code changes required

---

## Rollback Plan

If issues arise after implementation:

### Quick Rollback (< 5 minutes)
```bash
# Restore from backup branch
git checkout backup/pre-docker-simplification

# Or restore individual files
cp backups/docker-configs-YYYYMMDD/* .
```

### Selective Rollback
```bash
# Rollback only compose files
git checkout backup/pre-docker-simplification -- *.yml compose*.yml

# Rollback only environment files
git checkout backup/pre-docker-simplification -- .env*

# Rollback CI/CD workflow
git checkout backup/pre-docker-simplification -- .github/workflows/unified-ci-cd.yml
```

---

## Success Criteria

Implementation is successful when:

- ✅ All services start with single command: `./docker-dev.sh start`
- ✅ Environment switching works: `./docker-dev.sh start --env staging`
- ✅ CI/CD pipeline passes with new configuration
- ✅ Staging deployment successful using new compose files
- ✅ Production deployment successful (after staging validation)
- ✅ All team members can run local environment without issues
- ✅ Documentation updated and accurate
- ✅ No configuration drift between environments

---

## Next Steps

1. **Review this analysis** with team leads
2. **Get approval** for implementation plan
3. **Schedule implementation** during low-traffic period
4. **Execute phases** in order (1-7)
5. **Monitor and validate** each phase before proceeding
6. **Update team documentation** and communicate changes
7. **Close tracking issue** after successful deployment

---

## Questions and Answers

### Q: Why keep separate compose files instead of one unified file?

**A:** Separation of concerns and security:
- **Base (compose.yml):** Common service definitions
- **Override (compose.override.yml):** Development-only features (auto-loaded)
- **Staging/Production:** Environment-specific configuration
- **Benefit:** Base file is environment-agnostic, overrides only change what's needed

### Q: Why move all env files to root instead of keeping them with services?

**A:** Single source of truth and easier secrets management:
- All environment variables in one location
- Easier to manage secrets (single .env.production file)
- Clear environment inheritance
- No confusion about which .env file is loaded

### Q: Will this break existing developer workflows?

**A:** Minimal disruption:
- `docker compose up` still works (using new compose.yml)
- `./docker-dev.sh start` still works (enhanced with --env flag)
- Old commands can be documented for transition period
- Can add aliases in script for backward compatibility

### Q: What if docker-compose.yml and docker-compose.unified.yml have important differences?

**A:** Merge before deleting:
```bash
# Compare files
diff docker-compose.yml docker-compose.unified.yml > differences.txt

# Review differences and merge important changes
# Then delete duplicate
```

### Q: How do we handle service-specific environment variables after consolidation?

**A:** Prefix in single .env file:
```bash
# Before: backend/.env.docker
DB_HOST=db
DB_NAME=backend_db

# After: .env
BACKEND_DB_HOST=db
BACKEND_DB_NAME=backend_db
FRONTEND_API_URL=http://localhost
```

Or use sections in compose file:
```yaml
services:
  backend:
    environment:
      DB_HOST: ${DB_HOST:-db}
      DB_NAME: ${DB_NAME:-backend_db}
  frontend:
    environment:
      VITE_API_URL: ${VITE_API_URL:-http://localhost}
```

---

## References

- Docker Compose file reference: https://docs.docker.com/compose/compose-file/
- Docker Compose best practices: https://docs.docker.com/compose/production/
- Multi-stage builds: https://docs.docker.com/build/building/multi-stage/
- GitHub Actions Docker: https://docs.docker.com/build/ci/github-actions/

---

**Document Owner:** DevOps Team
**Last Updated:** 2025-10-27
**Next Review:** After implementation
