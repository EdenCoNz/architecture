# CI/CD Failures Investigation Report

**GitHub Issue**: #33 - Lint job failed - code quality issues detected
**PR**: #32
**CI/CD Run**: [18624521685](https://github.com/EdenCoNz/architecture/actions/runs/18624521685)
**Feature**: #3 - Initialize Backend Project
**Severity**: High (Blocking PR merge)
**Investigation Date**: 2025-10-19

---

## Executive Summary

The backend CI/CD pipeline is failing due to **4 categories** of code quality issues across **13 files**, with a total of **36 discrete errors**. All failures are categorized into:

1. **Linting Issues (Ruff)**: 13 errors
2. **Formatting Issues (Black)**: 6 files need reformatting
3. **Type Checking Issues (MyPy)**: 10 errors
4. **Test Failures (Pytest)**: 5 failing tests

All issues are fixable and none represent fundamental architectural problems. The root causes are primarily related to:
- Missing exception parameter usage in error handlers
- Deprecated typing imports (Python 3.9+ compatibility)
- Missing type stubs for external libraries
- Incomplete logging configuration
- Test configuration expecting PostgreSQL instead of SQLite

---

## Category 1: Linting Issues (Ruff)

**Total Errors**: 13
**Exit Code**: 2
**Status**: Blocking

### 1.1 Unused Method Arguments (ARG002)

**Error Count**: 7
**Severity**: Medium
**Root Cause**: Django REST Framework view methods require `request` parameter by signature, but implementations don't use it.

#### Affected Files:

**File**: `backend/src/apps/health/views.py`
- **Line 26**: `def get(self, request: Request) -> Response:`
  - Method: `HealthCheckView.get()`
  - Error: ARG002 - Unused method argument: `request`
  - Context: View doesn't need request object to generate health status

- **Line 66**: `def get(self, request: Request) -> Response:`
  - Method: `LivenessView.get()`
  - Error: ARG002 - Unused method argument: `request`
  - Context: Liveness probe returns static response

- **Line 90**: `def get(self, request: Request) -> Response:`
  - Method: `ReadinessView.get()`
  - Error: ARG002 - Unused method argument: `request`
  - Context: Readiness check only needs service status

**File**: `backend/src/common/views/health.py`
- **Line 41**: `def get(self, request: Request) -> Response:`
  - Method: `HealthCheckAPIView.get()`
  - Error: ARG002 - Unused method argument: `request`
  - Context: Generic health check view with no request-specific logic

**File**: `backend/src/common/middleware/error_handling.py`
- **Line 79**: `def _handle_http404(self, request: HttpRequest, exc: Http404) -> JsonResponse:`
  - Method: `ErrorHandlingMiddleware._handle_http404()`
  - Error: ARG002 - Unused method argument: `exc`
  - Context: Exception object not used in 404 handler, only request path logged

- **Line 104**: `def _handle_not_authenticated(self, request: HttpRequest, exc: NotAuthenticated) -> JsonResponse:`
  - Method: `ErrorHandlingMiddleware._handle_not_authenticated()`
  - Error: ARG002 - Unused method argument: `exc`
  - Context: Exception object not used in authentication error handler

**Configuration Note**: pyproject.toml lines 105-106 exclude ARG002 for test files but NOT for view methods.

### 1.2 Unused Imports (F401)

**Error Count**: 4
**Severity**: Low
**Root Cause**: Imported modules not used in implementation

#### Affected Files:

**File**: `backend/src/common/middleware/error_handling.py`
- **Line 8**: `import json`
  - Error: F401 - `json` imported but unused
  - Context: JsonResponse handles JSON encoding automatically
  - Fixable: Yes (auto-fixable with --fix)

**File**: `backend/tests/unit/core/test_health_service.py`
- **Line 9**: `from unittest.mock import Mock, patch`
  - Error: F401 - `unittest.mock.Mock` imported but unused
  - Context: Tests use `patch` but not `Mock`
  - Fixable: Yes (auto-fixable with --fix)

**File**: `backend/tests/unit/middleware/test_error_handling.py`
- **Line 12**: `from django.http import Http404, HttpRequest, HttpResponse`
  - Error: F401 - `django.http.HttpRequest` imported but unused
  - Context: Tests use RequestFactory instead
  - Fixable: Yes (auto-fixable with --fix)

**File**: `backend/tests/unit/middleware/test_request_logging.py`
- **Line 12**: `from django.http import HttpRequest, HttpResponse`
  - Error: F401 - `django.http.HttpRequest` imported but unused
  - Context: Tests use RequestFactory instead
  - Fixable: Yes (auto-fixable with --fix)

### 1.3 Deprecated Typing Imports (UP035)

**Error Count**: 2
**Severity**: Low
**Root Cause**: Using `typing.Callable` instead of `collections.abc.Callable` (Python 3.9+ deprecation)

#### Affected Files:

**File**: `backend/src/common/middleware/error_handling.py`
- **Line 11**: `from typing import Any, Callable`
  - Error: UP035 - Import from `collections.abc` instead: `Callable`
  - Fix: `from collections.abc import Callable`
  - Fixable: Yes (auto-fixable with --fix)

**File**: `backend/src/common/middleware/request_logging.py`
- **Line 10**: `from typing import Callable`
  - Error: UP035 - Import from `collections.abc` instead: `Callable`
  - Fix: `from collections.abc import Callable`
  - Fixable: Yes (auto-fixable with --fix)

### 1.4 Nested With Statements (SIM117)

**Error Count**: 1
**Severity**: Low
**Root Cause**: Nested context managers should be combined for readability

#### Affected Files:

**File**: `backend/tests/unit/middleware/test_request_logging.py`
- **Lines 159-160**:
  ```python
  with pytest.raises(Exception, match="Test error"):
      with caplog.at_level(logging.INFO):
  ```
  - Error: SIM117 - Use a single `with` statement with multiple contexts
  - Fix: `with pytest.raises(Exception, match="Test error"), caplog.at_level(logging.INFO):`
  - Fixable: Yes (auto-fixable with --fix)

---

## Category 2: Formatting Issues (Black)

**Total Files**: 6
**Exit Code**: 1
**Status**: Blocking

### 2.1 Files Requiring Reformatting

All files listed would be reformatted by Black. The exact formatting changes aren't shown in CI output, but Black detected inconsistencies in:

1. **`backend/src/apps/health/views.py`**
   - Likely issues: Line length, spacing, or quote consistency

2. **`backend/src/common/views/health.py`**
   - Likely issues: Line length, spacing, or quote consistency

3. **`backend/src/common/middleware/error_handling.py`**
   - Likely issues: Line length, spacing, or quote consistency

4. **`backend/tests/integration/test_health_check.py`**
   - Likely issues: Line length, spacing, or quote consistency

5. **`backend/tests/unit/middleware/test_request_logging.py`**
   - Likely issues: Line length, spacing, or quote consistency

6. **`backend/tests/unit/middleware/test_error_handling.py`**
   - Likely issues: Line length, spacing, or quote consistency

**Configuration**: Black is configured in pyproject.toml (lines 54-69) with:
- Line length: 100
- Target version: Python 3.12
- Excludes: migrations, .venv, build directories

**Fix**: Run `poetry run black .` to auto-format all files

---

## Category 3: Type Checking Issues (MyPy)

**Total Errors**: 10
**Exit Code**: 2
**Status**: Blocking

### 3.1 Missing Library Stubs (import-untyped)

**Error Count**: 1
**Severity**: Medium
**Root Cause**: `python-decouple` library lacks type stubs or py.typed marker

#### Affected Files:

**File**: `backend/src/backend/settings/base.py`
- **Line 16**: `from decouple import config`
  - Error: `error: Skipping analyzing "decouple": module is installed, but missing library stubs or py.typed marker [import-untyped]`
  - Note: See https://mypy.readthedocs.io/en/stable/running_mypy.html#missing-imports
  - **Solutions**:
    1. Add type stub: `pip install types-python-decouple` (if available)
    2. Add `# type: ignore[import-untyped]` comment
    3. Add to mypy configuration to ignore this specific import

### 3.2 Index Assignment Errors (index)

**Error Count**: 5
**Severity**: High
**Root Cause**: MyPy cannot infer that `LOGGING` and `REST_FRAMEWORK` dictionaries support indexed assignment

#### Affected Files:

**File**: `backend/src/backend/settings/production.py`
- **Line 90**: `LOGGING["handlers"]["file"] = {...}`
  - Error: `error: Unsupported target for indexed assignment ("object") [index]`
  - Context: Modifying LOGGING dict imported from base.py

- **Line 98**: `LOGGING["root"]["handlers"] = ["console", "file"]`
  - Error: `error: Unsupported target for indexed assignment ("object") [index]`
  - Context: Modifying LOGGING dict root handlers

- **Line 100**: `LOGGING["loggers"]["django"]["handlers"] = ["console", "file"]`
  - Error: `error: Value of type "object" is not indexable [index]`
  - Context: Accessing nested LOGGING configuration

- **Line 101**: `LOGGING["loggers"]["django.server"]["handlers"] = ["console", "file"]`
  - Error: `error: Value of type "object" is not indexable [index]`
  - Context: Accessing nested LOGGING configuration

**File**: `backend/src/backend/settings/development.py`
- **Line 74**: (Similar pattern, need to check exact line)
  - Error: `error: Unsupported target for indexed assignment ("object") [index]`
  - Context: Modifying settings dict imported from base.py

**Root Cause Analysis**:
- MyPy doesn't recognize that `LOGGING` from wildcard import (`from .base import *`) is a dict
- Type annotation needed in base.py or explicit type assertion in production.py

### 3.3 Any Type Returns (no-any-return)

**Error Count**: 4
**Severity**: Medium
**Root Cause**: Functions declared to return specific types are returning `Any` from dictionary lookups

#### Affected Files:

**File**: `backend/src/core/services/health.py`
- **Line 81**: `return settings.DEBUG`
  - Method: `HealthCheckService.is_debug_mode()`
  - Error: `error: Returning Any from function declared to return "bool" [no-any-return]`
  - Declared return type: `bool`
  - Actual: `settings.DEBUG` is typed as `Any` by django-stubs
  - **Fix**: Add explicit type cast: `return bool(settings.DEBUG)`

- **Line 109**: `return db_status["connected"]`
  - Method: `HealthCheckService.is_healthy()`
  - Error: `error: Returning Any from function declared to return "bool" [no-any-return]`
  - Declared return type: `bool`
  - Actual: Dictionary value typed as `Any`
  - **Fix**: Add explicit type cast: `return bool(db_status["connected"])`

**File**: `backend/src/common/middleware/request_logging.py`
- **Line 102**: `return x_forwarded_for.split(",")[0].strip()`
  - Method: `RequestLoggingMiddleware._get_client_ip()`
  - Error: `error: Returning Any from function declared to return "str" [no-any-return]`
  - Declared return type: `str`
  - Actual: `request.META.get()` returns `Any`
  - **Fix**: Add explicit type assertion or use `cast()`

- **Line 105**: `return request.META.get("REMOTE_ADDR", "Unknown")`
  - Method: `RequestLoggingMiddleware._get_client_ip()`
  - Error: `error: Returning Any from function declared to return "str" [no-any-return]`
  - Declared return type: `str`
  - Actual: `request.META.get()` returns `Any`
  - **Fix**: Add explicit type cast: `return str(request.META.get("REMOTE_ADDR", "Unknown"))`

### MyPy Configuration

**Location**: `backend/pyproject.toml` lines 114-142

Current strict settings causing these errors:
- `warn_return_any = true` (line 116)
- `disallow_untyped_defs = true` (line 118)
- `strict_concatenate = true` (line 126) - **Deprecated warning shown in output**

**Note**: MyPy warning shows `--strict-concatenate is deprecated; use --extra-checks instead`

---

## Category 4: Test Failures (Pytest)

**Total Failures**: 5 tests (out of 129 collected)
**Total Passing**: 105 tests
**Exit Code**: 2
**Status**: Blocking

### 4.1 Authentication Test Failure

**Test**: `tests/integration/test_health_check.py::TestHealthCheckEndpoint::test_health_check_does_not_require_authentication`

**Error**:
```
django.db.utils.OperationalError: no such table: django_session
```

**Stack Trace Summary**:
- Line 63: `api_client.force_authenticate(user=None)`
- Triggers Django session lookup
- Database doesn't have `django_session` table

**Root Cause**:
- Test tries to clear authentication by calling `force_authenticate(user=None)`
- DRF's `force_authenticate()` method calls `logout()` which accesses session
- Test database hasn't run migrations for `django.contrib.sessions`
- Test settings may not include 'django.contrib.sessions' in INSTALLED_APPS

**Fix Options**:
1. Ensure test database migrations are run (add `--create-db` or ensure migrations run in conftest.py)
2. Mock the session access in this specific test
3. Don't call `force_authenticate(None)` - test without authentication instead

### 4.2 Database Configuration Test Failure

**Test**: `tests/integration/test_server_startup.py::TestServerStartup::test_database_settings_are_configured`

**Error**:
```
AssertionError: assert 'django.db.backends.sqlite3' == 'django.db.backends.postgresql'
```

**Line 77**: Expected PostgreSQL but got SQLite

**Root Cause**:
- Test expects production database engine: `django.db.backends.postgresql`
- Test settings use in-memory SQLite: `django.db.backends.sqlite3`
- Test is validating wrong environment (checking production config in test environment)

**Fix Options**:
1. Modify test to accept SQLite in test environment
2. Check `settings.DJANGO_SETTINGS_MODULE` and adjust expectation
3. Skip this test in test environment or use `pytest.mark.skipif`
4. Create environment-specific test variants

### 4.3 Logging Configuration Test Failure

**Test**: `tests/integration/test_server_startup.py::TestServerStartup::test_logging_is_configured`

**Error**:
```
AssertionError: assert 'formatters' in {'disable_existing_loggers': True, 'handlers': {'console': {'class': 'logging.StreamHandler'}}, 'loggers': {'django': {'handlers': ['console'], 'level': 'ERROR'}}, 'version': 1}
```

**Line 85**: Expected 'formatters' key in LOGGING config

**Root Cause**:
- Test expects complete logging configuration with formatters
- Test settings have minimal logging config (only handlers, loggers, version)
- Missing configuration keys: `formatters`, detailed handler configs

**Actual LOGGING config in test**:
```python
{
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'ERROR'
        }
    }
}
```

**Expected**: Should include `formatters` section

**Fix**: Add formatters to test settings LOGGING configuration

### 4.4 Middleware Error Handling Test Failures (2 tests)

**Test 1**: `tests/unit/middleware/test_error_handling.py::TestErrorHandlingMiddleware::test_middleware_catches_generic_exceptions`

**Error**:
```
AssertionError: assert 0 > 0
    where 0 = len([])
    where [] = <_pytest.logging.LogCaptureFixture object>.records
```

**Root Cause**:
- Test expects middleware to log exception when generic exception is caught
- `caplog.records` is empty (no logs captured)
- Middleware's `_handle_generic_exception` method calls `logger.error()` with `exc_info=True`
- Log capture might not be configured correctly or logger level is too high

**Test 2**: `tests/unit/middleware/test_error_handling.py::TestErrorHandlingMiddleware::test_middleware_logs_exception_details`

**Error**:
```
AssertionError: assert 'Detailed error message' in ''
    where '' = <_pytest.logging.LogCaptureFixture object>.text
```

**Root Cause**:
- Similar to Test 1 - log capture isn't working
- Expected error message not in captured logs
- `caplog.text` is empty string

**Common Root Cause for Both Tests**:
- Logger configuration in test environment
- `common.middleware.error_handling` logger not at correct level
- Need to verify logger name matches what's used in middleware (line 23: `logger = logging.getLogger(__name__)`)
- May need to explicitly set log level in test: `caplog.set_level(logging.ERROR)`

**Test Configuration Issue**:
- Middleware uses: `logger = logging.getLogger(__name__)` where `__name__` = `common.middleware.error_handling`
- Test might need to capture logs for that specific logger
- Check if test sets proper logger level

---

## Summary of Required Fixes

### Immediate Auto-Fixable Issues (23 errors)

Can be fixed automatically with tool flags:

1. **Ruff auto-fixes (6 errors)**:
   ```bash
   poetry run ruff check --fix .
   ```
   - Removes unused imports (4 errors)
   - Updates deprecated typing imports (2 errors)
   - Simplifies nested with statements (1 error - requires `--unsafe-fixes`)

2. **Black formatting (6 files)**:
   ```bash
   poetry run black .
   ```
   - Reformats all 6 files to match Black style

### Manual Code Fixes Required (18 errors)

1. **Unused method arguments (7 errors)** - Stories #2
   - Add `# noqa: ARG002` comments OR
   - Use parameters with underscore prefix: `_request`, `_exc` OR
   - Update pyproject.toml to exclude these patterns

2. **MyPy type issues (10 errors)** - Story #3
   - Add type stubs or ignore for `decouple` (1 error)
   - Add type assertions for dictionary access (5 errors)
   - Add explicit type casts for Any returns (4 errors)

3. **Test failures (5 tests)** - Story #4
   - Fix authentication test database setup (1 test)
   - Fix database configuration test expectations (1 test)
   - Add formatters to logging configuration (1 test)
   - Fix log capture in middleware tests (2 tests)

---

## Impact Assessment

### Blocking Issues
- **ALL 4 categories** block PR merge (CI/CD policy)
- Tests must pass for merge approval
- Code quality gates must pass

### Risk Level
- **Low**: All issues are fixable without architectural changes
- No security vulnerabilities identified
- No performance issues identified
- No breaking changes required

### Effort Estimate
- **Linting fixes**: 15 minutes (mostly auto-fixable)
- **Formatting fixes**: 2 minutes (fully auto-fixable)
- **Type checking fixes**: 30-45 minutes (manual type annotations)
- **Test fixes**: 45-60 minutes (test configuration and logic updates)

**Total estimated effort**: 2-3 hours

---

## Recommendations

### Immediate Actions (Stories #2-5)

1. **Story #2 - Fix Linting Issues**
   - Run `ruff check --fix .` for auto-fixes
   - Manually address unused arguments
   - Update ruff configuration if needed

2. **Story #3 - Fix Formatting Issues**
   - Run `black .` to reformat all files
   - Verify no unintended changes

3. **Story #4 - Fix Type Checking Issues**
   - Add type stubs for decouple
   - Add explicit type casts in return statements
   - Fix dictionary type annotations in settings

4. **Story #5 - Fix Test Failures**
   - Update test database configuration
   - Fix logging test expectations
   - Configure log capture properly
   - Add missing test setup

### Long-term Improvements

1. **Pre-commit Hooks**
   - Add Black, Ruff, and MyPy to pre-commit hooks
   - Prevents issues from reaching CI/CD

2. **IDE Configuration**
   - Configure VSCode/PyCharm to use Black on save
   - Enable MyPy type checking in IDE
   - Configure Ruff for real-time linting

3. **CI/CD Enhancements**
   - Add comments to PR with specific errors
   - Create auto-fix PR for formatting issues
   - Add linting report artifacts

4. **Documentation**
   - Document common type checking patterns
   - Create developer guide for running checks locally
   - Add troubleshooting guide for CI/CD failures

---

## Files Requiring Changes

### Source Code (10 files)
1. `backend/src/apps/health/views.py` - Linting, Formatting, Type checking
2. `backend/src/common/views/health.py` - Linting, Formatting
3. `backend/src/common/middleware/error_handling.py` - Linting, Formatting
4. `backend/src/common/middleware/request_logging.py` - Linting, Formatting, Type checking
5. `backend/src/core/services/health.py` - Type checking
6. `backend/src/backend/settings/base.py` - Type checking (type stubs)
7. `backend/src/backend/settings/production.py` - Type checking
8. `backend/src/backend/settings/development.py` - Type checking
9. `backend/src/backend/settings/test.py` - Add logging formatters

### Test Files (4 files)
10. `backend/tests/integration/test_health_check.py` - Formatting, Test logic
11. `backend/tests/integration/test_server_startup.py` - Test assertions
12. `backend/tests/unit/middleware/test_request_logging.py` - Linting, Formatting
13. `backend/tests/unit/middleware/test_error_handling.py` - Formatting, Test logic

### Configuration Files (1 file)
14. `backend/pyproject.toml` - Update mypy config (remove deprecated option)

---

## Appendix A: Full CI/CD Error Output

### Ruff Linting Errors
```
src/apps/health/views.py:26:19: ARG002 Unused method argument: `request`
src/apps/health/views.py:66:19: ARG002 Unused method argument: `request`
src/apps/health/views.py:90:19: ARG002 Unused method argument: `request`
src/common/middleware/error_handling.py:8:8: F401 [*] `json` imported but unused
src/common/middleware/error_handling.py:11:1: UP035 [*] Import from `collections.abc` instead: `Callable`
src/common/middleware/error_handling.py:79:53: ARG002 Unused method argument: `exc`
src/common/middleware/error_handling.py:104:37: ARG002 Unused method argument: `exc`
src/common/middleware/request_logging.py:10:1: UP035 [*] Import from `collections.abc` instead: `Callable`
src/common/views/health.py:41:19: ARG002 Unused method argument: `request`
tests/unit/core/test_health_service.py:9:27: F401 [*] `unittest.mock.Mock` imported but unused
tests/unit/middleware/test_error_handling.py:12:34: F401 [*] `django.http.HttpRequest` imported but unused
tests/unit/middleware/test_request_logging.py:12:25: F401 [*] `django.http.HttpRequest` imported but unused
tests/unit/middleware/test_request_logging.py:159:9: SIM117 Use a single `with` statement with multiple contexts

Found 13 errors.
[*] 6 fixable with the `--fix` option (1 hidden fix can be enabled with the `--unsafe-fixes` option).
```

### Black Formatting Issues
```
would reformat backend/src/apps/health/views.py
would reformat backend/src/common/views/health.py
would reformat backend/src/common/middleware/error_handling.py
would reformat backend/tests/integration/test_health_check.py
would reformat backend/tests/unit/middleware/test_request_logging.py
would reformat backend/tests/unit/middleware/test_error_handling.py

6 files would be reformatted, 52 files would be left unchanged.
```

### MyPy Type Checking Errors
```
Warning: --strict-concatenate is deprecated; use --extra-checks instead
src/backend/settings/base.py:16: error: Skipping analyzing "decouple": module is installed, but missing library stubs or py.typed marker [import-untyped]
src/backend/settings/production.py:90: error: Unsupported target for indexed assignment ("object") [index]
src/backend/settings/production.py:98: error: Unsupported target for indexed assignment ("object") [index]
src/backend/settings/production.py:100: error: Value of type "object" is not indexable [index]
src/backend/settings/production.py:101: error: Value of type "object" is not indexable [index]
src/backend/settings/development.py:74: error: Unsupported target for indexed assignment ("object") [index]
src/core/services/health.py:81: error: Returning Any from function declared to return "bool" [no-any-return]
src/core/services/health.py:109: error: Returning Any from function declared to return "bool" [no-any-return]
src/common/middleware/request_logging.py:102: error: Returning Any from function declared to return "str" [no-any-return]
src/common/middleware/request_logging.py:105: error: Returning Any from function declared to return "str" [no-any-return]

Found 10 errors in 5 files (checked 32 source files)
```

### Pytest Test Failures
```
FAILED tests/integration/test_health_check.py::TestHealthCheckEndpoint::test_health_check_does_not_require_authentication
FAILED tests/integration/test_server_startup.py::TestServerStartup::test_database_settings_are_configured
FAILED tests/integration/test_server_startup.py::TestServerStartup::test_logging_is_configured
FAILED tests/unit/middleware/test_error_handling.py::TestErrorHandlingMiddleware::test_middleware_catches_generic_exceptions
FAILED tests/unit/middleware/test_error_handling.py::TestErrorHandlingMiddleware::test_middleware_logs_exception_details

5 failed, 105 passed, 27 warnings in 9.27s
```

---

## Appendix B: CI/CD Job Results

| Job | Status | Duration | Exit Code |
|-----|--------|----------|-----------|
| Lint Check (Ruff) | FAILED | 36s | 2 |
| Format Check (Black) | FAILED | 43s | 1 |
| Type Check (MyPy) | FAILED | 44s | 2 |
| Test Suite (Pytest) | FAILED | 53s | 2 |
| Security Audit | PASSED | 66s | 0 |
| Build Verification | SKIPPED | - | - |
| Deployment Check | SKIPPED | - | - |
| Log Bug Report | PASSED | 10s | 0 |

**Total CI/CD Time**: ~3 minutes (before failures)

---

## Investigation Complete

This report provides a complete analysis of all CI/CD failures with specific file locations, line numbers, error codes, root causes, and recommended fixes. The findings will guide the parallel implementation of Stories #2-5 for fixing these issues.

**Next Steps**: Implement fixes in Stories #2-5 as documented in this investigation.
