"""
Health check endpoints for monitoring application status.

Provides comprehensive health checks for the application and its dependencies:
- Database connectivity
- Redis connectivity (when implemented)
- Overall application status
"""
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from typing import Dict, Any
import logging

from app.core.config import settings
from app.core.database import check_db_connection

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    tags=["Health"],
    summary="Application health check",
    description="Returns the health status of the application and its dependencies",
    response_description="Health status information",
)
async def health_check() -> JSONResponse:
    """
    Comprehensive health check endpoint.

    This endpoint checks the health of all critical application components:
    - Application status
    - Database connectivity
    - Redis connectivity (future)
    - Version information

    Returns:
        JSONResponse: Health status with HTTP 200 if healthy, 503 if degraded
    """
    checks: Dict[str, Any] = {}
    overall_healthy = True

    # Check database connection
    try:
        db_healthy = await check_db_connection()
        checks["database"] = {
            "status": "healthy" if db_healthy else "unhealthy",
            "message": "Database connection successful" if db_healthy else "Database connection failed",
        }
        if not db_healthy:
            overall_healthy = False
    except Exception as exc:
        logger.error(f"Health check - database error: {exc}", exc_info=True)
        checks["database"] = {
            "status": "unhealthy",
            "message": f"Database check failed: {str(exc)}",
        }
        overall_healthy = False

    # TODO: Check Redis connection
    # checks["redis"] = {
    #     "status": "healthy",
    #     "message": "Redis connection successful",
    # }

    # Determine HTTP status code
    http_status = status.HTTP_200_OK if overall_healthy else status.HTTP_503_SERVICE_UNAVAILABLE

    # Build response
    response_data = {
        "status": "healthy" if overall_healthy else "degraded",
        "environment": settings.environment,
        "version": settings.app_version,
        "checks": checks,
    }

    return JSONResponse(
        status_code=http_status,
        content=response_data,
    )


@router.get(
    "/health/live",
    status_code=status.HTTP_200_OK,
    tags=["Health"],
    summary="Liveness probe",
    description="Simple liveness check for Kubernetes/container orchestration",
    response_description="Returns 200 if application is running",
)
async def liveness_check() -> Dict[str, str]:
    """
    Liveness probe endpoint for container orchestration.

    This is a simple check that the application process is running.
    It does not check dependencies, making it suitable for Kubernetes
    liveness probes that should only restart the pod if the process is dead.

    Returns:
        dict: Simple status message
    """
    return {
        "status": "alive",
        "version": settings.app_version,
    }


@router.get(
    "/health/ready",
    status_code=status.HTTP_200_OK,
    tags=["Health"],
    summary="Readiness probe",
    description="Readiness check for Kubernetes/container orchestration",
    response_description="Returns 200 if application is ready to serve traffic",
)
async def readiness_check() -> JSONResponse:
    """
    Readiness probe endpoint for container orchestration.

    This checks that the application is ready to serve traffic by
    verifying that all critical dependencies are available.
    Suitable for Kubernetes readiness probes.

    Returns:
        JSONResponse: Ready status with HTTP 200 if ready, 503 if not ready
    """
    ready = True

    # Check database connection
    try:
        db_healthy = await check_db_connection()
        if not db_healthy:
            ready = False
    except Exception as exc:
        logger.error(f"Readiness check - database error: {exc}", exc_info=True)
        ready = False

    # TODO: Check Redis connection
    # TODO: Check other critical dependencies

    http_status = status.HTTP_200_OK if ready else status.HTTP_503_SERVICE_UNAVAILABLE

    return JSONResponse(
        status_code=http_status,
        content={
            "status": "ready" if ready else "not_ready",
            "version": settings.app_version,
        },
    )
