"""
API serializers.
Placeholder file - serializers will be organized into separate modules as the API grows.
"""

from rest_framework import serializers


class FrontendApiConfigSerializer(serializers.Serializer):
    """Serializer for frontend API configuration section."""

    url = serializers.CharField(
        help_text="Backend API base URL",
        default="http://localhost:8000",
    )
    timeout = serializers.IntegerField(
        help_text="API request timeout in milliseconds",
        default=30000,
    )
    enableLogging = serializers.BooleanField(
        help_text="Enable API request logging",
        default=False,
    )


class FrontendAppConfigSerializer(serializers.Serializer):
    """Serializer for frontend application configuration section."""

    name = serializers.CharField(
        help_text="Application name",
        default="Frontend Application",
    )
    title = serializers.CharField(
        help_text="Application title displayed in browser",
        default="Frontend Application",
    )
    version = serializers.CharField(
        help_text="Application version",
        default="1.0.0",
    )
    environment = serializers.CharField(
        help_text="Runtime environment (development, production, etc.)",
        default="production",
    )


class FrontendFeaturesConfigSerializer(serializers.Serializer):
    """Serializer for frontend feature flags configuration section."""

    enableAnalytics = serializers.BooleanField(
        help_text="Enable analytics tracking",
        default=False,
    )
    enableDebugMode = serializers.BooleanField(
        help_text="Enable debug mode with additional logging",
        default=False,
    )


class FrontendConfigSerializer(serializers.Serializer):
    """
    Serializer for frontend configuration endpoint response.

    Defines the complete structure of runtime configuration provided to
    the frontend application.
    """

    api = FrontendApiConfigSerializer(help_text="API connection settings")
    app = FrontendAppConfigSerializer(help_text="Application metadata and settings")
    features = FrontendFeaturesConfigSerializer(help_text="Feature flags and toggles")
