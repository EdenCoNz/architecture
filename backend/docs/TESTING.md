# Testing Guide

Comprehensive guide for testing the backend application including unit tests, integration tests, and best practices for Test-Driven Development (TDD).

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Writing Tests](#writing-tests)
- [Test-Driven Development](#test-driven-development)
- [Coverage Reports](#coverage-reports)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Overview

The backend uses **pytest** as the testing framework with the following features:

- **pytest-django**: Django integration for pytest
- **pytest-cov**: Code coverage reporting
- **pytest-watch**: Continuous test runner for TDD workflow
- **pytest-xdist**: Parallel test execution
- **pytest-sugar**: Improved test output
- **pytest-mock**: Enhanced mocking capabilities
- **factory_boy**: Test data factories
- **freezegun**: Time mocking for tests
- **responses**: HTTP response mocking

## Quick Start

### Run All Tests

```bash
make test
```

### Watch Mode (TDD Workflow)

Run tests continuously, re-running automatically when files change:

```bash
make test-watch
```

### Fast Feedback (No Coverage)

```bash
make test-fast
```

### Run Specific Test Types

```bash
# Only unit tests
make test-unit

# Only integration tests
make test-integration

# Only smoke tests (critical functionality)
make test-smoke
```

### Parallel Testing

Run tests in parallel for faster execution:

```bash
make test-parallel
```

## Test Structure

Tests are organized in the `tests/` directory, mirroring the source structure:

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── fixtures/                # Test data and factories
│   ├── __init__.py
│   └── factories.py         # Factory Boy factories
├── unit/                    # Fast, isolated unit tests
│   ├── apps/                # App-specific unit tests
│   ├── common/              # Common utilities tests
│   └── core/                # Core services tests
├── integration/             # Component interaction tests
│   ├── api/                 # API endpoint tests
│   └── database/            # Database integration tests
├── e2e/                     # End-to-end workflow tests
└── test_*.py                # Top-level configuration tests
```

### Test Categories

Tests are marked with pytest markers to categorize them:

- `@pytest.mark.unit` - Fast, isolated unit tests
- `@pytest.mark.integration` - Integration tests with database/API
- `@pytest.mark.e2e` - End-to-end workflow tests
- `@pytest.mark.slow` - Tests that take >1 second
- `@pytest.mark.smoke` - Critical functionality tests
- `@pytest.mark.regression` - Tests for bug fixes
- `@pytest.mark.security` - Security-related tests
- `@pytest.mark.performance` - Performance benchmarks

## Running Tests

### Basic Commands

```bash
# Run all tests with coverage
make test

# Run specific test file
PYTHONPATH=src poetry run pytest tests/unit/core/test_health_service.py

# Run specific test class
PYTHONPATH=src poetry run pytest tests/unit/core/test_health_service.py::TestHealthCheckService

# Run specific test method
PYTHONPATH=src poetry run pytest tests/unit/core/test_health_service.py::TestHealthCheckService::test_service_initialization

# Run tests matching a pattern
PYTHONPATH=src poetry run pytest -k "health"
```

### Filter by Markers

```bash
# Run only unit tests
PYTHONPATH=src poetry run pytest -m unit

# Run only integration tests
PYTHONPATH=src poetry run pytest -m integration

# Run smoke tests
PYTHONPATH=src poetry run pytest -m smoke

# Run everything except slow tests
PYTHONPATH=src poetry run pytest -m "not slow"

# Combine markers
PYTHONPATH=src poetry run pytest -m "unit and not slow"
```

### Advanced Options

```bash
# Stop on first failure
PYTHONPATH=src poetry run pytest -x

# Show local variables on failure
PYTHONPATH=src poetry run pytest --showlocals

# Verbose output
PYTHONPATH=src poetry run pytest -v

# Very verbose output
PYTHONPATH=src poetry run pytest -vv

# Show print statements
PYTHONPATH=src poetry run pytest -s

# Run last failed tests
PYTHONPATH=src poetry run pytest --lf

# Run failed tests first, then all
PYTHONPATH=src poetry run pytest --ff
```

## Writing Tests

### Unit Tests

Unit tests should be fast, isolated, and test a single component:

```python
"""Example unit test."""
import pytest
from core.services.health import HealthCheckService

@pytest.mark.unit
class TestHealthCheckService:
    """Test suite for HealthCheckService."""

    def test_service_initialization(self) -> None:
        """Test that service can be instantiated."""
        service = HealthCheckService()
        assert service is not None

    def test_get_application_version(self) -> None:
        """Test that application version is retrieved correctly."""
        service = HealthCheckService()
        version = service.get_application_version()

        assert version is not None
        assert isinstance(version, str)
```

### Integration Tests

Integration tests verify components work together:

```python
"""Example integration test."""
import pytest
from django.urls import reverse
from rest_framework import status

@pytest.mark.integration
class TestHealthCheckAPI:
    """Integration tests for health check endpoint."""

    def test_health_endpoint_returns_200(self, api_client, db) -> None:
        """Test that health endpoint returns 200 OK."""
        url = reverse("health-check")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
```

### Using Fixtures

The project provides several useful fixtures:

```python
def test_with_user(user, db):
    """Test using the user fixture."""
    assert user.username == "testuser"

def test_with_api_client(api_client, db):
    """Test using unauthenticated API client."""
    response = api_client.get("/health/")
    assert response.status_code == 200

def test_with_authenticated_client(authenticated_client, db):
    """Test using authenticated API client."""
    response = authenticated_client.get("/api/protected/")
    assert response.status_code == 200

def test_with_admin(admin_user, admin_client, db):
    """Test using admin user and client."""
    assert admin_user.is_superuser
    response = admin_client.get("/admin/")
    assert response.status_code == 200
```

### Using Factories

Factories make it easy to create test data:

```python
from tests.fixtures.factories import UserFactory

def test_with_factory(db):
    """Test using factory to create test data."""
    # Create single user
    user = UserFactory()
    assert user.username.startswith("user")

    # Create user with custom values
    custom_user = UserFactory(username="custom", email="custom@example.com")
    assert custom_user.username == "custom"

    # Create multiple users
    users = UserFactory.create_batch(10)
    assert len(users) == 10
```

### Mocking

Use pytest-mock for mocking:

```python
from unittest.mock import patch

@patch("core.services.health.connection.cursor")
def test_with_mock(mock_cursor):
    """Test using mock."""
    mock_cursor.side_effect = DatabaseError("Connection refused")

    service = HealthCheckService()
    result = service.check_database()

    assert result["connected"] is False
```

## Test-Driven Development

### TDD Workflow (Red-Green-Refactor)

1. **Red**: Write a failing test first

```python
@pytest.mark.unit
def test_user_full_name():
    """Test that user full name is correctly formatted."""
    user = UserFactory(first_name="John", last_name="Doe")
    assert user.get_full_name() == "John Doe"
```

2. **Green**: Implement minimal code to make it pass

```python
class User(AbstractUser):
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
```

3. **Refactor**: Improve the code while keeping tests green

```python
class User(AbstractUser):
    def get_full_name(self) -> str:
        """Return user's full name."""
        return f"{self.first_name} {self.last_name}".strip()
```

### Watch Mode for TDD

The watch mode automatically re-runs tests when files change:

```bash
make test-watch
```

This will:
- Watch for file changes in `src/` and `tests/`
- Re-run only tests affected by changes (using pytest-testmon)
- Provide instant feedback during development

## Coverage Reports

### Generate Coverage Report

```bash
# Run tests with coverage (default)
make test

# View coverage in terminal
PYTHONPATH=src poetry run pytest --cov-report=term

# Generate HTML coverage report
PYTHONPATH=src poetry run pytest --cov-report=html

# Open coverage report in browser
make coverage
```

### Coverage Files

- `htmlcov/index.html` - Interactive HTML coverage report
- `coverage.xml` - XML format for CI/CD integration
- `coverage.json` - JSON format for programmatic access
- `.coverage` - Raw coverage data

### Coverage Thresholds

The project enforces a minimum coverage threshold of **80%**. Tests will fail if coverage drops below this threshold.

To adjust the threshold, edit `pyproject.toml`:

```toml
[tool.coverage.report]
fail_under = 80  # Change this value
```

## Best Practices

### Test Organization

1. **Mirror source structure**: Test files should mirror the source code structure
2. **One test file per module**: `src/core/services/health.py` → `tests/unit/core/test_health_service.py`
3. **Descriptive test names**: Use clear, descriptive test function names
4. **Group related tests**: Use test classes to group related tests
5. **Use markers**: Mark tests with appropriate pytest markers

### Test Content

1. **Arrange-Act-Assert**: Structure tests in three clear sections
   ```python
   def test_example():
       # Arrange: Set up test data
       service = HealthCheckService()

       # Act: Perform the action
       result = service.check_database()

       # Assert: Verify the result
       assert result["connected"] is True
   ```

2. **One assertion per test**: Each test should verify one specific behavior
3. **Use fixtures**: Leverage fixtures for setup and teardown
4. **Avoid test interdependence**: Tests should be independent and run in any order
5. **Test edge cases**: Include tests for error conditions and edge cases

### Performance

1. **Keep unit tests fast**: Unit tests should complete in milliseconds
2. **Use markers for slow tests**: Mark slow tests with `@pytest.mark.slow`
3. **Mock external dependencies**: Mock database, API calls, file I/O in unit tests
4. **Use transactions**: pytest-django automatically wraps tests in transactions
5. **Parallel execution**: Run tests in parallel for faster CI/CD

### Maintainability

1. **DRY principle**: Use fixtures and factories to avoid duplication
2. **Clear test names**: Test names should describe what is being tested
3. **Document complex tests**: Add docstrings to explain complex test scenarios
4. **Avoid magic values**: Use constants or fixtures for test data
5. **Keep tests simple**: Tests should be easier to read than production code

## Troubleshooting

### Common Issues

#### Import Errors

If you get import errors, ensure `PYTHONPATH` is set:

```bash
PYTHONPATH=src poetry run pytest
```

Or use the Makefile commands which set it automatically:

```bash
make test
```

#### Database Issues

If tests fail with database errors:

```bash
# Reset test database
PYTHONPATH=src poetry run python manage.py migrate --run-syncdb --settings=backend.settings.test

# Clear test database
rm -f db.sqlite3
```

#### Coverage Not Working

If coverage reports are empty:

```bash
# Clean coverage data
rm -rf .coverage htmlcov coverage.xml

# Run tests again
make test
```

#### Watch Mode Not Working

If watch mode doesn't detect changes:

```bash
# Clear testmon cache
rm -rf .testmondata

# Run watch mode again
make test-watch
```

### Debug Failing Tests

```bash
# Run with verbose output
PYTHONPATH=src poetry run pytest -vv

# Show local variables on failure
PYTHONPATH=src poetry run pytest --showlocals

# Drop into debugger on failure
PYTHONPATH=src poetry run pytest --pdb

# Show print statements
PYTHONPATH=src poetry run pytest -s
```

### Performance Issues

If tests are running slowly:

```bash
# Run without coverage for faster execution
make test-fast

# Run in parallel
make test-parallel

# Profile slow tests
PYTHONPATH=src poetry run pytest --durations=10
```

## Continuous Integration

The test suite is designed to run in CI/CD pipelines:

```bash
# CI-friendly test command
PYTHONPATH=src poetry run pytest \
  --verbose \
  --cov=src \
  --cov-report=xml \
  --cov-report=term \
  --junit-xml=test-results.xml
```

This generates:
- `coverage.xml` - Coverage report for tools like Codecov
- `test-results.xml` - JUnit XML for CI dashboards

## Additional Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-django documentation](https://pytest-django.readthedocs.io/)
- [factory_boy documentation](https://factoryboy.readthedocs.io/)
- [Django testing documentation](https://docs.djangoproject.com/en/5.1/topics/testing/)
- [REST Framework testing](https://www.django-rest-framework.org/api-guide/testing/)
