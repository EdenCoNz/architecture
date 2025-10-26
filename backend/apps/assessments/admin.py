"""
Admin configuration for Assessment model.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Assessment


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    """Admin interface for Assessment model."""

    # Fields to display in list view
    list_display = (
        "user",
        "sport",
        "age",
        "experience_level",
        "training_days",
        "equipment",
        "injuries",
        "created_at",
    )

    # Filters in sidebar
    list_filter = (
        "sport",
        "experience_level",
        "training_days",
        "equipment",
        "injuries",
        "created_at",
    )

    # Search fields
    search_fields = ("user__email", "user__first_name", "user__last_name")

    # Default ordering
    ordering = ("-created_at",)

    # Readonly fields
    readonly_fields = ("created_at", "updated_at")

    # Fields organization in detail view
    fieldsets = (
        (
            _("User Information"),
            {
                "fields": ("user",),
            },
        ),
        (
            _("Sport & Training"),
            {
                "fields": ("sport", "experience_level", "training_days"),
            },
        ),
        (
            _("Personal Details"),
            {
                "fields": ("age", "injuries", "equipment"),
            },
        ),
        (
            _("Timestamps"),
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    # Display user info in autocomplete
    autocomplete_fields = ["user"]

    # Number of items per page
    list_per_page = 25
