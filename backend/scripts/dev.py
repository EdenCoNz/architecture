#!/usr/bin/env python
"""
Development server script.

This script starts the Django development server with hot reload capabilities.
"""

import os
import sys
from pathlib import Path


def main() -> None:
    """Run the Django development server."""
    # Set up the Python path
    backend_dir = Path(__file__).resolve().parent.parent
    src_dir = backend_dir / "src"
    sys.path.insert(0, str(src_dir))

    # Set Django settings module for development
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings.development")

    # Import Django management command
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # Run migrations first
    print("Running migrations...")
    execute_from_command_line(["manage.py", "migrate", "--noinput"])

    # Collect static files (for admin interface)
    print("Collecting static files...")
    execute_from_command_line(["manage.py", "collectstatic", "--noinput", "--clear"])

    # Start development server
    print("Starting development server...")
    execute_from_command_line(["manage.py", "runserver", "0.0.0.0:8000"])


if __name__ == "__main__":
    main()
