"""
Logging configuration and utilities for structured logging.

This module provides centralized logging configuration with support for
different environments, structured logging (JSON format), and integration
with external logging services.
"""
import logging
import sys
import json
from typing import Any, Dict
from datetime import datetime
from pathlib import Path

from app.core.config import settings


class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging.

    Outputs log records as JSON objects with consistent fields:
    - timestamp: ISO 8601 formatted timestamp
    - level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    - logger: Logger name
    - message: Log message
    - extra: Any additional fields from extra parameter
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Format a log record as JSON.

        Args:
            record: The log record to format

        Returns:
            str: JSON formatted log record
        """
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add exception information if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info),
            }

        # Add extra fields
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        if hasattr(record, "method"):
            log_data["method"] = record.method
        if hasattr(record, "path"):
            log_data["path"] = record.path
        if hasattr(record, "status_code"):
            log_data["status_code"] = record.status_code
        if hasattr(record, "process_time_ms"):
            log_data["process_time_ms"] = record.process_time_ms
        if hasattr(record, "client_host"):
            log_data["client_host"] = record.client_host
        if hasattr(record, "user_agent"):
            log_data["user_agent"] = record.user_agent

        # Add any custom extra fields
        for key, value in record.__dict__.items():
            if key not in [
                "name", "msg", "args", "created", "filename", "funcName",
                "levelname", "levelno", "lineno", "module", "msecs",
                "message", "pathname", "process", "processName", "relativeCreated",
                "thread", "threadName", "exc_info", "exc_text", "stack_info",
                "request_id", "method", "path", "status_code", "process_time_ms",
                "client_host", "user_agent",
            ]:
                log_data[key] = value

        return json.dumps(log_data, default=str)


class StandardFormatter(logging.Formatter):
    """
    Standard text formatter for human-readable logs.

    Format: timestamp - logger - level - message
    """

    def __init__(self):
        super().__init__(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )


def setup_logging() -> None:
    """
    Configure application logging based on environment settings.

    Sets up:
    - Console handler with appropriate formatter (JSON for production, text for development)
    - File handler for persistent logs (optional)
    - Log level based on environment configuration
    - Third-party library log levels
    """
    # Get log level from settings
    log_level = getattr(logging, settings.log_level.upper())

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    # Use JSON formatter in production, standard formatter in development
    if settings.is_production:
        formatter = JSONFormatter()
    else:
        formatter = StandardFormatter()

    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Add file handler in production (optional)
    if settings.is_production:
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # Create file handler
        file_handler = logging.FileHandler(
            log_dir / "app.log",
            encoding="utf-8",
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(file_handler)

    # Set log levels for third-party libraries
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.database_echo else logging.WARNING
    )
    logging.getLogger("alembic").setLevel(logging.INFO)

    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info(
        f"Logging configured - Level: {settings.log_level}, Environment: {settings.environment}"
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.

    Args:
        name: The logger name (typically __name__)

    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(name)
