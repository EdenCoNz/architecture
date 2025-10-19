"""
Common utilities package.

This package contains shared code used across multiple Django apps.
It provides reusable components that don't belong to a specific feature.

Modules:
    middleware/     - Custom Django middleware components
    utils/          - General utility functions and helpers
    validators/     - Custom field validators
    exceptions/     - Custom exception classes
    mixins/         - Reusable class mixins
    serializers/    - Base serializer classes
    permissions/    - Custom DRF permission classes
    decorators/     - Function and class decorators

Best Practices:
    - Keep utilities generic and reusable
    - Document expected inputs and outputs
    - Write comprehensive unit tests for all utilities
    - Avoid circular dependencies with apps
"""
