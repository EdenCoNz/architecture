"""
Configuration package for the Django project.
Contains settings for different environments (base, development,
production, testing).

Configuration is validated on startup to catch errors early.
"""

import os

from config.env_config import check_configuration_on_startup

# Validate configuration when settings are imported
# This ensures invalid configuration is caught before the app starts
# Skip validation during mypy type checking
if not os.environ.get("MYPY_RUNNING"):
    check_configuration_on_startup()
