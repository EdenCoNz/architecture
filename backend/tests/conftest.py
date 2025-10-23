"""
Pytest configuration and fixtures.

This file contains shared fixtures and configuration for all tests.
Fixtures defined here are automatically available to all test modules.
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

# Import factories for use in fixtures
from tests.factories import AdminUserFactory, UserFactory

# Import test helpers
from tests.utils import APITestHelper, AuthenticationTestHelper

User = get_user_model()


# ==============================================================================
# API Client Fixtures
# ==============================================================================


@pytest.fixture
def api_client():
    """
    Provide a Django REST Framework API client for testing.

    Usage:
        def test_endpoint(api_client):
            response = api_client.get('/api/v1/users/')
            assert response.status_code == 200
    """
    return APIClient()


@pytest.fixture
def api_helper(api_client):
    """
    Provide an APITestHelper instance.

    Usage:
        def test_endpoint(api_helper):
            response = api_helper.get('/api/v1/users/')
            api_helper.assert_success(response)
    """
    return APITestHelper(api_client)


@pytest.fixture
def auth_helper(api_client):
    """
    Provide an AuthenticationTestHelper instance.

    Usage:
        def test_login(auth_helper):
            tokens = auth_helper.login('user@example.com', 'password')
            assert 'access' in tokens
    """
    return AuthenticationTestHelper(api_client)


# ==============================================================================
# User Fixtures
# ==============================================================================


@pytest.fixture
def user(db):
    """
    Create a test user using UserFactory.

    Usage:
        def test_user(user):
            assert user.is_active is True
    """
    return UserFactory()


@pytest.fixture
def admin_user(db):
    """
    Create a test admin user using AdminUserFactory.

    Usage:
        def test_admin(admin_user):
            assert admin_user.is_staff is True
    """
    return AdminUserFactory()


@pytest.fixture
def users(db):
    """
    Create multiple test users.

    Usage:
        def test_multiple_users(users):
            assert len(users) == 5
    """
    return UserFactory.create_batch(5)


# ==============================================================================
# Authenticated Client Fixtures
# ==============================================================================


@pytest.fixture
def authenticated_client(api_client, user):
    """
    Provide an authenticated API client using force_authenticate.

    This fixture uses Django's force_authenticate method which bypasses
    actual JWT token generation for faster tests.

    Usage:
        def test_protected_endpoint(authenticated_client):
            response = authenticated_client.get('/api/v1/auth/me/')
            assert response.status_code == 200
    """
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def authenticated_api_helper(api_client, user):
    """
    Provide an authenticated APITestHelper.

    Usage:
        def test_protected_endpoint(authenticated_api_helper):
            response = authenticated_api_helper.get('/api/v1/auth/me/')
            authenticated_api_helper.assert_success(response)
    """
    helper = APITestHelper(api_client)
    helper.authenticate(user)
    return helper


@pytest.fixture
def admin_client(api_client, admin_user):
    """
    Provide an API client authenticated as admin.

    Usage:
        def test_admin_endpoint(admin_client):
            response = admin_client.get('/api/v1/admin/users/')
            assert response.status_code == 200
    """
    api_client.force_authenticate(user=admin_user)
    return api_client


# ==============================================================================
# Database Fixtures
# ==============================================================================


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """
    Enable database access for all tests automatically.

    This is a convenience fixture that makes the database available
    without requiring @pytest.mark.django_db on every test.

    Note: Only use this if most of your tests need database access.
    For projects with many unit tests, it's better to explicitly mark
    tests that need the database.
    """
    pass


# ==============================================================================
# Test Data Cleanup Fixtures
# ==============================================================================


@pytest.fixture(autouse=True)
def reset_factory_sequences():
    """
    Reset factory sequences before each test for consistency.

    This ensures that factory-generated IDs and sequences start from
    the same point for each test, making test data more predictable.
    """
    from tests.factories import FixtureHelper

    FixtureHelper.reset_sequences()


# ==============================================================================
# Configuration and Settings Fixtures
# ==============================================================================


@pytest.fixture
def settings_with_debug(settings):
    """
    Provide settings with DEBUG=True for tests that need it.

    Usage:
        def test_debug_mode(settings_with_debug):
            assert settings_with_debug.DEBUG is True
    """
    settings.DEBUG = True
    return settings


# ==============================================================================
# Mock Fixtures (Examples)
# ==============================================================================


@pytest.fixture
def mock_external_api():
    """
    Example fixture for mocking external API calls.

    Usage:
        def test_with_mock_api(mock_external_api):
            mock_external_api.return_value = {'status': 'success'}
            # Test code that uses external API
    """
    from unittest.mock import Mock

    return Mock()
