"""
Configuration package for the Django project.
Contains settings for different environments (base, development,
production, testing).

Configuration is validated on startup to catch errors early.
"""

import os
from pathlib import Path

from config.env_config import check_configuration_on_startup

# Application version using semantic versioning (MAJOR.MINOR.PATCH)
# This version is used by all backend services and can be imported
# from any module: from config import __version__
__version__ = "1.0.6"

# Ensure required directories exist before Django initializes
# This prevents FileNotFoundError when logging configuration is loaded
BASE_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = BASE_DIR / "logs"

# Create logs directory if it doesn't exist
# This is idempotent and safe to run multiple times
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Validate configuration when settings are imported
# This ensures invalid configuration is caught before the app starts
# Skip validation during mypy type checking
if not os.environ.get("MYPY_RUNNING"):
    check_configuration_on_startup()
