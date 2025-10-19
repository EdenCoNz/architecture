# Backend Architecture Documentation

This document describes the architecture and organization of the backend project.

## Overview

The backend is built with Django 5.1 and Django REST Framework, following a scalable, feature-based architecture with clear separation of concerns. The project structure is designed to support rapid development while maintaining code quality and testability.

## Architecture Principles

### 1. Separation of Concerns
The codebase is organized into distinct layers:
- **Presentation Layer** (Views/Serializers): Handle HTTP requests/responses
- **Business Logic Layer** (Services): Implement domain logic and orchestration
- **Data Access Layer** (Repositories): Encapsulate database queries
- **Data Layer** (Models): Define data structure and basic validation

### 2. Feature-Based Organization
Django apps are organized by business domain/feature rather than technical function:
- Each app focuses on a specific domain (e.g., users, products, orders)
- Apps are self-contained and independently deployable
- Cross-app dependencies are minimized

### 3. DRY (Don't Repeat Yourself)
Common functionality is shared through:
- `common/` package for utilities, middleware, and helpers
- `core/` package for abstract models and shared business logic
- Reusable mixins, decorators, and base classes

### 4. Test-Driven Development
Test structure mirrors source structure:
- Unit tests for isolated components
- Integration tests for component interactions
- End-to-end tests for complete workflows
- Fixtures for reusable test data

## Directory Structure

### Source Code (`src/`)

#### `backend/` - Django Project Configuration
The main Django project containing settings, URLs, and WSGI/ASGI configurations.

**Key Files:**
- `settings/base.py` - Common settings for all environments
- `settings/development.py` - Development-specific settings
- `settings/production.py` - Production-specific settings
- `settings/test.py` - Test-specific settings
- `urls.py` - Root URL configuration
- `wsgi.py` - WSGI application entry point
- `asgi.py` - ASGI application entry point

**Environment Selection:**
Set `DJANGO_SETTINGS_MODULE` environment variable to choose settings:
```bash
export DJANGO_SETTINGS_MODULE=backend.settings.development
```

#### `apps/` - Feature-Based Applications
Contains all Django applications, each focused on a specific domain.

**Structure:**
```
apps/
└── <app_name>/
    ├── __init__.py
    ├── apps.py              # App configuration
    ├── models.py            # Database models
    ├── views.py             # View logic
    ├── serializers.py       # DRF serializers
    ├── urls.py              # URL routing
    ├── admin.py             # Admin interface
    ├── managers.py          # Custom model managers
    ├── signals.py           # Django signals
    ├── tasks.py             # Background tasks
    ├── migrations/          # Database migrations
    └── tests/               # App-specific tests
```

**Guidelines:**
- Apps should be loosely coupled
- Use clear, domain-focused names
- Keep apps focused on single responsibility
- Share common code through `common/` package
- See `backend/src/apps/README.md` for detailed guidelines

#### `common/` - Shared Utilities
Reusable components used across multiple apps.

**Modules:**

**`middleware/`** - Custom Django middleware
- Request/response processing
- Authentication middleware
- Logging and monitoring middleware
- Rate limiting middleware

**`utils/`** - General utility functions
- Date/time utilities
- String formatting
- File operations
- Data transformation helpers

**`validators/`** - Custom field validators
- Phone number validators
- Email validators
- File validators
- Business logic validators

**`exceptions/`** - Custom exception classes
- Business logic exceptions
- Validation exceptions
- API exceptions
- Error handling

**`mixins/`** - Reusable class mixins
- Timestamp mixin
- Soft delete mixin
- Audit log mixin
- View mixins

**`serializers/`** - Base serializer classes
- Base model serializers
- Dynamic fields serializers
- Reusable serializer mixins

**`permissions/`** - Custom DRF permissions
- Role-based permissions
- Object-level permissions
- Custom business permissions

**`decorators/`** - Function and class decorators
- Permission decorators
- Caching decorators
- Rate limiting decorators
- Logging decorators

#### `core/` - Core Business Logic
Shared domain models, services, and repositories.

**Modules:**

**`models/`** - Abstract base models
Common model functionality inherited by app models:
```python
from core.models import TimeStampedModel

class Product(TimeStampedModel):
    name = models.CharField(max_length=255)
    # Inherits: created_at, updated_at
```

Common abstract models:
- `TimeStampedModel` - Adds created_at and updated_at
- `SoftDeleteModel` - Implements soft delete
- `UUIDModel` - Uses UUID as primary key
- `AuditModel` - Adds audit trail fields

**`services/`** - Business logic layer
Service classes implement business logic and orchestration:
```python
class UserService:
    @staticmethod
    def create_user_with_profile(data):
        user = User.objects.create(**data)
        Profile.objects.create(user=user)
        send_welcome_email(user)
        return user
```

Service characteristics:
- Stateless and focused on business logic
- Coordinate between repositories and external services
- Handle transactions and error handling
- Return domain objects

**`repositories/`** - Data access layer
Repository classes encapsulate database queries:
```python
class ProductRepository:
    @staticmethod
    def get_active_products():
        return Product.objects.filter(is_active=True)

    @staticmethod
    def get_by_category(category_id):
        return Product.objects.filter(category_id=category_id)
```

Repository characteristics:
- Handle all database operations
- Encapsulate complex queries
- Return QuerySets or model instances
- Easily mocked for testing

### Test Suite (`tests/`)

Test structure mirrors source structure for easy navigation.

#### `unit/` - Unit Tests
Fast, isolated tests for individual components.

**Structure:**
```
unit/
├── apps/           # App-specific unit tests
├── common/         # Common utilities tests
└── core/           # Core services/repositories tests
```

**Guidelines:**
- Mock external dependencies
- Test one component at a time
- Use descriptive test names
- Follow AAA pattern (Arrange, Act, Assert)
- Aim for >80% code coverage

#### `integration/` - Integration Tests
Tests verifying component interactions.

**Structure:**
```
integration/
├── api/            # API endpoint tests
└── database/       # Database operation tests
```

**Guidelines:**
- Use test database (automatic with Django)
- Test real database interactions
- Verify error handling
- Use fixtures for test data

#### `e2e/` - End-to-End Tests
Complete workflow tests simulating real user interactions.

**Guidelines:**
- Focus on critical user journeys
- Use realistic test data
- Test happy path and error scenarios
- Run separately from unit/integration tests

#### `fixtures/` - Test Fixtures
Reusable test data and factories.

**Contains:**
- Model factories (factory_boy)
- JSON fixtures
- Test data generators
- Common test utilities

## Design Patterns

### Repository Pattern
Separates data access logic from business logic:
```python
# repositories.py
class UserRepository:
    @staticmethod
    def find_by_email(email):
        return User.objects.filter(email=email).first()

# services.py
class UserService:
    def __init__(self):
        self.repo = UserRepository()

    def authenticate(self, email, password):
        user = self.repo.find_by_email(email)
        if user and user.check_password(password):
            return user
        return None
```

### Service Layer Pattern
Encapsulates business logic:
```python
class OrderService:
    @staticmethod
    def create_order(user, items):
        # Validate business rules
        if not items:
            raise ValidationError("Order must have items")

        # Create order
        order = Order.objects.create(user=user)

        # Add items
        for item in items:
            OrderItem.objects.create(order=order, **item)

        # Send confirmation
        send_order_confirmation(order)

        return order
```

### Factory Pattern
For creating test data:
```python
# tests/fixtures/factories.py
import factory

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')

# Usage in tests
user = UserFactory.create()
```

## Best Practices

### 1. Models
- Keep models focused on data structure
- Use abstract models for common fields
- Add custom managers for common queries
- Use model validation for data integrity

### 2. Views
- Keep views thin - delegate to services
- Use viewsets for CRUD operations
- Use APIView for custom logic
- Handle errors gracefully

### 3. Serializers
- Use nested serializers for related data
- Implement custom validation in serializers
- Use read-only fields appropriately
- Consider performance with select_related/prefetch_related

### 4. Services
- Keep services stateless
- One service per domain/feature
- Handle transactions in services
- Return domain objects, not serializers

### 5. Repositories
- Encapsulate complex queries
- Use select_related/prefetch_related for optimization
- Return QuerySets for flexibility
- Keep repository methods focused

### 6. Testing
- Write tests before implementation (TDD)
- Use factories for test data
- Mock external services
- Test edge cases and error handling

## Adding New Features

Follow these steps when adding new functionality:

### 1. Create Django App
```bash
PYTHONPATH=src python manage.py startapp <app_name> src/apps/<app_name>
```

### 2. Configure App
Edit `src/apps/<app_name>/apps.py`:
```python
class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'
    verbose_name = 'User Management'
```

### 3. Register App
Add to `backend/settings/base.py`:
```python
LOCAL_APPS = [
    'apps.users',
    # ... other apps
]
```

### 4. Define Models
Create models in `models.py`:
```python
from core.models import TimeStampedModel

class Product(TimeStampedModel):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
```

### 5. Create Migrations
```bash
make migrations
make migrate
```

### 6. Add Business Logic
Create service in `services.py`:
```python
class ProductService:
    @staticmethod
    def create_product(data):
        # Business logic here
        return Product.objects.create(**data)
```

### 7. Create Serializers
Define serializers in `serializers.py`:
```python
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price']
```

### 8. Implement Views
Create views in `views.py`:
```python
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
```

### 9. Configure URLs
Add routes in `urls.py`:
```python
router = DefaultRouter()
router.register(r'products', ProductViewSet)
urlpatterns = router.urls
```

### 10. Write Tests
Create tests in `tests/`:
```python
def test_create_product():
    product = ProductFactory.create()
    assert product.name is not None
```

## Resources

- [Django Documentation](https://docs.djangoproject.com/en/5.1/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Django Best Practices](https://django-best-practices.readthedocs.io/)
- [Two Scoops of Django](https://www.feldroy.com/books/two-scoops-of-django-3-x)
