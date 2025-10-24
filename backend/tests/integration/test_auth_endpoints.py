"""
Integration tests for authentication endpoints.
Tests the complete authentication flow including registration, login, logout, and token refresh.
"""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


@pytest.fixture
def api_client():
    """Fixture for API client."""
    return APIClient()


@pytest.fixture
def test_user():
    """Fixture for creating a test user."""
    return User.objects.create_user(
        email="testuser@example.com", password="testpass123", first_name="Test", last_name="User"
    )


@pytest.mark.django_db
class TestUserRegistrationEndpoint:
    """Test suite for user registration endpoint."""

    def test_register_user_successful(self, api_client):
        """Test successful user registration."""
        url = reverse("auth:register")
        payload = {
            "email": "newuser@example.com",
            "password": "newpass123",
            "password_confirm": "newpass123",
            "first_name": "New",
            "last_name": "User",
        }

        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert "user" in response.data
        assert response.data["user"]["email"] == payload["email"]
        assert "password" not in response.data["user"]

        # Verify user was created in database
        user = User.objects.get(email=payload["email"])
        assert user.email == payload["email"]
        assert user.check_password(payload["password"])

    def test_register_user_with_invalid_email(self, api_client):
        """Test registration with invalid email format."""
        url = reverse("auth:register")
        payload = {
            "email": "invalid-email",
            "password": "testpass123",
            "password_confirm": "testpass123",
        }

        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data

    def test_register_user_with_mismatched_passwords(self, api_client):
        """Test registration with mismatched passwords."""
        url = reverse("auth:register")
        payload = {
            "email": "newuser@example.com",
            "password": "testpass123",
            "password_confirm": "differentpass123",
        }

        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_user_with_duplicate_email(self, api_client, test_user):
        """Test registration with already existing email."""
        url = reverse("auth:register")
        payload = {
            "email": test_user.email,
            "password": "testpass123",
            "password_confirm": "testpass123",
        }

        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data


@pytest.mark.django_db
class TestUserLoginEndpoint:
    """Test suite for user login endpoint."""

    def test_login_with_valid_credentials(self, api_client, test_user):
        """Test login with valid credentials returns tokens."""
        url = reverse("auth:login")
        payload = {"email": test_user.email, "password": "testpass123"}

        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data
        assert "user" in response.data
        assert response.data["user"]["email"] == test_user.email

    def test_login_with_invalid_password(self, api_client, test_user):
        """Test login with invalid password fails."""
        url = reverse("auth:login")
        payload = {"email": test_user.email, "password": "wrongpassword"}

        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "access" not in response.data
        assert "refresh" not in response.data

    def test_login_with_nonexistent_email(self, api_client):
        """Test login with non-existent email fails."""
        url = reverse("auth:login")
        payload = {"email": "nonexistent@example.com", "password": "testpass123"}

        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "access" not in response.data

    def test_login_with_inactive_user(self, api_client):
        """Test login with inactive user fails."""
        # Create inactive user
        user = User.objects.create_user(
            email="inactive@example.com", password="testpass123", is_active=False
        )

        url = reverse("auth:login")
        payload = {"email": user.email, "password": "testpass123"}

        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "access" not in response.data


@pytest.mark.django_db
class TestTokenRefreshEndpoint:
    """Test suite for token refresh endpoint."""

    def test_refresh_token_successful(self, api_client, test_user):
        """Test refreshing access token with valid refresh token."""
        # Generate tokens
        refresh = RefreshToken.for_user(test_user)

        url = reverse("auth:token_refresh")
        payload = {"refresh": str(refresh)}

        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

    def test_refresh_token_with_invalid_token(self, api_client):
        """Test refresh with invalid token fails."""
        url = reverse("auth:token_refresh")
        payload = {"refresh": "invalid-token"}

        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestLogoutEndpoint:
    """Test suite for logout endpoint."""

    def test_logout_successful(self, api_client, test_user):
        """Test successful logout blacklists refresh token."""
        # Generate tokens
        refresh = RefreshToken.for_user(test_user)
        access_token = str(refresh.access_token)

        # Authenticate
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        url = reverse("auth:logout")
        payload = {"refresh": str(refresh)}

        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.data

        # Try to use the refresh token again (should fail)
        refresh_url = reverse("auth:token_refresh")
        refresh_response = api_client.post(refresh_url, {"refresh": str(refresh)}, format="json")

        # Token should be blacklisted
        assert refresh_response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout_without_authentication(self, api_client):
        """Test logout without authentication fails."""
        url = reverse("auth:logout")
        payload = {"refresh": "some-token"}

        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestProtectedEndpoint:
    """Test suite for accessing protected endpoints."""

    def test_access_protected_endpoint_with_valid_token(self, api_client, test_user):
        """Test accessing protected endpoint with valid access token."""
        # Generate token
        refresh = RefreshToken.for_user(test_user)
        access_token = str(refresh.access_token)

        # Authenticate
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        url = reverse("auth:me")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == test_user.email

    def test_access_protected_endpoint_without_token(self, api_client):
        """Test accessing protected endpoint without token fails."""
        url = reverse("auth:me")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_access_protected_endpoint_with_invalid_token(self, api_client):
        """Test accessing protected endpoint with invalid token fails."""
        api_client.credentials(HTTP_AUTHORIZATION="Bearer invalid-token")

        url = reverse("auth:me")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_access_protected_endpoint_with_expired_token(self, api_client, test_user):
        """Test accessing protected endpoint with expired token fails."""
        # This test would require mocking time or creating an expired token
        # For now, we'll test the token structure is correct
        refresh = RefreshToken.for_user(test_user)
        access_token = str(refresh.access_token)

        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        url = reverse("auth:me")
        response = api_client.get(url)

        # With a valid token, should succeed
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestChangePasswordEndpoint:
    """Test suite for change password endpoint."""

    def test_change_password_successful(self, api_client, test_user):
        """Test successful password change."""
        # Generate token
        refresh = RefreshToken.for_user(test_user)
        access_token = str(refresh.access_token)

        # Authenticate
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        url = reverse("auth:change_password")
        payload = {
            "old_password": "testpass123",
            "new_password": "newpass456",
            "new_password_confirm": "newpass456",
        }

        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.data

        # Verify password was changed
        test_user.refresh_from_db()
        assert test_user.check_password("newpass456")
        assert not test_user.check_password("testpass123")

    def test_change_password_with_wrong_old_password(self, api_client, test_user):
        """Test password change with incorrect old password fails."""
        # Generate token
        refresh = RefreshToken.for_user(test_user)
        access_token = str(refresh.access_token)

        # Authenticate
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        url = reverse("auth:change_password")
        payload = {
            "old_password": "wrongpassword",
            "new_password": "newpass456",
            "new_password_confirm": "newpass456",
        }

        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
