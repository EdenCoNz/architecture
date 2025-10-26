# Integration Tests

## Overview

Integration tests validate API endpoints, service interactions, and backend logic. These tests run against the backend API with a real database and Redis instance.

## Framework

- **pytest** - Primary test framework
- **pytest-django** - Django integration
- **requests** - HTTP client for API testing
- **factory_boy** - Test data factories

## Test Organization

```
integration/
├── api/
│   ├── test_health.py
│   ├── test_auth.py
│   ├── test_assessment.py
│   ├── test_user_profile.py
│   └── test_config.py
├── services/
│   ├── test_user_service.py
│   ├── test_assessment_service.py
│   └── test_profile_service.py
├── models/
│   ├── test_user_model.py
│   └── test_assessment_model.py
├── conftest.py
└── README.md
```

## Running Integration Tests

**All integration tests:**
```bash
./testing/run-tests.sh --suite integration
```

**Specific test file:**
```bash
docker compose -f docker-compose.yml -f compose.test.yml run --rm test-runner \
    pytest integration/api/test_auth.py
```

**Specific test function:**
```bash
docker compose -f docker-compose.yml -f compose.test.yml run --rm test-runner \
    pytest integration/api/test_auth.py::test_login_success
```

**With coverage:**
```bash
docker compose -f docker-compose.yml -f compose.test.yml run --rm test-runner \
    pytest integration/ --cov=backend --cov-report=html
```

**Verbose output:**
```bash
docker compose -f docker-compose.yml -f compose.test.yml run --rm test-runner \
    pytest integration/ -v --tb=short
```

## Writing Integration Tests

### API Test Example

```python
import pytest
from rest_framework.test import APIClient

@pytest.mark.django_db
class TestAuthAPI:
    def test_login_success(self, api_client, test_user):
        """Test successful login with valid credentials."""
        response = api_client.post('/api/v1/auth/login/', {
            'email': test_user.email,
            'password': 'password123'
        })

        assert response.status_code == 200
        assert 'token' in response.json()
        assert response.json()['user']['email'] == test_user.email

    def test_login_invalid_credentials(self, api_client):
        """Test login failure with invalid credentials."""
        response = api_client.post('/api/v1/auth/login/', {
            'email': 'invalid@example.com',
            'password': 'wrongpassword'
        })

        assert response.status_code == 401
        assert 'error' in response.json()

    @pytest.mark.parametrize('field', ['email', 'password'])
    def test_login_missing_field(self, api_client, field):
        """Test login validation for missing required fields."""
        data = {'email': 'test@example.com', 'password': 'password123'}
        del data[field]

        response = api_client.post('/api/v1/auth/login/', data)

        assert response.status_code == 400
        assert field in response.json()
```

### Service Test Example

```python
import pytest
from apps.users.services import UserService

@pytest.mark.django_db
class TestUserService:
    def test_create_user(self):
        """Test user creation through service layer."""
        service = UserService()
        user = service.create_user(
            email='test@example.com',
            password='password123',
            first_name='Test',
            last_name='User'
        )

        assert user.id is not None
        assert user.email == 'test@example.com'
        assert user.check_password('password123')

    def test_create_duplicate_user(self, test_user):
        """Test duplicate user creation raises error."""
        service = UserService()

        with pytest.raises(ValidationError):
            service.create_user(
                email=test_user.email,  # Duplicate email
                password='password123'
            )
```

### Model Test Example

```python
import pytest
from apps.users.models import User

@pytest.mark.django_db
class TestUserModel:
    def test_user_creation(self):
        """Test basic user model creation."""
        user = User.objects.create_user(
            email='test@example.com',
            password='password123'
        )

        assert user.email == 'test@example.com'
        assert user.check_password('password123')
        assert user.is_active is True

    def test_user_str_representation(self, test_user):
        """Test user string representation."""
        assert str(test_user) == test_user.email
```

## Fixtures (conftest.py)

```python
import pytest
from rest_framework.test import APIClient
from apps.users.models import User

@pytest.fixture
def api_client():
    """Provide API client for tests."""
    return APIClient()

@pytest.fixture
def test_user(db):
    """Create a test user."""
    return User.objects.create_user(
        email='test@example.com',
        password='password123',
        first_name='Test',
        last_name='User'
    )

@pytest.fixture
def authenticated_client(api_client, test_user):
    """Provide authenticated API client."""
    api_client.force_authenticate(user=test_user)
    return api_client

@pytest.fixture
def test_assessment(test_user):
    """Create a test assessment."""
    from apps.assessment.models import Assessment
    return Assessment.objects.create(
        user=test_user,
        age=25,
        sport='running',
        level='intermediate',
        training_days=4
    )
```

## Test Markers

```python
# Mark tests requiring database
@pytest.mark.django_db

# Mark slow tests
@pytest.mark.slow

# Mark tests requiring Redis
@pytest.mark.redis

# Mark tests requiring Celery
@pytest.mark.celery

# Parametrize tests
@pytest.mark.parametrize('input,expected', [
    (1, 2),
    (2, 4),
    (3, 6),
])
```

## Best Practices

### Database Transactions

1. **Use `@pytest.mark.django_db` for database access:**
   ```python
   @pytest.mark.django_db
   def test_with_database():
       user = User.objects.create(...)
   ```

2. **Transaction rollback is automatic** - Each test runs in a transaction that's rolled back

3. **Use `django_db_reset_sequences` for tests needing real IDs:**
   ```python
   @pytest.mark.django_db(reset_sequences=True)
   def test_with_sequences():
       # IDs start from 1
   ```

### API Testing

1. **Use APIClient for authentication:**
   ```python
   client.force_authenticate(user=test_user)
   ```

2. **Test all response aspects:**
   ```python
   assert response.status_code == 200
   assert response['Content-Type'] == 'application/json'
   assert 'data' in response.json()
   ```

3. **Test error cases:**
   ```python
   def test_invalid_request():
       response = client.post('/api/endpoint/', {})
       assert response.status_code == 400
   ```

### Test Data

1. **Use fixtures for common data:**
   ```python
   @pytest.fixture
   def test_user(db):
       return User.objects.create_user(...)
   ```

2. **Use factories for complex objects:**
   ```python
   from factory_boy import UserFactory
   user = UserFactory.create(is_active=True)
   ```

3. **Keep tests independent:**
   - Don't rely on test execution order
   - Each test should create its own data
   - Use database transactions for isolation

## Coverage

**Generate coverage report:**
```bash
pytest integration/ --cov=backend --cov-report=html --cov-report=term
```

**View coverage report:**
```bash
open testing/reports/coverage/index.html
```

**Coverage thresholds:**
- Minimum: 80%
- Target: 90%+

## Debugging

### Print debug info:
```python
import pytest

def test_something(capsys):
    print("Debug info")
    # Test code
    captured = capsys.readouterr()
    print(captured.out)
```

### Use pytest debugger:
```bash
pytest integration/test_file.py --pdb
```

### Show print statements:
```bash
pytest integration/ -s
```

### Verbose output:
```bash
pytest integration/ -vv
```

## Common Patterns

### Testing Authentication
See future implementation in Story 13.3

### Testing Data Submission
Implemented in Story 13.7. See `test_assessment_submission.py` for comprehensive tests covering:
- Valid data submission and success confirmation
- Data storage verification (exact match with submitted data)
- Validation errors for incomplete/invalid data
- Edge cases (age boundaries, null values, special characters)
- Authentication requirements
- Duplicate submission handling

**Example:**
```python
def test_submit_valid_assessment_returns_success(
    authenticated_client, api_base_url, assessment_data
):
    """Test valid assessment submission returns success."""
    url = f"{api_base_url}/assessments/"
    response = authenticated_client.post(url, json=assessment_data)

    assert response.status_code == 201
    assert "id" in response.json()
    assert response.json()["age"] == assessment_data["age"]
```

### Testing Profile Creation
Implemented in Story 13.8. See `test_profile_creation.py` for comprehensive tests covering:
- Profile creation with assessment values
- Profile data accuracy (training days, sport type, level, equipment)
- User access to profile (authentication required)
- Personalized recommendation data availability
- Profile updates and multi-user isolation

**Example:**
```python
def test_profile_created_with_assessment_values_after_submission(
    authenticated_client, api_base_url, assessment_data, test_user
):
    """Test profile is created with assessment values."""
    url = f"{api_base_url}/assessments/"
    response = authenticated_client.post(url, json=assessment_data)
    assert response.status_code == 201

    # Verify profile was created
    profile = Assessment.objects.get(user_id=test_user["id"])
    assert profile.sport == assessment_data["sport"]
    assert profile.age == assessment_data["age"]
```

**Running Story 13.8 tests:**
```bash
./testing/integration/test_story_13_8.sh [--verbose] [--coverage] [--html]
```

### API Contract Validation
See future implementation in Story 13.10
