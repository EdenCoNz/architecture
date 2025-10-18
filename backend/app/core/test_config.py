"""
Test-specific configuration settings.

This module provides configuration overrides for testing environments,
including in-memory database setup and test-specific settings.
"""
from typing import Optional
from pydantic import Field
from pydantic_settings import SettingsConfigDict

from app.core.config import Settings


class TestSettings(Settings):
    """
    Test environment configuration settings.

    Overrides production settings with test-specific values:
    - Uses SQLite in-memory database by default (faster, isolated)
    - Disables database connection pooling (not needed for tests)
    - Simplifies JWT settings for faster test execution
    - Disables rate limiting
    - Uses simple password hashing (faster tests)
    """

    model_config = SettingsConfigDict(
        env_file=".env.test",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Environment
    ENVIRONMENT: str = "testing"
    DEBUG: bool = True

    # Database - default to SQLite in-memory for fast isolated tests
    # Override with TEST_DATABASE_URL environment variable for PostgreSQL testing
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///:memory:",
        description="Test database URL (default: in-memory SQLite)"
    )

    # Disable connection pooling for SQLite
    DATABASE_POOL_SIZE: int = 0
    DATABASE_MAX_OVERFLOW: int = 0
    DATABASE_POOL_TIMEOUT: int = 5
    DATABASE_POOL_RECYCLE: int = -1
    DATABASE_ECHO: bool = False  # Set to True to see SQL queries in tests

    # JWT settings - use simpler/faster settings for tests
    JWT_SECRET_KEY: str = "test-secret-key-not-for-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 1

    # Password hashing - use faster hashing for tests
    PWD_SCHEMES: list[str] = Field(default=["bcrypt"])
    PWD_DEPRECATED: str = Field(default="auto")

    # CORS - allow all for testing
    CORS_ORIGINS: list[str] = Field(default=["*"])
    CORS_ALLOW_CREDENTIALS: bool = True

    # Redis - use fake/mock Redis or separate test instance
    REDIS_URL: Optional[str] = Field(
        default=None,
        description="Redis URL for testing (optional, can use fakeredis)"
    )

    # API configuration
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "FastAPI Backend - Testing"
    VERSION: str = "0.1.0-test"

    # Rate limiting - disable for tests
    RATE_LIMIT_ENABLED: bool = False

    # Logging - reduce verbosity in tests
    LOG_LEVEL: str = "WARNING"
    LOG_FORMAT: str = "simple"

    # Email - use console backend for tests
    EMAIL_ENABLED: bool = False

    # File uploads
    UPLOAD_MAX_SIZE: int = 5_242_880  # 5MB
    UPLOAD_ALLOWED_EXTENSIONS: list[str] = Field(
        default=[".jpg", ".jpeg", ".png", ".pdf"]
    )

    # Security - relaxed for testing
    ALLOWED_HOSTS: list[str] = Field(default=["*"])
    TRUSTED_HOSTS: list[str] = Field(default=["*"])

    @property
    def is_sqlite(self) -> bool:
        """Check if using SQLite database."""
        return "sqlite" in self.DATABASE_URL.lower()

    @property
    def is_postgresql(self) -> bool:
        """Check if using PostgreSQL database."""
        return "postgresql" in self.DATABASE_URL.lower()


# Singleton test settings instance
test_settings = TestSettings()
