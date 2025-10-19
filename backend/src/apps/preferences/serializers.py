"""Serializers for user preferences."""

from rest_framework import serializers

from apps.preferences.models import UserPreferences


class UserPreferencesSerializer(serializers.ModelSerializer):
    """
    Serializer for UserPreferences model.

    Handles serialization and deserialization of user theme preferences.
    The user field is excluded as it's determined from the authenticated request.

    Fields:
        theme: User's preferred theme (light, dark, or auto)
        created_at: Read-only timestamp when preferences were created
        updated_at: Read-only timestamp when preferences were last updated
    """

    class Meta:
        """Meta options for UserPreferencesSerializer."""

        model = UserPreferences
        fields = ["theme", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]

    def validate_theme(self, value: str) -> str:
        """
        Validate theme value.

        Args:
            value: Theme value to validate

        Returns:
            str: Validated theme value

        Raises:
            serializers.ValidationError: If theme value is invalid
        """
        valid_themes = [choice[0] for choice in UserPreferences.THEME_CHOICES]
        if value not in valid_themes:
            raise serializers.ValidationError(
                f"Invalid theme. Must be one of: {', '.join(valid_themes)}"
            )
        return value
