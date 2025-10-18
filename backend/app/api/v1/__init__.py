"""
API v1 router configuration.

This module sets up the main API v1 router and includes all endpoint routers.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import health

# Create main API v1 router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(
    health.router,
    tags=["Health"],
)

# TODO: Include additional routers as they are created
# api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
# api_router.include_router(users.router, prefix="/users", tags=["Users"])

__all__ = ["api_router"]
