"""
Database models.

All models should be imported here for:
1. Alembic autogenerate to detect them
2. Easy access throughout the application
"""
from app.models.base import Base, BaseModel
from app.models.user import User

# Export all models for Alembic autogenerate and application use
__all__ = [
    "Base",
    "BaseModel",
    "User",
]
