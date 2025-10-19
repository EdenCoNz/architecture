# Contributing to Backend API

Thank you for your interest in contributing to the Backend API project! This document provides guidelines and best practices for contributing to the codebase.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Conventions](#coding-conventions)
- [Testing Requirements](#testing-requirements)
- [Pull Request Process](#pull-request-process)
- [Code Review Guidelines](#code-review-guidelines)

## Getting Started

### Prerequisites

Before you start contributing, ensure you have:

- Python 3.12 or higher
- Poetry for dependency management
- PostgreSQL (optional for local development; SQLite works for development)
- Git for version control
- A code editor with EditorConfig support (VS Code or PyCharm recommended)

### Initial Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd backend
   ```

2. Install dependencies:
   ```bash
   make install
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your local configuration
   ```

4. Run migrations:
   ```bash
   make migrate
   ```

5. Verify setup by running tests:
   ```bash
   make test
   ```

6. Start the development server:
   ```bash
   make dev
   ```

For detailed setup instructions, see [docs/QUICK_START.md](docs/QUICK_START.md).

## Development Workflow

### 1. Create a Feature Branch

Always create a new branch for your work:

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

Branch naming conventions:
- `feature/` - New features
- `fix/` - Bug fixes
- `refactor/` - Code refactoring
- `docs/` - Documentation updates
- `test/` - Test additions or improvements

### 2. Follow Test-Driven Development (TDD)

We follow the Red-Green-Refactor cycle:

1. **Red**: Write a failing test
   ```bash
   make test-watch  # Start watch mode
   ```

2. **Green**: Write minimal code to make it pass

3. **Refactor**: Improve code while keeping tests green

### 3. Make Your Changes

- Follow coding conventions (see [CODING_CONVENTIONS.md](CODING_CONVENTIONS.md))
- Write clear, descriptive commit messages
- Keep commits focused and atomic
- Add tests for all new functionality
- Update documentation as needed

### 4. Run Quality Checks

Before committing, ensure all quality checks pass:

```bash
# Format code
make format

# Run linting
make lint

# Run type checking
make type-check

# Run tests
make test
```

Or run all checks at once:
```bash
make format && make lint && make type-check && make test
```

### 5. Commit Your Changes

Write clear, descriptive commit messages:

```bash
git add .
git commit -m "Add user authentication feature

- Implement JWT token generation
- Add login and logout endpoints
- Create user registration flow
- Add comprehensive test coverage"
```

Commit message guidelines:
- Use imperative mood ("Add feature" not "Added feature")
- First line should be 50 characters or less
- Add detailed description after blank line if needed
- Reference issue numbers when applicable

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub following the PR template.

## Coding Conventions

### Python Code Style

We use automated tools to enforce code style:

- **Black**: Code formatting (line length: 100 characters)
- **Ruff**: Linting and import sorting
- **MyPy**: Type checking

Run these tools with:
```bash
make format     # Auto-format with Black
make lint       # Check with Ruff
make type-check # Type checking with MyPy
```

### Naming Conventions

**Files and Directories**:
- Use lowercase with underscores: `user_service.py`, `test_authentication.py`
- Test files: `test_*.py` or `*_test.py`
- Migration files: Django auto-generated naming

**Python Code**:
- Classes: `PascalCase` (e.g., `UserService`, `ProductRepository`)
- Functions/methods: `snake_case` (e.g., `get_user`, `create_order`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRIES`, `DEFAULT_TIMEOUT`)
- Private methods: Prefix with underscore (e.g., `_internal_helper`)
- Module-level variables: `snake_case`

**Django Specific**:
- Models: `PascalCase` singular (e.g., `User`, `Product`, not `Users`)
- Model fields: `snake_case` (e.g., `first_name`, `created_at`)
- Serializers: Model name + `Serializer` (e.g., `UserSerializer`)
- ViewSets: Model name + `ViewSet` (e.g., `UserViewSet`)
- URLs: `kebab-case` (e.g., `/api/user-profiles/`, `/api/order-items/`)

### Code Organization

**Import Order** (enforced by Ruff):
1. Standard library imports
2. Third-party imports
3. Django imports
4. Local application imports

```python
import os
from typing import Any

import requests
from rest_framework import status

from django.contrib.auth import get_user_model
from django.db import models

from apps.users.models import User
from core.services.auth import AuthenticationService
```

**Module Structure**:
```python
"""Module docstring explaining purpose."""

# Imports (grouped as above)

# Constants
MAX_RETRY_ATTEMPTS = 3

# Type definitions
UserDict = dict[str, Any]

# Classes and functions
class MyClass:
    """Class docstring."""
    pass

def my_function() -> None:
    """Function docstring."""
    pass
```

### Type Hints

All functions must have type hints (enforced by MyPy):

```python
def get_user_by_email(email: str) -> User | None:
    """Retrieve user by email address.

    Args:
        email: User's email address

    Returns:
        User instance if found, None otherwise
    """
    try:
        return User.objects.get(email=email)
    except User.DoesNotExist:
        return None
```

Use modern Python 3.12+ type hint syntax:
- `list[str]` instead of `List[str]`
- `dict[str, int]` instead of `Dict[str, int]`
- `str | None` instead of `Optional[str]`

### Documentation Standards

**Docstrings**:
- Use triple double-quotes: `"""Docstring"""`
- First line: Short description (imperative mood)
- Add blank line before extended description
- Document all public functions, classes, and modules

```python
def create_user(username: str, email: str, password: str) -> User:
    """Create a new user account.

    Creates a user with the provided credentials and sends a welcome email.
    The password is automatically hashed before storage.

    Args:
        username: Unique username for the account
        email: User's email address
        password: Plain text password (will be hashed)

    Returns:
        Created User instance

    Raises:
        ValidationError: If username or email already exists
        ValueError: If password is too weak
    """
    pass
```

**Comments**:
- Use comments to explain "why", not "what"
- Keep comments up-to-date with code changes
- Avoid obvious comments
- Use TODO comments sparingly with issue references

```python
# Good: Explains why
# We use a 5-minute cache because user preferences rarely change
# and this reduces database load by 80%
cache_timeout = 300

# Bad: States the obvious
# Set cache timeout to 300
cache_timeout = 300
```

For detailed coding conventions, see [CODING_CONVENTIONS.md](CODING_CONVENTIONS.md).

## Testing Requirements

### Test Coverage

- **Minimum coverage**: 80% overall
- **Critical business logic**: 100% coverage
- **New features**: Must include tests

### Test Organization

Tests should be organized by type:

```
tests/
├── unit/              # Fast, isolated tests
├── integration/       # Component interaction tests
├── e2e/              # End-to-end workflow tests
└── fixtures/         # Test data factories
```

### Writing Tests

**Test Structure** (AAA Pattern):
```python
import pytest
from apps.users.models import User

@pytest.mark.unit
class TestUserModel:
    """Unit tests for User model."""

    def test_user_full_name(self, db) -> None:
        """Test that full name is correctly formatted."""
        # Arrange: Set up test data
        user = User.objects.create(
            username="testuser",
            first_name="John",
            last_name="Doe"
        )

        # Act: Perform the action
        full_name = user.get_full_name()

        # Assert: Verify the result
        assert full_name == "John Doe"
```

**Test Naming**:
- Test files: `test_*.py`
- Test classes: `Test*` (e.g., `TestUserService`)
- Test functions: `test_*` (e.g., `test_user_creation`)
- Use descriptive names that explain what is being tested

**Test Markers**:
Use pytest markers to categorize tests:
```python
@pytest.mark.unit          # Fast, isolated tests
@pytest.mark.integration   # Database/API tests
@pytest.mark.slow          # Tests taking >1 second
@pytest.mark.smoke         # Critical functionality
```

### Running Tests

```bash
# Run all tests
make test

# Run specific test type
make test-unit
make test-integration

# Run tests in watch mode (TDD)
make test-watch

# Run specific test file
PYTHONPATH=src poetry run pytest tests/unit/test_user_service.py -v
```

For detailed testing documentation, see [docs/TESTING.md](docs/TESTING.md).

## Pull Request Process

### Before Submitting

1. **Ensure all tests pass**:
   ```bash
   make test
   ```

2. **Run quality checks**:
   ```bash
   make format
   make lint
   make type-check
   ```

3. **Update documentation** if needed:
   - Update README.md for user-facing changes
   - Update relevant docs/ files
   - Add/update docstrings
   - Update CHANGELOG.md (if applicable)

4. **Rebase on latest main**:
   ```bash
   git fetch origin
   git rebase origin/main
   ```

### Pull Request Template

When creating a PR, include:

```markdown
## Description
Brief description of changes and motivation

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] All tests pass locally
- [ ] Added tests for new functionality
- [ ] Coverage remains above 80%

## Checklist
- [ ] Code follows project conventions
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No linting/formatting errors
- [ ] Type checking passes
```

### CI/CD Checks

All PRs must pass these automated checks:

✅ **Lint Check** (Ruff)
✅ **Format Check** (Black)
✅ **Type Check** (MyPy)
✅ **Test Suite** (≥80% coverage)
✅ **Build Verification**

If any check fails, the PR cannot be merged. See [docs/CICD.md](docs/CICD.md) for troubleshooting.

## Code Review Guidelines

### For Authors

- Keep PRs focused and small (prefer multiple small PRs over one large PR)
- Respond promptly to review comments
- Be open to feedback and suggestions
- Update PR based on feedback
- Use "Request re-review" when ready

### For Reviewers

**What to Review**:

1. **Correctness**:
   - Does the code do what it's supposed to?
   - Are there any logical errors?
   - Are edge cases handled?

2. **Code Quality**:
   - Is the code readable and maintainable?
   - Are functions/classes appropriately sized?
   - Is there proper error handling?
   - Are there any code smells?

3. **Security**:
   - Are there any security vulnerabilities?
   - Is user input properly validated?
   - Are there any injection risks?
   - Is authentication/authorization correct?

4. **Performance**:
   - Are there any obvious performance issues?
   - Are database queries optimized?
   - Is caching used appropriately?

5. **Testing**:
   - Are there sufficient tests?
   - Do tests cover edge cases?
   - Is test coverage adequate?

6. **Documentation**:
   - Are docstrings present and clear?
   - Is documentation updated?
   - Are comments helpful?

**Review Etiquette**:
- Be constructive and respectful
- Explain the "why" behind suggestions
- Distinguish between required changes and suggestions
- Praise good solutions
- Use questions to understand intent
- Approve when satisfied, even if minor suggestions remain

## Common Patterns and Best Practices

### Django Models

```python
from django.db import models
from core.models import TimeStampedModel

class Product(TimeStampedModel):
    """Product model representing items in inventory."""

    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["is_active", "-created_at"]),
        ]

    def __str__(self) -> str:
        return self.name
```

### DRF Serializers

```python
from rest_framework import serializers
from apps.products.models import Product

class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model."""

    class Meta:
        model = Product
        fields = ["id", "name", "price", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_price(self, value: float) -> float:
        """Validate that price is positive."""
        if value <= 0:
            raise serializers.ValidationError("Price must be positive")
        return value
```

### Service Layer

```python
from typing import Any
from django.db import transaction
from apps.products.models import Product

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
        product = Product.objects.create(**data)
        # Additional business logic here
        return product
```

### ViewSets

```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet for product operations."""

    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    @action(detail=False, methods=["get"])
    def active(self, request) -> Response:
        """Get list of active products."""
        products = self.queryset.filter(is_active=True)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
```

## Getting Help

- **Documentation**: Check [backend/README.md](README.md) and [backend/docs/](docs/)
- **Questions**: Open a GitHub Discussion
- **Issues**: Create a GitHub Issue with detailed description
- **Code Review**: Request review in your PR

## Additional Resources

- [Django Documentation](https://docs.djangoproject.com/en/5.1/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [pytest Documentation](https://docs.pytest.org/)
- [Project Architecture](ARCHITECTURE.md)
- [Testing Guide](docs/TESTING.md)
- [Development Setup](docs/DEVELOPMENT.md)
- [CI/CD Pipeline](docs/CICD.md)

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.
