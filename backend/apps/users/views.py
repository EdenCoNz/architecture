"""
Authentication views for user registration, login, logout, and profile management.
"""

from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema, inline_serializer
from rest_framework import generics
from rest_framework import serializers as drf_serializers
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from .serializers import (
    ChangePasswordSerializer,
    UserLoginSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)

User = get_user_model()


@method_decorator(ratelimit(key="ip", rate="5/h", method="POST"), name="dispatch")
class UserRegistrationView(APIView):
    """
    View for user registration.
    Anyone can register a new account.
    Rate limited to 5 registrations per hour per IP address.
    """

    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    @extend_schema(
        summary="Register New User",
        description=(
            "Create a new user account. This endpoint allows anyone to register "
            "by providing email, password, and optional profile information. "
            "Password must meet security requirements (minimum 8 characters, not entirely numeric, etc.)."
        ),
        request=UserRegistrationSerializer,
        responses={
            201: OpenApiResponse(
                response=inline_serializer(
                    name="RegistrationResponse",
                    fields={
                        "message": drf_serializers.CharField(),
                        "user": UserSerializer(),
                    },
                ),
                description="User registered successfully",
                examples=[
                    OpenApiExample(
                        "Success Response",
                        value={
                            "message": "User registered successfully.",
                            "user": {
                                "id": 1,
                                "email": "user@example.com",
                                "first_name": "John",
                                "last_name": "Doe",
                                "is_active": True,
                                "date_joined": "2025-10-23T12:00:00Z",
                            },
                        },
                        response_only=True,
                    )
                ],
            ),
            400: OpenApiResponse(
                description="Validation error (passwords don't match, email already exists, etc.)",
                examples=[
                    OpenApiExample(
                        "Validation Error",
                        value={"password": ["Passwords do not match."]},
                        response_only=True,
                    ),
                    OpenApiExample(
                        "Email Already Exists",
                        value={"email": ["user with this email already exists."]},
                        response_only=True,
                    ),
                ],
            ),
        },
        examples=[
            OpenApiExample(
                "Registration Example",
                value={
                    "email": "user@example.com",
                    "password": "SecurePass123!",
                    "password_confirm": "SecurePass123!",
                    "first_name": "John",
                    "last_name": "Doe",
                },
                request_only=True,
            )
        ],
        tags=["Authentication"],
    )
    def post(self, request):
        """
        Handle user registration.
        Returns the created user data without tokens.
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            user_serializer = UserSerializer(user)

            return Response(
                {"message": "User registered successfully.", "user": user_serializer.data},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(ratelimit(key="ip", rate="10/m", method="POST"), name="dispatch")
class UserLoginView(APIView):
    """
    View for user login.
    Returns JWT access and refresh tokens on successful authentication.
    Rate limited to 10 login attempts per minute per IP address.
    """

    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer

    @extend_schema(
        summary="Login User",
        description=(
            "Authenticate a user and receive JWT tokens. "
            "The access token should be used for authenticating API requests "
            "(valid for 15 minutes). The refresh token can be used to obtain "
            "new access tokens without re-authenticating (valid for 7 days)."
        ),
        request=UserLoginSerializer,
        responses={
            200: OpenApiResponse(
                response=inline_serializer(
                    name="LoginResponse",
                    fields={
                        "message": drf_serializers.CharField(),
                        "user": UserSerializer(),
                        "access": drf_serializers.CharField(),
                        "refresh": drf_serializers.CharField(),
                    },
                ),
                description="Login successful",
                examples=[
                    OpenApiExample(
                        "Success Response",
                        value={
                            "message": "Login successful.",
                            "user": {
                                "id": 1,
                                "email": "user@example.com",
                                "first_name": "John",
                                "last_name": "Doe",
                                "is_active": True,
                                "date_joined": "2025-10-23T12:00:00Z",
                            },
                            "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                        },
                        response_only=True,
                    )
                ],
            ),
            400: OpenApiResponse(
                description="Invalid credentials or inactive account",
                examples=[
                    OpenApiExample(
                        "Invalid Credentials",
                        value={"non_field_errors": ["Invalid credentials. Please try again."]},
                        response_only=True,
                    ),
                    OpenApiExample(
                        "Inactive Account",
                        value={"non_field_errors": ["This account has been deactivated."]},
                        response_only=True,
                    ),
                ],
            ),
        },
        examples=[
            OpenApiExample(
                "Login Example",
                value={"email": "user@example.com", "password": "SecurePass123!"},
                request_only=True,
            )
        ],
        tags=["Authentication"],
    )
    def post(self, request):
        """
        Authenticate user and return JWT tokens.
        """
        serializer = self.serializer_class(data=request.data, context={"request": request})

        if serializer.is_valid():
            user = serializer.validated_data["user"]

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)

            # Serialize user data
            user_serializer = UserSerializer(user)

            return Response(
                {
                    "message": "Login successful.",
                    "user": user_serializer.data,
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogoutView(APIView):
    """
    View for user logout.
    Blacklists the refresh token to invalidate it.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Logout User",
        description=(
            "Logout the authenticated user by blacklisting their refresh token. "
            "After logout, the refresh token cannot be used to obtain new access tokens. "
            "Requires a valid access token in the Authorization header."
        ),
        request=inline_serializer(
            name="LogoutRequest",
            fields={
                "refresh": drf_serializers.CharField(help_text="The refresh token to blacklist"),
            },
        ),
        responses={
            200: OpenApiResponse(
                response=inline_serializer(
                    name="LogoutResponse",
                    fields={
                        "message": drf_serializers.CharField(),
                    },
                ),
                description="Logout successful",
                examples=[
                    OpenApiExample(
                        "Success Response",
                        value={"message": "Logout successful."},
                        response_only=True,
                    )
                ],
            ),
            400: OpenApiResponse(
                description="Invalid or missing refresh token",
                examples=[
                    OpenApiExample(
                        "Missing Token",
                        value={"error": "Refresh token is required."},
                        response_only=True,
                    ),
                    OpenApiExample(
                        "Invalid Token",
                        value={"error": "Invalid token or token already blacklisted."},
                        response_only=True,
                    ),
                ],
            ),
            401: OpenApiResponse(
                description="Authentication required",
            ),
        },
        examples=[
            OpenApiExample(
                "Logout Example",
                value={"refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."},
                request_only=True,
            )
        ],
        tags=["Authentication"],
    )
    def post(self, request):
        """
        Blacklist the refresh token.
        """
        try:
            refresh_token = request.data.get("refresh")

            if not refresh_token:
                return Response(
                    {"error": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST
                )

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"message": "Logout successful."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": "Invalid token or token already blacklisted."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom token refresh view.
    Extends the default TokenRefreshView with additional functionality.
    """

    @extend_schema(
        summary="Refresh Access Token",
        description=(
            "Obtain a new access token using a valid refresh token. "
            "Access tokens expire after 15 minutes, but refresh tokens are valid for 7 days. "
            "Use this endpoint to get a new access token without requiring the user to login again."
        ),
        request=inline_serializer(
            name="TokenRefreshRequest",
            fields={
                "refresh": drf_serializers.CharField(
                    help_text="Valid refresh token obtained from login"
                ),
            },
        ),
        responses={
            200: OpenApiResponse(
                response=inline_serializer(
                    name="TokenRefreshResponse",
                    fields={
                        "access": drf_serializers.CharField(help_text="New access token"),
                        "refresh": drf_serializers.CharField(
                            help_text="New refresh token (if rotation is enabled)"
                        ),
                    },
                ),
                description="Token refreshed successfully",
                examples=[
                    OpenApiExample(
                        "Success Response",
                        value={
                            "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                        },
                        response_only=True,
                    )
                ],
            ),
            401: OpenApiResponse(
                description="Invalid or expired refresh token",
                examples=[
                    OpenApiExample(
                        "Invalid Token",
                        value={"detail": "Token is invalid or expired", "code": "token_not_valid"},
                        response_only=True,
                    )
                ],
            ),
        },
        examples=[
            OpenApiExample(
                "Refresh Token Example",
                value={"refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."},
                request_only=True,
            )
        ],
        tags=["Authentication"],
    )
    def post(self, request, *args, **kwargs):
        """
        Handle token refresh requests.
        Delegates to the parent TokenRefreshView implementation.
        """
        return super().post(request, *args, **kwargs)


class CurrentUserView(APIView):
    """
    View for retrieving the current authenticated user's information.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get Current User",
        description=(
            "Retrieve the profile information of the currently authenticated user. "
            "Requires a valid access token in the Authorization header."
        ),
        responses={
            200: OpenApiResponse(
                response=UserSerializer,
                description="User profile retrieved successfully",
                examples=[
                    OpenApiExample(
                        "Success Response",
                        value={
                            "id": 1,
                            "email": "user@example.com",
                            "first_name": "John",
                            "last_name": "Doe",
                            "is_active": True,
                            "date_joined": "2025-10-23T12:00:00Z",
                        },
                        response_only=True,
                    )
                ],
            ),
            401: OpenApiResponse(
                description="Authentication required",
                examples=[
                    OpenApiExample(
                        "Unauthorized",
                        value={"detail": "Authentication credentials were not provided."},
                        response_only=True,
                    )
                ],
            ),
        },
        tags=["Users"],
    )
    def get(self, request):
        """
        Return the current user's data.
        """
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


@method_decorator(ratelimit(key="user", rate="5/h", method="POST"), name="dispatch")
class ChangePasswordView(APIView):
    """
    View for changing user password.
    Requires authentication.
    Rate limited to 5 password changes per hour per user.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    @extend_schema(
        summary="Change Password",
        description=(
            "Change the password for the currently authenticated user. "
            "Requires the current password for verification and the new password. "
            "New password must meet security requirements."
        ),
        request=ChangePasswordSerializer,
        responses={
            200: OpenApiResponse(
                response=inline_serializer(
                    name="ChangePasswordResponse",
                    fields={
                        "message": drf_serializers.CharField(),
                    },
                ),
                description="Password changed successfully",
                examples=[
                    OpenApiExample(
                        "Success Response",
                        value={"message": "Password changed successfully."},
                        response_only=True,
                    )
                ],
            ),
            400: OpenApiResponse(
                description="Validation error (incorrect old password, passwords don't match, etc.)",
                examples=[
                    OpenApiExample(
                        "Incorrect Old Password",
                        value={"old_password": ["Old password is incorrect."]},
                        response_only=True,
                    ),
                    OpenApiExample(
                        "Passwords Do Not Match",
                        value={"new_password": ["New passwords do not match."]},
                        response_only=True,
                    ),
                ],
            ),
            401: OpenApiResponse(
                description="Authentication required",
            ),
        },
        examples=[
            OpenApiExample(
                "Change Password Example",
                value={
                    "old_password": "OldPass123!",
                    "new_password": "NewSecurePass456!",
                    "new_password_confirm": "NewSecurePass456!",
                },
                request_only=True,
            )
        ],
        tags=["Users"],
    )
    def post(self, request):
        """
        Change the authenticated user's password.
        """
        serializer = self.serializer_class(data=request.data, context={"request": request})

        if serializer.is_valid():
            serializer.save()

            return Response(
                {"message": "Password changed successfully."}, status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
