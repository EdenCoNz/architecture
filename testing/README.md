# Test Execution Environment (Feature #13 - Story 13.1)

## Overview

This directory contains a **dedicated test execution environment** for running end-to-end tests that validate the complete application stack. The test environment is **completely isolated** from production and development environments, ensuring tests never affect other environments.

## Directory Structure

```
testing/
├── e2e/              # End-to-end tests (user workflows, UI interactions)
├── integration/      # Integration tests (API contracts, service interactions)
├── visual/           # Visual regression tests (UI consistency)
├── performance/      # Performance tests (load, stress, benchmarks)
├── fixtures/         # Test data and fixtures
├── reports/          # Test artifacts (logs, screenshots, reports)
├── config/           # Test configuration files
├── Dockerfile.test-runner   # Test runner container image
├── requirements.txt  # Python test dependencies
├── package.json      # Node.js test dependencies
├── run-tests.sh      # Test orchestration script
└── README.md         # This file
```

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- At least 4GB RAM available for test containers
- Ports 80, 5174, 5433, 6380, 8001 available (test environment ports)

### Running Tests

**All tests with clean environment:**
```bash
./testing/run-tests.sh --clean
```

**Specific test suite:**
```bash
./testing/run-tests.sh --suite e2e
./testing/run-tests.sh --suite integration
./testing/run-tests.sh --suite visual
./testing/run-tests.sh --suite performance
```

**E2E tests with visible browser (debugging):**
```bash
./testing/run-tests.sh --suite e2e --headed
```

**Verbose output:**
```bash
./testing/run-tests.sh --verbose
```

### Manual Test Execution

**Start test environment:**
```bash
docker compose -f docker-compose.yml -f compose.test.yml --env-file .env.test up -d
```

**Run specific tests:**
```bash
# E2E tests
docker compose -f docker-compose.yml -f compose.test.yml run --rm test-runner npx playwright test

# Integration tests
docker compose -f docker-compose.yml -f compose.test.yml run --rm test-runner pytest integration/

# Visual regression tests
docker compose -f docker-compose.yml -f compose.test.yml run --rm test-runner npm run test:visual

# Performance tests
docker compose -f docker-compose.yml -f compose.test.yml run --rm test-runner npm run test:performance
```

**Stop test environment:**
```bash
docker compose -f docker-compose.yml -f compose.test.yml --env-file .env.test down
```

**Clean test environment (remove volumes):**
```bash
docker compose -f docker-compose.yml -f compose.test.yml --env-file .env.test down -v
```

## Test Environment Isolation

The test environment is **completely isolated** from development and production:

| Component | Development | Test | Production |
|-----------|-------------|------|------------|
| Database Port | 5432 | 5433 | Internal only |
| Redis Port | 6379 | 6380 | Internal only |
| Backend Port | 8000 | 8001 | Internal only |
| Frontend Port | 5173 | 5174 | Internal only |
| Database Name | `backend_db` | `backend_test_db` | Environment-specific |
| Database User | `postgres` | `postgres_test` | Environment-specific |
| Container Names | `app-*` | `app-*-test` | Environment-specific |
| Volumes | `app-postgres-data` | `app-postgres-test-data` | Environment-specific |

## Test Artifacts

All test outputs are stored in the `testing/reports/` directory:

```
reports/
├── logs/            # Application and test execution logs
│   ├── application.log
│   ├── sql.log
│   ├── errors.log
│   └── services.log
├── screenshots/     # E2E test failure screenshots
├── videos/          # E2E test recordings
├── coverage/        # Code coverage reports
│   ├── integration/
│   ├── e2e/
│   └── combined/
├── html/            # HTML test reports
│   ├── integration-report.html
│   ├── e2e-report.html
│   ├── visual-report.html
│   └── performance-report.html
└── json/            # JSON test reports (for CI/CD)
    ├── integration-report.json
    ├── e2e-report.json
    └── visual-report.json
```

### Viewing Reports

**HTML Reports:**
```bash
# Open integration test report
open testing/reports/html/integration-report.html

# Open coverage report
open testing/reports/coverage/index.html

# Open Playwright report
npx playwright show-report testing/reports/playwright-report
```

**Logs:**
```bash
# View application logs
cat testing/reports/logs/application.log

# View SQL queries
cat testing/reports/logs/sql.log

# View error logs
cat testing/reports/logs/errors.log
```

## Test Types

### E2E Tests (`e2e/`)

End-to-end tests validate complete user workflows using Playwright.

**Framework:** Playwright
**Purpose:** User workflow validation, UI interactions
**Runs against:** Complete application stack (frontend + backend + database)

See [e2e/README.md](e2e/README.md) for details.

### Integration Tests (`integration/`)

Integration tests validate API contracts and service interactions using pytest.

**Framework:** pytest + pytest-django
**Purpose:** API validation, service integration
**Runs against:** Backend API + database + Redis

See [integration/README.md](integration/README.md) for details.

### Visual Regression Tests (`visual/`)

Visual tests detect unintended UI changes across releases.

**Framework:** Playwright + pixelmatch
**Purpose:** UI consistency, visual regression detection
**Runs against:** Frontend + backend

See [visual/README.md](visual/README.md) for details.

### Performance Tests (`performance/`)

Performance tests validate response times and throughput under load.

**Framework:** Locust
**Purpose:** Load testing, performance benchmarking
**Runs against:** Complete application stack

See [performance/README.md](performance/README.md) for details.

## Configuration

### Environment Variables (`.env.test`)

The test environment is configured via `.env.test` file in the project root:

```bash
# Database
TEST_DB_NAME=backend_test_db
TEST_DB_USER=postgres_test
TEST_DB_PASSWORD=postgres_test_secure_password

# Django
DJANGO_SETTINGS_MODULE=backend.settings.test
DEBUG=True

# Test execution
PYTEST_ARGS=--verbose --tb=short
PLAYWRIGHT_HEADLESS=true
PERFORMANCE_USERS=10
```

See `.env.test` for all available configuration options.

### Test Runner Configuration

**Python dependencies:** `testing/requirements.txt`
**Node.js dependencies:** `testing/package.json`
**Docker image:** `testing/Dockerfile.test-runner`

## Test Data and Fixtures

Test data is managed in the `fixtures/` directory:

```
fixtures/
├── users.json       # Test user accounts
├── assessments.json # Test assessment data
├── profiles.json    # Test user profiles
└── README.md        # Fixture documentation
```

**Loading fixtures:**
```bash
docker compose -f docker-compose.yml -f compose.test.yml exec backend \
    python manage.py loaddata testing/fixtures/users.json
```

See [fixtures/README.md](fixtures/README.md) for fixture creation and management.

## CI/CD Integration

### Running Tests in CI/CD

The test orchestration script is designed for CI/CD integration:

```yaml
# GitHub Actions example
- name: Run E2E Tests
  run: ./testing/run-tests.sh --suite e2e --clean

- name: Upload Test Reports
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: test-reports
    path: testing/reports/
```

### Test Reports in CI/CD

JSON reports are generated for CI/CD consumption:

```bash
# Parse test results in CI/CD
jq '.summary' testing/reports/json/integration-report.json
```

## Troubleshooting

### Tests Fail to Start

**Check service health:**
```bash
docker compose -f docker-compose.yml -f compose.test.yml ps
```

**View service logs:**
```bash
docker compose -f docker-compose.yml -f compose.test.yml logs backend
docker compose -f docker-compose.yml -f compose.test.yml logs frontend
docker compose -f docker-compose.yml -f compose.test.yml logs db
```

### Port Conflicts

If test ports are already in use, stop conflicting services:

```bash
# Check what's using test ports
lsof -i :5433  # Test database
lsof -i :6380  # Test Redis
lsof -i :8001  # Test backend
lsof -i :5174  # Test frontend
```

### Database Connection Errors

**Reset test database:**
```bash
docker compose -f docker-compose.yml -f compose.test.yml down -v
docker compose -f docker-compose.yml -f compose.test.yml up -d db
```

**Check database is ready:**
```bash
docker compose -f docker-compose.yml -f compose.test.yml exec db \
    pg_isready -U postgres_test -d backend_test_db
```

### Out of Disk Space

**Clean old test artifacts:**
```bash
# Remove old reports
rm -rf testing/reports/*

# Remove old Docker images
docker image prune -a

# Remove test volumes
docker compose -f docker-compose.yml -f compose.test.yml down -v
```

### Playwright Browser Issues

**Install browser dependencies:**
```bash
docker compose -f docker-compose.yml -f compose.test.yml run --rm test-runner \
    npx playwright install --with-deps
```

## Best Practices

### Test Isolation

1. **Always use the test environment** - Never run tests against dev/prod
2. **Clean state between runs** - Use `--clean` flag for reliable tests
3. **Independent tests** - Tests should not depend on each other
4. **Isolated data** - Each test should create and clean up its own data

### Performance

1. **Parallel execution** - Use `pytest-xdist` for faster integration tests
2. **Selective testing** - Run only affected test suites during development
3. **Cache dependencies** - Docker layer caching speeds up container builds
4. **Resource limits** - Configure appropriate memory/CPU limits

### Debugging

1. **Headed mode** - Use `--headed` flag to see browser during E2E tests
2. **Debug mode** - Use `--debug` flag for Playwright step-by-step debugging
3. **Verbose output** - Use `--verbose` flag for detailed logs
4. **Screenshots** - Automatically captured on test failures

### CI/CD

1. **Clean environment** - Always use `--clean` in CI/CD pipelines
2. **Artifact upload** - Upload reports and screenshots as CI/CD artifacts
3. **Fail fast** - Configure test timeout to prevent hung pipelines
4. **Parallel jobs** - Run different test suites in parallel CI/CD jobs

## Development Workflow

### Adding New Tests

1. **Create test file in appropriate directory:**
   - E2E: `testing/e2e/test_feature.spec.ts`
   - Integration: `testing/integration/test_feature.py`
   - Visual: `testing/visual/test_feature.spec.ts`
   - Performance: `testing/performance/test_feature.py`

2. **Run tests locally:**
   ```bash
   ./testing/run-tests.sh --suite e2e
   ```

3. **Verify test isolation:**
   ```bash
   ./testing/run-tests.sh --suite e2e --clean
   ```

4. **Commit tests with implementation code**

### Updating Test Environment

1. **Update dependencies:**
   - Python: `testing/requirements.txt`
   - Node.js: `testing/package.json`

2. **Rebuild test runner:**
   ```bash
   docker compose -f docker-compose.yml -f compose.test.yml build test-runner
   ```

3. **Test with clean environment:**
   ```bash
   ./testing/run-tests.sh --clean
   ```

## Support and Documentation

- **Test Framework Docs:**
  - Playwright: https://playwright.dev/
  - pytest: https://docs.pytest.org/
  - Locust: https://docs.locust.io/

- **Project Documentation:**
  - Feature #13 User Stories: `docs/features/13/user-stories.md`
  - Implementation Log: `docs/features/13/implementation-log.json`

- **Getting Help:**
  - Check troubleshooting section above
  - Review test suite README files
  - Check service logs for errors
  - Review CI/CD pipeline logs

## License

Same as main project.
