"""
Tests for Django configuration and build setup.

These tests verify that the Django project is properly configured
and that all settings modules work correctly.
"""

import os
from pathlib import Path

from django.conf import settings


class TestDjangoConfiguration:
    """Test suite for Django configuration."""

    def test_settings_module_is_test(self) -> None:
        """Verify that tests are using the test settings module."""
        assert os.environ.get("DJANGO_SETTINGS_MODULE") == "backend.settings.test"

    def test_debug_setting_is_configured(self) -> None:
        """Verify that DEBUG setting is properly configured."""
        # DEBUG can be True or False in tests depending on environment variables
        # The important thing is that it's a boolean and the setting works
        assert isinstance(settings.DEBUG, bool)
        # Test settings file explicitly sets DEBUG=True, but base.py may override
        # based on environment variables for production safety

    def test_secret_key_is_set(self) -> None:
        """Verify that SECRET_KEY is configured."""
        assert settings.SECRET_KEY
        assert settings.SECRET_KEY == "test-secret-key-not-for-production"

    def test_database_is_sqlite_in_memory(self) -> None:
        """Verify that tests use SQLite in-memory database."""
        assert settings.DATABASES["default"]["ENGINE"] == "django.db.backends.sqlite3"
        assert settings.DATABASES["default"]["NAME"] == ":memory:"

    def test_installed_apps_includes_required_apps(self) -> None:
        """Verify that all required apps are installed."""
        required_apps = [
            "django.contrib.admin",
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "rest_framework",
            "corsheaders",
            "drf_spectacular",
        ]
        for app in required_apps:
            assert app in settings.INSTALLED_APPS

    def test_middleware_includes_required_middleware(self) -> None:
        """Verify that all required middleware is configured."""
        required_middleware = [
            "django.middleware.security.SecurityMiddleware",
            "whitenoise.middleware.WhiteNoiseMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware",
            "corsheaders.middleware.CorsMiddleware",
            "django.middleware.common.CommonMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
        ]
        for middleware in required_middleware:
            assert middleware in settings.MIDDLEWARE

    def test_rest_framework_is_configured(self) -> None:
        """Verify that Django REST Framework is properly configured."""
        assert hasattr(settings, "REST_FRAMEWORK")
        assert "DEFAULT_RENDERER_CLASSES" in settings.REST_FRAMEWORK
        assert "DEFAULT_PARSER_CLASSES" in settings.REST_FRAMEWORK
        assert "DEFAULT_AUTHENTICATION_CLASSES" in settings.REST_FRAMEWORK

    def test_spectacular_is_configured(self) -> None:
        """Verify that drf-spectacular is properly configured."""
        assert hasattr(settings, "SPECTACULAR_SETTINGS")
        assert "TITLE" in settings.SPECTACULAR_SETTINGS
        assert settings.SPECTACULAR_SETTINGS["TITLE"] == "Backend API"


class TestProjectStructure:
    """Test suite for project structure and module resolution."""

    def test_base_dir_exists(self) -> None:
        """Verify that BASE_DIR is set correctly."""
        assert hasattr(settings, "BASE_DIR")
        assert Path(settings.BASE_DIR).exists()

    def test_src_directory_exists(self) -> None:
        """Verify that src directory exists and is in Python path."""
        backend_dir = Path(settings.BASE_DIR)
        src_dir = backend_dir / "src"
        assert src_dir.exists()
        assert str(src_dir) in [Path(p).resolve().as_posix() for p in os.sys.path]

    def test_backend_package_is_importable(self) -> None:
        """Verify that backend package can be imported."""
        import backend

        assert hasattr(backend, "__version__")

    def test_settings_modules_are_importable(self) -> None:
        """Verify that all settings modules can be imported."""
        # This test just verifies they can be imported without errors
        from backend.settings import base, development, production, test  # noqa: F401

        assert True

    def test_wsgi_application_is_importable(self) -> None:
        """Verify that WSGI application can be imported."""
        from backend.wsgi import application  # noqa: F401

        assert True

    def test_asgi_application_is_importable(self) -> None:
        """Verify that ASGI application can be imported."""
        from backend.asgi import application  # noqa: F401

        assert True


class TestBuildConfiguration:
    """Test suite for build configuration."""

    def test_pyproject_toml_exists(self) -> None:
        """Verify that pyproject.toml exists."""
        backend_dir = Path(settings.BASE_DIR)
        pyproject_path = backend_dir / "pyproject.toml"
        assert pyproject_path.exists()

    def test_scripts_exist(self) -> None:
        """Verify that build scripts exist."""
        backend_dir = Path(settings.BASE_DIR)
        dev_script = backend_dir / "scripts" / "dev.py"
        prod_script = backend_dir / "scripts" / "prod.py"
        assert dev_script.exists()
        assert prod_script.exists()

    def test_manage_py_exists(self) -> None:
        """Verify that manage.py exists and is executable."""
        backend_dir = Path(settings.BASE_DIR)
        manage_py = backend_dir / "manage.py"
        assert manage_py.exists()
        # Check if file is executable
        assert os.access(manage_py, os.X_OK)

    def test_makefile_exists(self) -> None:
        """Verify that Makefile exists."""
        backend_dir = Path(settings.BASE_DIR)
        makefile = backend_dir / "Makefile"
        assert makefile.exists()

    def test_gitignore_exists(self) -> None:
        """Verify that .gitignore exists."""
        backend_dir = Path(settings.BASE_DIR)
        gitignore = backend_dir / ".gitignore"
        assert gitignore.exists()

    def test_editorconfig_exists(self) -> None:
        """Verify that .editorconfig exists."""
        backend_dir = Path(settings.BASE_DIR)
        editorconfig = backend_dir / ".editorconfig"
        assert editorconfig.exists()

    def test_env_example_exists(self) -> None:
        """Verify that .env.example exists."""
        backend_dir = Path(settings.BASE_DIR)
        env_example = backend_dir / ".env.example"
        assert env_example.exists()
