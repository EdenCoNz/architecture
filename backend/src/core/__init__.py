"""
Core business logic package.

This package contains shared domain models, business services,
and data access patterns used across the application.

Modules:
    models/         - Shared abstract models and base classes
    services/       - Business logic and service layer
    repositories/   - Data access layer (repository pattern)

Architecture:
    - Models: Define data structure and basic validation
    - Services: Implement business logic and orchestration
    - Repositories: Encapsulate database queries and data access

Best Practices:
    - Keep business logic in services, not views or models
    - Use repositories for complex queries and data access
    - Abstract models should be used for common fields/behaviors
    - Services should be stateless and testable
"""
