# CI/CD Pipeline Documentation

This document describes the Continuous Integration and Continuous Deployment (CI/CD) pipeline for the backend application.

## Overview

The backend CI/CD pipeline is implemented using GitHub Actions and runs automatically on:
- Pull requests to `main` and `bau/**` branches
- Pushes to the `main` branch
- Manual workflow dispatch triggers

**Workflow File**: `.github/workflows/backend-ci.yml`

## Pipeline Architecture

The pipeline consists of 8 jobs organized in a dependency graph:

```
┌─────────────────────────────────────────────────────────┐
│  Parallel Quality Checks (Independent Jobs)             │
├─────────────┬─────────────┬─────────────┬──────────────┤
│   Lint      │   Format    │ Type Check  │   Security   │
│   (Ruff)    │   (Black)   │   (MyPy)    │   (Safety)   │
└──────┬──────┴──────┬──────┴──────┬──────┴──────┬───────┘
       │             │             │             │
       └─────────────┴─────────────┴─────────────┘
                          │
                     ┌────▼────┐
                     │  Test   │
                     │(Pytest) │
                     └────┬────┘
                          │
                     ┌────▼────────┐
                     │   Build     │
                     │ Verification│
                     └────┬────────┘
                          │
              ┌───────────┴──────────┐
              │                      │
         ┌────▼────────┐      ┌─────▼──────┐
         │ Deployment  │      │  Log Bugs  │
         │   Check     │      │ (on fail)  │
         │(main only)  │      └────────────┘
         └─────────────┘
```

## Jobs Description

### 1. Lint Check (Ruff)
**Duration**: ~2-3 minutes
**Purpose**: Validates code quality and style using Ruff linter

**What it checks**:
- PEP 8 code style compliance
- Common Python anti-patterns
- Import sorting (isort)
- Code simplification opportunities
- Unused imports and variables

**Command**: `make lint`

**Failure reasons**:
- Code style violations
- Unused imports or variables
- Complexity issues

### 2. Format Check (Black)
**Duration**: ~2-3 minutes
**Purpose**: Ensures consistent code formatting

**What it checks**:
- Code follows Black's formatting standards
- Line length compliance (100 characters)
- Consistent string quotes and whitespace

**Command**: `poetry run black --check .`

**Failure reasons**:
- Unformatted code (run `make format` to fix)
- Inconsistent formatting

### 3. Type Check (MyPy)
**Duration**: ~3-4 minutes
**Purpose**: Validates Python type hints and catches type errors

**What it checks**:
- Type hint correctness
- Type compatibility across function calls
- Missing or incorrect return types
- Django model type safety (via django-stubs)
- DRF serializer type safety (via djangorestframework-stubs)

**Command**: `make type-check`

**Failure reasons**:
- Missing type hints
- Type mismatches
- Invalid type annotations

### 4. Security Audit
**Duration**: ~2-3 minutes
**Purpose**: Scans for known vulnerabilities in dependencies

**What it checks**:
- Known CVEs in Python packages
- Outdated dependencies with security issues
- Dependency tree analysis

**Tools**:
- Poetry dependency tree analysis
- Safety vulnerability scanner

**Note**: Security issues are reported but don't block builds (informational only)

### 5. Test Suite (Pytest)
**Duration**: ~5-8 minutes
**Purpose**: Runs comprehensive test suite with coverage reporting

**What it tests**:
- Unit tests (fast, isolated)
- Integration tests (database, API)
- All test markers (smoke, regression, etc.)

**Coverage requirements**:
- Minimum 80% code coverage enforced
- Branch coverage included
- Coverage reports generated in multiple formats

**Command**: `make test`

**Artifacts**:
- HTML coverage report (`htmlcov/`)
- XML coverage report (`coverage.xml`)
- JSON coverage report (`coverage.json`)
- Retention: 7 days

**Failure reasons**:
- Test failures
- Coverage below 80% threshold
- Test timeout (>30 seconds per test)

### 6. Build Verification
**Duration**: ~3-4 minutes
**Purpose**: Verifies the application builds correctly for production
**Dependencies**: Runs only after lint, format, type-check, and test pass

**What it verifies**:
- Poetry package build succeeds
- Django deployment checks pass
- Static files collection works
- Production configuration is valid

**Commands**:
- `poetry build`
- `python manage.py check --deploy`
- `python manage.py collectstatic --noinput`

**Failure reasons**:
- Build errors
- Django configuration issues
- Missing static files
- Deployment check failures

### 7. Deployment Readiness Check
**Duration**: ~1 minute
**Purpose**: Final verification before deployment
**Trigger**: Only runs on `main` branch pushes
**Dependencies**: All previous jobs must pass

**What it verifies**:
- All quality checks passed
- Test coverage reports exist
- Build artifacts are valid
- Application is deployment-ready

**Artifacts downloaded**:
- Coverage reports from test job

### 8. Bug Logger (Conditional)
**Duration**: ~2-3 minutes
**Purpose**: Automatically creates GitHub issues for CI failures
**Trigger**: Only runs when any job fails

**What it does**:
- Extracts feature ID from branch name
- Creates detailed bug report using template
- Creates GitHub issue with failure details
- Posts PR comment with issue link
- Assigns issue to PR author

**Permissions required**:
- `contents: read` - Read repository code
- `issues: write` - Create GitHub issues
- `actions: read` - Fetch job logs

## Dependency Caching Strategy

The pipeline uses intelligent caching to speed up workflow execution:

### Poetry Installation Cache
- **Location**: `~/.local`
- **Key**: `poetry-${{ runner.os }}-${{ hashFiles('**/poetry.lock') }}`
- **Benefit**: Avoids Poetry reinstallation on every run
- **Invalidation**: When poetry.lock changes

### Virtual Environment Cache
- **Location**: `backend/.venv`
- **Key**: `venv-${{ runner.os }}-${{ hashFiles('**/poetry.lock') }}`
- **Benefit**: Skips dependency installation if unchanged
- **Invalidation**: When poetry.lock changes
- **Speed improvement**: ~3-5 minutes saved per workflow run

### How caching works:
1. First run: Cache miss → Full installation (~5 minutes)
2. Subsequent runs with same dependencies: Cache hit → Skip installation (~30 seconds)
3. After dependency changes: Cache miss → Reinstall and update cache

## Workflow Triggers

### Pull Request Trigger
```yaml
pull_request:
  branches: [main, 'bau/**']
```

Runs on:
- PRs targeting `main` branch
- PRs targeting any `bau/**` branch
- Every push to PR branches

### Push Trigger
```yaml
push:
  branches: [main]
```

Runs on:
- Direct pushes to `main` branch
- Merged PRs to `main` branch

### Manual Trigger
```yaml
workflow_dispatch:
```

Can be triggered manually from:
- GitHub Actions UI → Backend CI/CD → Run workflow

## Concurrency Control

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

**Behavior**:
- Only one workflow runs per branch at a time
- New pushes cancel in-progress workflows for the same branch
- Saves compute time and runner minutes
- Ensures latest code is always tested

## Environment Variables and Secrets

### Current Status
**No secrets required** for current operations.

The workflow runs completely with:
- Default `GITHUB_TOKEN` (auto-provided)
- Public repositories and packages
- No external service authentication

### Build Verification Variables
Used temporarily during build job:
```bash
DJANGO_SECRET_KEY=ci-build-secret-key-not-for-production
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1
```

**Note**: These are NOT real secrets, just placeholder values for CI build verification.

### Future Secrets (Not yet required)

**Database Testing**:
- `DATABASE_URL` - PostgreSQL for integration tests
- `REDIS_URL` - Redis for caching tests

**Docker Deployment**:
- `DOCKER_USERNAME` - Docker Hub username
- `DOCKER_TOKEN` - Docker Hub access token
- `GHCR_TOKEN` - GitHub Container Registry token

**Production Deployment**:
- `DJANGO_SECRET_KEY` - Production secret key
- `DATABASE_URL` - Production database
- `REDIS_URL` - Production Redis
- Cloud provider credentials
- Email service API keys
- Object storage credentials

See `.github/workflows/.env` for complete secrets documentation.

## Required Permissions

The workflow requires these GitHub permissions:

```yaml
permissions:
  contents: read      # Read repository code
  checks: write       # Update check status
  actions: read       # Fetch job logs for bug reporting
  issues: write       # Create issues on failure
```

These permissions are automatically granted via `GITHUB_TOKEN`.

## Status Checks for PR Merging

The following checks must pass before a PR can be merged to `main`:

✅ **Lint Check** - Ruff linting must pass
✅ **Format Check** - Black formatting must pass
✅ **Type Check** - MyPy type checking must pass
✅ **Test Suite** - All tests must pass with ≥80% coverage
✅ **Build Verification** - Production build must succeed

**Optional/Informational**:
- Security Audit (informational, doesn't block)
- Deployment Check (only on main branch)
- Bug Logger (only runs on failure)

## Branch Protection Configuration

Recommended branch protection rules for `main`:

1. **Require pull request reviews before merging**
   - Required approving reviews: 1
   - Dismiss stale reviews when new commits are pushed

2. **Require status checks to pass before merging**
   - Require branches to be up to date before merging
   - Required checks:
     - `Lint Check (Ruff)`
     - `Format Check (Black)`
     - `Type Check (MyPy)`
     - `Test Suite (Pytest)`
     - `Build Verification`

3. **Require conversation resolution before merging**

4. **Do not allow bypassing the above settings**

## Local Testing Before Push

To avoid CI failures, run these commands locally before pushing:

```bash
# Install dependencies
make install

# Run all quality checks
make lint          # Linting
make format        # Auto-format code
make type-check    # Type checking
make test          # Run tests with coverage

# Or run everything at once
make lint && make type-check && make test
```

## Troubleshooting CI Failures

### Lint Failures
**Error**: `Ruff found linting issues`

**Fix**:
```bash
# Check what's wrong
make lint

# Auto-fix most issues
poetry run ruff check --fix .
```

### Format Failures
**Error**: `Black formatting check failed`

**Fix**:
```bash
# Format all code
make format

# Then commit the formatting changes
git add .
git commit -m "Fix code formatting"
```

### Type Check Failures
**Error**: `MyPy found type errors`

**Fix**:
```bash
# See specific type errors
make type-check

# Common fixes:
# - Add missing type hints
# - Fix type mismatches
# - Add # type: ignore for complex cases (use sparingly)
```

### Test Failures
**Error**: `Tests failed` or `Coverage below 80%`

**Fix**:
```bash
# Run tests locally to debug
make test

# Run specific test file
PYTHONPATH=src poetry run pytest tests/path/to/test_file.py -v

# Check coverage report
make coverage  # Opens HTML report in browser
```

### Build Failures
**Error**: `Build verification failed`

**Fix**:
```bash
# Check Django configuration
PYTHONPATH=src poetry run python manage.py check --deploy

# Check if static files can be collected
PYTHONPATH=src poetry run python manage.py collectstatic --noinput

# Verify Poetry build
poetry build
```

### Cache Issues
**Error**: `Dependency installation takes too long` or `Stale dependencies`

**Fix**: Clear GitHub Actions cache
1. Go to repository → Actions → Caches
2. Delete caches for your branch
3. Re-run workflow (will rebuild cache)

## Performance Optimization

### Current Performance
With caching enabled:
- **Cold run** (cache miss): ~12-15 minutes
- **Warm run** (cache hit): ~8-10 minutes
- **Parallel jobs**: Lint, format, type-check, security run simultaneously

### Speed Improvements
1. **Dependency caching**: Saves ~3-5 minutes per run
2. **Parallel jobs**: Runs quality checks simultaneously
3. **Concurrency control**: Cancels outdated workflow runs
4. **Early failure**: Fails fast on linting/format errors

### Monitoring Workflow Performance
Check workflow run times in:
- GitHub → Actions → Backend CI/CD → Select workflow run
- Review job durations and identify bottlenecks

## Cost Considerations

### GitHub Actions Minutes
- **Public repositories**: Unlimited free minutes
- **Private repositories**: 2,000 free minutes/month

### Estimated Usage (per PR)
- ~10 minutes per workflow run
- ~2-4 runs per PR (initial + revisions)
- **Total**: ~20-40 minutes per PR

### Cost Optimization Tips
1. Use concurrency control to cancel old runs
2. Cache dependencies to reduce installation time
3. Run expensive jobs only when needed
4. Use branch protection to reduce failed workflow runs

## Monitoring and Observability

### Workflow Status
Check workflow status:
- GitHub → Actions → Backend CI/CD
- PR checks section (shows all job statuses)
- Branch protection status

### Job Summaries
Each job adds summary to GitHub Actions:
- Test coverage statistics
- Build verification results
- Security audit findings

Access summaries:
- Workflow run → Job → Summary tab

### Artifacts
Download generated artifacts:
- Coverage reports (HTML, XML, JSON)
- Retention: 7 days
- Location: Workflow run → Artifacts section

### Logs
View detailed logs:
- Workflow run → Select job → Expand step
- Full logs available for debugging
- Logs retained for 90 days

## Future Enhancements

### Planned Improvements
1. **Docker image building**
   - Build and test Docker containers
   - Push to container registry (GHCR)
   - Container vulnerability scanning

2. **Database integration testing**
   - PostgreSQL service container
   - Redis service container
   - Full integration test suite

3. **Deployment automation**
   - Automatic deployment to staging
   - Manual approval for production
   - Blue-green deployment strategy

4. **Enhanced security scanning**
   - SAST (Static Application Security Testing)
   - Dependency vulnerability scanning
   - Secret scanning

5. **Performance benchmarking**
   - API response time benchmarks
   - Database query performance
   - Memory and CPU profiling

## Related Documentation

- **GitHub Actions**: `.github/workflows/backend-ci.yml`
- **Secrets Configuration**: `.github/workflows/.env`
- **Testing Guide**: `docs/TESTING.md`
- **Development Guide**: `docs/DEVELOPMENT.md`
- **Quick Start**: `docs/QUICK_START.md`

## Support and Questions

For questions about the CI/CD pipeline:
1. Check this documentation first
2. Review workflow logs for error details
3. Check `.github/workflows/.env` for secrets configuration
4. Review GitHub Actions documentation for advanced features

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Poetry Documentation](https://python-poetry.org/docs/)
- [pytest Documentation](https://docs.pytest.org/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/)
