"""
Django settings module.

This package contains different settings configurations:
- base.py: Common settings for all environments
- development.py: Development-specific settings
- production.py: Production-specific settings
- test.py: Test-specific settings

The active settings module is determined by the DJANGO_SETTINGS_MODULE environment variable.
"""

import os

# Determine which settings to use based on environment
settings_module = os.environ.get("DJANGO_SETTINGS_MODULE", "backend.settings.development")

# Import all settings from the appropriate module
if settings_module.endswith(".development"):
    from .development import *  # noqa: F401, F403
elif settings_module.endswith(".production"):
    from .production import *  # noqa: F401, F403
elif settings_module.endswith(".test"):
    from .test import *  # noqa: F401, F403
else:
    from .base import *  # noqa: F401, F403
