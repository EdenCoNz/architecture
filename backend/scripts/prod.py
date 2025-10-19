#!/usr/bin/env python
"""
Production server script.

This script prepares and starts the production server using Gunicorn.
"""

import os
import subprocess
import sys
from pathlib import Path


def main() -> None:
    """Prepare and run the production server."""
    # Set up the Python path
    backend_dir = Path(__file__).resolve().parent.parent
    src_dir = backend_dir / "src"
    sys.path.insert(0, str(src_dir))

    # Set Django settings module for production
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings.production")

    # Import Django management command
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # Run migrations
    print("Running migrations...")
    execute_from_command_line(["manage.py", "migrate", "--noinput"])

    # Collect static files
    print("Collecting static files...")
    execute_from_command_line(["manage.py", "collectstatic", "--noinput", "--clear"])

    # Create logs directory
    logs_dir = backend_dir / "logs"
    logs_dir.mkdir(exist_ok=True)

    # Get configuration from environment
    port = os.environ.get("PORT", "8000")
    workers = os.environ.get("GUNICORN_WORKERS", "4")
    worker_class = os.environ.get("GUNICORN_WORKER_CLASS", "sync")
    timeout = os.environ.get("GUNICORN_TIMEOUT", "30")

    # Start Gunicorn
    print(f"Starting Gunicorn on port {port} with {workers} workers...")

    gunicorn_cmd = [
        "gunicorn",
        "backend.wsgi:application",
        "--bind",
        f"0.0.0.0:{port}",
        "--workers",
        workers,
        "--worker-class",
        worker_class,
        "--timeout",
        timeout,
        "--access-logfile",
        str(logs_dir / "access.log"),
        "--error-logfile",
        str(logs_dir / "error.log"),
        "--log-level",
        "info",
        "--pythonpath",
        str(src_dir),
    ]

    subprocess.run(gunicorn_cmd, check=True)


if __name__ == "__main__":
    main()
