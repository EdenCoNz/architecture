"""
User model for authentication and user management.

This module defines the User model with fields for:
- Authentication (email, password)
- Profile information (first_name, last_name)
- Account status (is_active, is_verified, is_superuser)
- Security tracking (last_login)
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, String, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class User(BaseModel):
    """
    User model for authentication and user management.

    Attributes:
        email: Unique email address for login
        hashed_password: Bcrypt hashed password
        first_name: User's first name
        last_name: User's last name
        is_active: Whether the account is active
        is_verified: Whether email has been verified
        is_superuser: Whether user has admin privileges
        last_login: Timestamp of last successful login
    """

    __tablename__ = "users"

    # Authentication fields
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Profile information
    first_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    last_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    # Account status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )

    # Security tracking
    last_login: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Composite indexes for common query patterns
    __table_args__ = (
        # Index for authentication queries
        Index("ix_users_email_active", "email", "is_active"),
        # Index for admin user queries
        Index("ix_users_superuser_active", "is_superuser", "is_active"),
    )

    def __repr__(self) -> str:
        """String representation of the user."""
        return f"<User(id={self.id}, email={self.email})>"

    @property
    def full_name(self) -> str:
        """
        Get user's full name.

        Returns:
            str: Full name or email if name not set
        """
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        return self.email
