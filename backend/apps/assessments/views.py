"""
Views for Assessment API endpoints.
Handles CRUD operations for user assessment data.
"""

from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer

from apps.assessments.models import Assessment
from apps.assessments.serializers import AssessmentSerializer
from apps.assessments.services import EquipmentService


class AssessmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user assessments.

    Provides endpoints for creating, retrieving, and updating user assessment data.
    Users can only access their own assessment data.
    """

    serializer_class = AssessmentSerializer
    permission_classes = [IsAuthenticated]
    queryset = Assessment.objects.all()

    def get_queryset(self):
        """
        Return assessments for the authenticated user only.

        Returns:
            QuerySet of Assessment objects for the current user
        """
        return Assessment.objects.filter(user=self.request.user)

    def perform_create(self, serializer: BaseSerializer) -> None:
        """
        Create assessment associated with authenticated user.

        Args:
            serializer: Validated serializer instance

        Raises:
            ValidationError: If user already has an assessment
        """
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Create a new assessment for the authenticated user.

        Args:
            request: HTTP request object

        Returns:
            Response with created assessment data or error
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED, headers=headers
            )
        except Exception as e:
            # Handle database integrity errors (e.g., duplicate assessment)
            return Response(
                {
                    "detail": "Unable to save assessment. You may already have an assessment."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request: Request) -> Response:
        """
        Retrieve the current user's assessment.

        This endpoint provides a convenient way to retrieve the authenticated
        user's assessment without needing to know the assessment ID.
        Used for program generation and profile display.

        Args:
            request: HTTP request object

        Returns:
            Response with assessment data or 404 if no assessment exists
        """
        try:
            assessment = Assessment.objects.get(user=request.user)
            serializer = self.get_serializer(assessment)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Assessment.DoesNotExist:
            return Response(
                {"detail": "No assessment found for this user."},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=False, methods=["get"], url_path="equipment-options")
    def equipment_options(self, request: Request) -> Response:
        """
        Retrieve predefined equipment options.

        This endpoint provides the list of predefined equipment items
        that users can select when specifying basic equipment during assessment.
        Options are configurable via system settings.

        Story 19.11: Predefined Equipment Options Management

        Args:
            request: HTTP request object

        Returns:
            Response with list of equipment options
        """
        options = EquipmentService.get_predefined_options()
        return Response({"options": options}, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Get available sport choices",
        description=(
            "Retrieve the list of available sports with both internal values "
            "and user-friendly display labels.\n\n"
            "**Story 21.3: Maintain Football Display Label for Users**\n\n"
            "The API returns sport choices where:\n"
            "- `value`: Internal database identifier (e.g., 'soccer')\n"
            "- `display_name`: User-facing display label (e.g., 'Football')\n\n"
            "This allows the frontend to show user-friendly labels while "
            "submitting correct internal values to the API."
        ),
        responses={
            200: OpenApiResponse(
                description="List of sport choices with display labels",
                response={
                    "type": "object",
                    "properties": {
                        "choices": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "value": {
                                        "type": "string",
                                        "description": "Internal database value",
                                        "example": "soccer",
                                    },
                                    "display_name": {
                                        "type": "string",
                                        "description": "User-friendly display label",
                                        "example": "Football",
                                    },
                                },
                                "required": ["value", "display_name"],
                            },
                            "example": [
                                {"value": "soccer", "display_name": "Football"},
                                {"value": "cricket", "display_name": "Cricket"},
                            ],
                        }
                    },
                },
            ),
        },
        tags=["assessments"],
    )
    @action(detail=False, methods=["get"], url_path="sport-choices")
    def sport_choices(self, request: Request) -> Response:
        """
        Retrieve available sport choices with display labels.

        This endpoint provides the list of available sports with both
        internal values and user-friendly display labels. This allows
        the frontend to present user-friendly labels while sending
        correct internal values to the API.

        Story 21.3: Maintain Football Display Label for Users

        Args:
            request: HTTP request object

        Returns:
            Response with list of sport choices, each containing:
            - value: Internal database value (e.g., "soccer")
            - display_name: User-friendly label (e.g., "Football")

        Example Response:
            {
                "choices": [
                    {"value": "soccer", "display_name": "Football"},
                    {"value": "cricket", "display_name": "Cricket"}
                ]
            }
        """
        choices = [
            {
                "value": value,
                "display_name": label,
            }
            for value, label in Assessment.Sport.choices
        ]
        return Response({"choices": choices}, status=status.HTTP_200_OK)
