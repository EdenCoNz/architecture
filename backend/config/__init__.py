"""
Configuration package for the Django project.
Contains settings for different environments (base, development, production, testing).

Configuration is validated on startup to catch errors early.
"""

from config.env_config import check_configuration_on_startup

# Validate configuration when settings are imported
# This ensures invalid configuration is caught before the app starts
check_configuration_on_startup()
