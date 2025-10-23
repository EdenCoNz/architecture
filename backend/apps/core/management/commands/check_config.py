"""
Management command to check and validate configuration.

Usage:
    python manage.py check_config
    python manage.py check_config --environment production
    python manage.py check_config --list-all
"""

from django.conf import settings
from django.core.management.base import BaseCommand

from config.env_config import (
    ConfigurationError,
    get_all_config_variables,
    get_environment,
    print_configuration_help,
    validate_configuration,
)


class Command(BaseCommand):
    """Check and validate environment-based configuration."""

    help = "Check and validate environment-based configuration"

    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            "--environment",
            type=str,
            help="Environment to validate (development, production, testing)",
        )
        parser.add_argument(
            "--list-all",
            action="store_true",
            help="List all configuration variables with descriptions",
        )

    def handle(self, *args, **options):
        """Execute the command."""
        # List all configuration variables if requested
        if options["list_all"]:
            self.stdout.write(self.style.SUCCESS("\n=== All Configuration Variables ===\n"))
            print_configuration_help()
            return

        # Determine environment
        environment = options.get("environment") or get_environment()

        self.stdout.write(
            self.style.WARNING(f"\nChecking configuration for '{environment}' environment...\n")
        )

        # Validate configuration
        try:
            validate_configuration(environment)
            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ Configuration validation passed for '{environment}' environment"
                )
            )

            # Show some key settings
            self.stdout.write(self.style.SUCCESS("\nKey Settings:"))
            self.stdout.write(f"  DJANGO_SETTINGS_MODULE: {settings.SETTINGS_MODULE}")
            self.stdout.write(f"  DEBUG: {settings.DEBUG}")
            self.stdout.write(f"  ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
            self.stdout.write(f"  DATABASE: {settings.DATABASES['default']['NAME']}")

        except ConfigurationError as e:
            self.stdout.write(self.style.ERROR(f"\n✗ Configuration validation failed:\n{str(e)}\n"))
            return

        self.stdout.write(self.style.SUCCESS("\n✓ Configuration check completed successfully\n"))
