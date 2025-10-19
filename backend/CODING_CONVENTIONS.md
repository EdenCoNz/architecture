# Coding Conventions

This document defines the coding conventions and standards for the Backend API project. All code contributions must follow these conventions to maintain consistency and quality across the codebase.

## Table of Contents

- [Python Style Guide](#python-style-guide)
- [Naming Conventions](#naming-conventions)
- [Code Organization](#code-organization)
- [Type Hints](#type-hints)
- [Documentation](#documentation)
- [Django Specific](#django-specific)
- [Error Handling](#error-handling)
- [Security Guidelines](#security-guidelines)
- [Performance Considerations](#performance-considerations)

## Python Style Guide

### Code Formatting

We use **Black** for automatic code formatting with these settings:

- **Line length**: 100 characters
- **Target version**: Python 3.12
- **Quote style**: Double quotes (Black default)
- **Indentation**: 4 spaces (never tabs)

Run Black before committing:
```bash
make format
```

### Linting

We use **Ruff** for fast Python linting with these rule sets:

- **E, W**: pycodestyle errors and warnings
- **F**: pyflakes (unused imports, undefined names)
- **I**: isort (import sorting)
- **B**: flake8-bugbear (likely bugs)
- **C4**: flake8-comprehensions (list/dict comprehension improvements)
- **UP**: pyupgrade (modern Python syntax)
- **ARG**: flake8-unused-arguments
- **SIM**: flake8-simplify (code simplification)

Run Ruff before committing:
```bash
make lint
```

### Type Checking

We use **MyPy** for static type checking with strict mode enabled:

- All functions must have type hints
- No implicit Optional types
- Strict equality checking
- Django and DRF type stubs enabled

Run MyPy before committing:
```bash
make type-check
```

## Naming Conventions

### Files and Directories

- **Python files**: `snake_case.py`
  - Examples: `user_service.py`, `product_repository.py`

- **Test files**: `test_*.py` or `*_test.py`
  - Examples: `test_user_service.py`, `authentication_test.py`

- **Directories**: `lowercase` or `snake_case`
  - Examples: `apps/`, `common/`, `core/`

- **Django apps**: `lowercase` (single word preferred)
  - Examples: `users/`, `products/`, `orders/`

### Python Identifiers

**Classes**: `PascalCase`
```python
class UserService:
    pass

class ProductRepository:
    pass

class OrderSerializer:
    pass
```

**Functions and Methods**: `snake_case`
```python
def get_user_by_email(email: str) -> User | None:
    pass

def create_order(user: User, items: list[OrderItem]) -> Order:
    pass

def _internal_helper() -> None:  # Private method
    pass
```

**Variables**: `snake_case`
```python
user_count = 10
active_products = Product.objects.filter(is_active=True)
order_total = calculate_total(items)
```

**Constants**: `UPPER_SNAKE_CASE`
```python
MAX_RETRY_ATTEMPTS = 3
DEFAULT_PAGE_SIZE = 20
API_VERSION = "v1"
DATABASE_TIMEOUT = 30
```

**Private Attributes**: Prefix with single underscore
```python
class Service:
    def __init__(self) -> None:
        self._cache = {}  # Private attribute
        self._initialized = False
```

**Internal Use Only**: Prefix with double underscore (name mangling)
```python
class Service:
    def __init__(self) -> None:
        self.__internal_state = {}  # Strongly private
```

### Django Specific Naming

**Models**: `PascalCase` (singular)
```python
class User(AbstractUser):
    pass

class Product(models.Model):
    pass

class OrderItem(models.Model):  # Not OrderItems
    pass
```

**Model Fields**: `snake_case`
```python
class User(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email_address = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

**Serializers**: Model name + `Serializer`
```python
class UserSerializer(serializers.ModelSerializer):
    pass

class ProductDetailSerializer(serializers.ModelSerializer):
    pass

class OrderCreateSerializer(serializers.Serializer):
    pass
```

**ViewSets**: Model name + `ViewSet`
```python
class UserViewSet(viewsets.ModelViewSet):
    pass

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    pass
```

**Services**: Domain name + `Service`
```python
class AuthenticationService:
    pass

class PaymentService:
    pass

class NotificationService:
    pass
```

**Repositories**: Model name + `Repository`
```python
class UserRepository:
    pass

class ProductRepository:
    pass
```

**URLs**: `kebab-case`
```python
urlpatterns = [
    path("user-profiles/", UserProfileViewSet.as_view()),
    path("order-items/", OrderItemViewSet.as_view()),
    path("api/v1/product-categories/", CategoryViewSet.as_view()),
]
```

## Code Organization

### Import Order

Imports must be organized in this order (enforced by Ruff):

1. Standard library imports
2. Third-party imports
3. Django imports
4. Local application imports

Each group separated by a blank line:

```python
# Standard library
import os
import sys
from datetime import datetime
from typing import Any

# Third-party
import requests
from rest_framework import status
from rest_framework.decorators import action

# Django
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

# Local
from apps.users.models import User
from common.exceptions import ValidationError
from core.services.email import EmailService
```

### Module Structure

Organize module content in this order:

```python
"""Module docstring explaining purpose and usage."""

# 1. Imports (organized as above)
from typing import Any
from django.db import models

# 2. Module-level constants
MAX_ATTEMPTS = 3
DEFAULT_TIMEOUT = 30

# 3. Type definitions
UserDict = dict[str, Any]
ConfigOptions = dict[str, str | int | bool]

# 4. Module-level functions
def get_default_config() -> ConfigOptions:
    """Return default configuration."""
    pass

# 5. Classes
class MyClass:
    """Class implementing specific functionality."""
    pass

# 6. Main execution (if applicable)
if __name__ == "__main__":
    pass
```

### Function/Method Structure

```python
def create_user(
    username: str,
    email: str,
    password: str,
    *,  # Force keyword-only arguments after this
    is_active: bool = True,
    send_welcome_email: bool = True,
) -> User:
    """Create a new user account.

    Args:
        username: Unique username
        email: User's email address
        password: Plain text password (will be hashed)
        is_active: Whether account is active (default: True)
        send_welcome_email: Send welcome email (default: True)

    Returns:
        Created User instance

    Raises:
        ValidationError: If username or email exists
        ValueError: If password is too weak
    """
    # 1. Input validation
    if not username or not email:
        raise ValidationError("Username and email are required")

    # 2. Main logic
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        is_active=is_active,
    )

    # 3. Side effects
    if send_welcome_email:
        send_email(user.email, "Welcome!")

    # 4. Return result
    return user
```

## Type Hints

### Required Type Hints

All public functions and methods must have complete type hints:

```python
# Good: Complete type hints
def get_user(user_id: int) -> User | None:
    """Get user by ID."""
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None

# Bad: Missing type hints
def get_user(user_id):  # Missing return type
    return User.objects.get(id=user_id)
```

### Modern Type Hint Syntax

Use Python 3.12+ syntax (PEP 604, PEP 585):

```python
# Good: Modern syntax
def process_items(items: list[str]) -> dict[str, int]:
    pass

def get_user(user_id: int) -> User | None:
    pass

def merge_data(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    pass

# Bad: Old syntax
from typing import List, Dict, Optional

def process_items(items: List[str]) -> Dict[str, int]:
    pass

def get_user(user_id: int) -> Optional[User]:
    pass
```

### Complex Types

```python
from typing import Any, TypeAlias
from collections.abc import Callable

# Type aliases for complex types
UserDict: TypeAlias = dict[str, Any]
ValidationFunc: TypeAlias = Callable[[Any], bool]

# Using type aliases
def validate_user_data(data: UserDict, validators: list[ValidationFunc]) -> bool:
    """Validate user data with provided validators."""
    return all(validator(data) for validator in validators)
```

### Generic Types

```python
from typing import TypeVar, Generic

T = TypeVar("T")

class Repository(Generic[T]):
    """Generic repository for database operations."""

    def get(self, id: int) -> T | None:
        """Get entity by ID."""
        pass

    def get_all(self) -> list[T]:
        """Get all entities."""
        pass

# Usage
user_repo: Repository[User] = Repository()
product_repo: Repository[Product] = Repository()
```

## Documentation

### Docstring Format

Use Google-style docstrings:

```python
def create_order(
    user: User,
    items: list[OrderItem],
    *,
    apply_discount: bool = False,
) -> Order:
    """Create a new order for the user.

    Creates an order with the provided items and optionally applies
    available discounts. The order total is calculated based on current
    product prices.

    Args:
        user: User placing the order
        items: List of items to include in order
        apply_discount: Whether to apply user's available discounts

    Returns:
        Created Order instance with all items

    Raises:
        ValidationError: If items list is empty
        InsufficientStock: If any item is out of stock
        PaymentError: If payment processing fails

    Example:
        >>> user = User.objects.get(username="john")
        >>> items = [OrderItem(product=product, quantity=2)]
        >>> order = create_order(user, items, apply_discount=True)
    """
    pass
```

### Docstring Components

**Module Docstrings**:
```python
"""User authentication and authorization services.

This module provides services for user authentication including
login, logout, token generation, and permission checking.
"""
```

**Class Docstrings**:
```python
class UserService:
    """Service for user-related business logic.

    Handles user creation, updates, and complex user operations
    that involve multiple models or external services.

    Attributes:
        email_service: Service for sending emails
        cache_timeout: Cache timeout in seconds
    """

    def __init__(self, email_service: EmailService) -> None:
        """Initialize UserService.

        Args:
            email_service: Email service instance
        """
        self.email_service = email_service
        self.cache_timeout = 300
```

**Property Docstrings**:
```python
class User(models.Model):
    @property
    def full_name(self) -> str:
        """Return user's full name."""
        return f"{self.first_name} {self.last_name}".strip()
```

### Comments

Use comments to explain "why", not "what":

```python
# Good: Explains reasoning
# We use a longer timeout for this endpoint because
# the third-party API is known to be slow during peak hours
timeout = 60

# We cache for 5 minutes because user preferences rarely change
# and this reduces database load by 80%
cache.set(key, value, timeout=300)

# Bad: States the obvious
# Set timeout to 60
timeout = 60

# Set cache timeout to 300
cache.set(key, value, timeout=300)
```

**TODO Comments**:
```python
# TODO(username): Add pagination support (#123)
# FIXME(username): Handle edge case when user is None (#456)
# NOTE: This is a temporary workaround until API v2 is ready
# HACK: Quick fix for production issue, needs proper solution
```

## Django Specific

### Model Definition

```python
from django.db import models
from core.models import TimeStampedModel

class Product(TimeStampedModel):
    """Product model representing items in catalog."""

    name = models.CharField(max_length=255, help_text="Product name")
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Product"
        verbose_name_plural = "Products"
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["is_active", "-created_at"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(price__gt=0),
                name="price_positive"
            )
        ]

    def __str__(self) -> str:
        """Return string representation."""
        return self.name

    def __repr__(self) -> str:
        """Return technical representation."""
        return f"<Product: {self.name} (${self.price})>"
```

### Serializer Definition

```python
from rest_framework import serializers
from apps.products.models import Product

class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model."""

    full_price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "price",
            "full_price",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_full_price(self, obj: Product) -> str:
        """Return formatted price with currency."""
        return f"${obj.price:.2f}"

    def validate_price(self, value: float) -> float:
        """Validate that price is positive."""
        if value <= 0:
            raise serializers.ValidationError("Price must be positive")
        return value

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validate entire object."""
        # Cross-field validation
        return attrs
```

### ViewSet Definition

```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet for product CRUD operations."""

    queryset = Product.objects.select_related("category").prefetch_related("tags")
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["is_active", "category"]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "price", "created_at"]

    def get_queryset(self):
        """Return queryset filtered by user access."""
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)
        return queryset

    @action(detail=False, methods=["get"])
    def featured(self, request) -> Response:
        """Get featured products."""
        products = self.get_queryset().filter(is_featured=True)[:10]
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
```

### Service Layer

```python
from typing import Any
from django.db import transaction
from apps.products.models import Product
from common.exceptions import ValidationError

class ProductService:
    """Service for product-related business logic."""

    @staticmethod
    @transaction.atomic
    def create_product(data: dict[str, Any]) -> Product:
        """Create a new product with validation.

        Args:
            data: Product data dictionary

        Returns:
            Created Product instance

        Raises:
            ValidationError: If data is invalid
        """
        # Validate business rules
        if data.get("price", 0) <= 0:
            raise ValidationError("Price must be positive")

        # Create product
        product = Product.objects.create(**data)

        # Trigger side effects
        notify_product_created(product)

        return product

    @staticmethod
    def get_active_products() -> list[Product]:
        """Get all active products ordered by name."""
        return list(
            Product.objects.filter(is_active=True)
            .select_related("category")
            .order_by("name")
        )
```

## Error Handling

### Exception Handling

```python
from django.core.exceptions import ValidationError
from django.db import IntegrityError
import logging

logger = logging.getLogger(__name__)

def create_user(username: str, email: str) -> User:
    """Create user with proper error handling."""
    try:
        user = User.objects.create(username=username, email=email)
        return user

    except IntegrityError as e:
        logger.warning(f"User creation failed for {username}: {e}")
        raise ValidationError(f"Username or email already exists")

    except Exception as e:
        logger.error(f"Unexpected error creating user {username}: {e}")
        raise
```

### Custom Exceptions

```python
# common/exceptions.py
class BaseAPIException(Exception):
    """Base exception for API errors."""

    def __init__(self, message: str, code: str | None = None) -> None:
        self.message = message
        self.code = code
        super().__init__(message)

class ValidationError(BaseAPIException):
    """Raised when validation fails."""
    pass

class AuthenticationError(BaseAPIException):
    """Raised when authentication fails."""
    pass

# Usage
from common.exceptions import ValidationError

def validate_age(age: int) -> None:
    """Validate that age is reasonable."""
    if age < 0 or age > 150:
        raise ValidationError("Age must be between 0 and 150", code="invalid_age")
```

## Security Guidelines

### Input Validation

```python
from django.core.validators import EmailValidator
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    """User serializer with validation."""

    email = serializers.EmailField(validators=[EmailValidator()])

    def validate_username(self, value: str) -> str:
        """Validate username format."""
        if len(value) < 3:
            raise serializers.ValidationError("Username too short")
        if not value.isalnum():
            raise serializers.ValidationError("Username must be alphanumeric")
        return value.lower()
```

### SQL Injection Prevention

```python
# Good: Use Django ORM (safe from SQL injection)
users = User.objects.filter(username=user_input)

# Good: Use parameterized queries if raw SQL needed
from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("SELECT * FROM users WHERE username = %s", [user_input])

# Bad: NEVER concatenate user input into SQL
# cursor.execute(f"SELECT * FROM users WHERE username = '{user_input}'")
```

### Password Handling

```python
from django.contrib.auth.hashers import make_password, check_password

# Good: Always hash passwords
user.password = make_password(plain_password)

# Good: Use built-in authentication
from django.contrib.auth import authenticate

user = authenticate(username=username, password=password)

# Bad: NEVER store plain text passwords
# user.password = plain_password  # WRONG!
```

### Sensitive Data in Logs

```python
import logging

logger = logging.getLogger(__name__)

# Good: Don't log sensitive data
logger.info(f"User {user.username} logged in")

# Bad: Don't log passwords, tokens, or PII
# logger.info(f"Login attempt: {username} / {password}")  # WRONG!
# logger.info(f"User email: {user.email}")  # Avoid logging PII
```

## Performance Considerations

### Database Queries

```python
# Good: Use select_related for ForeignKey
products = Product.objects.select_related("category").all()

# Good: Use prefetch_related for ManyToMany
products = Product.objects.prefetch_related("tags").all()

# Good: Use only() to fetch specific fields
products = Product.objects.only("id", "name", "price")

# Bad: N+1 query problem
products = Product.objects.all()
for product in products:
    category = product.category  # Each iteration = 1 query
```

### Caching

```python
from django.core.cache import cache

def get_user_preferences(user_id: int) -> dict[str, Any]:
    """Get user preferences with caching."""
    cache_key = f"user_prefs:{user_id}"

    # Try cache first
    prefs = cache.get(cache_key)
    if prefs is not None:
        return prefs

    # Cache miss - fetch from database
    prefs = UserPreference.objects.filter(user_id=user_id).values()

    # Cache for 5 minutes
    cache.set(cache_key, prefs, timeout=300)

    return prefs
```

### Bulk Operations

```python
# Good: Bulk create
users = [User(username=f"user{i}") for i in range(1000)]
User.objects.bulk_create(users)

# Good: Bulk update
User.objects.filter(is_active=False).update(deactivated_at=now())

# Bad: Loop with individual saves
for i in range(1000):
    User.objects.create(username=f"user{i}")  # 1000 queries!
```

## Additional Resources

- [PEP 8 - Python Style Guide](https://pep.python.org/pep-0008/)
- [PEP 257 - Docstring Conventions](https://pep.python.org/pep-0257/)
- [Django Coding Style](https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/coding-style/)
- [Black Documentation](https://black.readthedocs.io/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [MyPy Documentation](https://mypy.readthedocs.io/)
