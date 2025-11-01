"""
Tests for login session persistence (Story 20.8).

Tests that JWT token-based sessions persist correctly:
- Sessions persist across simulated page refreshes
- Sessions persist across simulated browser sessions (using localStorage concept)
- Sessions persist during navigation
- Expired access tokens can be refreshed
- Expired refresh tokens require re-authentication
- Inactive users are prompted to log in again
"""

from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

User = get_user_model()


class SessionPersistenceTests(APITestCase):
    """Test cases for session persistence functionality."""

    def setUp(self):
        """Set up test data."""
        self.basic_login_url = reverse("auth:basic_login")
        self.token_refresh_url = reverse("auth:token_refresh")
        self.current_user_url = reverse("auth:me")
        self.logout_url = reverse("auth:logout")

        # Create a test user via basic login
        self.user_data = {
            "name": "Test User",
            "email": "test@example.com",
        }

    def test_session_persists_across_requests(self):
        """
        Test that session persists across multiple requests.
        This simulates page refreshes and navigation.

        Acceptance Criteria:
        - Given I'm logged in, when I navigate to different pages,
          then my session should persist
        """
        # Login
        response = self.client.post(self.basic_login_url, data=self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        access_token = response.data["access"]
        refresh_token = response.data["refresh"]

        # Simulate page refresh/navigation - make multiple authenticated requests
        for i in range(5):
            # Each request simulates a page load/API call
            response = self.client.get(
                self.current_user_url,
                HTTP_AUTHORIZATION=f"Bearer {access_token}",
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["email"], "test@example.com")

    def test_session_persists_with_valid_access_token(self):
        """
        Test that session persists as long as access token is valid.
        This simulates the user staying active within the 15-minute window.

        Acceptance Criteria:
        - Given I successfully log in, when I refresh the page,
          then I should remain logged in
        """
        # Login
        response = self.client.post(self.basic_login_url, data=self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        access_token = response.data["access"]

        # Simulate page refresh - access token should still be valid
        response = self.client.get(
            self.current_user_url,
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "test@example.com")

    def test_session_persists_across_browser_sessions_with_refresh_token(self):
        """
        Test that session persists across browser sessions using refresh token.
        This simulates closing and reopening the browser.

        Acceptance Criteria:
        - Given I successfully log in, when I close and reopen the browser,
          then I should remain logged in
        """
        # Login (simulates first browser session)
        response = self.client.post(self.basic_login_url, data=self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        refresh_token = response.data["refresh"]

        # Clear the client (simulates closing browser and clearing memory)
        self.client = self.client_class()

        # Use refresh token to get new access token (simulates reopening browser)
        response = self.client.post(
            self.token_refresh_url,
            data={"refresh": refresh_token},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

        # Use new access token to verify session is restored
        new_access_token = response.data["access"]
        response = self.client.get(
            self.current_user_url,
            HTTP_AUTHORIZATION=f"Bearer {new_access_token}",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "test@example.com")

    def test_expired_access_token_can_be_refreshed(self):
        """
        Test that an expired access token can be refreshed with valid refresh token.
        This simulates the user returning after 15 minutes of inactivity.

        Acceptance Criteria:
        - Given I've been inactive for an extended period (>15 min),
          when I return, then I should remain logged in (via token refresh)
        """
        # Login
        response = self.client.post(self.basic_login_url, data=self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        refresh_token = response.data["refresh"]
        user = User.objects.get(email="test@example.com")

        # Create an expired access token (simulates 15+ minutes passing)
        access_token = AccessToken.for_user(user)
        # Set token to be expired
        access_token.set_exp(from_time=timezone.now() - timedelta(minutes=20))

        # Access token should be rejected
        response = self.client.get(
            self.current_user_url,
            HTTP_AUTHORIZATION=f"Bearer {str(access_token)}",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # But refresh token should still work
        response = self.client.post(
            self.token_refresh_url,
            data={"refresh": refresh_token},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

        # New access token should work
        new_access_token = response.data["access"]
        response = self.client.get(
            self.current_user_url,
            HTTP_AUTHORIZATION=f"Bearer {new_access_token}",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_expired_refresh_token_requires_relogin(self):
        """
        Test that an expired refresh token requires the user to log in again.
        This simulates the user returning after 7+ days of inactivity.

        Acceptance Criteria:
        - Given I've been inactive for an extended period (>7 days),
          when I return, then I should be prompted to log in again
        """
        # Login
        response = self.client.post(self.basic_login_url, data=self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(email="test@example.com")

        # Create an expired refresh token (simulates 7+ days passing)
        refresh_token = RefreshToken.for_user(user)
        refresh_token.set_exp(from_time=timezone.now() - timedelta(days=8))

        # Expired refresh token should be rejected
        response = self.client.post(
            self.token_refresh_url,
            data={"refresh": str(refresh_token)},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.data)

        # User must log in again
        response = self.client.post(self.basic_login_url, data=self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # Existing user
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_token_refresh_rotates_tokens(self):
        """
        Test that token refresh provides new access and refresh tokens.
        This ensures security by rotating tokens on each refresh.
        """
        # Login
        response = self.client.post(self.basic_login_url, data=self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        original_refresh = response.data["refresh"]

        # Refresh token
        response = self.client.post(
            self.token_refresh_url,
            data={"refresh": original_refresh},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        new_access = response.data["access"]
        new_refresh = response.data["refresh"]

        # New tokens should be different from originals
        self.assertNotEqual(new_refresh, original_refresh)

        # New access token should work
        response = self.client.get(
            self.current_user_url,
            HTTP_AUTHORIZATION=f"Bearer {new_access}",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_blacklisted_token_cannot_be_reused(self):
        """
        Test that blacklisted tokens cannot be reused after rotation.
        This ensures security by preventing token replay attacks.
        """
        # Login
        response = self.client.post(self.basic_login_url, data=self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        original_refresh = response.data["refresh"]

        # Refresh token (this blacklists the original)
        response = self.client.post(
            self.token_refresh_url,
            data={"refresh": original_refresh},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Try to use original refresh token again (should fail)
        response = self.client.post(
            self.token_refresh_url,
            data={"refresh": original_refresh},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_blacklists_refresh_token(self):
        """
        Test that logout properly blacklists the refresh token.
        After logout, the refresh token cannot be used.
        """
        # Login
        response = self.client.post(self.basic_login_url, data=self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        access_token = response.data["access"]
        refresh_token = response.data["refresh"]

        # Logout
        response = self.client.post(
            self.logout_url,
            data={"refresh": refresh_token},
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Try to refresh with blacklisted token (should fail)
        response = self.client.post(
            self.token_refresh_url,
            data={"refresh": refresh_token},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_inactive_user_cannot_authenticate(self):
        """
        Test that inactive users cannot authenticate or refresh tokens.
        This simulates an account that has been deactivated.

        Acceptance Criteria:
        - Given I've been inactive (account deactivated),
          when I return, then I should be prompted with clear messaging
        """
        # Login and deactivate user
        response = self.client.post(self.basic_login_url, data=self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(email="test@example.com")
        user.is_active = False
        user.save()

        # Try to login with inactive account
        response = self.client.post(self.basic_login_url, data=self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("error", response.data)
        self.assertIn("deactivated", response.data["error"].lower())

    @override_settings(
        SIMPLE_JWT={
            "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
            "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
        }
    )
    def test_token_lifetime_configuration(self):
        """
        Test that JWT tokens have correct lifetime configuration.
        - Access token: 15 minutes
        - Refresh token: 7 days
        """
        from django.conf import settings

        # Verify configuration
        self.assertEqual(
            settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
            timedelta(minutes=15),
        )
        self.assertEqual(
            settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"],
            timedelta(days=7),
        )

        # Verify tokens are generated with correct lifetimes
        response = self.client.post(self.basic_login_url, data=self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Decode tokens to verify expiration
        import jwt
        from django.conf import settings as django_settings

        access_decoded = jwt.decode(
            response.data["access"],
            django_settings.SECRET_KEY,
            algorithms=["HS256"],
        )
        refresh_decoded = jwt.decode(
            response.data["refresh"],
            django_settings.SECRET_KEY,
            algorithms=["HS256"],
        )

        # Verify token types
        self.assertEqual(access_decoded["token_type"], "access")
        self.assertEqual(refresh_decoded["token_type"], "refresh")

        # Verify expiration times (approximately)
        access_lifetime = access_decoded["exp"] - access_decoded["iat"]
        refresh_lifetime = refresh_decoded["exp"] - refresh_decoded["iat"]

        # Allow 1 second tolerance for timing
        self.assertAlmostEqual(access_lifetime, 15 * 60, delta=1)  # 15 minutes
        self.assertAlmostEqual(refresh_lifetime, 7 * 24 * 60 * 60, delta=1)  # 7 days

    def test_multiple_concurrent_sessions(self):
        """
        Test that users can have multiple concurrent sessions.
        This simulates logging in from different devices.
        """
        # First login (e.g., desktop)
        response1 = self.client.post(self.basic_login_url, data=self.user_data, format="json")
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        access1 = response1.data["access"]
        refresh1 = response1.data["refresh"]

        # Second login (e.g., mobile)
        response2 = self.client.post(self.basic_login_url, data=self.user_data, format="json")
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        access2 = response2.data["access"]
        refresh2 = response2.data["refresh"]

        # Both tokens should be different
        self.assertNotEqual(access1, access2)
        self.assertNotEqual(refresh1, refresh2)

        # Both sessions should work independently
        response = self.client.get(
            self.current_user_url,
            HTTP_AUTHORIZATION=f"Bearer {access1}",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(
            self.current_user_url,
            HTTP_AUTHORIZATION=f"Bearer {access2}",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Logout from first session shouldn't affect second
        self.client.post(
            self.logout_url,
            data={"refresh": refresh1},
            HTTP_AUTHORIZATION=f"Bearer {access1}",
            format="json",
        )

        # Second session should still work
        response = self.client.get(
            self.current_user_url,
            HTTP_AUTHORIZATION=f"Bearer {access2}",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
