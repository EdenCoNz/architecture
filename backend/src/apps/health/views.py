"""
Health check API views.

Provides REST API endpoints for health check functionality.
"""

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.services.health import HealthCheckService


class HealthCheckView(APIView):
    """
    Health check endpoint.

    Returns comprehensive health status of the application including
    database connectivity, version, and debug mode.
    """

    permission_classes = []  # Public endpoint
    authentication_classes = []  # No authentication required

    def get(self, request: Request) -> Response:
        """
        Handle GET request for health check.

        Args:
            request: HTTP request object

        Returns:
            Response: Health status information
        """
        service = HealthCheckService()
        health = service.get_health_status()

        response_data = {
            "status": health.status,
            "timestamp": health.timestamp.isoformat(),
            "version": health.version,
            "database": health.database,
            "debug_mode": health.debug_mode,
        }

        # Return 503 if unhealthy, 200 if healthy
        http_status = (
            status.HTTP_200_OK if health.status == "healthy" else status.HTTP_503_SERVICE_UNAVAILABLE
        )

        return Response(response_data, status=http_status)


class LivenessView(APIView):
    """
    Liveness probe endpoint.

    Simple endpoint to check if the application is running.
    Used by container orchestration systems.
    """

    permission_classes = []
    authentication_classes = []

    def get(self, request: Request) -> Response:
        """
        Handle GET request for liveness check.

        Args:
            request: HTTP request object

        Returns:
            Response: Simple OK response
        """
        return Response({"status": "alive"}, status=status.HTTP_200_OK)


class ReadinessView(APIView):
    """
    Readiness probe endpoint.

    Checks if the application is ready to accept traffic.
    Used by container orchestration systems.
    """

    permission_classes = []
    authentication_classes = []

    def get(self, request: Request) -> Response:
        """
        Handle GET request for readiness check.

        Args:
            request: HTTP request object

        Returns:
            Response: Readiness status
        """
        service = HealthCheckService()
        is_ready = service.is_healthy()

        if is_ready:
            return Response({"status": "ready"}, status=status.HTTP_200_OK)
        else:
            return Response({"status": "not_ready"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
