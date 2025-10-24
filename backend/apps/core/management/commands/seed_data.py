"""
Management command to seed the database with test data.
This is useful for development and testing environments.
"""

import sys
from typing import Any

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError, CommandParser
from django.db import transaction

User = get_user_model()


class Command(BaseCommand):
    help = "Seeds the database with test data for development and testing"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing data before seeding (DANGEROUS!)",
        )
        parser.add_argument(
            "--users",
            type=int,
            default=10,
            help="Number of test users to create (default: 10)",
        )
        parser.add_argument(
            "--admin",
            action="store_true",
            help="Create admin user (admin@example.com / admin123)",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        # Safety check: never run in production
        if not settings.DEBUG:
            raise CommandError(
                "Cannot seed data in production! " "This command only works when DEBUG=True."
            )

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=" * 70))
        self.stdout.write(self.style.SUCCESS("Database Seeding Tool"))
        self.stdout.write(self.style.SUCCESS("=" * 70))
        self.stdout.write("")

        # Confirm clear operation
        if options["clear"]:
            self.stdout.write(self.style.WARNING("⚠ WARNING: This will DELETE all existing data!"))
            confirm = input("Are you sure you want to continue? (yes/no): ")
            if confirm.lower() != "yes":
                self.stdout.write(self.style.ERROR("Aborted."))
                sys.exit(1)

            self.stdout.write("Clearing existing data...")
            self._clear_data()
            self.stdout.write(self.style.SUCCESS("✓ Data cleared"))
            self.stdout.write("")

        # Seed data
        with transaction.atomic():
            self.stdout.write("Seeding database...")
            self.stdout.write("")

            # Create admin user if requested
            if options["admin"]:
                self._create_admin_user()

            # Create test users
            self._create_test_users(options["users"])

            self.stdout.write("")
            self.stdout.write(self.style.SUCCESS("=" * 70))
            self.stdout.write(self.style.SUCCESS("✓ Database seeded successfully!"))
            self.stdout.write(self.style.SUCCESS("=" * 70))
            self.stdout.write("")

            # Display created data summary
            self._display_summary()

    def _clear_data(self) -> None:
        """Clear all data from the database."""
        # Clear users (except superusers to be safe)
        deleted_count = User.objects.filter(is_superuser=False).delete()[0]
        self.stdout.write(f"  Deleted {deleted_count} non-superuser users")

        # Add more models to clear here as your application grows
        # Example:
        # from apps.myapp.models import MyModel
        # deleted_count = MyModel.objects.all().delete()[0]
        # self.stdout.write(f'  Deleted {deleted_count} MyModel records')

    def _create_admin_user(self) -> None:
        """Create an admin user for testing."""
        email = "admin@example.com"
        password = "admin123"

        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f"  ⚠ Admin user already exists: {email}"))
            return

        User.objects.create_superuser(  # type: ignore[attr-defined]
            email=email,
            username="admin",
            password=password,
            first_name="Admin",
            last_name="User",
        )

        self.stdout.write(self.style.SUCCESS(f"  ✓ Created admin user: {email}"))
        self.stdout.write(f"    Password: {password}")

    def _create_test_users(self, count: int) -> None:
        """Create test users."""
        self.stdout.write(f"Creating {count} test users...")

        created_count = 0
        for i in range(1, count + 1):
            username = f"testuser{i}"
            email = f"testuser{i}@example.com"

            if User.objects.filter(email=email).exists():
                continue

            User.objects.create_user(  # type: ignore[attr-defined]
                email=email,
                username=username,
                password="password123",
                first_name=f"Test{i}",
                last_name="User",
            )
            created_count += 1

        self.stdout.write(self.style.SUCCESS(f"  ✓ Created {created_count} test users"))

        if created_count < count:
            skipped = count - created_count
            self.stdout.write(self.style.WARNING(f"  ⚠ Skipped {skipped} users (already exist)"))

    def _display_summary(self) -> None:
        """Display a summary of seeded data."""
        self.stdout.write("Database Summary:")
        self.stdout.write(f"  Total users: {User.objects.count()}")
        admin_count = User.objects.filter(is_superuser=True).count()
        self.stdout.write(f"  Admin users: {admin_count}")
        regular_count = User.objects.filter(is_superuser=False).count()
        self.stdout.write(f"  Regular users: {regular_count}")
        self.stdout.write("")

        # Display admin credentials if they exist
        if User.objects.filter(email="admin@example.com").exists():
            self.stdout.write(self.style.SUCCESS("Admin Credentials:"))
            self.stdout.write("  Email: admin@example.com")
            self.stdout.write("  Password: admin123")
            self.stdout.write("")

        # Add more summary info here as your application grows
