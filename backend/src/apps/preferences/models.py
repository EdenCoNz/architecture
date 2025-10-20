"""User preferences models."""

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

User = get_user_model()


class UserPreferences(models.Model):
    """
    Store user-specific preferences and settings.

    This model maintains a one-to-one relationship with the User model
    and stores various user preferences including theme selection.

    Attributes:
        user: One-to-one relationship to User model
        theme: User's preferred theme (light, dark, or auto)
        created_at: Timestamp when preferences were created
        updated_at: Timestamp when preferences were last updated
    """

    THEME_CHOICES = [
        ("light", "Light"),
        ("dark", "Dark"),
        ("auto", "Auto"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="preferences",
        help_text="User who owns these preferences",
    )

    theme = models.CharField(
        max_length=10,
        choices=THEME_CHOICES,
        default="auto",
        help_text="Preferred color theme (light, dark, or auto)",
    )

    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Timestamp when preferences were created"
    )

    updated_at = models.DateTimeField(
        auto_now=True, help_text="Timestamp when preferences were last updated"
    )

    class Meta:
        """Meta options for UserPreferences model."""

        verbose_name = "User Preference"
        verbose_name_plural = "User Preferences"
        ordering = ["-updated_at"]
        db_table = "user_preferences"

    def __str__(self) -> str:
        """
        Return string representation of user preferences.

        Returns:
            str: String showing username and preferences label
        """
        return f"{self.user.username}'s preferences"

    def clean(self) -> None:
        """
        Validate model fields.

        Raises:
            ValidationError: If theme value is not valid
        """
        super().clean()
        valid_themes = [choice[0] for choice in self.THEME_CHOICES]
        if self.theme not in valid_themes:
            raise ValidationError({"theme": f"Theme must be one of: {', '.join(valid_themes)}"})
