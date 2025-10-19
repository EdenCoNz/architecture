"""
Health check service for monitoring application status.

This service provides health check functionality to verify that the
application and its dependencies are functioning correctly.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from django.conf import settings
from django.db import connection


@dataclass
class HealthStatus:
    """Health status response model."""

    status: str
    timestamp: datetime
    version: str
    database: dict[str, Any]
    debug_mode: bool


class HealthCheckService:
    """
    Service for performing health checks on the application.

    This service checks various aspects of the application health including:
    - Database connectivity
    - Application version
    - Debug mode status
    """

    def __init__(self) -> None:
        """Initialize the health check service."""
        pass

    def check_database(self) -> dict[str, Any]:
        """
        Check database connectivity.

        Returns:
            dict: Database status information

        Raises:
            Exception: If database connection fails
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            return {
                "status": "healthy",
                "connected": True,
                "engine": settings.DATABASES["default"]["ENGINE"],
            }
        except Exception as e:
            return {"status": "unhealthy", "connected": False, "error": str(e)}

    def get_application_version(self) -> str:
        """
        Get the application version.

        Returns:
            str: Application version string
        """
        from backend import __version__

        return __version__

    def is_debug_mode(self) -> bool:
        """
        Check if application is running in debug mode.

        Returns:
            bool: True if debug mode is enabled
        """
        return settings.DEBUG

    def get_health_status(self) -> HealthStatus:
        """
        Get comprehensive health status of the application.

        Returns:
            HealthStatus: Complete health status information
        """
        db_status = self.check_database()
        overall_status = "healthy" if db_status["connected"] else "unhealthy"

        return HealthStatus(
            status=overall_status,
            timestamp=datetime.now(),
            version=self.get_application_version(),
            database=db_status,
            debug_mode=self.is_debug_mode(),
        )

    def is_healthy(self) -> bool:
        """
        Check if application is healthy.

        Returns:
            bool: True if all health checks pass
        """
        db_status = self.check_database()
        return db_status["connected"]
