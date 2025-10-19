"""URL configuration for preferences app."""

from django.urls import path

from apps.preferences.views import ThemePreferenceView

app_name = "preferences"

urlpatterns = [
    path("theme/", ThemePreferenceView.as_view(), name="theme"),
]
