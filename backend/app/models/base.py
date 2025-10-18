"""
Base model class with common fields for all database models.

All models should inherit from this base class to get standard fields:
- id: Primary key (UUID)
- created_at: Timestamp of record creation
- updated_at: Timestamp of last record update
"""
from datetime import datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    # SQLAlchemy 2.0 style type annotation support
    type_annotation_map = {
        datetime: DateTime(timezone=True),
    }


class BaseModel(Base):
    """
    Abstract base model with common fields.

    Attributes:
        id: UUID primary key
        created_at: Timestamp when record was created
        updated_at: Timestamp when record was last updated
    """

    __abstract__ = True

    # Primary key - UUID for better scalability and security
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
        unique=True,
        nullable=False,
        index=True,
    )

    # Timestamps - automatically managed
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        """String representation of the model."""
        return f"<{self.__class__.__name__}(id={self.id})>"

    def to_dict(self) -> dict[str, Any]:
        """
        Convert model instance to dictionary.

        Returns:
            dict: Dictionary representation of the model
        """
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
