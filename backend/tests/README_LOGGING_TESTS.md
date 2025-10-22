# Logging and Error Handling Tests

## Overview

This directory contains comprehensive tests for the request logging middleware and exception handling system.

## Test Files

### test_middleware.py
Tests for the custom middleware components that handle request logging and performance monitoring.

**Test Cases:**

1. **Request Logging Tests**
   - `test_middleware_logs_request_with_basic_info`: Verifies that basic request information (method, path, status) is logged
   - `test_middleware_logs_response_time`: Ensures response time is measured and logged
   - `test_middleware_logs_user_info_for_authenticated_user`: Validates user information logging for authenticated requests
   - `test_middleware_logs_query_parameters`: Confirms query parameters are captured
   - `test_middleware_logs_different_http_methods`: Tests logging for various HTTP methods (GET, POST, PUT, PATCH, DELETE)
   - `test_middleware_logs_error_status_codes`: Verifies 4xx errors are logged at WARNING level
   - `test_middleware_logs_server_errors`: Ensures 5xx errors are logged at ERROR level
   - `test_middleware_includes_request_id`: Confirms each request gets a unique ID
   - `test_middleware_sanitizes_sensitive_data`: Validates sensitive data (passwords, tokens) are redacted from logs

2. **Coverage Areas**
   - Request tracking and timing
   - User identification
   - Status code based log levels
   - Sensitive data sanitization
   - Request ID generation
   - Query parameter logging

### test_exception_handler.py
Tests for the custom exception handler that provides consistent error responses and comprehensive error logging.

**Test Cases:**

1. **Exception Response Format Tests**
   - `test_validation_error_returns_consistent_format`: Validates consistent error response structure for validation errors
   - `test_permission_denied_error_logged_and_returned`: Tests permission denied error handling
   - `test_authentication_error_logged_and_returned`: Verifies authentication error handling
   - `test_http_404_error_handled_properly`: Ensures 404 errors are handled correctly
   - `test_generic_api_exception_handled`: Tests generic API exception handling

2. **Environment-Aware Error Handling Tests**
   - `test_unhandled_exception_in_development_includes_details`: Confirms detailed error information in development mode
   - `test_unhandled_exception_in_production_hides_details`: Validates sensitive details are hidden in production
   - `test_exception_logs_include_stack_trace_in_dev`: Ensures stack traces are logged in development

3. **Logging Context Tests**
   - `test_exception_includes_request_context`: Verifies request context is included in exception logs
   - `test_exception_handler_includes_timestamp`: Confirms timestamps are included
   - `test_exception_handler_sanitizes_sensitive_fields`: Tests sensitive field sanitization

4. **Response Consistency Tests**
   - `test_exception_response_structure_consistency`: Validates all exceptions return the same response structure

## Running the Tests

### Run All Logging Tests
```bash
pytest tests/test_middleware.py tests/test_exception_handler.py -v
```

### Run Specific Test File
```bash
# Middleware tests only
pytest tests/test_middleware.py -v

# Exception handler tests only
pytest tests/test_exception_handler.py -v
```

### Run Specific Test Case
```bash
pytest tests/test_middleware.py::RequestLoggingMiddlewareTestCase::test_middleware_logs_request_with_basic_info -v
```

### Run with Coverage
```bash
pytest tests/test_middleware.py tests/test_exception_handler.py --cov=apps.core --cov-report=html --cov-report=term
```

## Test Requirements

The tests require the following to be installed:
- Django
- Django REST Framework
- pytest
- pytest-django

Install with:
```bash
pip install -r requirements/dev.txt
```

## Test Configuration

Tests use the testing settings file: `config/settings/testing.py`

Set the Django settings module before running tests:
```bash
export DJANGO_SETTINGS_MODULE=config.settings.testing
pytest tests/test_middleware.py tests/test_exception_handler.py
```

Or use the `--settings` flag:
```bash
pytest tests/test_middleware.py tests/test_exception_handler.py --settings=config.settings.testing
```

## Mocking Strategy

The tests use mocking to:
- Isolate middleware and exception handler logic
- Prevent actual log files from being written during tests
- Verify logging calls without side effects
- Test different response scenarios

Example:
```python
@patch('apps.core.middleware.logger')
def test_middleware_logs_request(self, mock_logger):
    # Test code here
    self.assertTrue(mock_logger.info.called)
```

## Test Data

Tests use:
- `RequestFactory` to create mock requests
- `MagicMock` for response objects
- Anonymous and authenticated user objects
- Various HTTP status codes (200, 400, 404, 500)

## Assertions

Tests verify:
- Logger method calls (info, warning, error)
- Log message content
- Extra context data
- Response status codes
- Response data structure
- Sensitive data sanitization

## Expected Behavior

### Request Logging Middleware
- All requests logged with timestamp, method, path, status, duration
- User information captured for authenticated requests
- Query parameters logged (sanitized)
- Unique request ID generated
- Response times measured in milliseconds
- Different log levels based on status code:
  - 2xx: INFO
  - 4xx: WARNING
  - 5xx: ERROR

### Exception Handler
- Consistent error response structure
- Request ID included in responses
- Timestamp included
- Environment-aware detail exposure:
  - Development: Full details including stack traces
  - Production: Generic messages without sensitive information
- All exceptions logged with context
- Sensitive data sanitized

## Integration with CI/CD

These tests should be run as part of:
1. Pre-commit hooks
2. Pull request checks
3. Continuous integration pipeline
4. Before deployment

## Troubleshooting

### Tests failing with import errors
Ensure Django is installed and DJANGO_SETTINGS_MODULE is set:
```bash
pip install -r requirements/dev.txt
export DJANGO_SETTINGS_MODULE=config.settings.testing
```

### Mock assertions failing
Check that:
- Logger names match the implementation
- Mock patches are applied to the correct module paths
- Test data matches expected formats

### Coverage issues
Run with verbose output to see which branches aren't covered:
```bash
pytest tests/test_middleware.py --cov=apps.core.middleware --cov-report=term-missing -v
```

## Future Test Additions

Consider adding tests for:
1. Performance logging middleware
2. Health check logging exemption middleware
3. Concurrent request handling
4. Log rotation behavior
5. JSON log format validation
6. Integration tests with real database
7. Load testing for logging performance impact
