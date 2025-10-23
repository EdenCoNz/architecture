"""
Database connectivity and health check utilities.

Provides utilities for checking database connectivity, handling connection
errors gracefully, and monitoring database health.
"""

import logging
import time
from typing import Any, Dict

from django.db import connections
from django.db.utils import DatabaseError, OperationalError

logger = logging.getLogger(__name__)


class DatabaseHealthCheck:
    """
    Database health check utility.

    Provides methods to check database connectivity and return detailed
    health status information including connection details and response times.
    """

    def __init__(self, database_alias: str = "default"):
        """
        Initialize health check for a specific database.

        Args:
            database_alias: The database alias to check (default: 'default')
        """
        self.database_alias = database_alias
        self.connection = connections[database_alias]

    def check(self) -> Dict[str, Any]:
        """
        Perform a health check on the database connection.

        Returns:
            Dictionary containing health status information:
            - status: 'healthy' or 'unhealthy'
            - database: 'connected' or 'disconnected'
            - response_time_ms: Query response time in milliseconds
            - connection_info: Database connection details (without password)
            - error: Error message if unhealthy

        Example:
            >>> checker = DatabaseHealthCheck()
            >>> result = checker.check()
            >>> print(result['status'])
            'healthy'
        """
        start_time = time.time()

        try:
            # Attempt a simple query to verify connectivity
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()

            response_time = (time.time() - start_time) * 1000  # Convert to ms

            return {
                "status": "healthy",
                "database": "connected",
                "response_time_ms": round(response_time, 2),
                "connection_info": self._get_connection_info(),
            }

        except (OperationalError, DatabaseError) as e:
            error_message = str(e)
            logger.error(
                f"Database health check failed: {error_message}",
                exc_info=True,
                extra={"database": self.database_alias},
            )

            return {
                "status": "unhealthy",
                "database": "disconnected",
                "error": self._format_error_message(error_message),
                "connection_info": self._get_connection_info(),
            }

        except Exception as e:
            error_message = str(e)
            logger.error(
                f"Unexpected error during database health check: {error_message}",
                exc_info=True,
                extra={"database": self.database_alias},
            )

            return {
                "status": "unhealthy",
                "database": "disconnected",
                "error": self._format_error_message(error_message),
                "connection_info": self._get_connection_info(),
            }

    def _get_connection_info(self) -> Dict[str, Any]:
        """
        Get database connection information without exposing credentials.

        Returns:
            Dictionary with safe connection details (no password)
        """
        settings = self.connection.settings_dict

        return {
            "engine": settings.get("ENGINE", "unknown"),
            "host": settings.get("HOST", "unknown"),
            "port": settings.get("PORT", "unknown"),
            "name": settings.get("NAME", "unknown"),
            "user": settings.get("USER", "unknown"),
            # Explicitly DO NOT include PASSWORD
        }

    def _format_error_message(self, error: str) -> str:
        """
        Format error messages to be more user-friendly.

        Args:
            error: Raw error message from database

        Returns:
            Formatted, user-friendly error message
        """
        error_lower = error.lower()

        # Check for connection errors first (most common)
        if "connection refused" in error_lower or "could not connect" in error_lower:
            host = self.connection.settings_dict.get("HOST", "unknown")
            port = self.connection.settings_dict.get("PORT", "unknown")
            return (
                f"Could not connect to PostgreSQL database server at "
                f"{host}:{port}. Please ensure PostgreSQL is running and "
                f"check DB_HOST and DB_PORT."
            )

        if "does not exist" in error_lower and "database" in error_lower:
            db_name = self.connection.settings_dict.get("NAME", "unknown")
            return (
                f"Database '{db_name}' does not exist. Please create the "
                f"database or check DB_NAME environment variable."
            )

        if "authentication failed" in error_lower or (
            "password" in error_lower and "failed" in error_lower
        ):
            user = self.connection.settings_dict.get("USER", "unknown")
            return (
                f"Authentication failed for user '{user}'. Please check "
                f"DB_USER and DB_PASSWORD environment variables."
            )

        if "role" in error_lower and "does not exist" in error_lower:
            user = self.connection.settings_dict.get("USER", "unknown")
            return (
                f"Database user '{user}' does not exist. Please create "
                f"the user or check DB_USER environment variable."
            )

        # Return original error if we can't format it better
        return error


def check_database_connection(verbose: bool = False) -> bool:
    """
    Check if database connection is available.

    Args:
        verbose: If True, print detailed status information

    Returns:
        True if database is connected, False otherwise

    Example:
        >>> if check_database_connection(verbose=True):
        ...     print("Database is ready!")
    """
    checker = DatabaseHealthCheck()
    result = checker.check()

    if verbose:
        if result["status"] == "healthy":
            print("✓ Database connection successful")
            print(f"  Response time: {result['response_time_ms']}ms")
            print(f"  Host: {result['connection_info']['host']}")
            print(f"  Database: {result['connection_info']['name']}")
        else:
            print("✗ Database connection failed")
            print(f"  Error: {result.get('error', 'Unknown error')}")

    is_healthy: bool = result["status"] == "healthy"
    return is_healthy


def get_database_status() -> Dict[str, Any]:
    """
    Get comprehensive database status information.

    Returns:
        Dictionary containing database status, configuration, and health info

    Example:
        >>> status = get_database_status()
        >>> print(status['connected'])
        True
    """
    checker = DatabaseHealthCheck()
    health = checker.check()

    return {
        "connected": health["status"] == "healthy",
        "status": health["status"],
        "response_time_ms": health.get("response_time_ms"),
        "database": health["connection_info"].get("name"),
        "host": health["connection_info"].get("host"),
        "port": health["connection_info"].get("port"),
        "engine": health["connection_info"].get("engine"),
        "error": health.get("error"),
        "connection_pooling": {
            "enabled": (connections["default"].settings_dict.get("CONN_MAX_AGE", 0) > 0),
            "max_age": (connections["default"].settings_dict.get("CONN_MAX_AGE", 0)),
        },
        "atomic_requests": (connections["default"].settings_dict.get("ATOMIC_REQUESTS", False)),
    }


def ensure_database_connection() -> None:
    """
    Ensure database connection is available or raise clear error.

    Raises:
        OperationalError: If database connection cannot be established

    Example:
        >>> try:
        ...     ensure_database_connection()
        ... except OperationalError as e:
        ...     print(f"Cannot start: {e}")
    """
    checker = DatabaseHealthCheck()
    result = checker.check()

    if result["status"] != "healthy":
        error_msg = result.get("error", "Unknown database error")
        raise OperationalError(f"Cannot establish database connection: {error_msg}")

    logger.info(
        "Database connection established successfully",
        extra={
            "response_time_ms": result.get("response_time_ms"),
            "database": result["connection_info"].get("name"),
        },
    )
