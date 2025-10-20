"""Views for user preferences API."""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.preferences.models import UserPreferences
from apps.preferences.serializers import UserPreferencesSerializer


@extend_schema_view(
    get=extend_schema(
        summary="Get user theme preference",
        description="Retrieve the authenticated user's theme preference. "
        "Creates default preferences (auto theme) if none exist.",
        responses={200: UserPreferencesSerializer},
        tags=["Preferences"],
    ),
    patch=extend_schema(
        summary="Update user theme preference",
        description="Update the authenticated user's theme preference. "
        "Creates preferences if none exist.",
        request=UserPreferencesSerializer,
        responses={200: UserPreferencesSerializer},
        tags=["Preferences"],
    ),
)
class ThemePreferenceView(APIView):
    """
    API view for managing user theme preferences.

    Handles GET and PATCH requests to retrieve and update theme preferences.
    Automatically creates default preferences if they don't exist.

    Endpoints:
        GET /api/preferences/theme/ - Get current theme preference
        PATCH /api/preferences/theme/ - Update theme preference

    Authentication:
        Requires user authentication
    """

    def get(self, request: Request) -> Response:
        """
        Get the authenticated user's theme preference.

        Creates default preferences with 'auto' theme if none exist.

        Args:
            request: HTTP request with authenticated user

        Returns:
            Response: Serialized theme preference data
        """
        preferences, created = UserPreferences.objects.get_or_create(
            user=request.user, defaults={"theme": "auto"}
        )

        serializer = UserPreferencesSerializer(preferences)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request: Request) -> Response:
        """
        Update the authenticated user's theme preference.

        Creates preferences if they don't exist. Performs partial update
        allowing only the theme field to be updated.

        Args:
            request: HTTP request with theme data and authenticated user

        Returns:
            Response: Updated serialized theme preference data or validation errors
        """
        preferences, created = UserPreferences.objects.get_or_create(
            user=request.user, defaults={"theme": "auto"}
        )

        serializer = UserPreferencesSerializer(preferences, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
