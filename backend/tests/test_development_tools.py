"""
Tests for development environment tools.

This module tests that all development tools (linting, formatting, type checking,
hot reload) are properly configured and working.
"""

import shutil
import subprocess
from pathlib import Path


def get_poetry_command() -> list[str]:
    """
    Get the poetry command to use for running commands.

    Returns:
        List of command parts to execute poetry
    """
    # Check if poetry is in PATH
    if shutil.which("poetry"):
        return ["poetry"]

    # Check common installation locations
    local_poetry = Path.home() / ".local" / "bin" / "poetry"
    if local_poetry.exists():
        return [str(local_poetry)]

    # Fallback to assuming poetry is in PATH (will fail if not found)
    return ["poetry"]


class TestCodeLinting:
    """Test suite for code linting configuration."""

    def test_ruff_is_installed(self) -> None:
        """Test that Ruff is installed and available."""
        poetry_cmd = get_poetry_command()
        result = subprocess.run(
            [*poetry_cmd, "run", "ruff", "--version"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, "Ruff should be installed"
        assert "ruff" in result.stdout.lower(), "Ruff version should be displayed"

    def test_ruff_configuration_exists(self) -> None:
        """Test that Ruff configuration exists in pyproject.toml."""
        backend_dir = Path(__file__).parent.parent
        pyproject_path = backend_dir / "pyproject.toml"

        assert pyproject_path.exists(), "pyproject.toml should exist"

        content = pyproject_path.read_text()
        assert "[tool.ruff]" in content, "Ruff configuration should exist"
        assert "line-length" in content, "Line length should be configured"
        assert "target-version" in content, "Target version should be configured"

    def test_ruff_lint_rules_configured(self) -> None:
        """Test that Ruff lint rules are properly configured."""
        backend_dir = Path(__file__).parent.parent
        pyproject_path = backend_dir / "pyproject.toml"
        content = pyproject_path.read_text()

        assert "[tool.ruff.lint]" in content, "Lint configuration should exist"
        assert "select" in content, "Lint rules should be selected"

        # Check for important rule categories
        assert '"E"' in content or "'E'" in content, "pycodestyle errors should be enabled"
        assert '"F"' in content or "'F'" in content, "pyflakes should be enabled"
        assert '"I"' in content or "'I'" in content, "isort should be enabled"

    def test_ruff_can_check_code(self) -> None:
        """Test that Ruff can check code in the project."""
        backend_dir = Path(__file__).parent.parent
        poetry_cmd = get_poetry_command()

        result = subprocess.run(
            [*poetry_cmd, "run", "ruff", "check", "src", "--exit-zero"],
            capture_output=True,
            text=True,
            cwd=backend_dir,
            check=False,
        )
        # Should not crash, even if there are linting errors
        assert result.returncode == 0, "Ruff check should execute successfully"


class TestCodeFormatting:
    """Test suite for code formatting configuration."""

    def test_black_is_installed(self) -> None:
        """Test that Black is installed and available."""
        poetry_cmd = get_poetry_command()
        result = subprocess.run(
            [*poetry_cmd, "run", "black", "--version"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, "Black should be installed"
        assert "black" in result.stdout.lower(), "Black version should be displayed"

    def test_black_configuration_exists(self) -> None:
        """Test that Black configuration exists in pyproject.toml."""
        backend_dir = Path(__file__).parent.parent
        pyproject_path = backend_dir / "pyproject.toml"

        content = pyproject_path.read_text()
        assert "[tool.black]" in content, "Black configuration should exist"
        assert "line-length" in content, "Line length should be configured"
        assert "target-version" in content, "Target version should be configured"

    def test_black_can_check_formatting(self) -> None:
        """Test that Black can check code formatting."""
        backend_dir = Path(__file__).parent.parent
        poetry_cmd = get_poetry_command()

        result = subprocess.run(
            [*poetry_cmd, "run", "black", "--check", "src", "--exclude", "migrations"],
            capture_output=True,
            text=True,
            cwd=backend_dir,
            check=False,
        )
        # Should execute without crashing
        assert result.returncode in [0, 1], "Black check should execute"


class TestEditorConfiguration:
    """Test suite for editor configuration."""

    def test_editorconfig_exists(self) -> None:
        """Test that .editorconfig file exists."""
        backend_dir = Path(__file__).parent.parent
        editorconfig_path = backend_dir / ".editorconfig"

        assert editorconfig_path.exists(), ".editorconfig file should exist"

    def test_editorconfig_has_root(self) -> None:
        """Test that .editorconfig has root = true."""
        backend_dir = Path(__file__).parent.parent
        editorconfig_path = backend_dir / ".editorconfig"

        content = editorconfig_path.read_text()
        assert "root = true" in content, ".editorconfig should have root = true"

    def test_editorconfig_python_settings(self) -> None:
        """Test that .editorconfig has Python-specific settings."""
        backend_dir = Path(__file__).parent.parent
        editorconfig_path = backend_dir / ".editorconfig"

        content = editorconfig_path.read_text()
        assert "[*.py]" in content, ".editorconfig should have Python settings"
        assert "indent_style" in content, "Indent style should be configured"
        assert "indent_size" in content, "Indent size should be configured"

    def test_editorconfig_general_settings(self) -> None:
        """Test that .editorconfig has general settings for all files."""
        backend_dir = Path(__file__).parent.parent
        editorconfig_path = backend_dir / ".editorconfig"

        content = editorconfig_path.read_text()
        assert "[*]" in content, ".editorconfig should have general settings"
        assert "charset" in content, "Charset should be configured"
        assert "end_of_line" in content, "End of line should be configured"
        assert "insert_final_newline" in content, "Final newline should be configured"


class TestTypeChecking:
    """Test suite for type checking configuration."""

    def test_mypy_is_installed(self) -> None:
        """Test that MyPy is installed and available."""
        poetry_cmd = get_poetry_command()
        result = subprocess.run(
            [*poetry_cmd, "run", "mypy", "--version"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, "MyPy should be installed"
        assert "mypy" in result.stdout.lower(), "MyPy version should be displayed"

    def test_mypy_configuration_exists(self) -> None:
        """Test that MyPy configuration exists in pyproject.toml."""
        backend_dir = Path(__file__).parent.parent
        pyproject_path = backend_dir / "pyproject.toml"

        content = pyproject_path.read_text()
        assert "[tool.mypy]" in content, "MyPy configuration should exist"
        assert "python_version" in content, "Python version should be configured"

    def test_mypy_strict_mode_enabled(self) -> None:
        """Test that MyPy strict mode checks are enabled."""
        backend_dir = Path(__file__).parent.parent
        pyproject_path = backend_dir / "pyproject.toml"

        content = pyproject_path.read_text()
        assert "disallow_untyped_defs" in content, "Untyped defs should be disallowed"
        assert "warn_return_any" in content, "Return any warnings should be enabled"

    def test_django_stubs_configured(self) -> None:
        """Test that Django type stubs are configured."""
        backend_dir = Path(__file__).parent.parent
        pyproject_path = backend_dir / "pyproject.toml"

        content = pyproject_path.read_text()
        assert "mypy_django_plugin" in content, "Django plugin should be configured"


class TestHotReload:
    """Test suite for hot reload configuration."""

    def test_development_script_exists(self) -> None:
        """Test that development server script exists."""
        backend_dir = Path(__file__).parent.parent
        dev_script = backend_dir / "scripts" / "dev.py"

        assert dev_script.exists(), "Development script should exist"

    def test_development_script_uses_runserver(self) -> None:
        """Test that development script uses Django's runserver command."""
        backend_dir = Path(__file__).parent.parent
        dev_script = backend_dir / "scripts" / "dev.py"

        content = dev_script.read_text()
        assert "runserver" in content, "Development script should use runserver"

    def test_development_settings_configured(self) -> None:
        """Test that development settings module exists."""
        backend_dir = Path(__file__).parent.parent
        dev_settings = backend_dir / "src" / "backend" / "settings" / "development.py"

        assert dev_settings.exists(), "Development settings should exist"


class TestMakefileCommands:
    """Test suite for Makefile commands."""

    def test_makefile_exists(self) -> None:
        """Test that Makefile exists."""
        backend_dir = Path(__file__).parent.parent
        makefile_path = backend_dir / "Makefile"

        assert makefile_path.exists(), "Makefile should exist"

    def test_makefile_has_lint_command(self) -> None:
        """Test that Makefile has lint command."""
        backend_dir = Path(__file__).parent.parent
        makefile_path = backend_dir / "Makefile"

        content = makefile_path.read_text()
        assert "lint:" in content, "Makefile should have lint target"
        assert "ruff check" in content, "Lint should use Ruff"

    def test_makefile_has_format_command(self) -> None:
        """Test that Makefile has format command."""
        backend_dir = Path(__file__).parent.parent
        makefile_path = backend_dir / "Makefile"

        content = makefile_path.read_text()
        assert "format:" in content, "Makefile should have format target"
        assert "black" in content, "Format should use Black"

    def test_makefile_has_type_check_command(self) -> None:
        """Test that Makefile has type-check command."""
        backend_dir = Path(__file__).parent.parent
        makefile_path = backend_dir / "Makefile"

        content = makefile_path.read_text()
        assert "type-check:" in content, "Makefile should have type-check target"
        assert "mypy" in content, "Type-check should use MyPy"

    def test_makefile_has_dev_command(self) -> None:
        """Test that Makefile has dev command."""
        backend_dir = Path(__file__).parent.parent
        makefile_path = backend_dir / "Makefile"

        content = makefile_path.read_text()
        assert "dev:" in content, "Makefile should have dev target"


class TestDevelopmentDependencies:
    """Test suite for development dependencies."""

    def test_all_dev_tools_installed(self) -> None:
        """Test that all development tools are installed."""
        backend_dir = Path(__file__).parent.parent
        pyproject_path = backend_dir / "pyproject.toml"

        content = pyproject_path.read_text()

        # Check for key development dependencies
        assert "black" in content, "Black should be in dependencies"
        assert "ruff" in content, "Ruff should be in dependencies"
        assert "mypy" in content, "MyPy should be in dependencies"
        assert "pytest" in content, "Pytest should be in dependencies"
        assert "django-stubs" in content, "Django stubs should be in dependencies"

    def test_poetry_dev_group_exists(self) -> None:
        """Test that Poetry dev dependencies group exists."""
        backend_dir = Path(__file__).parent.parent
        pyproject_path = backend_dir / "pyproject.toml"

        content = pyproject_path.read_text()
        assert (
            "[tool.poetry.group.dev.dependencies]" in content
        ), "Dev dependencies group should exist"
