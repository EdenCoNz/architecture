# Test Data Generation Utilities Guide

## Overview

The test data generation utilities provide a consistent, maintainable way to create realistic test data for users and assessments. These utilities are designed to support all testing needs including unit tests, integration tests, and end-to-end tests.

## Features

- **Realistic Data**: Generates user accounts and assessments with realistic profile data
- **Varied Attributes**: Creates assessments with different sports, experience levels, training days, and equipment
- **Edge Cases**: Supports generating boundary values (min/max ages, all enum combinations)
- **Validation**: All generated data passes Django model validation
- **Flexible**: Supports both model instances and dictionaries for API testing

## Installation

The test data generators are available in two locations:

1. **Backend Unit Tests**: `backend/tests/test_data_generators.py`
2. **Integration Tests**: `testing/fixtures/test_data_generators.py`

No installation required - the modules are included in the project.

## Usage

### Basic User Generation

```python
from tests.test_data_generators import UserDataGenerator

# Generate a single user
user_gen = UserDataGenerator()
user = user_gen.generate_user()

# Generate with custom attributes
user = user_gen.generate_user(
    email='custom@example.com',
    first_name='John'
)

# Generate multiple users
users = user_gen.generate_users(count=10)

# Generate admin user
admin = user_gen.generate_admin_user()

# Generate user with known credentials for login testing
user, password = user_gen.generate_user_with_credentials(
    password='TestPass123!'
)
```

### Basic Assessment Generation

```python
from tests.test_data_generators import AssessmentDataGenerator

# Generate a single assessment
assessment_gen = AssessmentDataGenerator()
assessment = assessment_gen.generate_assessment()

# Generate with specific sport
assessment = assessment_gen.generate_assessment(sport='cricket')

# Generate multiple assessments with variation
assessments = assessment_gen.generate_assessments(count=10)

# Generate sport-specific assessments
football_assessment = assessment_gen.generate_football_assessment()
cricket_assessment = assessment_gen.generate_cricket_assessment()

# Generate level-specific assessments
beginner = assessment_gen.generate_beginner_assessment()
advanced = assessment_gen.generate_advanced_assessment()

# Generate assessment with injuries
injured = assessment_gen.generate_assessment_with_injuries()
```

### Edge Case Generation

```python
from tests.test_data_generators import EdgeCaseDataGenerator

edge_gen = EdgeCaseDataGenerator()

# Generate boundary values
min_age = edge_gen.generate_minimum_age_assessment()  # age=13
max_age = edge_gen.generate_maximum_age_assessment()  # age=100

# Generate all equipment combinations
equipment_assessments = edge_gen.generate_all_equipment_combinations()
# Returns 3 assessments: no_equipment, basic_equipment, full_gym

# Generate all sport combinations
sport_assessments = edge_gen.generate_all_sport_combinations()
# Returns 2 assessments: football, cricket

# Generate all experience level combinations
level_assessments = edge_gen.generate_all_experience_level_combinations()
# Returns 3 assessments: beginner, intermediate, advanced

# Generate all training days combinations
training_assessments = edge_gen.generate_all_training_days_combinations()
# Returns 3 assessments: 2-3, 4-5, 6-7

# Generate comprehensive edge cases
all_edge_cases = edge_gen.generate_comprehensive_edge_cases()
# Returns all boundary values and combinations
```

### Complete Scenario Generation

```python
from tests.test_data_generators import TestDataGenerator

test_gen = TestDataGenerator()

# Generate realistic test scenario
scenario = test_gen.generate_realistic_scenario(
    user_count=5,
    assessment_count=5
)
users = scenario['users']
assessments = scenario['assessments']

# Generate user with assessment
user, assessment = test_gen.generate_user_with_assessment(
    sport='football',
    experience_level='beginner'
)

# Generate complete onboarding scenario
onboarding = test_gen.generate_complete_onboarding_scenario()
beginner_user = onboarding['beginner_user']
advanced_user = onboarding['advanced_user']
injured_user = onboarding['injured_user']

# Generate bulk test data for performance testing
bulk_data = test_gen.generate_bulk_test_data(
    user_count=100,
    assessment_count=80
)
```

### API Testing with Dictionaries

```python
from tests.test_data_generators import AssessmentDataGenerator

assessment_gen = AssessmentDataGenerator()

# Generate assessment data as dictionary for API requests
assessment_dict = assessment_gen.generate_assessment_dict()
# Returns: {'sport': 'football', 'age': 25, ...}

# Use in API tests
response = client.post('/api/v1/assessments/', json=assessment_dict)

# Generate with specific values
custom_dict = assessment_gen.generate_assessment_dict(
    sport='cricket',
    age=30,
    experience_level='advanced'
)
```

## Integration with pytest Fixtures

```python
import pytest
from tests.test_data_generators import TestDataGenerator

@pytest.fixture
def test_scenario():
    """Provide a complete test scenario with users and assessments."""
    generator = TestDataGenerator()
    return generator.generate_realistic_scenario()

def test_with_scenario(test_scenario):
    users = test_scenario['users']
    assessments = test_scenario['assessments']

    assert len(users) > 0
    assert len(assessments) > 0
```

## Common Patterns

### Testing User Registration

```python
from tests.test_data_generators import UserDataGenerator

def test_user_registration():
    user_gen = UserDataGenerator()
    user, password = user_gen.generate_user_with_credentials()

    # Test registration logic
    assert user.check_password(password)
```

### Testing Assessment Validation

```python
from tests.test_data_generators import EdgeCaseDataGenerator

def test_age_validation():
    edge_gen = EdgeCaseDataGenerator()

    # Test minimum age
    min_age = edge_gen.generate_minimum_age_assessment()
    min_age.full_clean()  # Should pass validation

    # Test maximum age
    max_age = edge_gen.generate_maximum_age_assessment()
    max_age.full_clean()  # Should pass validation
```

### Testing Multiple Variations

```python
from tests.test_data_generators import AssessmentDataGenerator

def test_assessment_variations():
    assessment_gen = AssessmentDataGenerator()
    assessments = assessment_gen.generate_assessments(count=20)

    # Verify variation in data
    sports = [a.sport for a in assessments]
    assert 'football' in sports
    assert 'cricket' in sports
```

### Performance Testing

```python
from tests.test_data_generators import TestDataGenerator

def test_bulk_data_creation():
    test_gen = TestDataGenerator()

    # Generate large dataset
    data = test_gen.generate_bulk_test_data(
        user_count=1000,
        assessment_count=800
    )

    # Verify data was created
    assert len(data['users']) == 1000
    assert len(data['assessments']) == 800
```

## Acceptance Criteria Coverage

### AC #1: Generate User Accounts with Realistic Profile Data

✅ **Implemented**: `UserDataGenerator` creates users with:
- Unique email addresses
- Realistic first and last names (using Faker)
- Proper password hashing
- Admin and inactive user variations

### AC #2: Generate Valid Assessment Submissions with Varied Attributes

✅ **Implemented**: `AssessmentDataGenerator` creates assessments with:
- Different sports (football, cricket)
- Varied experience levels (beginner, intermediate, advanced)
- Different training days (2-3, 4-5, 6-7)
- All equipment types (no_equipment, basic_equipment, full_gym)
- Injury variations

### AC #3: Support Creating Boundary Values

✅ **Implemented**: `EdgeCaseDataGenerator` creates:
- Minimum age boundary (13 years)
- Maximum age boundary (100 years)
- All equipment combinations
- All sport combinations
- All experience level combinations
- All training days combinations
- Comprehensive edge case sets

### AC #4: Generated Data Should Be Valid

✅ **Implemented**: All generators:
- Pass Django model validation (`full_clean()`)
- Can be saved to database
- Generate realistic, representative data
- Support customization via kwargs

## API Reference

### UserDataGenerator

| Method | Description | Returns |
|--------|-------------|---------|
| `generate_user(**kwargs)` | Generate a single user | User instance |
| `generate_users(count, **kwargs)` | Generate multiple users | List[User] |
| `generate_admin_user(**kwargs)` | Generate admin user | User instance |
| `generate_inactive_user(**kwargs)` | Generate inactive user | User instance |
| `generate_user_with_credentials(email, password)` | Generate user with known credentials | Tuple[User, str] |

### AssessmentDataGenerator

| Method | Description | Returns |
|--------|-------------|---------|
| `generate_assessment(**kwargs)` | Generate a single assessment | Assessment instance |
| `generate_assessments(count, **kwargs)` | Generate multiple assessments | List[Assessment] |
| `generate_football_assessment(**kwargs)` | Generate football assessment | Assessment instance |
| `generate_cricket_assessment(**kwargs)` | Generate cricket assessment | Assessment instance |
| `generate_beginner_assessment(**kwargs)` | Generate beginner assessment | Assessment instance |
| `generate_advanced_assessment(**kwargs)` | Generate advanced assessment | Assessment instance |
| `generate_assessment_with_injuries(**kwargs)` | Generate assessment with injuries | Assessment instance |
| `generate_assessment_dict(**kwargs)` | Generate assessment as dict for API testing | Dict[str, Any] |

### EdgeCaseDataGenerator

| Method | Description | Returns |
|--------|-------------|---------|
| `generate_minimum_age_assessment(**kwargs)` | Generate assessment with age=13 | Assessment instance |
| `generate_maximum_age_assessment(**kwargs)` | Generate assessment with age=100 | Assessment instance |
| `generate_all_equipment_combinations()` | Generate all equipment types | List[Assessment] |
| `generate_all_sport_combinations()` | Generate all sports | List[Assessment] |
| `generate_all_experience_level_combinations()` | Generate all experience levels | List[Assessment] |
| `generate_all_training_days_combinations()` | Generate all training days | List[Assessment] |
| `generate_comprehensive_edge_cases()` | Generate all edge cases | List[Assessment] |

### TestDataGenerator

| Method | Description | Returns |
|--------|-------------|---------|
| `generate_realistic_scenario(user_count, assessment_count)` | Generate realistic scenario | Dict[str, List] |
| `generate_user_with_assessment(sport, level, **kwargs)` | Generate user with assessment | Tuple[User, Assessment] |
| `generate_complete_onboarding_scenario()` | Generate complete onboarding scenario | Dict[str, Any] |
| `generate_bulk_test_data(user_count, assessment_count)` | Generate bulk test data | Dict[str, List] |

## Best Practices

1. **Use specific generators**: Use `FootballAssessmentFactory` instead of `AssessmentFactory(sport='football')`
2. **Leverage edge cases**: Use `EdgeCaseDataGenerator` for boundary testing
3. **Reuse scenarios**: Create fixtures for common test scenarios
4. **Validate data**: Call `full_clean()` when testing validation logic
5. **Use dictionaries for API tests**: Use `generate_assessment_dict()` for API endpoint testing
6. **Generate bulk data efficiently**: Use `generate_bulk_test_data()` for performance tests

## Troubleshooting

### Import Errors

If you encounter import errors, ensure Django is properly set up:

```python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.testing')
sys.path.insert(0, '/path/to/backend')
django.setup()
```

### Unique Constraint Violations

If you get unique constraint errors, it's because factories use sequences. Clean up data between tests:

```python
from tests.factories import FixtureHelper

# Clean all test data
FixtureHelper.cleanup_all()
```

### Factory Deprecation Warnings

If you see deprecation warnings about `_after_postgeneration`, these are from factory-boy and can be safely ignored. They will be addressed in a future release.

## Related Documentation

- [Django Factory Boy Documentation](https://factoryboy.readthedocs.io/)
- [Faker Documentation](https://faker.readthedocs.io/)
- [pytest Fixtures](https://docs.pytest.org/en/stable/fixture.html)
- [Backend Testing Guide](../../backend/tests/README.md)

## Support

For questions or issues:
1. Check the test files in `backend/tests/test_test_data_generators.py` for examples
2. Review the docstrings in `backend/tests/test_data_generators.py`
3. Consult the main testing documentation in `testing/README.md`
