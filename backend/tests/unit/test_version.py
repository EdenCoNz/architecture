"""
Unit tests for application version configuration.

Tests verify that the version is correctly defined, accessible,
and follows semantic versioning conventions.
"""

import re

import pytest


class TestApplicationVersion:
    """Test suite for application version configuration."""

    def test_version_is_defined(self):
        """Test that __version__ is defined in config package."""
        from config import __version__

        assert __version__ is not None, "Version should be defined"

    def test_version_is_string(self):
        """Test that __version__ is a string."""
        from config import __version__

        assert isinstance(__version__, str), "Version should be a string"

    def test_version_follows_semantic_versioning(self):
        """Test that version follows semantic versioning format (MAJOR.MINOR.PATCH)."""
        from config import __version__

        # Semantic versioning pattern: MAJOR.MINOR.PATCH
        # Each component should be a non-negative integer
        semver_pattern = r"^\d+\.\d+\.\d+$"
        assert re.match(
            semver_pattern, __version__
        ), f"Version '{__version__}' should follow semantic versioning (MAJOR.MINOR.PATCH)"

    def test_version_not_empty(self):
        """Test that version is not empty."""
        from config import __version__

        assert __version__ != "", "Version should not be empty"
        assert len(__version__) > 0, "Version should have content"

    def test_version_can_be_imported_directly(self):
        """Test that version can be imported from config package."""
        # This import pattern should work from any module
        from config import __version__

        assert __version__ is not None, "Version should be importable"

    def test_version_accessible_from_config_module(self):
        """Test that version is accessible via config module."""
        import config

        assert hasattr(config, "__version__"), "config module should have __version__ attribute"
        assert config.__version__ is not None, "Version should be accessible"

    def test_version_components_are_valid(self):
        """Test that version components are valid integers."""
        from config import __version__

        major, minor, patch = __version__.split(".")

        # Should be able to convert to integers
        assert int(major) >= 0, "Major version should be non-negative integer"
        assert int(minor) >= 0, "Minor version should be non-negative integer"
        assert int(patch) >= 0, "Patch version should be non-negative integer"

    @pytest.mark.parametrize(
        "import_style",
        [
            "from config import __version__",
            "import config; version = config.__version__",
        ],
    )
    def test_version_import_styles(self, import_style):
        """Test that version can be imported using different import styles."""
        # Test different import patterns work
        namespace = {}
        exec(import_style, namespace)

        # Verify version was successfully imported
        version = namespace.get("__version__") or namespace.get("version")
        assert version is not None, f"Import style '{import_style}' should work"
        assert isinstance(version, str), f"Version from '{import_style}' should be a string"
