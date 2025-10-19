"""
Data access layer (repository pattern).

This module contains repository classes that encapsulate database queries
and data access logic. Repositories abstract the data layer from business logic.

Repository Pattern:
    - Repositories handle all database operations
    - Complex queries are encapsulated in repository methods
    - Repositories return QuerySets or model instances
    - Repositories can be easily mocked for testing

Example:
    class UserRepository:
        def get_active_users(self):
            return User.objects.filter(is_active=True)

        def find_by_email(self, email):
            return User.objects.filter(email=email).first()
"""
