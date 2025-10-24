"""
Core models - Base models and abstract classes.
"""

from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """
    Abstract base model that provides created_at and updated_at fields.
    """

    created_at: models.DateTimeField = models.DateTimeField(
        auto_now_add=True, db_index=True
    )  # type: ignore[assignment]
    updated_at: models.DateTimeField = models.DateTimeField(
        auto_now=True
    )  # type: ignore[assignment]

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class SoftDeleteModel(models.Model):
    """
    Abstract base model that provides soft delete functionality.
    """

    is_deleted: models.BooleanField = models.BooleanField(
        default=False, db_index=True
    )  # type: ignore[assignment]
    deleted_at: models.DateTimeField = models.DateTimeField(
        null=True, blank=True
    )  # type: ignore[assignment]

    class Meta:
        abstract = True

    def soft_delete(self) -> None:
        """Mark the object as deleted."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at"])

    def restore(self) -> None:
        """Restore a soft-deleted object."""
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=["is_deleted", "deleted_at"])
