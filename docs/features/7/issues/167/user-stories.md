# User Stories: Fix Issue #167 - Backend CI/CD Test Failures

## Issue Context
- **Issue Number**: #167
- **Feature ID**: 7
- **Branch**: feature/7-initialise-backend-api
- **Total Failures**: 2
- **Failure Categories**: Database connection management, Test database configuration

## Story Overview

This fix addresses two test failures in the backend test suite:
1. Database connection closure and reopening functionality
2. Test database name configuration expectations

## Execution Order

### Phase 1: Parallel Fixes (Stories 1-2)
Both stories can be implemented in parallel as they address independent test failures.

---

## Story 1: Fix Database Connection Reuse After Closure

**ID**: 7-167-1
**Title**: Fix database connection reopening after manual closure
**Assigned Agent**: backend-developer
**Priority**: High
**Estimated Effort**: 1 day

### User Story

As a system administrator, I need the application to properly handle database connection lifecycle events so that the system can recover from connection closures without crashing.

### Context

When a database connection is manually closed, the system currently cannot reopen it because the connection object remains in a "closed" state. This prevents proper error recovery and connection pool management, which could cause application failures in production when connections need to be recycled or recovered after errors.

### Acceptance Criteria

**Given** the application has an active database connection
**When** the connection is manually closed using Django's connection management
**Then** the system should be able to establish a new connection when database operations are attempted

**Given** a database connection has been closed
**When** a database query is executed
**Then** the query should succeed without raising "connection already closed" errors

**Given** the database connection lifecycle is being tested
**When** running the test suite with connection close/reopen scenarios
**Then** all connection management tests should pass

### Technical Reference

The following technical details are provided for implementation guidance:

- **Test File**: `tests/unit/test_database_connectivity.py:35`
- **Error**: `django.db.utils.InterfaceError: connection already closed`
- **Root Cause**: After calling `connection.close()`, Django cannot reopen the connection because the psycopg2 connection object is in a closed state
- **Impact Area**: Connection pool management and error recovery scenarios

**Error Traceback**:
```
File: tests/unit/test_database_connectivity.py:35
Error: django.db.utils.InterfaceError: connection already closed
Traceback:
  tests/unit/test_database_connectivity.py:35: in test_database_connection_can_be_closed_and_reopened
    with connection.cursor() as cursor:
  django/db/backends/postgresql/base.py:429: in create_cursor
    cursor = self.connection.cursor()
  psycopg2.InterfaceError: connection already closed
```

### Definition of Done

- [ ] Database connections can be closed and reopened without errors
- [ ] Test `test_database_connection_can_be_closed_and_reopened` passes
- [ ] Solution handles Django's connection lifecycle properly
- [ ] All existing database connectivity tests continue to pass
- [ ] CI/CD pipeline passes for this test scenario

---

## Story 2: Fix Test Database Name Validation

**ID**: 7-167-2
**Title**: Update test database configuration validation
**Assigned Agent**: backend-developer
**Priority**: Medium
**Estimated Effort**: 0.5 days

### User Story

As a developer running the test suite, I need the test database configuration tests to account for Django's automatic test database naming conventions so that tests accurately validate the configuration without false failures.

### Context

When using pytest-xdist for parallel testing, Django automatically modifies the test database name by adding a "test_" prefix and a worker suffix (e.g., "_gw0"). The current test expects the exact database name from environment variables, which doesn't account for this standard Django behavior. This is a test implementation issue, not an application configuration problem.

### Acceptance Criteria

**Given** the test suite is running with parallel test execution enabled
**When** validating the test database configuration
**Then** the test should account for Django's automatic "test_" prefix and worker suffixes

**Given** Django creates a test database with name modifications
**When** checking database credentials match environment variables
**Then** the validation should verify the base database name is derived from the environment variable

**Given** the test suite runs with different parallel worker configurations
**When** validating database names
**Then** tests should pass regardless of worker count or parallel execution settings

### Technical Reference

The following technical details are provided for implementation guidance:

- **Test File**: `tests/unit/test_test_database_config.py:58`
- **Error**: `AssertionError: Should use DB_NAME from environment, expected test_backend_db but got test_test_backend_db_gw0`
- **Root Cause**: Test assertions don't account for Django's automatic test database naming convention (prefix "test_" + worker suffix "_gw0")
- **Impact**: This is a test issue, not an application configuration issue
- **Django Behavior**: When using pytest-xdist, Django automatically:
  - Prefixes database names with "test_"
  - Adds worker suffixes like "_gw0", "_gw1", etc.

**Error Details**:
```
File: tests/unit/test_test_database_config.py:58
Error: AssertionError: Should use DB_NAME from environment, expected test_backend_db but got test_test_backend_db_gw0
  assert 'test_test_backend_db_gw0' == 'test_backend_db'
    - test_backend_db
    + test_test_backend_db_gw0
    ? +++++               ++++
```

### Definition of Done

- [ ] Test validates that base database name comes from environment variable
- [ ] Test accounts for Django's "test_" prefix
- [ ] Test accounts for pytest-xdist worker suffixes
- [ ] Test `test_database_uses_credentials_from_env_variables` passes
- [ ] Test works correctly with both single-threaded and parallel execution
- [ ] CI/CD pipeline passes for this test scenario

---

## Summary

### Story Breakdown
- **Total Stories**: 2
- **Assigned Agents**: backend-developer (2 stories)
- **Execution Phases**: 1 (parallel)
- **Estimated Total Effort**: 1.5 days

### Story Quality Validation
- All stories focus on observable test outcomes
- All stories are implementation-agnostic (no specific library constraints)
- All acceptance criteria describe testable behaviors
- No prescriptive technical implementation details in user stories
- Technical references provided separately for developer guidance

### Execution Strategy
Both stories can be implemented in parallel as they address independent test failures with no dependencies between them.
