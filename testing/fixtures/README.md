# Test Fixtures

## Overview

Test fixtures provide consistent, reusable test data for all test types. Fixtures ensure tests are repeatable and don't depend on external data sources.

## Organization

```
fixtures/
├── users.json           # User account fixtures
├── assessments.json     # Assessment data fixtures
├── profiles.json        # User profile fixtures
├── auth_tokens.json     # Authentication token fixtures
├── factories.py         # Factory Boy factories for dynamic data
└── README.md           # This file
```

## Fixture Types

### Static Fixtures (JSON)

Pre-defined test data loaded from JSON files.

**Advantages:**
- Consistent across test runs
- Easy to review and modify
- Version controlled
- Fast to load

**Use cases:**
- Known test users
- Reference data
- Baseline configurations

### Dynamic Fixtures (Factories)

Programmatically generated test data using Factory Boy.

**Advantages:**
- Flexible data generation
- Random/realistic data
- Customizable attributes
- Handles relationships

**Use cases:**
- Large datasets
- Edge cases
- Performance testing
- Randomized testing

## Using Static Fixtures

### Loading in Django

```python
# In test setup
from django.core.management import call_command

def setup_fixtures():
    call_command('loaddata', 'testing/fixtures/users.json')
    call_command('loaddata', 'testing/fixtures/assessments.json')
```

### Loading in pytest

```python
# conftest.py
import pytest
from django.core.management import call_command

@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    """Load fixtures for all tests."""
    with django_db_blocker.unblock():
        call_command('loaddata', 'testing/fixtures/users.json')
        call_command('loaddata', 'testing/fixtures/assessments.json')
```

### Creating Fixtures

**Export existing data:**
```bash
python manage.py dumpdata apps.users.User \
    --indent 2 \
    --output testing/fixtures/users.json
```

**Manual creation:**
```json
[
  {
    "model": "users.user",
    "pk": 1,
    "fields": {
      "email": "test@example.com",
      "first_name": "Test",
      "last_name": "User",
      "is_active": true,
      "date_joined": "2024-01-01T00:00:00Z"
    }
  }
]
```

## Using Dynamic Fixtures (Factories)

### Factory Definition

```python
# fixtures/factories.py
import factory
from factory.django import DjangoModelFactory
from apps.users.models import User
from apps.assessment.models import Assessment

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f'user{n}@example.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    is_active = True
    password = factory.PostGenerationMethodCall('set_password', 'password123')

class AssessmentFactory(DjangoModelFactory):
    class Meta:
        model = Assessment

    user = factory.SubFactory(UserFactory)
    age = factory.Faker('random_int', min=18, max=65)
    sport = factory.Faker('random_element', elements=['running', 'cycling', 'swimming'])
    level = factory.Faker('random_element', elements=['beginner', 'intermediate', 'advanced'])
    training_days = factory.Faker('random_int', min=1, max=7)
```

### Using Factories in Tests

```python
from testing.fixtures.factories import UserFactory, AssessmentFactory

# Create single instance
user = UserFactory.create()

# Create with specific attributes
admin_user = UserFactory.create(is_staff=True, is_superuser=True)

# Create multiple instances
users = UserFactory.create_batch(10)

# Build without saving to database
user = UserFactory.build()

# Create related objects
assessment = AssessmentFactory.create(
    user=user,
    age=25,
    sport='running'
)
```

## Test Data Patterns

### Pattern 1: Minimal Test Data

Create only the data needed for the specific test.

```python
def test_user_login():
    # Create minimal user
    user = UserFactory.create(email='test@example.com')

    # Test login
    response = client.post('/api/v1/auth/login/', {
        'email': user.email,
        'password': 'password123'
    })

    assert response.status_code == 200
```

### Pattern 2: Fixture Setup

Use pytest fixtures for reusable test data.

```python
# conftest.py
@pytest.fixture
def test_user(db):
    """Create a standard test user."""
    return UserFactory.create(email='test@example.com')

@pytest.fixture
def test_assessment(test_user):
    """Create a test assessment for test user."""
    return AssessmentFactory.create(user=test_user)

# In test
def test_assessment_retrieval(test_user, test_assessment):
    response = client.get(f'/api/v1/assessment/{test_assessment.id}/')
    assert response.status_code == 200
```

### Pattern 3: Bulk Data Generation

Generate large datasets for performance testing.

```python
def setup_performance_test_data():
    """Create 1000 users with assessments for performance testing."""
    users = UserFactory.create_batch(1000)
    for user in users:
        AssessmentFactory.create_batch(5, user=user)
```

## Realistic Test Data

Use Faker for realistic data generation:

```python
from faker import Faker

fake = Faker()

class UserFactory(DjangoModelFactory):
    email = factory.Faker('email')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    date_of_birth = factory.Faker('date_of_birth', minimum_age=18, maximum_age=65)
    phone_number = factory.Faker('phone_number')
    address = factory.Faker('address')
```

## Edge Cases and Boundary Values

Test edge cases with specific factory traits:

```python
class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    class Params:
        # Traits for common scenarios
        is_admin = factory.Trait(is_staff=True, is_superuser=True)
        is_inactive = factory.Trait(is_active=False)
        is_new = factory.Trait(date_joined=factory.LazyFunction(timezone.now))

# Usage
admin_user = UserFactory.create(is_admin=True)
inactive_user = UserFactory.create(is_inactive=True)
new_user = UserFactory.create(is_new=True)
```

## Authentication Fixtures

### Test Users

```python
# Standard test users
TEST_USERS = {
    'admin': {
        'email': 'admin@example.com',
        'password': 'admin123',
        'is_staff': True,
        'is_superuser': True
    },
    'active_user': {
        'email': 'user@example.com',
        'password': 'user123',
        'is_active': True
    },
    'inactive_user': {
        'email': 'inactive@example.com',
        'password': 'inactive123',
        'is_active': False
    }
}
```

### Authentication Tokens

```python
@pytest.fixture
def auth_token(test_user):
    """Generate authentication token for test user."""
    from rest_framework.authtoken.models import Token
    token, _ = Token.objects.get_or_create(user=test_user)
    return token.key

@pytest.fixture
def authenticated_client(api_client, test_user):
    """API client authenticated as test user."""
    api_client.force_authenticate(user=test_user)
    return api_client
```

## Data Cleanup

### Automatic Cleanup (pytest)

pytest automatically rolls back database transactions:

```python
@pytest.mark.django_db
def test_with_auto_cleanup():
    user = UserFactory.create()
    # User automatically deleted after test
```

### Manual Cleanup

For tests that need explicit cleanup:

```python
@pytest.fixture
def test_data():
    # Setup
    users = UserFactory.create_batch(10)

    yield users

    # Cleanup
    User.objects.filter(pk__in=[u.pk for u in users]).delete()
```

## Best Practices

1. **Use factories for flexibility:**
   - Static fixtures for known data
   - Factories for dynamic/randomized data

2. **Keep fixtures minimal:**
   - Only create necessary data
   - Avoid over-complex fixtures

3. **Make fixtures independent:**
   - Don't rely on execution order
   - Each test should set up its own data

4. **Use realistic data:**
   - Faker for believable values
   - Edge cases for boundary testing

5. **Clean up properly:**
   - Use database transactions
   - Explicit cleanup when needed

6. **Version control fixtures:**
   - Commit static fixtures to git
   - Document fixture changes

7. **Document fixture usage:**
   - Comment complex factories
   - Maintain fixture README

## Example Fixtures

See fixture files:
- `users.json` - Standard test users
- `assessments.json` - Test assessment data
- `profiles.json` - Test user profiles
- `factories.py` - Factory Boy factories

## Future Implementation

Fixtures will be expanded as test suites are implemented:
- Story 13.2: Test data isolation
- Story 13.14: Test data generation utilities
