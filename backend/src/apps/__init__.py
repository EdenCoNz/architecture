"""
Django applications package.

This package contains all feature-based Django applications.
Each app should be self-contained and focused on a specific domain or feature.

Structure:
    apps/
        <app_name>/
            __init__.py
            apps.py              # App configuration
            models.py            # Database models
            views.py             # View logic (or views/ for multiple files)
            serializers.py       # DRF serializers
            urls.py              # URL routing
            admin.py             # Admin interface
            managers.py          # Custom model managers
            signals.py           # Django signals
            tasks.py             # Background tasks (Celery)
            migrations/          # Database migrations
            tests/               # App-specific tests

Best Practices:
    - Keep apps focused on a single domain or feature
    - Use clear, descriptive app names (e.g., 'users', 'products', 'orders')
    - Share common functionality via 'common' package, not between apps
    - Apps should be loosely coupled and independently deployable
"""
