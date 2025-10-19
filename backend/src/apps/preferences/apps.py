"""Django app configuration for user preferences."""

from django.apps import AppConfig


class PreferencesConfig(AppConfig):
    """Configuration for the preferences app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.preferences"
    verbose_name = "User Preferences"

    def ready(self) -> None:
        """Import signal handlers when app is ready."""
        # Import signals here if needed in the future
        pass
