"""
Test to verify the backend directory structure is properly organized.

This test ensures that all required directories and packages exist
and are properly configured as Python packages.
"""

from pathlib import Path


def test_source_directories_exist():
    """Test that all source directories exist."""
    base_dir = Path(__file__).resolve().parent.parent.parent
    src_dir = base_dir / "src"

    # Core directories
    assert (src_dir / "backend").exists()
    assert (src_dir / "apps").exists()
    assert (src_dir / "common").exists()
    assert (src_dir / "core").exists()

    # Common subdirectories
    assert (src_dir / "common" / "middleware").exists()
    assert (src_dir / "common" / "utils").exists()
    assert (src_dir / "common" / "validators").exists()
    assert (src_dir / "common" / "exceptions").exists()
    assert (src_dir / "common" / "mixins").exists()
    assert (src_dir / "common" / "serializers").exists()
    assert (src_dir / "common" / "permissions").exists()
    assert (src_dir / "common" / "decorators").exists()

    # Core subdirectories
    assert (src_dir / "core" / "models").exists()
    assert (src_dir / "core" / "services").exists()
    assert (src_dir / "core" / "repositories").exists()


def test_test_directories_exist():
    """Test that all test directories exist."""
    base_dir = Path(__file__).resolve().parent.parent.parent
    tests_dir = base_dir / "tests"

    # Test type directories
    assert (tests_dir / "unit").exists()
    assert (tests_dir / "integration").exists()
    assert (tests_dir / "e2e").exists()
    assert (tests_dir / "fixtures").exists()

    # Unit test subdirectories
    assert (tests_dir / "unit" / "apps").exists()
    assert (tests_dir / "unit" / "common").exists()
    assert (tests_dir / "unit" / "core").exists()

    # Integration test subdirectories
    assert (tests_dir / "integration" / "api").exists()
    assert (tests_dir / "integration" / "database").exists()


def test_packages_are_importable():
    """Test that all packages have __init__.py and are importable."""
    base_dir = Path(__file__).resolve().parent.parent.parent
    src_dir = base_dir / "src"

    # Core packages
    assert (src_dir / "apps" / "__init__.py").exists()
    assert (src_dir / "common" / "__init__.py").exists()
    assert (src_dir / "core" / "__init__.py").exists()

    # Common subpackages
    assert (src_dir / "common" / "middleware" / "__init__.py").exists()
    assert (src_dir / "common" / "utils" / "__init__.py").exists()
    assert (src_dir / "common" / "validators" / "__init__.py").exists()
    assert (src_dir / "common" / "exceptions" / "__init__.py").exists()
    assert (src_dir / "common" / "mixins" / "__init__.py").exists()
    assert (src_dir / "common" / "serializers" / "__init__.py").exists()
    assert (src_dir / "common" / "permissions" / "__init__.py").exists()
    assert (src_dir / "common" / "decorators" / "__init__.py").exists()

    # Core subpackages
    assert (src_dir / "core" / "models" / "__init__.py").exists()
    assert (src_dir / "core" / "services" / "__init__.py").exists()
    assert (src_dir / "core" / "repositories" / "__init__.py").exists()


def test_test_packages_have_init():
    """Test that test directories have __init__.py files."""
    base_dir = Path(__file__).resolve().parent.parent.parent
    tests_dir = base_dir / "tests"

    # Main test directories
    assert (tests_dir / "unit" / "__init__.py").exists()
    assert (tests_dir / "integration" / "__init__.py").exists()
    assert (tests_dir / "e2e" / "__init__.py").exists()
    assert (tests_dir / "fixtures" / "__init__.py").exists()

    # Unit test subdirectories
    assert (tests_dir / "unit" / "apps" / "__init__.py").exists()
    assert (tests_dir / "unit" / "common" / "__init__.py").exists()
    assert (tests_dir / "unit" / "core" / "__init__.py").exists()

    # Integration test subdirectories
    assert (tests_dir / "integration" / "api" / "__init__.py").exists()
    assert (tests_dir / "integration" / "database" / "__init__.py").exists()


def test_can_import_packages():
    """Test that packages can be imported without errors."""
    # These imports should not raise any errors
    try:
        import apps
        import common
        import core

        assert apps is not None
        assert common is not None
        assert core is not None
    except ImportError as e:
        # Fail the test with a clear message
        raise AssertionError(f"Failed to import packages: {e}") from e
