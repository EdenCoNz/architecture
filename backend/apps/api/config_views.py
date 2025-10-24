"""
Frontend configuration API endpoint.

This module provides runtime configuration to the frontend application,
allowing the same frontend image to be deployed across different environments
(dev, staging, production) without rebuilding.
"""

import os

from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([AllowAny])  # Public endpoint - no authentication required
def frontend_config(request):
    """
    Frontend configuration endpoint.

    Returns runtime configuration for the frontend application based on
    environment variables. This allows the same frontend container image
    to be used across different environments.

    **Response Format:**
    ```json
    {
        "api": {
            "url": "https://api.example.com",
            "timeout": 30000,
            "enableLogging": false
        },
        "app": {
            "name": "Frontend Application",
            "title": "Frontend Application",
            "version": "1.0.0",
            "environment": "production"
        },
        "features": {
            "enableAnalytics": false,
            "enableDebugMode": false
        }
    }
    ```

    **Environment Variables:**
    - `FRONTEND_API_URL`: Backend API base URL (default: http://localhost:8000)
    - `FRONTEND_API_TIMEOUT`: API request timeout in ms (default: 30000)
    - `FRONTEND_API_ENABLE_LOGGING`: Enable API logging (default: false)
    - `FRONTEND_APP_NAME`: Application name (default: "Frontend Application")
    - `FRONTEND_APP_TITLE`: Application title (default: "Frontend Application")
    - `FRONTEND_APP_VERSION`: Application version (default: "1.0.0")
    - `FRONTEND_ENABLE_ANALYTICS`: Enable analytics (default: false)
    - `FRONTEND_ENABLE_DEBUG`: Enable debug mode (default: false)
    """

    # Determine environment
    environment = os.getenv("DJANGO_ENV", "production")
    if hasattr(settings, "DEBUG") and settings.DEBUG:
        environment = "development"

    # Build configuration from environment variables
    config = {
        "api": {
            "url": os.getenv("FRONTEND_API_URL", "http://localhost:8000"),
            "timeout": int(os.getenv("FRONTEND_API_TIMEOUT", "30000")),
            "enableLogging": os.getenv("FRONTEND_API_ENABLE_LOGGING", "false").lower() == "true",
        },
        "app": {
            "name": os.getenv("FRONTEND_APP_NAME", "Frontend Application"),
            "title": os.getenv("FRONTEND_APP_TITLE", "Frontend Application"),
            "version": os.getenv("FRONTEND_APP_VERSION", "1.0.0"),
            "environment": environment,
        },
        "features": {
            "enableAnalytics": os.getenv("FRONTEND_ENABLE_ANALYTICS", "false").lower() == "true",
            "enableDebugMode": os.getenv("FRONTEND_ENABLE_DEBUG", "false").lower() == "true",
        },
    }

    return Response(config, status=status.HTTP_200_OK)
