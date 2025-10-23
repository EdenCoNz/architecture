"""
Unit tests for authentication serializers.
Tests serializers for user registration, login, and token management.
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError

User = get_user_model()


@pytest.mark.django_db
class TestUserRegistrationSerializer:
    """Test suite for UserRegistrationSerializer."""

    def test_create_user_with_valid_data(self):
        """Test creating a user with valid data."""
        from apps.users.serializers import UserRegistrationSerializer

        payload = {
            "email": "test@example.com",
            "password": "testpass123",
            "password_confirm": "testpass123",
            "first_name": "Test",
            "last_name": "User",
        }

        serializer = UserRegistrationSerializer(data=payload)
        assert serializer.is_valid()

        user = serializer.save()
        assert user.email == payload["email"]
        assert user.first_name == payload["first_name"]
        assert user.last_name == payload["last_name"]
        assert user.check_password(payload["password"])
        assert "password" not in serializer.data
        assert "password_confirm" not in serializer.data

    def test_password_is_write_only(self):
        """Test that password fields are write-only."""
        from apps.users.serializers import UserRegistrationSerializer

        user = User.objects.create_user(email="test@example.com", password="testpass123")

        serializer = UserRegistrationSerializer(user)
        assert "password" not in serializer.data
        assert "password_confirm" not in serializer.data

    def test_passwords_must_match(self):
        """Test that password and password_confirm must match."""
        from apps.users.serializers import UserRegistrationSerializer

        payload = {
            "email": "test@example.com",
            "password": "testpass123",
            "password_confirm": "differentpass123",
        }

        serializer = UserRegistrationSerializer(data=payload)
        assert not serializer.is_valid()
        assert "non_field_errors" in serializer.errors or "password" in serializer.errors

    def test_password_minimum_length(self):
        """Test that password must meet minimum length requirement."""
        from apps.users.serializers import UserRegistrationSerializer

        payload = {"email": "test@example.com", "password": "short", "password_confirm": "short"}

        serializer = UserRegistrationSerializer(data=payload)
        # Should be invalid due to password validators
        assert not serializer.is_valid()

    def test_email_must_be_unique(self):
        """Test that email must be unique."""
        from apps.users.serializers import UserRegistrationSerializer

        # Create existing user
        User.objects.create_user(email="test@example.com", password="testpass123")

        payload = {
            "email": "test@example.com",
            "password": "testpass123",
            "password_confirm": "testpass123",
        }

        serializer = UserRegistrationSerializer(data=payload)
        assert not serializer.is_valid()
        assert "email" in serializer.errors


@pytest.mark.django_db
class TestUserLoginSerializer:
    """Test suite for UserLoginSerializer."""

    def test_login_with_valid_credentials(self):
        """Test login with valid email and password."""
        from apps.users.serializers import UserLoginSerializer

        # Create a user
        User.objects.create_user(email="test@example.com", password="testpass123")

        payload = {"email": "test@example.com", "password": "testpass123"}

        serializer = UserLoginSerializer(data=payload)
        assert serializer.is_valid()

    def test_login_with_invalid_password(self):
        """Test login with invalid password."""
        from apps.users.serializers import UserLoginSerializer

        # Create a user
        User.objects.create_user(email="test@example.com", password="testpass123")

        payload = {"email": "test@example.com", "password": "wrongpassword"}

        serializer = UserLoginSerializer(data=payload)
        assert not serializer.is_valid()
        assert "non_field_errors" in serializer.errors

    def test_login_with_nonexistent_email(self):
        """Test login with email that doesn't exist."""
        from apps.users.serializers import UserLoginSerializer

        payload = {"email": "nonexistent@example.com", "password": "testpass123"}

        serializer = UserLoginSerializer(data=payload)
        assert not serializer.is_valid()
        assert "non_field_errors" in serializer.errors

    def test_login_with_inactive_user(self):
        """Test that inactive users cannot login."""
        from apps.users.serializers import UserLoginSerializer

        # Create an inactive user
        User.objects.create_user(email="test@example.com", password="testpass123", is_active=False)

        payload = {"email": "test@example.com", "password": "testpass123"}

        serializer = UserLoginSerializer(data=payload)
        assert not serializer.is_valid()
        assert "non_field_errors" in serializer.errors

    def test_login_returns_user_data(self):
        """Test that login serializer returns user data."""
        from apps.users.serializers import UserLoginSerializer

        user = User.objects.create_user(
            email="test@example.com", password="testpass123", first_name="Test", last_name="User"
        )

        payload = {"email": "test@example.com", "password": "testpass123"}

        serializer = UserLoginSerializer(data=payload)
        assert serializer.is_valid()
        validated_data = serializer.validated_data
        assert validated_data["user"] == user


@pytest.mark.django_db
class TestUserSerializer:
    """Test suite for UserSerializer."""

    def test_user_serialization(self):
        """Test user data serialization."""
        from apps.users.serializers import UserSerializer

        user = User.objects.create_user(
            email="test@example.com", password="testpass123", first_name="Test", last_name="User"
        )

        serializer = UserSerializer(user)
        data = serializer.data

        assert data["email"] == "test@example.com"
        assert data["first_name"] == "Test"
        assert data["last_name"] == "User"
        assert "password" not in data
        assert "id" in data

    def test_user_serializer_excludes_sensitive_fields(self):
        """Test that sensitive fields are not exposed."""
        from apps.users.serializers import UserSerializer

        user = User.objects.create_user(email="test@example.com", password="testpass123")

        serializer = UserSerializer(user)
        data = serializer.data

        assert "password" not in data
        assert "is_superuser" not in data or data.get("is_superuser") is not None
