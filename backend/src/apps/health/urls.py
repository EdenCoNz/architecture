"""URL configuration for health check endpoints."""

from django.urls import path

from .views import HealthCheckView, LivenessView, ReadinessView

app_name = "health"

urlpatterns = [
    path("", HealthCheckView.as_view(), name="health"),
    path("live/", LivenessView.as_view(), name="liveness"),
    path("ready/", ReadinessView.as_view(), name="readiness"),
]
