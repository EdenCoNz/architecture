"""
Serializers for user authentication and management.
"""

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    Used for displaying user information.
    """

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'is_active', 'date_joined')
        read_only_fields = ('id', 'date_joined', 'is_active')


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Validates password confirmation and creates new users.
    """

    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'password_confirm', 'first_name', 'last_name')
        read_only_fields = ('id',)

    def validate(self, attrs):
        """
        Validate that passwords match and meet requirements.
        """
        password = attrs.get('password')
        password_confirm = attrs.pop('password_confirm', None)

        if password != password_confirm:
            raise ValidationError({'password': 'Passwords do not match.'})

        # Validate password against Django's password validators
        validate_password(password)

        return attrs

    def create(self, validated_data):
        """
        Create a new user with encrypted password.
        """
        password = validated_data.pop('password')
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    Validates credentials and returns authenticated user.
    """

    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        write_only=True
    )

    def validate(self, attrs):
        """
        Validate user credentials.
        """
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            # Check if user exists and is active
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise ValidationError(
                    {'non_field_errors': ['Invalid credentials. Please try again.']}
                )

            if not user.is_active:
                raise ValidationError(
                    {'non_field_errors': ['This account has been deactivated.']}
                )

            # Authenticate user
            user = authenticate(
                request=self.context.get('request'),
                username=email,
                password=password
            )

            if not user:
                raise ValidationError(
                    {'non_field_errors': ['Invalid credentials. Please try again.']}
                )

            attrs['user'] = user
            return attrs
        else:
            raise ValidationError(
                {'non_field_errors': ['Email and password are required.']}
            )


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """

    old_password = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        write_only=True
    )
    new_password = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        write_only=True
    )
    new_password_confirm = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        write_only=True
    )

    def validate_old_password(self, value):
        """
        Validate that the old password is correct.
        """
        user = self.context['request'].user
        if not user.check_password(value):
            raise ValidationError('Old password is incorrect.')
        return value

    def validate(self, attrs):
        """
        Validate that new passwords match and meet requirements.
        """
        new_password = attrs.get('new_password')
        new_password_confirm = attrs.get('new_password_confirm')

        if new_password != new_password_confirm:
            raise ValidationError({'new_password': 'New passwords do not match.'})

        # Validate password against Django's password validators
        validate_password(new_password, user=self.context['request'].user)

        return attrs

    def save(self, **kwargs):
        """
        Update the user's password.
        """
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
