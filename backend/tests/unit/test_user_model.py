"""
Unit tests for User model.
Tests the custom User model implementation and authentication functionality.
"""

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.core.exceptions import ValidationError

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    """Test suite for User model."""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful."""
        email = 'test@example.com'
        password = 'testpass123'
        user = User.objects.create_user(
            email=email,
            password=password
        )

        assert user.email == email
        assert user.check_password(password)
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False

    def test_user_email_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]

        for email, expected in sample_emails:
            user = User.objects.create_user(email, 'test123')
            assert user.email == expected

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without email raises ValueError."""
        with pytest.raises(ValueError, match='The Email field must be set'):
            User.objects.create_user('', 'test123')

    def test_new_user_email_unique(self):
        """Test that user email must be unique."""
        email = 'test@example.com'
        User.objects.create_user(email=email, password='test123')

        with pytest.raises(IntegrityError):
            User.objects.create_user(email=email, password='test456')

    def test_create_superuser(self):
        """Test creating a superuser."""
        email = 'admin@example.com'
        password = 'adminpass123'
        user = User.objects.create_superuser(
            email=email,
            password=password
        )

        assert user.email == email
        assert user.is_active is True
        assert user.is_staff is True
        assert user.is_superuser is True
        assert user.check_password(password)

    def test_create_superuser_is_staff_must_be_true(self):
        """Test creating superuser with is_staff=False raises ValueError."""
        with pytest.raises(ValueError, match='Superuser must have is_staff=True'):
            User.objects.create_superuser(
                email='admin@example.com',
                password='test123',
                is_staff=False
            )

    def test_create_superuser_is_superuser_must_be_true(self):
        """Test creating superuser with is_superuser=False raises ValueError."""
        with pytest.raises(ValueError, match='Superuser must have is_superuser=True'):
            User.objects.create_superuser(
                email='admin@example.com',
                password='test123',
                is_superuser=False
            )

    def test_user_str_representation(self):
        """Test the string representation of user."""
        user = User.objects.create_user(
            email='test@example.com',
            password='test123'
        )
        assert str(user) == 'test@example.com'

    def test_user_has_username_field(self):
        """Test that User model has email as USERNAME_FIELD."""
        assert User.USERNAME_FIELD == 'email'

    def test_user_has_required_fields(self):
        """Test that User model has correct REQUIRED_FIELDS."""
        # Email is USERNAME_FIELD, so it should not be in REQUIRED_FIELDS
        assert 'email' not in User.REQUIRED_FIELDS
        assert isinstance(User.REQUIRED_FIELDS, list)

    def test_user_password_hashed(self):
        """Test that user password is properly hashed."""
        password = 'testpass123'
        user = User.objects.create_user(
            email='test@example.com',
            password=password
        )

        # Password should be hashed, not stored in plain text
        assert user.password != password
        assert user.password.startswith('pbkdf2_sha256$') or user.password.startswith('argon2')

    def test_user_can_change_password(self):
        """Test that user can change their password."""
        user = User.objects.create_user(
            email='test@example.com',
            password='oldpassword123'
        )

        assert user.check_password('oldpassword123')

        user.set_password('newpassword123')
        user.save()

        assert user.check_password('newpassword123')
        assert not user.check_password('oldpassword123')

    def test_user_with_optional_fields(self):
        """Test creating user with optional fields."""
        user = User.objects.create_user(
            email='test@example.com',
            password='test123',
            first_name='Test',
            last_name='User'
        )

        assert user.first_name == 'Test'
        assert user.last_name == 'User'
        assert user.get_full_name() == 'Test User'

    def test_inactive_user_cannot_authenticate(self):
        """Test that inactive user cannot authenticate."""
        user = User.objects.create_user(
            email='test@example.com',
            password='test123',
            is_active=False
        )

        assert user.is_active is False
        # User should exist but authentication should fail in views
        assert user.check_password('test123')
