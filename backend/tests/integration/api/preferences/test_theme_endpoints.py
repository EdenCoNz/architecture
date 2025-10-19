"""Integration tests for theme preference API endpoints."""

import pytest
from django.urls import reverse
from rest_framework import status

from apps.preferences.models import UserPreferences


@pytest.mark.django_db
@pytest.mark.integration
class TestThemePreferenceAPI:
    """Test suite for theme preference API endpoints."""

    def test_get_theme_preference_authenticated_user(self, authenticated_client, user):
        """Test getting theme preference for authenticated user."""
        # Create preferences for the user
        UserPreferences.objects.create(user=user, theme="dark")

        url = reverse("preferences:theme")
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["theme"] == "dark"
        assert "created_at" in response.data
        assert "updated_at" in response.data

    def test_get_theme_preference_unauthenticated_user(self, api_client):
        """Test that unauthenticated users cannot access theme preferences."""
        url = reverse("preferences:theme")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_theme_preference_creates_default_if_not_exists(
        self, authenticated_client, user
    ):
        """Test that GET creates default preferences if they don't exist."""
        # Ensure no preferences exist
        assert not UserPreferences.objects.filter(user=user).exists()

        url = reverse("preferences:theme")
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["theme"] == "auto"  # Default value

        # Verify preferences were created
        assert UserPreferences.objects.filter(user=user).exists()

    def test_update_theme_preference_to_light(self, authenticated_client, user):
        """Test updating theme preference to light mode."""
        UserPreferences.objects.create(user=user, theme="dark")

        url = reverse("preferences:theme")
        data = {"theme": "light"}
        response = authenticated_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["theme"] == "light"

        # Verify database was updated
        user.refresh_from_db()
        assert user.preferences.theme == "light"

    def test_update_theme_preference_to_dark(self, authenticated_client, user):
        """Test updating theme preference to dark mode."""
        UserPreferences.objects.create(user=user, theme="light")

        url = reverse("preferences:theme")
        data = {"theme": "dark"}
        response = authenticated_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["theme"] == "dark"

        user.refresh_from_db()
        assert user.preferences.theme == "dark"

    def test_update_theme_preference_to_auto(self, authenticated_client, user):
        """Test updating theme preference to auto mode."""
        UserPreferences.objects.create(user=user, theme="light")

        url = reverse("preferences:theme")
        data = {"theme": "auto"}
        response = authenticated_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["theme"] == "auto"

        user.refresh_from_db()
        assert user.preferences.theme == "auto"

    def test_update_theme_preference_with_invalid_value(self, authenticated_client, user):
        """Test that updating with invalid theme value returns error."""
        UserPreferences.objects.create(user=user, theme="light")

        url = reverse("preferences:theme")
        data = {"theme": "invalid"}
        response = authenticated_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "theme" in response.data

    def test_update_theme_preference_unauthenticated(self, api_client):
        """Test that unauthenticated users cannot update theme preferences."""
        url = reverse("preferences:theme")
        data = {"theme": "dark"}
        response = api_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_theme_preference_creates_if_not_exists(
        self, authenticated_client, user
    ):
        """Test that PATCH creates preferences if they don't exist."""
        # Ensure no preferences exist
        assert not UserPreferences.objects.filter(user=user).exists()

        url = reverse("preferences:theme")
        data = {"theme": "dark"}
        response = authenticated_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["theme"] == "dark"

        # Verify preferences were created
        assert UserPreferences.objects.filter(user=user).exists()
        assert user.preferences.theme == "dark"

    def test_update_theme_with_empty_string(self, authenticated_client, user):
        """Test that updating with empty string returns validation error."""
        UserPreferences.objects.create(user=user, theme="light")

        url = reverse("preferences:theme")
        data = {"theme": ""}
        response = authenticated_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "theme" in response.data

    def test_update_theme_with_missing_field(self, authenticated_client, user):
        """Test that PATCH request with missing theme field returns error."""
        UserPreferences.objects.create(user=user, theme="light")

        url = reverse("preferences:theme")
        data = {}
        response = authenticated_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_multiple_users_independent_preferences(
        self, authenticated_client, user, admin_user
    ):
        """Test that different users have independent preferences."""
        # Create preferences for both users
        UserPreferences.objects.create(user=user, theme="light")
        UserPreferences.objects.create(user=admin_user, theme="dark")

        url = reverse("preferences:theme")
        response = authenticated_client.get(url)

        # Should get the authenticated user's preferences (light)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["theme"] == "light"

        # Admin user should still have dark theme
        assert admin_user.preferences.theme == "dark"

    def test_theme_preference_persistence(self, authenticated_client, user):
        """Test that theme preference persists across multiple requests."""
        url = reverse("preferences:theme")

        # Set theme to dark
        data = {"theme": "dark"}
        response1 = authenticated_client.patch(url, data, format="json")
        assert response1.status_code == status.HTTP_200_OK

        # Get theme (should still be dark)
        response2 = authenticated_client.get(url)
        assert response2.status_code == status.HTTP_200_OK
        assert response2.data["theme"] == "dark"

        # Update to light
        data = {"theme": "light"}
        response3 = authenticated_client.patch(url, data, format="json")
        assert response3.status_code == status.HTTP_200_OK

        # Verify it's now light
        response4 = authenticated_client.get(url)
        assert response4.status_code == status.HTTP_200_OK
        assert response4.data["theme"] == "light"
