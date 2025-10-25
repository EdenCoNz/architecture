"""URL configuration for assessments app."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.assessments.views import AssessmentViewSet

router = DefaultRouter()
router.register(r"assessments", AssessmentViewSet, basename="assessment")

urlpatterns = [
    path("", include(router.urls)),
]
