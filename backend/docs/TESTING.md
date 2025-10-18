# Testing Guide

Comprehensive guide for testing the FastAPI backend application using pytest, httpx, and best practices from the 2025 testing ecosystem.

## Table of Contents

- [Quick Start](#quick-start)
- [Testing Infrastructure](#testing-infrastructure)
- [Test Organization](#test-organization)
- [Writing Tests](#writing-tests)
- [Running Tests](#running-tests)
- [Coverage Reporting](#coverage-reporting)
- [Testing Patterns](#testing-patterns)
- [Best Practices](#best-practices)
- [CI/CD Integration](#cicd-integration)

## Quick Start

### Running All Tests

```bash
# Run all tests with coverage
pytest

# Run specific test file
pytest tests/test_health.py

# Run specific test function
pytest tests/test_health.py::TestHealthCheckEndpoint::test_health_check_returns_200_when_healthy

# Run tests matching a pattern
pytest -k "health"
```

### Running Tests by Marker

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run database tests
pytest -m database

# Skip slow tests
pytest -m "not slow"
```

### Running with Different Verbosity

```bash
# Verbose output
pytest -v

# Very verbose (show test names and local variables)
pytest -vv

# Quiet mode (minimal output)
pytest -q
```

## Testing Infrastructure

### Test Configuration

Tests are configured in three places:

1. **pytest.ini** - pytest configuration including markers, coverage settings, and test discovery
2. **.env.test** - test environment variables (database URL, secrets, etc.)
3. **app/core/test_config.py** - test-specific settings class

### Test Database

The testing infrastructure supports two database configurations:

#### SQLite In-Memory (Default)

Fast, isolated tests using SQLite in-memory database:

```python
# .env.test
DATABASE_URL=sqlite+aiosqlite:///:memory:
```

**Advantages:**
- Extremely fast (no disk I/O)
- Perfect isolation (each test gets fresh database)
- No setup required

**Disadvantages:**
- Not 100% compatible with PostgreSQL features
- Cannot test PostgreSQL-specific functionality

#### PostgreSQL Test Database

For integration testing with real PostgreSQL:

```python
# .env.test
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/app_test
```

**Advantages:**
- Tests against production database type
- Tests PostgreSQL-specific features
- More realistic integration tests

**Disadvantages:**
- Slower than SQLite
- Requires PostgreSQL server running
- Needs database setup/teardown

### Test Fixtures

Common fixtures are defined in `tests/conftest.py`:

```python
# Database fixtures
test_db_engine     # Async database engine
test_db_session    # Async database session
db_session         # Alias for test_db_session

# HTTP client fixtures
client             # AsyncClient with database override

# Mock fixtures
mock_db_healthy    # Mock healthy database
mock_db_unhealthy  # Mock unhealthy database

# Utility fixtures
test_environment   # Environment information
clean_db           # Clean database state
reset_dependency_overrides  # Auto-reset after each test
```

## Test Organization

### Directory Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── test_health.py           # Health endpoint tests
├── test_middleware.py       # Middleware tests
├── unit/                    # Unit tests
│   └── test_*.py
├── integration/             # Integration tests
│   └── test_*.py
└── e2e/                     # End-to-end tests
    └── test_*.py
```

### Test Markers

Use markers to categorize tests:

```python
@pytest.mark.unit
def test_unit_example():
    """Unit test - tests single component in isolation."""
    pass

@pytest.mark.integration
@pytest.mark.database
async def test_integration_example(client):
    """Integration test - tests multiple components together."""
    pass

@pytest.mark.e2e
@pytest.mark.slow
async def test_e2e_example(client):
    """End-to-end test - tests complete user workflow."""
    pass
```

### Naming Conventions

- Test files: `test_*.py`
- Test functions: `test_*`
- Test classes: `Test*`
- Test methods: `test_*`

```python
# Good
def test_user_creation_with_valid_data():
    pass

class TestUserAuthentication:
    def test_login_with_valid_credentials(self):
        pass

# Bad
def user_creation_test():  # Missing 'test_' prefix
    pass
```

## Writing Tests

### Basic Test Structure

```python
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_endpoint_example(client: AsyncClient):
    """Test endpoint returns expected response."""
    # Arrange
    expected_status = 200

    # Act
    response = await client.get("/api/v1/endpoint")

    # Assert
    assert response.status_code == expected_status
    assert response.json()["key"] == "value"
```

### Testing API Endpoints

```python
@pytest.mark.asyncio
@pytest.mark.api
async def test_get_endpoint(client: AsyncClient):
    """Test GET endpoint."""
    response = await client.get("/api/v1/resource")

    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "name" in data


@pytest.mark.asyncio
@pytest.mark.api
async def test_post_endpoint(client: AsyncClient):
    """Test POST endpoint."""
    payload = {
        "name": "Test Resource",
        "description": "Test description"
    }

    response = await client.post("/api/v1/resource", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert "id" in data
```

### Testing Database Operations

```python
import pytest
from sqlalchemy import select
from app.models.user import User


@pytest.mark.asyncio
@pytest.mark.database
async def test_user_creation(db_session):
    """Test creating a user in database."""
    # Create user
    user = User(
        email="test@example.com",
        hashed_password="hashed_password_here",
        first_name="Test",
        last_name="User"
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Verify user was created
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.is_active is True

    # Query user from database
    result = await db_session.execute(
        select(User).where(User.email == "test@example.com")
    )
    db_user = result.scalar_one_or_none()

    assert db_user is not None
    assert db_user.id == user.id
```

### Testing with Mocks

```python
@pytest.mark.asyncio
async def test_with_mock_database(client: AsyncClient, mock_db_healthy):
    """Test endpoint with mocked database health check."""
    response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["checks"]["database"]["status"] == "healthy"


@pytest.mark.asyncio
async def test_error_handling(client: AsyncClient, mock_db_unhealthy):
    """Test error handling when database is down."""
    response = await client.get("/health")

    assert response.status_code == 503
    data = response.json()
    assert data["status"] == "degraded"
```

### Parametrized Tests

```python
@pytest.mark.asyncio
@pytest.mark.parametrize("status_code,path", [
    (200, "/health"),
    (200, "/health/live"),
    (200, "/health/ready"),
    (404, "/nonexistent"),
])
async def test_endpoint_status_codes(client: AsyncClient, status_code: int, path: str):
    """Test various endpoints return expected status codes."""
    response = await client.get(path)
    assert response.status_code == status_code
```

## Running Tests

### Basic Commands

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific file
pytest tests/test_health.py

# Run specific test
pytest tests/test_health.py::test_health_check_returns_200_when_healthy

# Run tests matching pattern
pytest -k "health"
```

### Coverage Commands

```bash
# Run with coverage report
pytest --cov

# Generate HTML coverage report
pytest --cov --cov-report=html

# Open HTML coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Marker-Based Execution

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only API tests
pytest -m api

# Run database tests
pytest -m database

# Skip slow tests
pytest -m "not slow"

# Run integration or e2e tests
pytest -m "integration or e2e"
```

### Advanced Options

```bash
# Stop after first failure
pytest -x

# Stop after N failures
pytest --maxfail=3

# Run last failed tests
pytest --lf

# Run failed tests first
pytest --ff

# Show local variables on failure
pytest -l

# Show 10 slowest tests
pytest --durations=10

# Parallel execution (requires pytest-xdist)
pytest -n auto
```

## Coverage Reporting

### Coverage Configuration

Coverage is configured in `pytest.ini`:

```ini
[coverage:run]
source = app
omit = */tests/*, */migrations/*, */alembic/*
branch = true

[coverage:report]
precision = 2
show_missing = true
skip_covered = false
```

### Coverage Targets

- **Minimum**: 80% (enforced by `--cov-fail-under=80`)
- **Target**: 90%+
- **Goal**: 95%+ for critical paths

### Viewing Coverage

```bash
# Terminal report
pytest --cov --cov-report=term-missing

# HTML report (most detailed)
pytest --cov --cov-report=html
open htmlcov/index.html

# XML report (for CI/CD)
pytest --cov --cov-report=xml

# All reports
pytest --cov --cov-report=term-missing --cov-report=html --cov-report=xml
```

### Excluding Code from Coverage

```python
def debug_only_function():  # pragma: no cover
    """This function is excluded from coverage."""
    pass

if TYPE_CHECKING:  # pragma: no cover
    from typing import SomeType
```

## Testing Patterns

### Test-Driven Development (TDD)

Follow the Red-Green-Refactor cycle:

```python
# 1. RED - Write failing test first
@pytest.mark.asyncio
async def test_create_user(client: AsyncClient):
    """Test creating a new user."""
    payload = {
        "email": "new@example.com",
        "password": "SecurePass123!",
        "first_name": "New",
        "last_name": "User"
    }

    response = await client.post("/api/v1/users", json=payload)

    assert response.status_code == 201
    assert response.json()["email"] == payload["email"]

# 2. GREEN - Implement minimal code to pass
# (implement endpoint in app/api/v1/endpoints/users.py)

# 3. REFACTOR - Improve code while keeping tests green
# (refactor implementation, tests still pass)
```

### Arrange-Act-Assert (AAA) Pattern

```python
@pytest.mark.asyncio
async def test_user_login(client: AsyncClient):
    """Test user login flow."""
    # Arrange - Set up test data
    user_data = {
        "email": "test@example.com",
        "password": "SecurePass123!"
    }

    # Act - Perform the action
    response = await client.post("/api/v1/auth/login", json=user_data)

    # Assert - Verify results
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "token_type" in response.json()
```

### Testing Edge Cases

```python
@pytest.mark.asyncio
class TestUserCreationEdgeCases:
    """Test edge cases for user creation."""

    async def test_duplicate_email(self, client: AsyncClient):
        """Test creating user with duplicate email."""
        payload = {"email": "duplicate@example.com", "password": "Pass123!"}

        # Create first user
        await client.post("/api/v1/users", json=payload)

        # Attempt to create duplicate
        response = await client.post("/api/v1/users", json=payload)

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()

    async def test_invalid_email(self, client: AsyncClient):
        """Test creating user with invalid email."""
        payload = {"email": "not-an-email", "password": "Pass123!"}

        response = await client.post("/api/v1/users", json=payload)

        assert response.status_code == 422
        assert "email" in response.json()["detail"][0]["loc"]

    async def test_weak_password(self, client: AsyncClient):
        """Test creating user with weak password."""
        payload = {"email": "test@example.com", "password": "123"}

        response = await client.post("/api/v1/users", json=payload)

        assert response.status_code == 400
        assert "password" in response.json()["detail"].lower()
```

## Best Practices

### 1. Write Independent Tests

```python
# Good - each test is independent
@pytest.mark.asyncio
async def test_create_user(client: AsyncClient):
    """Test user creation."""
    payload = {"email": "user1@example.com", "password": "Pass123!"}
    response = await client.post("/api/v1/users", json=payload)
    assert response.status_code == 201

@pytest.mark.asyncio
async def test_get_user(client: AsyncClient):
    """Test getting user."""
    # Create user for this test
    payload = {"email": "user2@example.com", "password": "Pass123!"}
    create_response = await client.post("/api/v1/users", json=payload)
    user_id = create_response.json()["id"]

    # Test getting user
    response = await client.get(f"/api/v1/users/{user_id}")
    assert response.status_code == 200

# Bad - tests depend on each other
@pytest.mark.asyncio
async def test_01_create_user(client: AsyncClient):
    """Must run first."""
    global user_id  # Bad practice
    payload = {"email": "user@example.com", "password": "Pass123!"}
    response = await client.post("/api/v1/users", json=payload)
    user_id = response.json()["id"]

@pytest.mark.asyncio
async def test_02_get_user(client: AsyncClient):
    """Depends on test_01."""
    response = await client.get(f"/api/v1/users/{user_id}")  # Fails if test_01 didn't run
    assert response.status_code == 200
```

### 2. Use Descriptive Test Names

```python
# Good
def test_user_creation_fails_with_invalid_email()
def test_authenticated_user_can_access_protected_endpoint()
def test_unauthenticated_user_receives_401_on_protected_endpoint()

# Bad
def test_user()
def test_endpoint()
def test_1()
```

### 3. Test Behavior, Not Implementation

```python
# Good - tests behavior
@pytest.mark.asyncio
async def test_user_can_update_profile(client: AsyncClient):
    """Test user can update their profile."""
    # Create user
    create_payload = {"email": "user@example.com", "password": "Pass123!"}
    create_response = await client.post("/api/v1/users", json=create_payload)
    user_id = create_response.json()["id"]

    # Update profile
    update_payload = {"first_name": "John", "last_name": "Doe"}
    response = await client.patch(f"/api/v1/users/{user_id}", json=update_payload)

    assert response.status_code == 200
    assert response.json()["first_name"] == "John"
    assert response.json()["last_name"] == "Doe"

# Bad - tests implementation details
def test_user_model_has_first_name_field():
    """Tests internal model structure instead of behavior."""
    assert hasattr(User, 'first_name')  # Don't test this
```

### 4. Use Fixtures for Common Setup

```python
# Good - reusable fixture
@pytest.fixture
async def created_user(client: AsyncClient):
    """Fixture that creates a user for testing."""
    payload = {"email": "fixture@example.com", "password": "Pass123!"}
    response = await client.post("/api/v1/users", json=payload)
    return response.json()

@pytest.mark.asyncio
async def test_with_fixture(client: AsyncClient, created_user):
    """Test using fixture."""
    response = await client.get(f"/api/v1/users/{created_user['id']}")
    assert response.status_code == 200

# Bad - duplicate setup in each test
@pytest.mark.asyncio
async def test_1(client: AsyncClient):
    # Duplicate setup
    payload = {"email": "user1@example.com", "password": "Pass123!"}
    user = (await client.post("/api/v1/users", json=payload)).json()
    # test code...

@pytest.mark.asyncio
async def test_2(client: AsyncClient):
    # Duplicate setup again
    payload = {"email": "user2@example.com", "password": "Pass123!"}
    user = (await client.post("/api/v1/users", json=payload)).json()
    # test code...
```

### 5. Mock External Dependencies

```python
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
@patch('app.services.email.send_email')
async def test_user_registration_sends_email(mock_send_email, client: AsyncClient):
    """Test that user registration sends welcome email."""
    mock_send_email.return_value = AsyncMock()

    payload = {"email": "new@example.com", "password": "Pass123!"}
    response = await client.post("/api/v1/users", json=payload)

    assert response.status_code == 201
    mock_send_email.assert_called_once()
```

## CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/backend-tests.yml
name: Backend Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: app_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'

      - name: Install dependencies
        run: |
          pip install -r requirements/test.txt

      - name: Run tests
        run: |
          pytest --cov --cov-report=xml --cov-report=term
        env:
          DATABASE_URL: postgresql+asyncpg://postgres:postgres@localhost:5432/app_test

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
          fail_ci_if_error: true
```

### Running Tests Locally with Docker

```bash
# Start test database
docker-compose -f docker-compose.dev.yml up -d postgres

# Run tests against PostgreSQL
TEST_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/app_test pytest

# Stop database
docker-compose -f docker-compose.dev.yml down
```

## Troubleshooting

### Common Issues

**Issue**: Tests fail with "database is locked" (SQLite)

**Solution**: Use `StaticPool` for SQLite in-memory:
```python
engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    poolclass=StaticPool,
    connect_args={"check_same_thread": False}
)
```

**Issue**: Async tests not running

**Solution**: Add `@pytest.mark.asyncio` decorator:
```python
@pytest.mark.asyncio
async def test_example():
    pass
```

**Issue**: Coverage not detecting tested code

**Solution**: Ensure `source` is set correctly in pytest.ini:
```ini
[coverage:run]
source = app
```

**Issue**: Tests pass individually but fail when run together

**Solution**: Tests are not independent. Use fixtures and avoid shared state:
```python
# Bad - shared state
user_id = None

@pytest.mark.asyncio
async def test_1():
    global user_id
    user_id = 1

# Good - independent
@pytest.mark.asyncio
async def test_1(created_user):
    user_id = created_user["id"]
```

## Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [httpx Testing](https://www.python-httpx.org/advanced/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [Coverage.py](https://coverage.readthedocs.io/)
