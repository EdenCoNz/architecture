"""
Test data factories using factory_boy.

This module provides factories for creating test data with realistic
values. Factories make it easy to create test objects with sensible
defaults while allowing customization of specific fields.

Usage:
    # Create a user with default values
    user = UserFactory()

    # Create a user with custom values
    user = UserFactory(username="custom", email="custom@example.com")

    # Create multiple users
    users = UserFactory.create_batch(5)
"""

from typing import Any

import factory
from django.contrib.auth import get_user_model
from faker import Faker

fake = Faker()
User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating User instances for testing.

    Generates realistic user data with unique usernames and emails.
    """

    class Meta:
        model = User
        django_get_or_create = ("username",)

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    is_active = True
    is_staff = False
    is_superuser = False

    @factory.post_generation
    def password(self, create: bool, extracted: Any, **kwargs: Any) -> None:
        """
        Set user password after creation.

        Args:
            create: Whether object is being created or built
            extracted: Explicitly passed password value
            **kwargs: Additional arguments
        """
        if not create:
            return

        if extracted:
            self.set_password(extracted)
        else:
            self.set_password("testpass123")


class AdminUserFactory(UserFactory):
    """
    Factory for creating admin User instances.

    Creates users with staff and superuser privileges.
    """

    is_staff = True
    is_superuser = True
    username = factory.Sequence(lambda n: f"admin{n}")


class StaffUserFactory(UserFactory):
    """
    Factory for creating staff User instances.

    Creates users with staff privileges but not superuser.
    """

    is_staff = True
    is_superuser = False
    username = factory.Sequence(lambda n: f"staff{n}")


# Example of how to create custom factories for your models
# Uncomment and modify when you add your own models
#
# class ProductFactory(factory.django.DjangoModelFactory):
#     """Factory for creating Product instances."""
#
#     class Meta:
#         model = "apps.products.Product"
#
#     name = factory.Faker("word")
#     description = factory.Faker("text", max_nb_chars=200)
#     price = factory.Faker("pydecimal", left_digits=5, right_digits=2, positive=True)
#     created_by = factory.SubFactory(UserFactory)
