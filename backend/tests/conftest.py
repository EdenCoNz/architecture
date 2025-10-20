"""
Pytest configuration and fixtures for backend tests.

This module sets up the Django test environment and provides common fixtures
for testing including API clients, users, and database setup.
"""

import os
import sys
from pathlib import Path
from typing import Any

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

# Add src directory to Python path for proper module resolution
backend_dir = Path(__file__).resolve().parent.parent
src_dir = backend_dir / "src"
sys.path.insert(0, str(src_dir))

# Set environment variables for test configuration before Django setup
# Note: pytest-django will handle django.setup() automatically
os.environ.setdefault("DEBUG", "True")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings.test")

User = get_user_model()


# ============================================================================
# Database Fixtures
# ============================================================================


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup: Any, django_db_blocker: Any) -> None:
    """
    Configure the test database.

    This fixture is automatically used by pytest-django to set up the
    test database before any tests run. It ensures migrations are applied.

    Args:
        django_db_setup: pytest-django's database setup fixture
        django_db_blocker: pytest-django's database blocker fixture
    """
    from django.core.management import call_command

    with django_db_blocker.unblock():
        call_command("migrate", "--noinput")


@pytest.fixture
def db_cleanup(db: Any) -> None:
    """
    Clean up database after each test.

    This fixture ensures database is in a clean state between tests.

    Args:
        db: pytest-django database fixture
    """
    yield
    # Cleanup happens automatically with pytest-django's transaction rollback


# ============================================================================
# API Client Fixtures
# ============================================================================


@pytest.fixture
def api_client() -> APIClient:
    """
    Provide an unauthenticated API client for testing REST endpoints.

    Returns:
        APIClient: Django REST Framework test client
    """
    return APIClient()


@pytest.fixture
def user(db: Any) -> Any:
    """
    Create a regular test user.

    Args:
        db: pytest-django database fixture

    Returns:
        User: Test user instance
    """
    return User.objects.create_user(
        username="testuser", email="test@example.com", password="testpass123"
    )


@pytest.fixture
def admin_user(db: Any) -> Any:
    """
    Create an admin test user.

    Args:
        db: pytest-django database fixture

    Returns:
        User: Admin user instance
    """
    return User.objects.create_superuser(
        username="admin", email="admin@example.com", password="adminpass123"
    )


@pytest.fixture
def staff_user(db: Any) -> Any:
    """
    Create a staff test user.

    Args:
        db: pytest-django database fixture

    Returns:
        User: Staff user instance
    """
    user = User.objects.create_user(
        username="staff", email="staff@example.com", password="staffpass123"
    )
    user.is_staff = True
    user.save()
    return user


@pytest.fixture
def authenticated_client(api_client: APIClient, user: Any) -> APIClient:
    """
    Provide an authenticated API client with a regular user.

    Args:
        api_client: API client fixture
        user: User fixture

    Returns:
        APIClient: Authenticated API client
    """
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def admin_client(api_client: APIClient, admin_user: Any) -> APIClient:
    """
    Provide an authenticated API client with an admin user.

    Args:
        api_client: API client fixture
        admin_user: Admin user fixture

    Returns:
        APIClient: Authenticated admin API client
    """
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def staff_client(api_client: APIClient, staff_user: Any) -> APIClient:
    """
    Provide an authenticated API client with a staff user.

    Args:
        api_client: API client fixture
        staff_user: Staff user fixture

    Returns:
        APIClient: Authenticated staff API client
    """
    api_client.force_authenticate(user=staff_user)
    return api_client


# ============================================================================
# Factory Fixtures
# ============================================================================


@pytest.fixture
def user_factory() -> type:
    """
    Provide UserFactory for creating test users.

    Returns:
        type: UserFactory class
    """
    from tests.fixtures.factories import UserFactory

    return UserFactory


@pytest.fixture
def admin_factory() -> type:
    """
    Provide AdminUserFactory for creating admin users.

    Returns:
        type: AdminUserFactory class
    """
    from tests.fixtures.factories import AdminUserFactory

    return AdminUserFactory


# ============================================================================
# Test Data Fixtures
# ============================================================================


@pytest.fixture
def sample_users(db: Any) -> list[Any]:
    """
    Create multiple test users for list/pagination testing.

    Args:
        db: pytest-django database fixture

    Returns:
        list: List of User instances
    """
    users = []
    for i in range(5):
        user = User.objects.create_user(
            username=f"user{i}", email=f"user{i}@example.com", password="testpass123"
        )
        users.append(user)
    return users
