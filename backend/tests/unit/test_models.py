"""
Unit tests for database models.

This module demonstrates testing patterns for SQLAlchemy models,
including model creation, relationships, validation, and utility methods.
"""
import pytest
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models.user import User


@pytest.mark.unit
@pytest.mark.database
class TestUserModel:
    """Test suite for User model."""

    @pytest.mark.asyncio
    async def test_user_creation_with_required_fields(self, db_session):
        """Test creating a user with only required fields."""
        # Arrange
        user_data = {
            "email": "test@example.com",
            "hashed_password": "hashed_password_value"
        }

        # Act
        user = User(**user_data)
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Assert
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.hashed_password == "hashed_password_value"
        assert user.is_active is True  # Default value
        assert user.is_verified is False  # Default value
        assert user.is_superuser is False  # Default value
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)

    @pytest.mark.asyncio
    async def test_user_creation_with_all_fields(self, db_session):
        """Test creating a user with all fields populated."""
        # Arrange
        user_data = {
            "email": "full@example.com",
            "hashed_password": "hashed_password",
            "first_name": "John",
            "last_name": "Doe",
            "is_active": True,
            "is_verified": True,
            "is_superuser": False,
        }

        # Act
        user = User(**user_data)
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Assert
        assert user.email == "full@example.com"
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.is_active is True
        assert user.is_verified is True
        assert user.is_superuser is False

    @pytest.mark.asyncio
    async def test_user_email_must_be_unique(self, db_session):
        """Test that email field has unique constraint."""
        # Arrange
        email = "unique@example.com"
        user1 = User(email=email, hashed_password="pass1")
        user2 = User(email=email, hashed_password="pass2")

        # Act & Assert
        db_session.add(user1)
        await db_session.commit()

        db_session.add(user2)
        with pytest.raises(IntegrityError):
            await db_session.commit()

    @pytest.mark.asyncio
    async def test_user_full_name_property_with_names(self, db_session):
        """Test full_name property returns first and last name."""
        # Arrange
        user = User(
            email="name@example.com",
            hashed_password="pass",
            first_name="Jane",
            last_name="Smith"
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Act
        full_name = user.full_name

        # Assert
        assert full_name == "Jane Smith"

    @pytest.mark.asyncio
    async def test_user_full_name_property_without_names(self, db_session):
        """Test full_name property falls back to email when names are None."""
        # Arrange
        user = User(
            email="fallback@example.com",
            hashed_password="pass"
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Act
        full_name = user.full_name

        # Assert
        assert full_name == "fallback@example.com"

    @pytest.mark.asyncio
    async def test_user_full_name_property_with_partial_names(self, db_session):
        """Test full_name property with only first or last name."""
        # Arrange - only first name
        user1 = User(
            email="first@example.com",
            hashed_password="pass",
            first_name="John"
        )
        db_session.add(user1)
        await db_session.commit()
        await db_session.refresh(user1)

        # Assert
        assert user1.full_name == "John"

        # Arrange - only last name
        user2 = User(
            email="last@example.com",
            hashed_password="pass",
            last_name="Doe"
        )
        db_session.add(user2)
        await db_session.commit()
        await db_session.refresh(user2)

        # Assert
        assert user2.full_name == "Doe"

    @pytest.mark.asyncio
    async def test_user_created_at_auto_populated(self, db_session):
        """Test that created_at is automatically set on creation."""
        # Arrange
        before_creation = datetime.now(timezone.utc)
        user = User(email="time@example.com", hashed_password="pass")

        # Act
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        after_creation = datetime.now(timezone.utc)

        # Assert
        assert user.created_at is not None
        assert before_creation <= user.created_at.replace(tzinfo=timezone.utc) <= after_creation

    @pytest.mark.asyncio
    async def test_user_updated_at_changes_on_update(self, db_session):
        """Test that updated_at changes when user is updated."""
        # Arrange - create user
        user = User(email="update@example.com", hashed_password="pass")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        original_updated_at = user.updated_at

        # Act - update user
        user.first_name = "Updated"
        await db_session.commit()
        await db_session.refresh(user)

        # Assert
        assert user.updated_at > original_updated_at

    @pytest.mark.asyncio
    async def test_user_query_by_email(self, db_session):
        """Test querying user by email."""
        # Arrange
        user = User(email="query@example.com", hashed_password="pass")
        db_session.add(user)
        await db_session.commit()

        # Act
        result = await db_session.execute(
            select(User).where(User.email == "query@example.com")
        )
        found_user = result.scalar_one_or_none()

        # Assert
        assert found_user is not None
        assert found_user.email == "query@example.com"
        assert found_user.id == user.id

    @pytest.mark.asyncio
    async def test_user_query_active_users(self, db_session):
        """Test querying only active users."""
        # Arrange - create active and inactive users
        active_user = User(email="active@example.com", hashed_password="pass", is_active=True)
        inactive_user = User(email="inactive@example.com", hashed_password="pass", is_active=False)
        db_session.add_all([active_user, inactive_user])
        await db_session.commit()

        # Act
        result = await db_session.execute(
            select(User).where(User.is_active == True)
        )
        active_users = result.scalars().all()

        # Assert
        assert len(active_users) == 1
        assert active_users[0].email == "active@example.com"

    @pytest.mark.asyncio
    async def test_user_query_superusers(self, db_session):
        """Test querying only superuser users."""
        # Arrange
        regular_user = User(email="regular@example.com", hashed_password="pass", is_superuser=False)
        super_user = User(email="super@example.com", hashed_password="pass", is_superuser=True)
        db_session.add_all([regular_user, super_user])
        await db_session.commit()

        # Act
        result = await db_session.execute(
            select(User).where(User.is_superuser == True)
        )
        superusers = result.scalars().all()

        # Assert
        assert len(superusers) == 1
        assert superusers[0].email == "super@example.com"

    @pytest.mark.asyncio
    async def test_user_last_login_nullable(self, db_session):
        """Test that last_login can be None for new users."""
        # Arrange
        user = User(email="nologin@example.com", hashed_password="pass")

        # Act
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Assert
        assert user.last_login is None

    @pytest.mark.asyncio
    async def test_user_update_last_login(self, db_session):
        """Test updating last_login timestamp."""
        # Arrange
        user = User(email="login@example.com", hashed_password="pass")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Act
        login_time = datetime.now(timezone.utc)
        user.last_login = login_time
        await db_session.commit()
        await db_session.refresh(user)

        # Assert
        assert user.last_login is not None
        assert user.last_login.replace(tzinfo=timezone.utc) == login_time.replace(microsecond=0)

    @pytest.mark.asyncio
    async def test_user_repr_method(self, db_session):
        """Test __repr__ method returns expected string."""
        # Arrange
        user = User(email="repr@example.com", hashed_password="pass")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Act
        repr_string = repr(user)

        # Assert
        assert "User" in repr_string
        assert str(user.id) in repr_string

    @pytest.mark.asyncio
    async def test_user_to_dict_method(self, db_session):
        """Test to_dict method returns dictionary representation."""
        # Arrange
        user = User(
            email="dict@example.com",
            hashed_password="pass",
            first_name="Dict",
            last_name="Test"
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Act
        user_dict = user.to_dict()

        # Assert
        assert isinstance(user_dict, dict)
        assert user_dict["email"] == "dict@example.com"
        assert user_dict["first_name"] == "Dict"
        assert user_dict["last_name"] == "Test"
        assert "id" in user_dict
        assert "created_at" in user_dict
        assert "updated_at" in user_dict
        # Password should not be in dict
        assert "hashed_password" not in user_dict
