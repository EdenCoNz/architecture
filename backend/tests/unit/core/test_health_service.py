"""
Unit tests for the HealthCheckService.

These tests verify the health check service functionality including
database connectivity checks, version reporting, and overall health status.
"""

from datetime import datetime
from unittest.mock import patch

import pytest
from django.conf import settings
from django.db import DatabaseError

from core.services.health import HealthCheckService, HealthStatus


@pytest.mark.unit
class TestHealthCheckService:
    """Test suite for HealthCheckService."""

    def test_service_initialization(self) -> None:
        """Test that service can be instantiated."""
        service = HealthCheckService()
        assert service is not None
        assert isinstance(service, HealthCheckService)

    def test_get_application_version(self) -> None:
        """Test that application version is retrieved correctly."""
        service = HealthCheckService()
        version = service.get_application_version()

        assert version is not None
        assert isinstance(version, str)
        assert version == "0.1.0"

    def test_is_debug_mode_returns_boolean(self) -> None:
        """Test that debug mode check returns a boolean."""
        service = HealthCheckService()
        debug_mode = service.is_debug_mode()

        assert isinstance(debug_mode, bool)

    @patch("core.services.health.settings.DEBUG", True)
    def test_is_debug_mode_when_enabled(self) -> None:
        """Test debug mode check when DEBUG is True."""
        service = HealthCheckService()
        assert service.is_debug_mode() is True

    @patch("core.services.health.settings.DEBUG", False)
    def test_is_debug_mode_when_disabled(self) -> None:
        """Test debug mode check when DEBUG is False."""
        service = HealthCheckService()
        assert service.is_debug_mode() is False


@pytest.mark.unit
class TestHealthCheckServiceDatabase:
    """Test suite for database health checks."""

    def test_check_database_when_healthy(self, db) -> None:
        """Test database check when connection is healthy."""
        service = HealthCheckService()
        result = service.check_database()

        assert result["status"] == "healthy"
        assert result["connected"] is True
        assert "engine" in result
        assert result["engine"] == settings.DATABASES["default"]["ENGINE"]

    @patch("core.services.health.connection.cursor")
    def test_check_database_when_unhealthy(self, mock_cursor) -> None:
        """Test database check when connection fails."""
        # Simulate database connection failure
        mock_cursor.side_effect = DatabaseError("Connection refused")

        service = HealthCheckService()
        result = service.check_database()

        assert result["status"] == "unhealthy"
        assert result["connected"] is False
        assert "error" in result
        assert "Connection refused" in result["error"]

    @patch("core.services.health.connection.cursor")
    def test_check_database_handles_exceptions(self, mock_cursor) -> None:
        """Test that database check handles unexpected exceptions."""
        # Simulate unexpected error
        mock_cursor.side_effect = Exception("Unexpected error")

        service = HealthCheckService()
        result = service.check_database()

        assert result["status"] == "unhealthy"
        assert result["connected"] is False
        assert "error" in result

    def test_is_healthy_when_database_connected(self, db) -> None:
        """Test is_healthy returns True when database is connected."""
        service = HealthCheckService()
        assert service.is_healthy() is True

    @patch("core.services.health.connection.cursor")
    def test_is_healthy_when_database_disconnected(self, mock_cursor) -> None:
        """Test is_healthy returns False when database is disconnected."""
        mock_cursor.side_effect = DatabaseError("Connection refused")

        service = HealthCheckService()
        assert service.is_healthy() is False


@pytest.mark.unit
class TestHealthStatus:
    """Test suite for HealthStatus model."""

    def test_health_status_creation(self) -> None:
        """Test that HealthStatus can be created with all fields."""
        timestamp = datetime.now()
        status = HealthStatus(
            status="healthy",
            timestamp=timestamp,
            version="0.1.0",
            database={"status": "healthy", "connected": True},
            debug_mode=True,
        )

        assert status.status == "healthy"
        assert status.timestamp == timestamp
        assert status.version == "0.1.0"
        assert status.database["status"] == "healthy"
        assert status.debug_mode is True

    def test_health_status_is_dataclass(self) -> None:
        """Test that HealthStatus is a dataclass."""
        timestamp = datetime.now()
        status = HealthStatus(
            status="healthy",
            timestamp=timestamp,
            version="0.1.0",
            database={},
            debug_mode=False,
        )

        # Dataclasses have __dataclass_fields__
        assert hasattr(status, "__dataclass_fields__")


@pytest.mark.unit
class TestGetHealthStatus:
    """Test suite for comprehensive health status retrieval."""

    def test_get_health_status_structure(self, db) -> None:
        """Test that get_health_status returns proper structure."""
        service = HealthCheckService()
        health = service.get_health_status()

        assert isinstance(health, HealthStatus)
        assert hasattr(health, "status")
        assert hasattr(health, "timestamp")
        assert hasattr(health, "version")
        assert hasattr(health, "database")
        assert hasattr(health, "debug_mode")

    def test_get_health_status_when_healthy(self, db) -> None:
        """Test get_health_status when all systems are healthy."""
        service = HealthCheckService()
        health = service.get_health_status()

        assert health.status == "healthy"
        assert isinstance(health.timestamp, datetime)
        assert health.version == "0.1.0"
        assert health.database["connected"] is True

    @patch("core.services.health.connection.cursor")
    def test_get_health_status_when_unhealthy(self, mock_cursor) -> None:
        """Test get_health_status when database is down."""
        mock_cursor.side_effect = DatabaseError("Connection refused")

        service = HealthCheckService()
        health = service.get_health_status()

        assert health.status == "unhealthy"
        assert isinstance(health.timestamp, datetime)
        assert health.database["connected"] is False

    @patch("core.services.health.settings.DEBUG", True)
    def test_get_health_status_includes_debug_mode(self, db) -> None:
        """Test that health status includes debug mode information."""
        service = HealthCheckService()
        health = service.get_health_status()

        assert isinstance(health.debug_mode, bool)
        assert health.debug_mode is True

    def test_get_health_status_timestamp_is_recent(self, db) -> None:
        """Test that health status timestamp is current."""
        service = HealthCheckService()
        before = datetime.now()
        health = service.get_health_status()
        after = datetime.now()

        # Timestamp should be between before and after
        assert before <= health.timestamp <= after


@pytest.mark.unit
@pytest.mark.smoke
class TestHealthCheckIntegration:
    """Smoke tests for critical health check functionality."""

    def test_health_service_end_to_end(self, db) -> None:
        """Test complete health check workflow."""
        service = HealthCheckService()

        # Check individual components
        version = service.get_application_version()
        assert version is not None

        db_status = service.check_database()
        assert db_status["connected"] is True

        is_healthy = service.is_healthy()
        assert is_healthy is True

        # Check comprehensive status
        health = service.get_health_status()
        assert health.status == "healthy"
        assert health.version == version
