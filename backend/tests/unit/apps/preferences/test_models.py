"""Unit tests for UserPreferences model."""

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from apps.preferences.models import UserPreferences

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.unit
class TestUserPreferencesModel:
    """Test suite for UserPreferences model."""

    def test_create_user_preferences_with_default_theme(self, user):
        """Test creating user preferences with default theme value."""
        preferences = UserPreferences.objects.create(user=user)

        assert preferences.user == user
        assert preferences.theme == "auto"
        assert preferences.created_at is not None
        assert preferences.updated_at is not None

    def test_create_user_preferences_with_light_theme(self, user):
        """Test creating user preferences with light theme."""
        preferences = UserPreferences.objects.create(user=user, theme="light")

        assert preferences.theme == "light"

    def test_create_user_preferences_with_dark_theme(self, user):
        """Test creating user preferences with dark theme."""
        preferences = UserPreferences.objects.create(user=user, theme="dark")

        assert preferences.theme == "dark"

    def test_create_user_preferences_with_auto_theme(self, user):
        """Test creating user preferences with auto theme."""
        preferences = UserPreferences.objects.create(user=user, theme="auto")

        assert preferences.theme == "auto"

    def test_create_user_preferences_with_invalid_theme(self, user):
        """Test that creating preferences with invalid theme raises ValidationError."""
        preferences = UserPreferences(user=user, theme="invalid")

        with pytest.raises(ValidationError) as exc_info:
            preferences.full_clean()

        assert "theme" in exc_info.value.message_dict

    def test_user_preferences_one_to_one_relationship(self, user):
        """Test that each user can only have one preferences record."""
        UserPreferences.objects.create(user=user, theme="light")

        # Attempting to create another preferences for the same user should fail
        with pytest.raises(IntegrityError):
            UserPreferences.objects.create(user=user, theme="dark")

    def test_user_preferences_cascade_delete(self, user):
        """Test that preferences are deleted when user is deleted."""
        preferences = UserPreferences.objects.create(user=user)
        preferences_id = preferences.id

        user.delete()

        assert not UserPreferences.objects.filter(id=preferences_id).exists()

    def test_update_theme_preference(self, user):
        """Test updating theme preference."""
        preferences = UserPreferences.objects.create(user=user, theme="light")

        preferences.theme = "dark"
        preferences.save()

        preferences.refresh_from_db()
        assert preferences.theme == "dark"

    def test_user_preferences_str_representation(self, user):
        """Test string representation of UserPreferences."""
        preferences = UserPreferences.objects.create(user=user)

        assert str(preferences) == f"{user.username}'s preferences"

    def test_get_or_create_preferences(self, user):
        """Test get_or_create pattern for user preferences."""
        preferences, created = UserPreferences.objects.get_or_create(
            user=user, defaults={"theme": "dark"}
        )

        assert created is True
        assert preferences.theme == "dark"

        # Second call should return existing preferences
        preferences2, created2 = UserPreferences.objects.get_or_create(
            user=user, defaults={"theme": "light"}
        )

        assert created2 is False
        assert preferences2.id == preferences.id
        assert preferences2.theme == "dark"  # Should keep original theme

    def test_updated_at_changes_on_save(self, user):
        """Test that updated_at timestamp changes when record is saved."""
        preferences = UserPreferences.objects.create(user=user, theme="light")
        original_updated_at = preferences.updated_at

        # Small delay to ensure timestamp difference
        import time

        time.sleep(0.01)

        preferences.theme = "dark"
        preferences.save()

        preferences.refresh_from_db()
        assert preferences.updated_at > original_updated_at
