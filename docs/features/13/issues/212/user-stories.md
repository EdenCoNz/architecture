# User Stories - Fix Issue #212: CI/CD Pipeline Failed (Build and Test - Run #5)

**Feature ID**: 13
**Issue Number**: 212
**Branch**: feature/13-end-to-end-testing
**Created**: 2025-10-26

## Issue Summary

The CI/CD pipeline is failing during the "Build and Test" stage with two distinct errors:

1. **Docker cache configuration issue**: The Docker build process attempts to import cached images from a registry that requires authorization, causing a non-critical warning that slows down builds
2. **Django test settings module error**: The backend test runner is configured to use a settings module named `config.settings.test`, but the actual settings file is named `testing.py` (not `test.py`), causing all backend tests to fail with a critical ModuleNotFoundError

These failures block the entire CI/CD pipeline and prevent the deployment workflow from proceeding.

---

## Story 13-212.1: Fix Django Test Settings Module Configuration

**Assigned to**: devops-engineer

### Description

As a developer running the CI/CD pipeline, I need the backend test runner to use the correct Django settings module so that backend tests can execute successfully and validate code quality before deployment.

Currently, the workflow configures the backend test container with `DJANGO_SETTINGS_MODULE=config.settings.test`, but the actual settings file is named `testing.py`. This mismatch causes Django to fail when attempting to load settings, preventing any tests from running and blocking the entire pipeline.

The test environment should seamlessly load the correct testing configuration module, allowing automated tests to verify backend functionality.

### Acceptance Criteria

**Given** the backend test suite needs to run in the CI/CD pipeline
**When** the test runner container starts with test environment configuration
**Then** Django should successfully load the testing settings module without errors

**Given** the workflow defines test environment variables
**When** the backend container executes pytest with the test database configuration
**Then** all backend tests should execute and report results without settings import failures

**Given** the testing settings module exists at `config/settings/testing.py`
**When** the CI/CD workflow references the Django settings module
**Then** the environment variable should correctly point to `config.settings.testing` (not `config.settings.test`)

**Given** developers commit changes to the backend code
**When** the automated pipeline validates backend tests
**Then** the configuration validation and test execution should complete successfully without ModuleNotFoundError

### Notes

**Technical Context**:
- The workflow file is located at `.github/workflows/unified-ci-cd.yml`
- The problematic configuration is on line 141: `DJANGO_SETTINGS_MODULE=config.settings.test`
- The actual settings file is at `backend/config/settings/testing.py`
- The correct module path should be `config.settings.testing`

**Related Configuration**:
- Backend test execution happens in the "Run backend tests" step
- The same settings module name may be referenced in other configuration files or documentation

---

## Story 13-212.2: Optimize Docker Build Cache Configuration

**Assigned to**: devops-engineer

### Description

As a developer waiting for CI/CD pipeline builds, I want the Docker build process to use efficient caching strategies so that builds complete faster without unnecessary warnings or failed cache import attempts.

Currently, the Docker build step attempts to import cached layers from a registry (`backend-dev:latest`) that either doesn't exist or requires authorization that isn't configured. This produces error messages in the build logs and forces Docker to rebuild all layers from scratch, slowing down the build process unnecessarily.

The build process should either successfully use cache from an accessible location or skip cache import gracefully without generating error messages, allowing builds to proceed efficiently.

### Acceptance Criteria

**Given** the CI/CD workflow builds Docker images
**When** the build process attempts to use layer caching
**Then** no authorization errors should appear in the build logs

**Given** Docker attempts to import cached images during the build
**When** the cache source is not available or configured
**Then** the build should proceed from scratch without error messages about failed cache imports

**Given** builds run on GitHub Actions runners
**When** Docker Buildx is configured for the build step
**Then** the cache configuration should use an appropriate cache backend (local, GitHub Actions cache, or properly configured registry) that doesn't require additional authorization

**Given** the same branch is built multiple times
**When** subsequent builds execute
**Then** builds should leverage cached layers when available to reduce build time

### Notes

**Technical Context**:
- The error occurs during the "Build complete application stack" step in `.github/workflows/unified-ci-cd.yml`
- Current build command uses `--build-arg BUILDKIT_INLINE_CACHE=1`
- Error message: `ERROR: failed to configure registry cache importer: pull access denied, repository does not exist or may require authorization: server message: insufficient_scope: authorization failed`

**Possible Solutions** (Implementation choice left to devops-engineer):
- Use GitHub Actions cache backend (`--cache-from type=gha --cache-to type=gha`)
- Use local cache (`--cache-from type=local --cache-to type=local`)
- Configure registry authentication if a registry cache is preferred
- Remove inline cache configuration if not beneficial for the current setup

**Impact**:
- Non-critical: Builds still succeed but are slower
- Primary benefit is improved build performance and cleaner logs

---

## Execution Order

### Sequential Phases

**Phase 1: Critical Fix - Django Settings**
- Story 13-212.1 (devops-engineer) - BLOCKS ALL BACKEND TESTS

**Phase 2: Optional Optimization - Docker Cache**
- Story 13-212.2 (devops-engineer) - Performance improvement

### Dependencies

- Story 13-212.1 MUST be completed first as it blocks all backend testing
- Story 13-212.2 is independent and can be addressed after the critical fix or in a separate commit

---

## Summary

- **Total Stories**: 2
- **Assigned Agents**: devops-engineer (2 stories)
- **Critical Stories**: 1 (Story 13-212.1)
- **Optional Stories**: 1 (Story 13-212.2)
- **Execution Phases**: 2 sequential

**Story Quality**:
- All stories are implementation-agnostic ✅
- All stories focus on WHAT, not HOW ✅
- All acceptance criteria are user-observable ✅
- No technical implementation details prescribed ✅
- Stories work for any CI/CD approach ✅
