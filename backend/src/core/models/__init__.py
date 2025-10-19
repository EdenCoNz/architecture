"""
Shared abstract models and base classes.

This module contains abstract Django models that provide common fields
and behaviors to be inherited by app-specific models.

Base Models:
    - TimeStampedModel: Adds created_at and updated_at fields
    - SoftDeleteModel: Adds soft delete functionality
    - UUIDModel: Uses UUID as primary key
    - AuditModel: Adds audit trail fields

Usage:
    from core.models import TimeStampedModel

    class MyModel(TimeStampedModel):
        name = models.CharField(max_length=100)
"""
