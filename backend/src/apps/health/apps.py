"""App configuration for health check application."""

from django.apps import AppConfig


class HealthConfig(AppConfig):
    """Health check app configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.health"
    verbose_name = "Health Check"
