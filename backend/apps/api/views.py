"""
API views.
Placeholder file - views will be organized into separate modules as the API grows.
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


@api_view(['GET'])
def api_root(request):
    """
    API root endpoint.
    Returns basic information about the API.
    """
    return Response({
        'message': 'Welcome to the Backend API',
        'version': '1.0.0',
        'documentation': request.build_absolute_uri('/api/v1/docs/'),
    })
