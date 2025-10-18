"""
Database connection and session management for SQLAlchemy.

This module provides:
- Async database engine with connection pooling
- Async session factory with proper transaction management
- Database initialization and health check utilities
- Dependency injection for FastAPI endpoints
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.pool import NullPool, QueuePool
from sqlalchemy import text, event
from sqlalchemy.engine import Engine

from app.core.config import settings


# Database Engine Configuration
def get_engine_config() -> dict:
    """
    Get database engine configuration based on environment.

    Returns:
        dict: Engine configuration with connection pooling settings
    """
    # Common configuration for all environments
    config = {
        "echo": settings.database_echo or settings.debug,  # Log SQL statements
        "echo_pool": settings.debug,  # Log connection pool activity in debug
        "pool_pre_ping": True,  # Verify connections before using them
        "pool_recycle": settings.database_pool_recycle,  # Recycle connections
        "pool_timeout": settings.database_pool_timeout,  # Wait for connection from pool
        "poolclass": QueuePool,
        "pool_size": settings.database_pool_size,  # Min connections
        "max_overflow": settings.database_max_overflow,  # Extra connections
        "connect_args": {
            "server_settings": {
                "application_name": settings.app_name,
            },
            "command_timeout": 60,  # Command timeout in seconds
            "timeout": 10,  # Connection timeout in seconds
        },
    }

    return config


# Create async database engine
engine: AsyncEngine = create_async_engine(
    str(settings.database_url),
    **get_engine_config()
)


# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Don't expire objects after commit
    autocommit=False,  # Manual transaction control
    autoflush=False,  # Manual flush control for better performance
)


# Dependency for FastAPI endpoints
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides a database session.

    Yields:
        AsyncSession: Database session with automatic transaction management

    Example:
        @app.get("/users/{user_id}")
        async def get_user(
            user_id: int,
            db: AsyncSession = Depends(get_db)
        ):
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            return user
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()  # Auto-commit on success
        except Exception:
            await session.rollback()  # Auto-rollback on error
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize database by creating all tables.

    Note: In production, use Alembic migrations instead.
    This is primarily for development and testing.
    """
    from app.models import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db() -> None:
    """
    Drop all database tables.

    WARNING: This will delete all data!
    Should only be used in testing environments.
    """
    from app.models import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def check_db_connection() -> bool:
    """
    Check if database connection is healthy.

    Returns:
        bool: True if connection is successful, False otherwise

    Example:
        @app.get("/health")
        async def health_check():
            db_healthy = await check_db_connection()
            return {"status": "healthy" if db_healthy else "unhealthy"}
    """
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        # Log the error in production
        print(f"Database connection check failed: {e}")
        return False


async def get_db_info() -> dict:
    """
    Get database connection information for debugging.

    Returns:
        dict: Database connection metadata
    """
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text(
                "SELECT version(), current_database(), current_user, inet_server_addr(), inet_server_port()"
            ))
            version, database, user, host, port = result.fetchone()

            return {
                "version": version,
                "database": database,
                "user": user,
                "host": host,
                "port": port,
                "pool_size": settings.database_pool_size,
                "max_overflow": settings.database_max_overflow,
                "is_async": True,
                "driver": "asyncpg",
            }
    except Exception as e:
        return {
            "error": str(e),
            "status": "connection_failed"
        }


async def close_db_connections() -> None:
    """
    Close all database connections.

    Should be called on application shutdown.
    """
    await engine.dispose()


# Event listeners for connection lifecycle (optional)
@event.listens_for(Engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """
    Event listener called when a new connection is created.
    Useful for setting up connection-specific configurations.
    """
    # Example: Set statement timeout for PostgreSQL
    # cursor = dbapi_conn.cursor()
    # cursor.execute("SET statement_timeout = '60s'")
    # cursor.close()
    pass


@event.listens_for(Engine, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    """
    Event listener called when a connection is retrieved from the pool.
    Useful for validating or logging connection usage.
    """
    pass
