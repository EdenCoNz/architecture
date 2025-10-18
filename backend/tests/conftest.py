"""
Pytest configuration and shared fixtures for tests.

This module provides common test fixtures and configuration used across
all test modules. It includes fixtures for:
- Database engine and session management
- HTTP client with dependency overrides
- Mock fixtures for external dependencies
- Test data factories and utilities
"""
import os
import pytest
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool, StaticPool

from app.core.test_config import test_settings
from app.core.database import Base, get_db
from main import app


# Use test settings for database URL
TEST_DATABASE_URL = test_settings.DATABASE_URL


@pytest.fixture(scope="session")
def anyio_backend():
    """Specify the async backend for pytest-asyncio."""
    return "asyncio"


@pytest.fixture(scope="function")
async def test_db_engine():
    """
    Create a test database engine for each test.

    Uses SQLite in-memory database for fast, isolated tests.
    For PostgreSQL testing, set TEST_DATABASE_URL environment variable.

    The fixture:
    1. Creates a new database engine
    2. Creates all tables
    3. Yields the engine for test use
    4. Drops all tables after test
    5. Disposes the engine
    """
    # Choose poolclass based on database type
    if test_settings.is_sqlite:
        # SQLite in-memory needs StaticPool to share connection
        poolclass = StaticPool
    else:
        # PostgreSQL uses NullPool to avoid connection pooling in tests
        poolclass = NullPool

    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=poolclass,
        echo=test_settings.DATABASE_ECHO,
        # SQLite specific settings for better test compatibility
        connect_args={"check_same_thread": False} if test_settings.is_sqlite else {},
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
async def test_db_session(test_db_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Create a test database session for each test.

    Args:
        test_db_engine: The test database engine

    Yields:
        AsyncSession: Test database session
    """
    async_session = async_sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with async_session() as session:
        yield session


@pytest.fixture(scope="function")
async def client(test_db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Create a test client for making HTTP requests to the application.

    Args:
        test_db_session: The test database session

    Yields:
        AsyncClient: HTTP test client
    """
    # Override the database dependency
    async def override_get_db():
        yield test_db_session

    app.dependency_overrides[get_db] = override_get_db

    # Create test client
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as test_client:
        yield test_client

    # Clear overrides
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def mock_db_healthy(monkeypatch):
    """
    Mock database health check to return True.

    Use this fixture when testing endpoints that check database health
    but you want to simulate a healthy database without actual connection.
    """
    async def mock_check():
        return True

    from app.core import database
    monkeypatch.setattr(database, "check_db_connection", mock_check)


@pytest.fixture(scope="function")
def mock_db_unhealthy(monkeypatch):
    """
    Mock database health check to return False.

    Use this fixture when testing error handling for database failures.
    """
    async def mock_check():
        return False

    from app.core import database
    monkeypatch.setattr(database, "check_db_connection", mock_check)


# Additional test fixtures and utilities


@pytest.fixture(scope="function")
async def db_session(test_db_session: AsyncSession) -> AsyncSession:
    """
    Alias for test_db_session for convenience.

    Allows tests to use @pytest.mark.asyncio and db_session
    instead of test_db_session.
    """
    return test_db_session


@pytest.fixture(scope="function")
def clean_db(test_db_session: AsyncSession):
    """
    Fixture that ensures a clean database state.

    Use this when you need to explicitly clean database between test steps.
    """
    async def _clean():
        # Rollback any pending transactions
        await test_db_session.rollback()
        # Clear session
        await test_db_session.close()

    return _clean


@pytest.fixture(scope="session")
def test_environment():
    """
    Fixture that provides test environment information.

    Useful for conditional test behavior based on environment.
    """
    return {
        "database_url": TEST_DATABASE_URL,
        "is_sqlite": test_settings.is_sqlite,
        "is_postgresql": test_settings.is_postgresql,
        "environment": test_settings.ENVIRONMENT,
    }


@pytest.fixture(autouse=True)
def reset_dependency_overrides():
    """
    Automatically reset FastAPI dependency overrides after each test.

    This prevents test pollution from dependency mocking.
    """
    yield
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def anyio_backend_options():
    """Configure anyio backend options for async tests."""
    return {"use_uvloop": False}  # Disable uvloop for tests (better compatibility)
