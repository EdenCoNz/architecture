# Django Applications

This directory contains all feature-based Django applications. Each app should be self-contained and focused on a specific domain or feature area.

## Creating a New App

To create a new Django app:

```bash
cd src/apps
django-admin startapp <app_name>
```

Or from the project root:

```bash
PYTHONPATH=src python manage.py startapp <app_name> src/apps/<app_name>
```

## App Structure

Each app should follow Django's standard structure:

```
<app_name>/
├── __init__.py
├── apps.py              # App configuration
├── models.py            # Database models
├── views.py             # View logic (or views/ directory)
├── serializers.py       # DRF serializers
├── urls.py              # URL routing
├── admin.py             # Django admin configuration
├── managers.py          # Custom model managers (optional)
├── signals.py           # Django signals (optional)
├── tasks.py             # Background tasks (optional)
├── migrations/          # Database migrations
│   └── __init__.py
└── tests/               # App-specific tests
    ├── __init__.py
    ├── test_models.py
    ├── test_views.py
    └── test_serializers.py
```

## Best Practices

### 1. Single Responsibility
Each app should focus on a single domain or feature:
- Good: `users`, `products`, `orders`, `payments`
- Avoid: `core`, `main`, `common` (these are too broad)

### 2. Loose Coupling
Apps should be loosely coupled and not directly depend on each other:
- Use Django signals for cross-app communication
- Share common functionality through the `common` package
- Define clear interfaces between apps

### 3. App Configuration
Always configure your app in `apps.py`:

```python
from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'
    verbose_name = 'User Management'

    def ready(self):
        # Import signals here to avoid circular imports
        import apps.users.signals
```

### 4. Register in Settings
Add your app to `LOCAL_APPS` in `backend/settings/base.py`:

```python
LOCAL_APPS = [
    'apps.users',
    'apps.products',
    # ... other apps
]
```

### 5. Use Abstract Models
For common model fields, use abstract models from `core.models`:

```python
from core.models import TimeStampedModel

class Product(TimeStampedModel):
    name = models.CharField(max_length=255)
    # created_at and updated_at are inherited
```

### 6. Service Layer
Put complex business logic in service classes, not in views or models:

```python
# services.py
class UserService:
    @staticmethod
    def create_user_with_profile(data):
        # Complex logic here
        user = User.objects.create(**data)
        Profile.objects.create(user=user)
        send_welcome_email(user)
        return user

# views.py
from .services import UserService

class UserCreateView(APIView):
    def post(self, request):
        user = UserService.create_user_with_profile(request.data)
        return Response(serializer.data)
```

### 7. Repository Pattern
For complex queries, use repository classes:

```python
# repositories.py
class ProductRepository:
    @staticmethod
    def get_active_products():
        return Product.objects.filter(is_active=True)

    @staticmethod
    def get_products_by_category(category_id):
        return Product.objects.filter(category_id=category_id)
```

### 8. Testing
Write comprehensive tests for your app:
- Unit tests for models, serializers, and business logic
- Integration tests for API endpoints
- Use fixtures for test data

## Example Apps

### User Management App
```python
# apps/users/models.py
from django.contrib.auth.models import AbstractUser
from core.models import TimeStampedModel

class User(AbstractUser, TimeStampedModel):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)

# apps/users/serializers.py
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone']

# apps/users/views.py
from rest_framework import viewsets

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# apps/users/urls.py
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'users', UserViewSet)
urlpatterns = router.urls
```

## Common Patterns

### ViewSets vs APIView
- Use ViewSets for CRUD operations on models
- Use APIView for custom endpoints or non-CRUD operations

### Permissions
Define custom permissions in `common/permissions/` for reuse across apps.

### Validators
Define custom validators in `common/validators/` for reuse across apps.

### Signals
Use signals sparingly and only for cross-cutting concerns:
```python
# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
```

## Resources

- [Django Apps Documentation](https://docs.djangoproject.com/en/5.1/ref/applications/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Django Signals](https://docs.djangoproject.com/en/5.1/topics/signals/)
