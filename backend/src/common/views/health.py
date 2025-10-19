"""
Health check view for monitoring server status.

This module provides a comprehensive health check endpoint that returns
server status information including database connectivity without requiring
authentication.
"""

from typing import Any

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.services.health import HealthCheckService


class HealthCheckView(APIView):
    """
    Health check endpoint for monitoring server availability.

    This endpoint is publicly accessible and returns comprehensive server status
    including database connectivity, version, and debug mode information.
    It can be used by load balancers, monitoring tools, or orchestration
    platforms to verify the service is running and healthy.

    Returns:
        JSON response with:
        - status: Current health status ("healthy" or "unhealthy")
        - timestamp: ISO format timestamp of the check
        - version: Application version
        - database: Database connectivity status
        - debug_mode: Whether debug mode is enabled
    """

    permission_classes = [AllowAny]
    authentication_classes: list[Any] = []

    def get(self, request: Request) -> Response:
        """
        Handle GET request for health check.

        Args:
            request: HTTP request object

        Returns:
            Response with health status information
        """
        service = HealthCheckService()
        health = service.get_health_status()

        response_data = {
            "status": health.status,
            "timestamp": health.timestamp.isoformat(),
            "version": health.version,
            "service": "backend-api",
            "database": health.database,
            "debug_mode": health.debug_mode,
        }

        # Return 503 if unhealthy, 200 if healthy
        http_status = (
            status.HTTP_200_OK if health.status == "healthy" else status.HTTP_503_SERVICE_UNAVAILABLE
        )

        return Response(response_data, status=http_status)
