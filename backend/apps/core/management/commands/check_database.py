"""
Django management command to check database connectivity.

Usage:
    python manage.py check_database
    python manage.py check_database --wait
"""

import sys
import time
from typing import Any, Dict

from django.core.management.base import BaseCommand, CommandError, CommandParser

from apps.core.database import DatabaseHealthCheck, get_database_status


class Command(BaseCommand):
    """
    Check database connectivity and display status information.

    This command verifies that the database is accessible and properly
    configured. Useful for startup checks and debugging connection issues.
    """

    help = "Check database connectivity and display status information"

    def add_arguments(self, parser: CommandParser) -> None:
        """Add command arguments."""
        parser.add_argument(
            "--wait",
            type=int,
            default=0,
            help="Wait up to N seconds for database to become available",
        )
        parser.add_argument(
            "--retry-interval",
            type=int,
            default=2,
            help="Seconds between retry attempts (default: 2)",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        """Execute the command."""
        wait_seconds = options["wait"]
        retry_interval = options["retry_interval"]

        self.stdout.write("\nChecking database connectivity...")
        self.stdout.write("=" * 60)

        if wait_seconds > 0:
            # Wait mode - retry until timeout
            return self._check_with_retry(wait_seconds, retry_interval)
        else:
            # Single check mode
            return self._check_once()

    def _check_once(self) -> None:
        """Perform a single database check."""
        status: Dict[str, Any] = get_database_status()

        if status["connected"]:
            self._print_success(status)
        else:
            self._print_failure(status)
            raise CommandError("Database connection failed")

    def _check_with_retry(self, max_wait: int, retry_interval: int) -> None:
        """
        Check database with retries.

        Args:
            max_wait: Maximum seconds to wait
            retry_interval: Seconds between retries
        """
        start_time = time.time()
        attempt = 1

        while True:
            status = get_database_status()

            if status["connected"]:
                elapsed = time.time() - start_time
                attempts_str = "s" if attempt > 1 else ""
                self.stdout.write(
                    self.style.SUCCESS(
                        f"\n✓ Database connected after {elapsed:.1f}s "
                        f"({attempt} attempt{attempts_str})"
                    )
                )
                self._print_success(status)
                return

            elapsed = time.time() - start_time
            if elapsed >= max_wait:
                self.stdout.write(
                    self.style.ERROR(
                        f"\n✗ Database connection failed after {max_wait}s " f"({attempt} attempts)"
                    )
                )
                self._print_failure(status)
                raise CommandError("Database connection timeout")

            remaining = max_wait - elapsed
            self.stdout.write(
                self.style.WARNING(
                    f"Attempt {attempt}: Connection failed. "
                    f"Retrying in {retry_interval}s "
                    f"(timeout in {remaining:.0f}s)..."
                )
            )

            time.sleep(retry_interval)
            attempt += 1

    def _print_success(self, status: Dict[str, Any]) -> None:
        """Print success information."""
        self.stdout.write(self.style.SUCCESS("\n✓ Database connection successful!\n"))

        self.stdout.write(self.style.HTTP_INFO("Connection Details:"))
        self.stdout.write(f"  Database:  {status['database']}")
        self.stdout.write(f"  Host:      {status['host']}:{status['port']}")
        self.stdout.write(f"  Engine:    {status['engine']}")
        response_time = status.get("response_time_ms", "N/A")
        self.stdout.write(f"  Response:  {response_time}ms")

        self.stdout.write(self.style.HTTP_INFO("\nConfiguration:"))
        pool_enabled = status["connection_pooling"]["enabled"]
        pool_status = "Enabled" if pool_enabled else "Disabled"
        if pool_enabled:
            max_age = status["connection_pooling"]["max_age"]
            pool_status += f" (max age: {max_age}s)"
        self.stdout.write(f"  Connection Pooling: {pool_status}")

        atomic = "Enabled" if status["atomic_requests"] else "Disabled"
        self.stdout.write(f"  Atomic Requests:    {atomic}")

        self.stdout.write("")

    def _print_failure(self, status: Dict[str, Any]) -> None:
        """Print failure information."""
        self.stdout.write(self.style.ERROR("\n✗ Database connection failed!\n"))

        self.stdout.write(self.style.HTTP_INFO("Error Details:"))
        error = status.get("error", "Unknown error")
        self.stdout.write(self.style.ERROR(f"  {error}"))

        self.stdout.write(self.style.HTTP_INFO("\nConnection Configuration:"))
        self.stdout.write(f"  Database:  {status['database']}")
        self.stdout.write(f"  Host:      {status['host']}:{status['port']}")
        self.stdout.write(f"  Engine:    {status['engine']}")

        self.stdout.write(self.style.HTTP_INFO("\nTroubleshooting:"))
        self.stdout.write("  1. Ensure PostgreSQL is running")
        self.stdout.write("  2. Check database connection settings in .env file")
        self.stdout.write("  3. Verify database exists: createdb backend_db")
        self.stdout.write("  4. Verify user credentials: psql -U postgres -h localhost")
        self.stdout.write("  5. Check firewall settings if using remote database")
        self.stdout.write("")


class DatabaseReadyCheck:
    """
    Utility for checking database readiness during application startup.

    Provides graceful degradation when database is not available.
    """

    @staticmethod
    def check_and_warn() -> bool:
        """
        Check database and warn if unavailable.

        Returns:
            True if database is available, False otherwise
        """
        checker = DatabaseHealthCheck()
        result = checker.check()

        if result["status"] != "healthy":
            error = result.get("error", "Unknown error")
            print(
                f"\n{'=' * 60}\n"
                f"⚠️  WARNING: Database connection failed!\n"
                f"{'=' * 60}\n"
                f"Error: {error}\n\n"
                f"The application will start but database operations will fail.\n"
                f"Please check your database configuration and connectivity.\n"
                f"\nTo diagnose the issue, run:\n"
                f"  python manage.py check_database\n"
                f"{'=' * 60}\n",
                file=sys.stderr,
            )
            return False

        return True

    @staticmethod
    def ensure_or_fail() -> None:
        """
        Ensure database is available or fail application startup.

        Raises:
            SystemExit: If database is not available
        """
        checker = DatabaseHealthCheck()
        result = checker.check()

        if result["status"] != "healthy":
            error = result.get("error", "Unknown error")
            print(
                f"\n{'=' * 60}\n"
                f"❌ FATAL: Database connection failed!\n"
                f"{'=' * 60}\n"
                f"Error: {error}\n\n"
                f"Cannot start application without database connectivity.\n"
                f"\nTo diagnose the issue, run:\n"
                f"  python manage.py check_database\n"
                f"{'=' * 60}\n",
                file=sys.stderr,
            )
            sys.exit(1)

        # Success - print confirmation
        response_time = result.get("response_time_ms", "N/A")
        db_name = result["connection_info"].get("name", "unknown")
        print(f"✓ Database connected: {db_name} ({response_time}ms)")
