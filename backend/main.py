"""
FastAPI application entry point.

This module initializes the FastAPI application with middleware,
CORS, exception handlers, and API routes.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import check_db_connection, close_db_connections
from app.core.logging import setup_logging, get_logger
from app.middleware import RequestLoggingMiddleware, ErrorHandlingMiddleware
from app.api.v1 import api_router

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Initialize FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    openapi_url=settings.openapi_url if not settings.is_production else None,
    docs_url=settings.docs_url if not settings.is_production else None,
    redoc_url=settings.redoc_url if not settings.is_production else None,
    description="Production-ready FastAPI backend with PostgreSQL, Redis, and JWT authentication",
)


# Add custom middleware (order matters - first added is outermost)
# 1. Error handling middleware (catches all exceptions)
app.add_middleware(ErrorHandlingMiddleware)

# 2. Request logging middleware (logs all requests/responses)
app.add_middleware(RequestLoggingMiddleware)

# 3. CORS middleware (handles cross-origin requests)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# 4. Trusted host middleware for production security (validates Host header)
if settings.is_production:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.cors_origins
    )


@app.on_event("startup")
async def startup_event():
    """
    Application startup event handler.
    Initialize database connections, Redis, and other resources.
    """
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")

    # Check database connection
    logger.info("Checking database connection...")
    db_healthy = await check_db_connection()
    if db_healthy:
        logger.info("✓ Database connection established successfully")
    else:
        logger.error("✗ Database connection failed - application may not function correctly")

    # TODO: Initialize Redis connection
    # TODO: Run database migrations check

    logger.info("Application startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown event handler.
    Clean up database connections, Redis, and other resources.
    """
    logger.info("Shutting down application...")

    # Close database connections
    logger.info("Closing database connections...")
    await close_db_connections()
    logger.info("✓ Database connections closed")

    # TODO: Close Redis connection

    logger.info("Application shutdown complete")


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint returning basic API information.
    """
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "docs": settings.docs_url if not settings.is_production else None,
        "redoc": settings.redoc_url if not settings.is_production else None,
    }


# Include API v1 router
app.include_router(api_router, prefix=settings.api_v1_prefix)


# Backward compatibility: Keep root /health endpoint
# (also available at /api/v1/health)
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.

    Note: This endpoint is also available at /api/v1/health
    This root endpoint is kept for backward compatibility with monitoring tools.

    Returns:
        dict: Health status of the application and its dependencies
    """
    # Check database connection
    db_healthy = await check_db_connection()

    # Determine overall status
    status = "healthy" if db_healthy else "degraded"

    return {
        "status": status,
        "environment": settings.environment,
        "version": settings.app_version,
        "checks": {
            "database": "healthy" if db_healthy else "unhealthy",
            # TODO: Add Redis health check
        }
    }


# Note: Exception handlers are now handled by ErrorHandlingMiddleware
# which provides more comprehensive error handling with consistent JSON responses


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
