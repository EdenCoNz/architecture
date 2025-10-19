# Testing Quick Reference

Quick reference guide for common testing tasks and commands.

## Common Commands

```bash
# Run all tests
make test

# Watch mode (TDD)
make test-watch

# Fast tests (no coverage)
make test-fast

# Only unit tests
make test-unit

# Only integration tests
make test-integration

# Parallel execution
make test-parallel

# Smoke tests
make test-smoke

# View coverage
make coverage
```

## Writing Tests

### Basic Unit Test

```python
import pytest

@pytest.mark.unit
class TestMyService:
    def test_basic_functionality(self):
        """Test description."""
        # Arrange
        service = MyService()

        # Act
        result = service.do_something()

        # Assert
        assert result == expected_value
```

### Integration Test with Database

```python
import pytest
from django.urls import reverse
from rest_framework import status

@pytest.mark.integration
class TestMyAPI:
    def test_endpoint(self, api_client, db):
        """Test API endpoint."""
        url = reverse("my-endpoint")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["key"] == "value"
```

### Using Fixtures

```python
def test_with_user(user, db):
    """Test with user fixture."""
    assert user.username == "testuser"

def test_with_authenticated_client(authenticated_client, db):
    """Test with authenticated client."""
    response = authenticated_client.get("/api/protected/")
    assert response.status_code == 200
```

### Using Factories

```python
from tests.fixtures.factories import UserFactory

def test_with_factory(db):
    # Create single user
    user = UserFactory()

    # Create with custom values
    user = UserFactory(username="custom")

    # Create multiple
    users = UserFactory.create_batch(5)
```

### Mocking

```python
from unittest.mock import patch

@patch("module.function")
def test_with_mock(mock_function):
    mock_function.return_value = "mocked"
    result = my_function()
    assert result == "mocked"
```

## Running Specific Tests

```bash
# Specific file
pytest tests/test_file.py

# Specific class
pytest tests/test_file.py::TestClass

# Specific method
pytest tests/test_file.py::TestClass::test_method

# Pattern matching
pytest -k "health"

# By marker
pytest -m unit
pytest -m "unit and not slow"
```

## Debugging Tests

```bash
# Verbose output
pytest -vv

# Show local variables
pytest --showlocals

# Stop on first failure
pytest -x

# Drop into debugger
pytest --pdb

# Show print statements
pytest -s

# Last failed
pytest --lf
```

## Coverage

```bash
# With coverage (default)
make test

# HTML report
pytest --cov-report=html

# Terminal report
pytest --cov-report=term

# Open in browser
make coverage
```

## TDD Workflow

1. Write failing test (Red)
2. Run: `make test-watch`
3. Implement minimal code (Green)
4. Refactor (Keep tests green)
5. Repeat

## Common Markers

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.e2e` - End-to-end tests
- `@pytest.mark.slow` - Slow tests
- `@pytest.mark.smoke` - Critical tests
- `@pytest.mark.security` - Security tests

## Available Fixtures

### Database
- `db` - Database access
- `transactional_db` - Non-transactional database

### Users
- `user` - Regular user
- `admin_user` - Admin user
- `staff_user` - Staff user
- `sample_users` - Multiple users

### API Clients
- `api_client` - Unauthenticated
- `authenticated_client` - Regular user
- `admin_client` - Admin user
- `staff_client` - Staff user

### Factories
- `user_factory` - UserFactory
- `admin_factory` - AdminUserFactory

## Test Organization

```
tests/
├── conftest.py          # Shared fixtures
├── fixtures/            # Factories and test data
├── unit/                # Unit tests (fast)
├── integration/         # Integration tests
└── e2e/                 # End-to-end tests
```

## Best Practices

1. Use descriptive test names
2. One assertion per test (when possible)
3. Use fixtures for setup
4. Mark tests appropriately
5. Keep unit tests fast (<100ms)
6. Mock external dependencies
7. Test edge cases and errors
8. Follow AAA pattern (Arrange-Act-Assert)

## Troubleshooting

```bash
# Import errors
PYTHONPATH=src pytest

# Clear coverage
rm -rf .coverage htmlcov

# Clear pytest cache
rm -rf .pytest_cache

# Clear testmon data
rm -rf .testmondata

# Reset test database
PYTHONPATH=src python manage.py migrate --settings=backend.settings.test
```

## CI/CD

```bash
# CI-friendly command
PYTHONPATH=src pytest \
  --verbose \
  --cov=src \
  --cov-report=xml \
  --junit-xml=test-results.xml
```

## More Information

See [docs/TESTING.md](TESTING.md) for comprehensive testing documentation.
