"""
Business logic and service layer.

This module contains service classes that implement business logic,
orchestrate operations across multiple models/repositories, and
enforce business rules.

Service Pattern:
    - Services are stateless and focused on business logic
    - Services coordinate between repositories and external services
    - Services handle transactions and error handling
    - Services return domain objects, not database models directly

Example:
    class UserService:
        def create_user(self, data):
            # Validate business rules
            # Create user
            # Send welcome email
            # Return user object
"""
