# Testing Guide

## Overview

This document provides comprehensive guidance on testing in this Django REST Framework API project. We follow Test-Driven Development (TDD) principles and maintain high code coverage to ensure reliability and prevent regressions.

## Table of Contents

- [Quick Start](#quick-start)
- [Testing Philosophy](#testing-philosophy)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Writing Tests](#writing-tests)
- [Test Utilities](#test-utilities)
- [Test Data Management](#test-data-management)
- [Best Practices](#best-practices)
- [Coverage Requirements](#coverage-requirements)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

### Running All Tests

```bash
# From backend/ directory
pytest

# Or using make
make test
```

### Running Specific Test Types

```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# End-to-end tests only
pytest -m e2e

# Acceptance tests only
pytest -m acceptance
```

### Running with Coverage

```bash
# Generate coverage report
pytest --cov=apps --cov-report=html --cov-report=term

# Or using make
make coverage
```

---

## Testing Philosophy

This project follows **Test-Driven Development (TDD)**:

### The Red-Green-Refactor Cycle

1. **Red**: Write a failing test that defines desired functionality
2. **Green**: Write minimal code to make the test pass
3. **Refactor**: Improve code while keeping tests green

### Why TDD?

- **Better Design**: Writing tests first forces you to think about API design
- **Living Documentation**: Tests serve as executable documentation
- **Confidence**: Refactor with confidence knowing tests will catch regressions
- **Coverage**: Naturally achieve high test coverage
- **Debugging**: Catch bugs early when they're cheapest to fix

### Testing Principles

1. **Tests should be FAST**: Unit tests run in milliseconds, not seconds
2. **Tests should be INDEPENDENT**: Order shouldn't matter
3. **Tests should be REPEATABLE**: Same result every time
4. **Tests should be SELF-VALIDATING**: Pass or fail, no manual checking
5. **Tests should be TIMELY**: Written before or with the production code

---

## Test Structure

### Directory Organization

```
tests/
├── README.md                    # This file
├── conftest.py                  # Pytest configuration and shared fixtures
├── factories.py                 # Factory Boy factories for test data
├── utils.py                     # Test utilities and helpers
├── test_example_patterns.py     # Example tests demonstrating patterns
│
├── unit/                        # Unit tests (isolated component tests)
│   ├── __init__.py
│   ├── test_user_model.py
│   ├── test_auth_serializers.py
│   └── test_*.py
│
├── integration/                 # Integration tests (component interaction tests)
│   ├── __init__.py
│   ├── test_auth_endpoints.py
│   ├── test_health_endpoints_integration.py
│   └── test_*.py
│
├── e2e/                         # End-to-end tests (full workflow tests)
│   ├── __init__.py
│   └── test_*.py
│
└── acceptance/                  # Acceptance tests (user story validation)
    ├── __init__.py
    ├── test_story_4_acceptance.py
    ├── test_story_5_acceptance.py
    └── test_*.py
```

### Test Types

#### Unit Tests (`tests/unit/`)

- Test individual functions/methods in isolation
- Mock external dependencies
- Fast execution (< 1 second total)
- No network or database calls when possible

```python
@pytest.mark.unit
def test_email_normalization():
    """Test that emails are normalized correctly."""
    user = UserFactory.build()  # build() doesn't hit database
    assert '@' in user.email
```

#### Integration Tests (`tests/integration/`)

- Test component interactions
- Use real database (test database)
- Test API endpoints end-to-end
- Verify database state changes

```python
@pytest.mark.integration
@pytest.mark.django_db
def test_user_registration_endpoint(api_client):
    """Test user registration creates user in database."""
    response = api_client.post('/api/v1/auth/register/', data)
    assert response.status_code == 201
    assert User.objects.filter(email=data['email']).exists()
```

#### End-to-End Tests (`tests/e2e/`)

- Test complete user workflows
- Multiple API calls in sequence
- Simulate real user behavior
- Test critical paths

```python
@pytest.mark.e2e
@pytest.mark.django_db
def test_complete_authentication_flow(api_client):
    """Test complete auth flow: register -> login -> access protected resource."""
    # Register, login, access profile, logout
    ...
```

#### Acceptance Tests (`tests/acceptance/`)

- Validate user story acceptance criteria
- One test file per user story
- Map directly to requirements
- Business-readable test names

```python
@pytest.mark.acceptance
@pytest.mark.django_db
def test_story_6_user_can_authenticate_with_valid_credentials():
    """
    Story #6 Acceptance Criteria:
    When I provide valid credentials, I should be able to authenticate successfully.
    """
    ...
```

---

## Running Tests

### Basic Commands

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_user_model.py

# Run specific test class
pytest tests/unit/test_user_model.py::TestUserModel

# Run specific test method
pytest tests/unit/test_user_model.py::TestUserModel::test_create_user

# Run tests matching pattern
pytest -k "authentication"
```

### Using Test Markers

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only API tests
pytest -m api

# Run only slow tests
pytest -m slow

# Run everything EXCEPT slow tests
pytest -m "not slow"

# Combine markers (unit OR integration)
pytest -m "unit or integration"
```

### Parallel Execution

```bash
# Run tests in parallel (faster)
pytest -n auto

# Run on 4 processes
pytest -n 4
```

### Coverage Reports

```bash
# Terminal report with missing lines
pytest --cov=apps --cov-report=term-missing

# HTML report (view in browser)
pytest --cov=apps --cov-report=html
# Then open htmlcov/index.html

# Both terminal and HTML
pytest --cov=apps --cov-report=term --cov-report=html

# Coverage for specific module
pytest --cov=apps.users --cov-report=term
```

### Debugging Failed Tests

```bash
# Stop at first failure
pytest -x

# Stop after N failures
pytest --maxfail=3

# Show local variables on failure
pytest -l

# Enter debugger on failure
pytest --pdb

# More detailed output
pytest -vv

# Show print statements
pytest -s
```

---

## Writing Tests

### Test File Naming

- Unit tests: `tests/unit/test_<module>.py`
- Integration tests: `tests/integration/test_<feature>_integration.py`
- E2E tests: `tests/e2e/test_<workflow>_e2e.py`
- Acceptance tests: `tests/acceptance/test_story_<number>_<title>.py`

### Test Method Naming

Use descriptive names that explain what is being tested:

```python
# Good
def test_user_creation_with_valid_email_succeeds():
    ...

def test_login_with_invalid_password_returns_400():
    ...

# Bad
def test_user():
    ...

def test_1():
    ...
```

### Test Structure (Arrange-Act-Assert)

```python
def test_example():
    # Arrange: Set up test data and conditions
    user = UserFactory(email='test@example.com')
    client = APIClient()

    # Act: Perform the action being tested
    response = client.post('/api/v1/auth/login/', {
        'email': user.email,
        'password': 'testpass123'
    })

    # Assert: Verify the results
    assert response.status_code == 200
    assert 'access' in response.data
```

### Using Markers

```python
import pytest

@pytest.mark.unit
def test_unit_example():
    ...

@pytest.mark.integration
@pytest.mark.django_db
def test_integration_example():
    ...

@pytest.mark.slow
def test_slow_operation():
    ...

@pytest.mark.skip(reason="Feature not implemented yet")
def test_future_feature():
    ...
```

---

## Test Utilities

The project provides several helper modules to make testing easier and more consistent.

### APITestHelper

Helper for testing API endpoints:

```python
from tests.utils import APITestHelper

def test_endpoint(api_client):
    helper = APITestHelper(api_client)

    # Make requests
    response = helper.get('/api/v1/users/')
    response = helper.post('/api/v1/users/', data={'email': 'test@example.com'})

    # Authenticate
    access_token, refresh_token = helper.authenticate(user)

    # Assertions
    helper.assert_success(response)
    helper.assert_has_keys(response.data, ['id', 'email'])
    helper.assert_missing_keys(response.data, ['password'])
```

### AuthenticationTestHelper

Helper for testing authentication flows:

```python
from tests.utils import AuthenticationTestHelper

def test_auth_flow(api_client):
    auth_helper = AuthenticationTestHelper(api_client)

    # Login
    tokens = auth_helper.login('user@example.com', 'password')

    # Refresh token
    new_tokens = auth_helper.refresh_token(tokens['refresh'])

    # Logout
    auth_helper.logout(tokens['refresh'])
```

### DatabaseTestHelper

Helper for database assertions:

```python
from tests.utils import DatabaseTestHelper
from django.contrib.auth import get_user_model

User = get_user_model()

def test_database_operations():
    # Assert object exists
    DatabaseTestHelper.assert_object_exists(User, email='test@example.com')

    # Assert object doesn't exist
    DatabaseTestHelper.assert_object_not_exists(User, email='deleted@example.com')

    # Assert count
    DatabaseTestHelper.assert_count(User, 5)
    DatabaseTestHelper.assert_count(User, 2, is_active=True)

    # Get or fail
    user = DatabaseTestHelper.get_or_fail(User, email='test@example.com')
```

### AssertionHelper

Helper for common assertions:

```python
from tests.utils import AssertionHelper

def test_assertions():
    # Assert valid UUID
    AssertionHelper.assert_valid_uuid(user.id)

    # Assert valid timestamp
    AssertionHelper.assert_valid_timestamp(response.data['created_at'])

    # Assert dictionary subset
    expected = {'email': 'test@example.com', 'is_active': True}
    AssertionHelper.assert_dict_subset(expected, response.data)
```

---

## Test Data Management

### Using Factories

Factories provide consistent, reusable test data creation:

```python
from tests.factories import UserFactory, AdminUserFactory

# Create single user
user = UserFactory()

# Create with custom attributes
user = UserFactory(email='custom@example.com', first_name='John')

# Create multiple users
users = UserFactory.create_batch(5)

# Build without saving to database
user = UserFactory.build()

# Create admin user
admin = AdminUserFactory()
```

### Factory Customization

```python
# Override specific attributes
user = UserFactory(
    email='specific@example.com',
    first_name='Jane',
    last_name='Doe',
    is_active=False
)

# Create with custom password
user = UserFactory(password='custompass123')
```

### TestDataBuilder

Helper for complex test scenarios:

```python
from tests.factories import TestDataBuilder

# Create batch of users
users = TestDataBuilder.create_users_batch(10)

# Create complete authentication scenario
scenario = TestDataBuilder.create_authenticated_scenario()
regular_user = scenario['user']
admin_user = scenario['admin']
inactive_user = scenario['inactive_user']

# Create user with known credentials
user, password = TestDataBuilder.create_user_with_credentials(
    email='test@example.com',
    password='testpass123'
)
```

### Fixtures

Reusable setup using pytest fixtures:

```python
import pytest
from tests.factories import UserFactory

@pytest.fixture
def sample_user():
    """Provide a sample user for tests."""
    return UserFactory()

@pytest.fixture
def admin_user():
    """Provide an admin user for tests."""
    return UserFactory(is_staff=True, is_superuser=True)

@pytest.fixture
def multiple_users():
    """Provide multiple users for tests."""
    return UserFactory.create_batch(5)

# Use in tests
def test_with_fixture(sample_user):
    assert sample_user.is_active is True
```

---

## Best Practices

### 1. Write Tests First (TDD)

```python
# Step 1: Write failing test (RED)
def test_user_can_update_profile():
    user = UserFactory()
    client = APIClient()
    helper = APITestHelper(client)
    helper.authenticate(user)

    response = helper.patch('/api/v1/users/me/', {
        'first_name': 'Updated'
    })

    helper.assert_success(response)
    assert response.data['first_name'] == 'Updated'

# Step 2: Implement feature (GREEN)
# ... implement the endpoint ...

# Step 3: Refactor (REFACTOR)
# ... clean up code while tests stay green ...
```

### 2. One Assertion Per Test (When Possible)

```python
# Good - focused test
def test_user_email_is_normalized():
    user = UserFactory(email='Test@EXAMPLE.COM')
    assert user.email == 'Test@example.com'

# Also good - related assertions
def test_user_creation_sets_defaults():
    user = UserFactory()
    assert user.is_active is True
    assert user.is_staff is False
    assert user.is_superuser is False
```

### 3. Test Both Success and Failure Cases

```python
def test_login_with_valid_credentials_succeeds():
    # Test happy path
    ...

def test_login_with_invalid_password_fails():
    # Test error case
    ...

def test_login_with_inactive_user_fails():
    # Test edge case
    ...
```

### 4. Use Descriptive Test Names

```python
# Good
def test_user_cannot_delete_other_users_account():
    ...

def test_expired_token_returns_401_unauthorized():
    ...

# Bad
def test_user():
    ...

def test_delete():
    ...
```

### 5. Keep Tests Independent

```python
# Good - each test is independent
def test_create_user():
    user = UserFactory()
    assert user.email is not None

def test_update_user():
    user = UserFactory()  # Create fresh user
    user.first_name = 'Updated'
    user.save()
    assert user.first_name == 'Updated'

# Bad - tests depend on each other
user = None

def test_create_user():
    global user
    user = UserFactory()

def test_update_user():
    global user
    user.first_name = 'Updated'  # Depends on previous test
```

### 6. Mock External Dependencies

```python
from unittest.mock import patch

@patch('apps.services.external_api.call')
def test_external_api_integration(mock_call):
    # Mock external API call
    mock_call.return_value = {'status': 'success'}

    # Test your code without actually calling external API
    result = my_function_that_calls_external_api()

    assert mock_call.called
    assert result['status'] == 'success'
```

### 7. Use Meaningful Docstrings

```python
def test_user_registration_with_valid_data():
    """
    Test that user registration with valid data creates a user account.

    This test verifies the acceptance criteria:
    "When I provide valid registration data, I should be able to create an account."
    """
    ...
```

### 8. Clean Up After Tests

```python
# Use fixtures for setup and teardown
@pytest.fixture
def temp_file():
    # Setup
    file_path = '/tmp/test_file.txt'
    with open(file_path, 'w') as f:
        f.write('test')

    yield file_path

    # Teardown
    import os
    if os.path.exists(file_path):
        os.remove(file_path)
```

---

## Coverage Requirements

### Target Coverage

- **Overall**: Minimum 80% code coverage
- **Critical paths**: 100% coverage (authentication, authorization, data integrity)
- **New code**: All new code must have tests

### Checking Coverage

```bash
# Generate coverage report
pytest --cov=apps --cov-report=term-missing

# View detailed HTML report
pytest --cov=apps --cov-report=html
open htmlcov/index.html

# Check coverage for specific module
pytest --cov=apps.users --cov-report=term-missing

# Fail if coverage below threshold
pytest --cov=apps --cov-fail-under=80
```

### Coverage Reports

The HTML coverage report shows:
- Overall coverage percentage
- Coverage by module
- Lines covered/missed (highlighted in red)
- Branch coverage

---

## Troubleshooting

### Tests Not Found

**Problem**: `pytest` doesn't find any tests

**Solution**:
```bash
# Ensure you're in the backend/ directory
cd backend/

# Check pytest can find tests
pytest --collect-only

# Verify DJANGO_SETTINGS_MODULE is set
export DJANGO_SETTINGS_MODULE=config.settings.testing
```

### Database Errors

**Problem**: `django.db.utils.OperationalError: no such table`

**Solution**:
```bash
# Tests use separate test database
# Ensure migrations are up to date
python manage.py migrate

# Or use --reuse-db flag
pytest --reuse-db
```

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'apps'`

**Solution**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Install dependencies
pip install -r requirements/dev.txt

# Verify Python path includes project root
export PYTHONPATH=/path/to/backend:$PYTHONPATH
```

### Slow Tests

**Problem**: Tests are running slowly

**Solution**:
```bash
# Run tests in parallel
pytest -n auto

# Identify slow tests
pytest --durations=10

# Reuse database between tests
pytest --reuse-db

# Skip slow tests during development
pytest -m "not slow"
```

### Mock Not Working

**Problem**: Mock not being used in tests

**Solution**:
```python
# Ensure patch path is correct - patch where it's USED, not where it's DEFINED
# Wrong
@patch('some.module.function')

# Right - patch where it's imported
@patch('apps.views.function')  # If imported in views

# Verify mock is called
assert mock.called
print(mock.call_args)  # Debug what was passed
```

---

## Example Test Patterns

See `test_example_patterns.py` for comprehensive examples of:

- Unit tests with factories
- Integration tests with API client
- Mocking external dependencies
- Using test utilities and helpers
- Test data management with factories
- Different assertion patterns
- Fixture usage
- Parameterized tests
- Complex scenario testing
- Edge case and error handling

---

## Additional Resources

### Internal Documentation

- `tests/test_example_patterns.py` - Comprehensive testing examples
- `tests/factories.py` - Factory documentation and usage
- `tests/utils.py` - Test utility documentation
- `tests/conftest.py` - Shared fixtures

### External Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-django documentation](https://pytest-django.readthedocs.io/)
- [Factory Boy documentation](https://factoryboy.readthedocs.io/)
- [Django Testing documentation](https://docs.djangoproject.com/en/stable/topics/testing/)
- [DRF Testing documentation](https://www.django-rest-framework.org/api-guide/testing/)

---

## Questions?

If you have questions about testing:

1. Review `test_example_patterns.py` for patterns
2. Look at existing tests for similar functionality
3. Check this README for guidance
4. Consult the team or create an issue

Remember: **Good tests are the foundation of maintainable code!**
