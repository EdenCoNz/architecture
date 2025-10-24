"""
API URL configuration for v1.
"""

from django.urls import include, path
from drf_spectacular.renderers import (
    OpenApiJsonRenderer,
    OpenApiJsonRenderer2,
    OpenApiYamlRenderer,
    OpenApiYamlRenderer2,
)
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

from apps.api.health_views import HealthCheckView, LivenessView, ReadinessView, StatusView

# Create a router for viewsets
router = DefaultRouter()

# Register viewsets here as they are created
# Example: router.register(r'users', UserViewSet, basename='user')

app_name = "api"

urlpatterns = [
    # Router URLs
    path("", include(router.urls)),
    # API Documentation
    # Schema endpoint with JSON renderer as first choice for better test compatibility
    path(
        "schema/",
        SpectacularAPIView.as_view(
            renderer_classes=[
                OpenApiJsonRenderer,
                OpenApiJsonRenderer2,
                OpenApiYamlRenderer,
                OpenApiYamlRenderer2,
            ]
        ),
        name="schema",
    ),
    path(
        "docs/",
        SpectacularSwaggerView.as_view(url_name="api:schema"),
        name="swagger-ui",
    ),
    path(
        "redoc/",
        SpectacularRedocView.as_view(url_name="api:schema"),
        name="redoc",
    ),
    # Health check endpoints (Story #5)
    path("health/", HealthCheckView.as_view(), name="health"),
    path("status/", StatusView.as_view(), name="status"),
    path("health/ready/", ReadinessView.as_view(), name="readiness"),
    path("health/live/", LivenessView.as_view(), name="liveness"),
]
