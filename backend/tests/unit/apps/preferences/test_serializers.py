"""Unit tests for preferences serializers."""

import pytest
from django.contrib.auth import get_user_model

from apps.preferences.models import UserPreferences
from apps.preferences.serializers import UserPreferencesSerializer

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.unit
class TestUserPreferencesSerializer:
    """Test suite for UserPreferencesSerializer."""

    def test_serialize_user_preferences(self, user):
        """Test serializing UserPreferences instance."""
        preferences = UserPreferences.objects.create(user=user, theme="dark")

        serializer = UserPreferencesSerializer(preferences)
        data = serializer.data

        assert data["theme"] == "dark"
        assert "created_at" in data
        assert "updated_at" in data
        # User field should not be included in serialization
        assert "user" not in data

    def test_deserialize_valid_theme(self, user):
        """Test deserializing valid theme data."""
        data = {"theme": "light"}

        serializer = UserPreferencesSerializer(data=data)

        assert serializer.is_valid()
        assert serializer.validated_data["theme"] == "light"

    def test_deserialize_dark_theme(self, user):
        """Test deserializing dark theme."""
        data = {"theme": "dark"}

        serializer = UserPreferencesSerializer(data=data)

        assert serializer.is_valid()
        assert serializer.validated_data["theme"] == "dark"

    def test_deserialize_auto_theme(self, user):
        """Test deserializing auto theme."""
        data = {"theme": "auto"}

        serializer = UserPreferencesSerializer(data=data)

        assert serializer.is_valid()
        assert serializer.validated_data["theme"] == "auto"

    def test_deserialize_invalid_theme(self, user):
        """Test deserializing invalid theme raises validation error."""
        data = {"theme": "invalid"}

        serializer = UserPreferencesSerializer(data=data)

        assert not serializer.is_valid()
        assert "theme" in serializer.errors

    def test_deserialize_empty_theme(self, user):
        """Test deserializing empty theme raises validation error."""
        data = {"theme": ""}

        serializer = UserPreferencesSerializer(data=data)

        assert not serializer.is_valid()
        assert "theme" in serializer.errors

    def test_deserialize_missing_theme(self, user):
        """Test deserializing with missing theme field."""
        data = {}

        serializer = UserPreferencesSerializer(data=data)

        # Should fail because theme is required
        assert not serializer.is_valid()
        assert "theme" in serializer.errors

    def test_update_theme_preference(self, user):
        """Test updating theme preference through serializer."""
        preferences = UserPreferences.objects.create(user=user, theme="light")
        data = {"theme": "dark"}

        serializer = UserPreferencesSerializer(preferences, data=data)

        assert serializer.is_valid()
        updated_preferences = serializer.save()

        assert updated_preferences.theme == "dark"
        assert updated_preferences.user == user

    def test_partial_update(self, user):
        """Test partial update of preferences."""
        preferences = UserPreferences.objects.create(user=user, theme="light")
        data = {"theme": "auto"}

        serializer = UserPreferencesSerializer(preferences, data=data, partial=True)

        assert serializer.is_valid()
        updated_preferences = serializer.save()

        assert updated_preferences.theme == "auto"

    def test_read_only_fields(self, user):
        """Test that created_at and updated_at are read-only."""
        preferences = UserPreferences.objects.create(user=user, theme="light")
        original_created_at = preferences.created_at

        data = {
            "theme": "dark",
            "created_at": "2020-01-01T00:00:00Z",
            "updated_at": "2020-01-01T00:00:00Z",
        }

        serializer = UserPreferencesSerializer(preferences, data=data)

        assert serializer.is_valid()
        updated_preferences = serializer.save()

        # Timestamps should not have changed to the provided values
        assert updated_preferences.created_at == original_created_at

    def test_theme_choices_validation(self, user):
        """Test that only valid theme choices are accepted."""
        valid_themes = ["light", "dark", "auto"]

        for theme in valid_themes:
            data = {"theme": theme}
            serializer = UserPreferencesSerializer(data=data)
            assert serializer.is_valid(), f"Theme '{theme}' should be valid"

        invalid_themes = ["LIGHT", "DARK", "Light", "Dark", "system", "custom", 123, None]

        for theme in invalid_themes:
            data = {"theme": theme}
            serializer = UserPreferencesSerializer(data=data)
            assert not serializer.is_valid(), f"Theme '{theme}' should be invalid"
