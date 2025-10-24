"""
Management command to check and validate configuration.

Usage:
    python manage.py check_config
    python manage.py check_config --environment production
    python manage.py check_config --list-all
"""

from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand, CommandParser

from config.env_config import (
    ConfigurationError,
    get_environment,
    print_configuration_help,
    validate_configuration,
)


class Command(BaseCommand):
    """Check and validate environment-based configuration."""

    help = "Check and validate environment-based configuration"

    def add_arguments(self, parser: CommandParser) -> None:
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
        parser.add_argument(
            "--quiet",
            action="store_true",
            help="Suppress non-essential output",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        """Execute the command."""
        quiet = options.get("quiet", False)

        # List all configuration variables if requested
        if options["list_all"]:
            if not quiet:
                self.stdout.write(self.style.SUCCESS("\n=== All Configuration Variables ===\n"))
            print_configuration_help()
            return

        # Determine environment
        environment = options.get("environment") or get_environment()

        if not quiet:
            self.stdout.write(self.style.WARNING(f"\n=== Configuration Validation ===\n"))
            self.stdout.write(f"Checking configuration for '{environment}' environment...\n")

        # Validate configuration
        try:
            validate_configuration(environment)
            if quiet:
                self.stdout.write("Configuration valid")
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Configuration validation passed for " f"'{environment}' environment"
                    )
                )

                # Show some key settings
                self.stdout.write(self.style.SUCCESS("\nKey Settings:"))
                self.stdout.write(f"  DJANGO_SETTINGS_MODULE: {settings.SETTINGS_MODULE}")
                self.stdout.write(f"  DEBUG: {settings.DEBUG}")
                self.stdout.write(f"  ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
                self.stdout.write(f"  DATABASE: {settings.DATABASES['default']['NAME']}")

        except ConfigurationError as e:
            if quiet:
                self.stdout.write(f"Configuration validation failed: {str(e)}")
            else:
                self.stdout.write(
                    self.style.ERROR(f"\n✗ Configuration validation failed:\n{str(e)}\n")
                )
            return

        if not quiet:
            self.stdout.write(
                self.style.SUCCESS("\n✓ Configuration check completed successfully\n")
            )
