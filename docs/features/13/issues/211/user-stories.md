# Feature #13 - Issue #211: Fix Backend Test Database Connectivity

**Issue**: CI/CD Pipeline Failed: Build and Test - Run #3
**Branch**: feature/13-end-to-end-testing
**Created**: 2025-10-26
**Type**: Fix

## Problem Summary

The CI/CD pipeline is failing during the backend test execution step. The backend test container cannot establish a connection to the PostgreSQL database service, receiving "Connection refused" errors when attempting to connect to `db:5432`. This prevents the backend test suite from running and blocks the entire CI/CD pipeline.

### Root Cause Analysis

The workflow uses `docker compose run --rm backend pytest` to execute tests, which creates a new ephemeral container. However, this container is experiencing one of the following issues:

1. **Race Condition**: The database service might not be fully ready to accept connections despite passing the `pg_isready` check
2. **Network Connectivity**: The ephemeral test container created by `docker compose run` might have networking issues connecting to the `db` service on the `app-network`
3. **Service Discovery**: The `db` hostname might not be resolving correctly for the ephemeral test container
4. **Health Check Timing**: The current health check validation might not be sufficient to ensure the database is truly ready for test connections

### Business Impact

- Backend tests cannot execute, preventing validation of code changes
- CI/CD pipeline is blocked, preventing deployment to staging and production
- Development velocity is reduced as developers cannot merge code until tests pass
- Quality assurance is compromised without automated test validation

---

## User Stories

### Story 13-Fix-211.1: Ensure Database Service is Ready for Test Connections

**As a** developer running automated tests
**I want** the database service to be fully ready before tests execute
**So that** my test suite can reliably connect and validate backend functionality

**Description**:

When the CI/CD pipeline executes backend tests, the database service must be completely ready to accept connections before the test container attempts to connect. Currently, the workflow waits for `pg_isready` to succeed, but this only validates that PostgreSQL is running - not that it's ready to accept application connections.

The system should implement more robust database readiness validation that ensures:
- PostgreSQL is accepting TCP connections on port 5432
- The database can process queries successfully
- Connection pooling is initialized and ready
- The test database is accessible and functional

**Acceptance Criteria**:

1. **Given** the CI/CD workflow starts the database service, **when** the readiness check completes successfully, **then** the database should be able to accept test connections immediately without connection refused errors

2. **Given** the backend test container attempts to connect to the database, **when** the connection is established, **then** the connection should succeed within the first attempt without retry logic needed

3. **Given** the CI/CD workflow executes the backend test step, **when** tests run using `docker compose run --rm backend pytest`, **then** the test database connection initialization should succeed without "Connection refused" errors

4. **Given** the workflow validates database readiness, **when** checking if the service is ready, **then** the validation should confirm the database can execute queries, not just that the process is running

**Technical Context** (for implementer reference):

From CI/CD logs (Job ID: 53670800831):
```
Run docker compose exec -T backend pytest tests/unit/ --maxfail=1 -v
Testing database connection...
Traceback (most recent call last):
  File "/usr/local/lib/python3.12/site-packages/psycopg/conninfo.py", line 736, in connect
    raise ex.with_traceback(None)
psycopg.OperationalError: connection failed: Connection refused
	Is the server running on host "db" (172.26.0.4) and accepting
	TCP/IP connections on port 5432?
```

Current workflow approach:
```yaml
# Start dependencies
docker compose up -d db redis

# Wait for dependencies
timeout 60 bash -c 'until docker compose exec -T db pg_isready -U postgres; do sleep 2; done'
timeout 60 bash -c 'until docker compose exec -T redis redis-cli ping | grep -q PONG; do sleep 2; done'

# Run backend tests
docker compose run --rm \
  -e DJANGO_SETTINGS_MODULE=config.settings.test \
  -e SECRET_KEY=test-secret-key \
  backend \
  pytest --cov=apps --cov-report=xml --cov-report=term-missing --junitxml=pytest-report.xml -n auto
```

**Assigned Agent**: devops-engineer

---

### Story 13-Fix-211.2: Verify Test Container Network Connectivity

**As a** CI/CD pipeline operator
**I want** ephemeral test containers to reliably connect to database services
**So that** automated tests can execute successfully in isolated containers

**Description**:

When using `docker compose run --rm backend pytest` to execute tests, Docker creates a new ephemeral container that must connect to the existing database service over the Docker network. The test container must be able to resolve the `db` hostname and establish TCP connections to port 5432.

The system should ensure that ephemeral containers created with `docker compose run` have proper network connectivity to all dependent services (database, Redis) and can successfully resolve service hostnames via Docker's internal DNS.

This story focuses on validating and documenting the network connectivity behavior, and implementing any necessary configuration to ensure reliable service-to-service communication for ephemeral test containers.

**Acceptance Criteria**:

1. **Given** a test container is created with `docker compose run --rm backend`, **when** the container attempts DNS resolution for `db` hostname, **then** it should successfully resolve to the database service's IP address on the `app-network`

2. **Given** the test container has resolved the database hostname, **when** it attempts to establish a TCP connection to port 5432, **then** the connection should succeed without "Connection refused" errors

3. **Given** the CI/CD workflow runs backend tests, **when** using `docker compose run --rm backend pytest`, **then** the test container should successfully connect to both the database service (db:5432) and cache service (redis:6379)

4. **Given** the test execution completes, **when** reviewing logs and diagnostics, **then** there should be evidence that network connectivity was established successfully (connection logs, successful queries, etc.)

**Technical Context** (for implementer reference):

Current docker-compose.yml network configuration:
```yaml
networks:
  app-network:
    driver: bridge
    name: ${COMPOSE_PROJECT_NAME:-app}-network
```

Database service configuration:
```yaml
db:
  image: postgres:15-alpine
  container_name: app-db
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-postgres} -d ${DB_NAME:-backend_db} || exit 1"]
    interval: 5s
    timeout: 3s
    retries: 5
    start_period: 15s
  networks:
    - app-network
```

Backend service configuration (for reference):
```yaml
backend:
  depends_on:
    db:
      condition: service_healthy
      restart: true
    redis:
      condition: service_healthy
      restart: true
  networks:
    - app-network
```

The error indicates the database service is running at IP 172.26.0.4 but refusing connections. Need to verify:
1. Ephemeral containers join the `app-network` correctly
2. Hostname resolution works for `db` service name
3. Port 5432 is accessible from ephemeral containers
4. PostgreSQL is configured to accept connections from all network IPs

**Assigned Agent**: devops-engineer

---

## Execution Order

### Sequential Execution

1. **Story 13-Fix-211.1** - Enhance database readiness validation
   - Implement robust health checks that verify database can accept connections
   - Add query-based validation to confirm database is fully operational
   - Update CI/CD workflow to use enhanced readiness checks

2. **Story 13-Fix-211.2** - Verify and validate network connectivity
   - Test ephemeral container network connectivity to database service
   - Document network behavior and validate service discovery
   - Implement diagnostics or configuration changes if needed

### Dependencies

- Story 13-Fix-211.2 depends on Story 13-Fix-211.1 being completed
  - Database must be properly initialized before network connectivity can be validated
  - Enhanced health checks ensure database is ready before connectivity tests

---

## Success Criteria

- CI/CD pipeline backend test step executes successfully without database connection errors
- All backend tests run and complete in the CI/CD environment
- Database connectivity is established reliably on first attempt
- No "Connection refused" errors in test execution logs
- Pipeline progresses to subsequent stages (linting, frontend tests, deployment)

---

## Notes for Implementation

### Key Investigation Areas

1. **Health Check Enhancement**: The current `pg_isready` check only verifies the PostgreSQL process is running, not that it's ready for connections. Consider:
   - Adding a test query execution (e.g., `SELECT 1`)
   - Validating connection pool initialization
   - Adding additional wait time after health check passes

2. **Docker Compose Run Behavior**: The `docker compose run` command creates ephemeral containers that should join the same network as `docker compose up` services. Verify:
   - Network attachment is correct (`app-network`)
   - Service discovery DNS is working
   - PostgreSQL `pg_hba.conf` allows connections from all container IPs

3. **Timing and Race Conditions**: There may be a delay between the health check passing and the database being ready for application connections. Consider:
   - Adding a brief sleep after health check success
   - Implementing retry logic in test initialization
   - Using Docker's `start_period` more effectively

4. **Environment Variables**: Ensure the test container has correct database connection parameters:
   - `DB_HOST=db` (uses service name)
   - `DB_PORT=5432`
   - Credentials match docker-compose environment

### References

- Docker Compose documentation: https://docs.docker.com/compose/
- PostgreSQL connection troubleshooting: https://www.postgresql.org/docs/current/server-start.html
- Docker networking: https://docs.docker.com/network/
- GitHub Actions workflow file: `.github/workflows/unified-ci-cd.yml` (lines 110-133)
- Docker Compose configuration: `docker-compose.yml` (lines 77-125)
