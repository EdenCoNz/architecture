"""Assessments app configuration."""

from django.apps import AppConfig


class AssessmentsConfig(AppConfig):
    """Configuration for assessments app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.assessments"
    verbose_name = "Assessments"
