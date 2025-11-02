"""
Pytest configuration and fixtures for integration tests.
Provides common test fixtures for API testing, authentication, and test data.
"""

import os
import sys
from typing import Any, Dict

import django
import pytest
import requests  # type: ignore[import-untyped]

# Setup Django before importing models
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.testing")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))
django.setup()

from django.contrib.auth import get_user_model  # noqa: E402

User = get_user_model()

# Base API URL for tests
API_BASE_URL = os.getenv("TEST_API_BASE_URL", "http://backend:8000/api/v1")


@pytest.fixture
def api_base_url() -> str:
    """Provide base API URL for tests."""
    return API_BASE_URL


@pytest.fixture
def api_client() -> requests.Session:
    """
    Provide HTTP client for API testing.

    Returns:
        requests.Session configured for API testing
    """
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture
def test_user(django_db_blocker) -> Dict[str, Any]:
    """
    Create a test user for authentication tests.

    Returns:
        Dictionary with user data including credentials
    """
    with django_db_blocker.unblock():
        # Clean up any existing test user
        User.objects.filter(email="testuser@example.com").delete()

        user = User.objects.create_user(
            email="testuser@example.com",
            password="TestPass123!",
            first_name="Test",
            last_name="User",
        )

        return {
            "id": user.id,
            "email": user.email,
            "password": "TestPass123!",
            "first_name": user.first_name,
            "last_name": user.last_name,
            "user_obj": user,
        }


@pytest.fixture
def authenticated_client(
    api_client: requests.Session, test_user: Dict[str, Any], api_base_url: str
) -> requests.Session:
    """
    Provide authenticated HTTP client.

    Args:
        api_client: Base API client session
        test_user: Test user fixture
        api_base_url: Base API URL

    Returns:
        Authenticated requests.Session
    """
    # Login to get authentication token
    login_url = f"{api_base_url}/auth/login/"
    response = api_client.post(
        login_url,
        json={"email": test_user["email"], "password": test_user["password"]},
    )

    if response.status_code == 200:
        token = response.json().get("token")
        if token:
            api_client.headers.update({"Authorization": f"Token {token}"})

    return api_client


@pytest.fixture
def assessment_data() -> Dict[str, Any]:
    """
    Provide valid assessment data for testing.

    Returns:
        Dictionary with valid assessment data
    """
    return {
        "sport": "soccer",
        "age": 25,
        "experience_level": "intermediate",
        "training_days": "4-5",
        "injuries": "no",
        "equipment": "basic_equipment",
    }


@pytest.fixture(autouse=True)
def cleanup_assessments(django_db_blocker):
    """
    Clean up assessments after each test to ensure test isolation.

    This fixture runs automatically after each test.
    """
    yield
    # Cleanup after test
    with django_db_blocker.unblock():
        from apps.assessments.models import Assessment  # noqa: E402

        Assessment.objects.all().delete()
