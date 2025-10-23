"""
Health check and status views for API monitoring.

Provides endpoints for monitoring the API's operational status, including:
- Basic health check (GET /api/v1/health/)
- Detailed status information (GET /api/v1/status/)
- Kubernetes readiness probe (GET /api/v1/health/ready/)
- Kubernetes liveness probe (GET /api/v1/health/live/)
"""

import platform
import time
from datetime import datetime
from typing import Any, Dict

import psutil
from django.conf import settings
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.database import DatabaseHealthCheck
from config.env_config import get_environment

# Track server start time for uptime calculation
SERVER_START_TIME = time.time()


def get_version_info() -> Dict[str, str]:
    """
    Get version information for the API.

    Returns:
        Dictionary containing version information
    """
    return {
        "version": "1.0.0",  # Application version
        "api_version": "v1",
        "django_version": platform.python_version(),
        "python_version": platform.python_version(),
    }


def get_memory_usage() -> Dict[str, Any]:
    """
    Get current memory usage statistics.

    Returns:
        Dictionary containing memory usage information
    """
    process = psutil.Process()
    memory_info = process.memory_info()

    return {
        "used_mb": round(memory_info.rss / 1024 / 1024, 2),
        "percent": round(process.memory_percent(), 2),
    }


def get_uptime_seconds() -> float:
    """
    Get server uptime in seconds.

    Returns:
        Uptime in seconds since server start
    """
    return round(time.time() - SERVER_START_TIME, 2)


def get_database_health() -> Dict[str, Any]:
    """
    Get database health status.

    Returns:
        Dictionary containing database health information
    """
    checker = DatabaseHealthCheck()
    result = checker.check()

    database_info = {
        "status": result["database"],
        "response_time_ms": result.get("response_time_ms"),
        "engine": result["connection_info"].get("engine"),
    }

    # Include error if present
    if "error" in result:
        database_info["error"] = result["error"]

    return database_info


class HealthCheckView(APIView):
    """
    Basic health check endpoint for monitoring.

    Returns the operational status of the API and its dependencies.
    Useful for load balancers and monitoring systems.

    Responses:
        - 200 OK: Service is healthy and operational
        - 503 Service Unavailable: Service is unhealthy (database down, etc.)
    """

    permission_classes = [AllowAny]

    @extend_schema(
        summary="Health Check",
        description="Check if the API is operational and healthy. "
        "Returns 200 if healthy, 503 if unhealthy.",
        responses={
            200: OpenApiResponse(
                description="Service is healthy",
                response={
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "example": "healthy"},
                        "timestamp": {"type": "string", "format": "date-time"},
                        "database": {
                            "type": "object",
                            "properties": {
                                "status": {"type": "string", "example": "connected"},
                                "response_time_ms": {"type": "number", "example": 15.5},
                                "engine": {"type": "string"},
                            },
                        },
                    },
                },
            ),
            503: OpenApiResponse(
                description="Service is unhealthy",
                response={
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "example": "unhealthy"},
                        "timestamp": {"type": "string", "format": "date-time"},
                        "database": {
                            "type": "object",
                            "properties": {
                                "status": {"type": "string", "example": "disconnected"},
                                "error": {"type": "string"},
                            },
                        },
                    },
                },
            ),
        },
        tags=["Health"],
    )
    def get(self, request) -> Response:
        """
        Check API health status.

        Returns:
            Response with health status and HTTP 200 if healthy,
            HTTP 503 if unhealthy
        """
        database_health = get_database_health()

        # Determine overall health status
        is_healthy = database_health["status"] == "connected"

        response_data = {
            "status": "healthy" if is_healthy else "unhealthy",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "database": database_health,
        }

        http_status = status.HTTP_200_OK if is_healthy else status.HTTP_503_SERVICE_UNAVAILABLE

        return Response(response_data, status=http_status)


class StatusView(APIView):
    """
    Detailed status endpoint with comprehensive system information.

    Returns detailed information about the API including version,
    uptime, memory usage, and database status. Always returns 200 OK
    even if dependencies are down (useful for troubleshooting).

    Response includes:
        - Version information
        - Uptime statistics
        - Memory usage
        - Database status
        - Environment information
    """

    permission_classes = [AllowAny]

    @extend_schema(
        summary="System Status",
        description="Get detailed system status including version, uptime, "
        "memory usage, and database status.",
        responses={
            200: OpenApiResponse(
                description="System status information",
                response={
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "example": "healthy"},
                        "timestamp": {"type": "string", "format": "date-time"},
                        "version": {"type": "string", "example": "1.0.0"},
                        "api_version": {"type": "string", "example": "v1"},
                        "environment": {"type": "string", "example": "development"},
                        "uptime_seconds": {"type": "number", "example": 3600.5},
                        "memory": {
                            "type": "object",
                            "properties": {
                                "used_mb": {"type": "number", "example": 256.5},
                                "percent": {"type": "number", "example": 12.5},
                            },
                        },
                        "database": {
                            "type": "object",
                            "properties": {
                                "status": {"type": "string", "example": "connected"},
                                "response_time_ms": {"type": "number", "example": 15.5},
                                "engine": {"type": "string"},
                            },
                        },
                    },
                },
            )
        },
        tags=["Health"],
    )
    def get(self, request) -> Response:
        """
        Get detailed system status.

        Returns:
            Response with comprehensive status information (always HTTP 200)
        """
        database_health = get_database_health()
        version_info = get_version_info()

        # Determine overall health status
        is_healthy = database_health["status"] == "connected"

        response_data = {
            "status": "healthy" if is_healthy else "unhealthy",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "version": version_info["version"],
            "api_version": version_info["api_version"],
            "environment": get_environment(),
            "uptime_seconds": get_uptime_seconds(),
            "memory": get_memory_usage(),
            "database": database_health,
        }

        # Status endpoint always returns 200 (even if unhealthy)
        # This allows monitoring to see details when something is wrong
        return Response(response_data, status=status.HTTP_200_OK)


class ReadinessView(APIView):
    """
    Kubernetes readiness probe endpoint.

    Indicates whether the service is ready to accept traffic.
    Returns 200 if ready, 503 if not ready (e.g., database unavailable).

    Use this endpoint for Kubernetes readiness probes to control
    traffic routing to this pod.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        summary="Readiness Probe",
        description="Check if the service is ready to accept traffic. "
        "Used by Kubernetes readiness probes.",
        responses={
            200: OpenApiResponse(
                description="Service is ready",
                response={
                    "type": "object",
                    "properties": {
                        "ready": {"type": "boolean", "example": True},
                        "timestamp": {"type": "string", "format": "date-time"},
                    },
                },
            ),
            503: OpenApiResponse(
                description="Service is not ready",
                response={
                    "type": "object",
                    "properties": {
                        "ready": {"type": "boolean", "example": False},
                        "timestamp": {"type": "string", "format": "date-time"},
                    },
                },
            ),
        },
        tags=["Health"],
    )
    def get(self, request) -> Response:
        """
        Check if service is ready to accept traffic.

        Returns:
            Response with ready status and HTTP 200 if ready,
            HTTP 503 if not ready
        """
        database_health = get_database_health()
        is_ready = database_health["status"] == "connected"

        response_data = {
            "ready": is_ready,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        http_status = status.HTTP_200_OK if is_ready else status.HTTP_503_SERVICE_UNAVAILABLE

        return Response(response_data, status=http_status)


class LivenessView(APIView):
    """
    Kubernetes liveness probe endpoint.

    Indicates whether the service is alive and responsive.
    Always returns 200 if the server is running (does not check dependencies).

    Use this endpoint for Kubernetes liveness probes. If this returns
    non-200, Kubernetes will restart the pod.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        summary="Liveness Probe",
        description="Check if the service is alive and responsive. "
        "Always returns 200 if server is running. "
        "Used by Kubernetes liveness probes.",
        responses={
            200: OpenApiResponse(
                description="Service is alive",
                response={
                    "type": "object",
                    "properties": {
                        "alive": {"type": "boolean", "example": True},
                        "timestamp": {"type": "string", "format": "date-time"},
                    },
                },
            )
        },
        tags=["Health"],
    )
    def get(self, request) -> Response:
        """
        Check if service is alive.

        Returns:
            Response with alive status (always HTTP 200)
        """
        response_data = {
            "alive": True,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        return Response(response_data, status=status.HTTP_200_OK)
