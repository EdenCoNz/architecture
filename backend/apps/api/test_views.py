"""
Test endpoint views for frontend-backend integration testing (Story-10.1).

This module provides a simple test endpoint that allows frontend developers
to verify connectivity between the frontend and backend applications.
"""

from datetime import datetime, timezone

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@extend_schema(
    operation_id="test_backend_connection",
    tags=["Testing"],
    description=(
        "Test endpoint for verifying frontend-backend connectivity. "
        "This endpoint returns a simple response with a success message and timestamp "
        "to confirm the backend is accessible and responding correctly. "
        "No authentication is required."
    ),
    responses={
        200: {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Success message indicating backend is operational",
                    "example": "Backend is operational",
                },
                "timestamp": {
                    "type": "string",
                    "format": "date-time",
                    "description": "ISO 8601 timestamp of when the response was generated",
                    "example": "2025-10-25T12:34:56.789Z",
                },
            },
            "required": ["message", "timestamp"],
        }
    },
    summary="Test backend connectivity",
)
@api_view(["GET"])
@permission_classes([AllowAny])
def test_connection(request):
    """
    Test endpoint for frontend-backend connectivity verification.

    This endpoint provides a simple way for frontend developers to verify
    that the frontend application can successfully communicate with the
    backend API.

    Acceptance Criteria:
    - Returns HTTP 200 success response
    - Includes a success message indicating backend is operational
    - Includes a timestamp showing when the response was generated
    - Accessible without authentication
    - CORS headers allow frontend application to receive the response

    Returns:
        Response: JSON response with message and timestamp
    """
    return Response(
        {
            "message": "Backend is operational",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
        status=status.HTTP_200_OK,
    )
