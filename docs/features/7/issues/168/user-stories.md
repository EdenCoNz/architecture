# User Stories: Fix Issue #168 - Backend CI/CD Test Failures

## Issue Context
- **Issue Number**: #168
- **Feature ID**: 7
- **Branch**: feature/7-initialise-backend-api
- **Total Failures**: 1
- **Failure Categories**: Database connection lifecycle management
- **Additional Concerns**: 313 deprecation warnings (non-blocking)

## Story Overview

This fix addresses one critical test failure and deprecation warnings in the backend test suite:
1. Database connection closure and reopening functionality (CRITICAL - blocking CI/CD)
2. Deprecated datetime API usage (LOW PRIORITY - non-blocking, cleanup task)

## Execution Order

### Phase 1: Critical Fix (Story 1)
Must be completed to unblock CI/CD pipeline.

### Phase 2: Code Quality Improvement (Story 2)
Can be completed after Story 1, or deferred to future maintenance cycle.

---

## Story 1: Fix Database Connection Lifecycle Management

**ID**: 7-168-1
**Title**: Enable database connection recovery after closure
**Assigned Agent**: backend-developer
**Priority**: Critical
**Estimated Effort**: 1 day

### User Story

As a system operator, I need the application to recover from database connection failures so that the system can automatically reconnect without requiring manual intervention or application restarts.

### Context

When a database connection is closed (either manually or due to network issues, timeouts, or server restarts), the application currently cannot reestablish connectivity. Attempting to use a cursor after connection closure results in "connection already closed" errors. This prevents the application from recovering gracefully from database disconnections, which could lead to prolonged downtime in production environments where database connections may be dropped due to network issues, connection pool recycling, or maintenance operations.

### Acceptance Criteria

**Given** the application has an established database connection
**When** the connection is closed due to errors, timeouts, or manual closure
**Then** the application should be able to reestablish a new connection automatically when database operations are attempted

**Given** a database connection has been closed
**When** a database query or operation is executed
**Then** the operation should succeed by automatically creating a new connection rather than failing with "connection already closed" errors

**Given** the database connection management system is being tested
**When** running tests that simulate connection closure and reopening scenarios
**Then** all connection lifecycle tests should pass, demonstrating proper connection recovery behavior

### Technical Reference

The following technical details are provided for implementation guidance:

- **Test File**: `tests/unit/test_database_connectivity.py:35`
- **Test Name**: `test_database_connection_can_be_closed_and_reopened`
- **Error**: `django.db.utils.InterfaceError: connection already closed`
- **Root Cause**: After calling `connection.close()`, the code attempts to create a cursor using the closed connection object without properly reconnecting
- **Impact**: Prevents automatic recovery from database disconnections, requiring application restarts

**Error Traceback**:
```
tests/unit/test_database_connectivity.py:35: in test_database_connection_can_be_closed_and_reopened
    with connection.cursor() as cursor:
         ^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.12.12/x64/lib/python3.12/site-packages/django/utils/asyncio.py:26: in inner
    return func(*args, **kwargs)
/opt/hostedtoolcache/Python/3.12.12/x64/lib/python3.12/site-packages/django/db/backends/base/base.py:320: in cursor
/opt/hostedtoolcache/Python/3.12.12/x64/lib/python3.12/site-packages/django/db/backends/base/base.py:298: in _cursor
    return self._prepare_cursor(self.create_cursor(name))
/opt/hostedtoolcache/Python/3.12.12/x64/lib/python3.12/site-packages/django/db/backends/postgresql/base.py:429: in create_cursor
    cursor = self.connection.cursor()
psycopg2.InterfaceError: connection already closed
```

### Definition of Done

- [ ] Database connections can be closed and reopened without errors
- [ ] Test `test_database_connection_can_be_closed_and_reopened` passes
- [ ] The application properly handles connection lifecycle events
- [ ] All existing database connectivity tests continue to pass (428 passing tests maintained)
- [ ] CI/CD pipeline passes without connection-related failures

---

## Story 2: Update Deprecated Datetime API Usage

**ID**: 7-168-2
**Title**: Replace deprecated datetime.utcnow() with timezone-aware alternative
**Assigned Agent**: backend-developer
**Priority**: Low
**Estimated Effort**: 0.5 days

### User Story

As a developer maintaining the codebase, I need the application to use current Python datetime APIs so that the code remains compatible with future Python versions and follows modern best practices for timezone handling.

### Context

The codebase currently uses `datetime.datetime.utcnow()` which has been deprecated in favor of the timezone-aware `datetime.datetime.now(datetime.UTC)`. While this is non-blocking and the code continues to function, the deprecation warnings clutter the test output (313 warnings) and indicate technical debt that should be addressed to maintain forward compatibility with future Python versions.

### Acceptance Criteria

**Given** the application generates timestamps for error handling or logging
**When** timestamp creation code is executed
**Then** it should use timezone-aware datetime methods that follow current Python standards

**Given** the test suite is executed
**When** running tests with deprecation warnings enabled
**Then** there should be no deprecation warnings related to datetime.utcnow() usage

**Given** the codebase uses timezone-aware datetime methods
**When** timestamps are compared or stored
**Then** all datetime operations should maintain timezone awareness and UTC semantics

### Technical Reference

The following technical details are provided for implementation guidance:

- **Affected File**: `backend/apps/core/exceptions.py`
- **Affected Lines**: 76, 166, 201
- **Current Usage**: `datetime.datetime.utcnow()`
- **Recommended Replacement**: `datetime.datetime.now(datetime.UTC)`
- **Warning Count**: 313 deprecation warnings
- **Impact**: Non-blocking - code continues to work but uses deprecated API
- **Deprecation Context**: Python is moving toward explicit timezone-aware datetime handling

**Warning Pattern**:
```
DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
```

### Definition of Done

- [ ] All instances of `datetime.datetime.utcnow()` are replaced with timezone-aware alternatives
- [ ] No deprecation warnings related to datetime.utcnow() appear in test output
- [ ] All datetime operations maintain UTC timezone semantics
- [ ] All existing tests continue to pass (428 passing tests maintained)
- [ ] CI/CD pipeline runs without deprecation warnings related to datetime usage

---

## Summary

### Story Breakdown
- **Total Stories**: 2
- **Critical Stories**: 1 (Story 1)
- **Low Priority Stories**: 1 (Story 2)
- **Assigned Agents**: backend-developer (2 stories)
- **Execution Phases**: 2 (sequential)
- **Estimated Total Effort**: 1.5 days

### Story Quality Validation
- All stories focus on observable system behaviors and outcomes
- All stories are implementation-agnostic (no specific library or framework constraints beyond existing stack)
- All acceptance criteria describe testable, user-observable behaviors
- Technical references provided separately for developer guidance
- Stories prioritized based on CI/CD blocking impact

### Execution Strategy
**Phase 1 (Critical)**: Story 1 must be completed first to unblock the CI/CD pipeline. This is the only test failure preventing the pipeline from passing.

**Phase 2 (Cleanup)**: Story 2 can be completed after Story 1, or deferred to a future maintenance cycle as it is non-blocking. While the 313 warnings are noisy, they do not prevent the application from functioning or tests from passing.

### Impact Assessment
- **Test Statistics**: 1 failed, 428 passed, 2 skipped
- **CI/CD Status**: BLOCKED by Story 1, Story 2 is optional cleanup
- **Production Impact**: Story 1 addresses potential production reliability issue with connection recovery
- **Code Quality**: Story 2 addresses technical debt and future compatibility
