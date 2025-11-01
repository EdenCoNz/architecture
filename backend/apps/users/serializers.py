"""
Serializers for user authentication and management.
"""

import re
from typing import Any, Dict

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

User = get_user_model()


def sanitize_html_input(value: str) -> str:
    """
    Sanitize input by removing HTML tags and script content.
    This prevents XSS attacks by stripping potentially dangerous HTML.
    """
    if not value:
        return value
    # Remove script tags and their content
    value = re.sub(r"<script[^>]*>.*?</script>", "", value, flags=re.IGNORECASE | re.DOTALL)
    # Remove all HTML tags
    value = re.sub(r"<[^>]+>", "", value)
    return value


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    Used for displaying user information.
    """

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "date_joined",
        )
        read_only_fields = ("id", "date_joined", "is_active")


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Validates password confirmation and creates new users.
    """

    password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )
    password_confirm = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
        )
        read_only_fields = ("id",)

    def validate_first_name(self, value: str) -> str:
        """Sanitize first name to prevent XSS attacks."""
        return sanitize_html_input(value)

    def validate_last_name(self, value: str) -> str:
        """Sanitize last name to prevent XSS attacks."""
        return sanitize_html_input(value)

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate that passwords match and meet requirements.
        """
        password = attrs.get("password")
        password_confirm = attrs.pop("password_confirm", None)

        if password != password_confirm:
            raise ValidationError({"password": "Passwords do not match."})

        # Validate password against Django's password validators
        validate_password(password)

        return attrs

    def create(self, validated_data: Dict[str, Any]) -> Any:
        """
        Create a new user with encrypted password.
        """
        pwd = validated_data.pop("password")
        user = User.objects.create_user(  # type: ignore[attr-defined]
            password=pwd, **validated_data
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    Validates credentials and returns authenticated user.
    """

    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True, style={"input_type": "password"}, write_only=True
    )

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate user credentials.
        """
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            # Check if user exists and is active
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise ValidationError(
                    {"non_field_errors": ["Invalid credentials. Please try again."]}
                )

            if not user.is_active:
                raise ValidationError({"non_field_errors": ["This account has been deactivated."]})

            # Authenticate user
            authenticated_user = authenticate(
                request=self.context.get("request"),
                username=email,
                password=password,
            )

            if not authenticated_user:
                raise ValidationError(
                    {"non_field_errors": ["Invalid credentials. Please try again."]}
                )

            attrs["user"] = authenticated_user
            return attrs
        else:
            raise ValidationError({"non_field_errors": ["Email and password are required."]})


class BasicLoginSerializer(serializers.Serializer):
    """
    Serializer for basic login/registration.
    Allows users to authenticate using only name and email.
    """

    name = serializers.CharField(
        required=True, max_length=255, help_text="User's full name (first and last name)"
    )
    email = serializers.EmailField(
        required=True, max_length=254, help_text="User's email address (unique identifier)"
    )

    def validate_name(self, value: str) -> str:
        """
        Validate and sanitize name to prevent XSS attacks.
        """
        if not value or not value.strip():
            raise ValidationError("This field may not be blank.")
        return sanitize_html_input(value)

    def validate_email(self, value: str) -> str:
        """
        Validate email format and normalize to lowercase.
        """
        if not value:
            raise ValidationError("This field is required.")
        # Normalize email to lowercase for consistency
        return value.lower()

    def parse_name(self, full_name: str) -> tuple[str, str]:
        """
        Split full name into first and last name.

        Args:
            full_name: User's full name

        Returns:
            Tuple of (first_name, last_name)
        """
        full_name = full_name.strip()
        parts = full_name.split(" ", 1)

        if len(parts) == 1:
            return parts[0], ""

        return parts[0], parts[1]

    def create_or_update_user(self, validated_data: Dict[str, Any]) -> tuple[Any, bool]:
        """
        Create or update user for basic login.

        Args:
            validated_data: Validated name and email

        Returns:
            Tuple of (user, is_new_user)
        """
        email = validated_data["email"]
        name = validated_data["name"]

        first_name, last_name = self.parse_name(name)

        # Sanitize name fields
        first_name = sanitize_html_input(first_name)
        last_name = sanitize_html_input(last_name)

        # Check if user exists
        try:
            user = User.objects.get(email=email)
            # Update name if changed
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            is_new_user = False
        except User.DoesNotExist:
            # Create new user without password
            user = User.objects.create(
                email=email,
                first_name=first_name,
                last_name=last_name,
                is_active=True,
            )
            is_new_user = True

        return user, is_new_user


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """

    old_password = serializers.CharField(
        required=True, style={"input_type": "password"}, write_only=True
    )
    new_password = serializers.CharField(
        required=True, style={"input_type": "password"}, write_only=True
    )
    new_password_confirm = serializers.CharField(
        required=True, style={"input_type": "password"}, write_only=True
    )

    def validate_old_password(self, value: str) -> str:
        """
        Validate that the old password is correct.
        """
        user = self.context["request"].user
        if not user.check_password(value):
            raise ValidationError("Old password is incorrect.")
        return value

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate that new passwords match and meet requirements.
        """
        new_password = attrs.get("new_password")
        new_password_confirm = attrs.get("new_password_confirm")

        if new_password != new_password_confirm:
            raise ValidationError({"new_password": "New passwords do not match."})

        # Validate password against Django's password validators
        if new_password:
            validate_password(str(new_password), user=self.context["request"].user)

        return attrs

    def save(self, **kwargs: Any) -> Any:
        """
        Update the user's password.
        """
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user
