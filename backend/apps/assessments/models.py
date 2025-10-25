"""
Assessment models for user onboarding data.
Stores user profile information for personalized training program generation.
"""

from typing import ClassVar

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedModel


class Assessment(TimeStampedModel):
    """
    User assessment data collected during onboarding.

    Stores information about user's sport, age, experience level,
    training availability, injury history, and equipment access.
    """

    class Sport(models.TextChoices):
        """Supported sports."""

        FOOTBALL = "football", _("Football")
        CRICKET = "cricket", _("Cricket")

    class ExperienceLevel(models.TextChoices):
        """Training experience levels."""

        BEGINNER = "beginner", _("Beginner")
        INTERMEDIATE = "intermediate", _("Intermediate")
        ADVANCED = "advanced", _("Advanced")

    class TrainingDays(models.TextChoices):
        """Weekly training frequency options."""

        TWO_THREE = "2-3", _("2-3 days per week")
        FOUR_FIVE = "4-5", _("4-5 days per week")
        SIX_SEVEN = "6-7", _("6-7 days per week")

    class Equipment(models.TextChoices):
        """Available equipment options."""

        NO_EQUIPMENT = "no_equipment", _("No Equipment")
        BASIC_EQUIPMENT = "basic_equipment", _("Basic Equipment")
        FULL_GYM = "full_gym", _("Full Gym")

    # User association - one assessment per user
    user: models.OneToOneField = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assessment",
        verbose_name=_("user"),
    )

    # Sport selection
    sport: models.CharField = models.CharField(
        _("sport"),
        max_length=20,
        choices=Sport.choices,
        help_text=_("Primary sport for training focus"),
    )

    # Age with validation
    age: models.PositiveSmallIntegerField = models.PositiveSmallIntegerField(
        _("age"),
        validators=[
            MinValueValidator(
                13, message=_("You must be at least 13 years old to use this service")
            ),
            MaxValueValidator(100, message=_("Please enter a valid age")),
        ],
        help_text=_("User age (13-100 years)"),
    )

    # Experience level
    experience_level: models.CharField = models.CharField(
        _("experience level"),
        max_length=20,
        choices=ExperienceLevel.choices,
        help_text=_("Current training experience level"),
    )

    # Training frequency
    training_days: models.CharField = models.CharField(
        _("training days"),
        max_length=10,
        choices=TrainingDays.choices,
        help_text=_("Days per week available for training"),
    )

    # Injury history (optional)
    injuries: models.CharField = models.CharField(
        _("injuries"),
        max_length=10,
        choices=[("no", _("No injuries")), ("yes", _("I have injury history"))],
        default="no",
        help_text=_("Current or recent injury status"),
    )

    # Equipment availability
    equipment: models.CharField = models.CharField(
        _("equipment"),
        max_length=20,
        choices=Equipment.choices,
        help_text=_("Available training equipment"),
    )

    class Meta:
        verbose_name = _("assessment")
        verbose_name_plural = _("assessments")
        db_table = "assessments"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["sport"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        """String representation of the assessment."""
        return f"Assessment for {self.user.email} - {self.sport}"

    @property
    def has_injuries(self) -> bool:
        """Check if user has reported injuries."""
        return self.injuries == "yes"
