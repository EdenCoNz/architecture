"""
Code Quality Regression Test Suite.

This module contains automated regression tests to validate that code quality
standards are maintained across the codebase. These tests detect common violations
like unused imports, formatting issues, and style inconsistencies.

Tests run as part of continuous integration pipeline to prevent code quality
regressions from being merged.
"""

import ast
import subprocess
from pathlib import Path
from typing import Any

import pytest


class TestUnusedImportsDetection:
    """
    Test suite for detecting unused imports in Python source code.

    These tests use AST analysis to identify imports that are declared but
    never used in the code, which can indicate dead code or copy-paste errors.
    """

    def test_can_analyze_python_file_with_ast(self) -> None:
        """Test that we can parse Python files using AST."""
        # Create a test file content
        test_code = """
import os
import sys

def example():
    return sys.version
"""
        # Parse the code
        tree = ast.parse(test_code)
        assert tree is not None
        assert isinstance(tree, ast.Module)

    def test_detect_unused_import_in_code(self) -> None:
        """Test detection of unused imports using AST analysis."""
        test_code = """
import os  # unused
import sys  # used

def example():
    return sys.version
"""
        tree = ast.parse(test_code)

        # Extract imports
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)

        # Extract names used in the code
        used_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                used_names.add(node.id)

        # Find unused imports
        unused = [imp for imp in imports if imp not in used_names]

        assert "os" in unused, "os import should be detected as unused"
        assert "sys" not in unused, "sys import should be detected as used"

    def test_detect_unused_from_imports(self) -> None:
        """Test detection of unused imports from 'from X import Y' statements."""
        test_code = """
from pathlib import Path  # used
from typing import Any  # unused

def example():
    return Path.cwd()
"""
        tree = ast.parse(test_code)

        # Extract from imports
        from_imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    from_imports.append(alias.name)

        # Extract names used
        used_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                used_names.add(node.id)

        # Find unused
        unused = [imp for imp in from_imports if imp not in used_names]

        assert "Any" in unused, "Any import should be detected as unused"
        assert "Path" not in unused, "Path import should be detected as used"

    def test_scan_source_files_for_unused_imports(self) -> None:
        """
        Test scanning actual source files for unused imports using Ruff.

        This test uses Ruff's F401 rule which detects unused imports.
        """
        backend_dir = Path(__file__).parent.parent.parent
        src_dir = backend_dir / "src"

        # Use Ruff to check for unused imports (F401)
        result = subprocess.run(
            [
                "poetry",
                "run",
                "ruff",
                "check",
                "--select=F401",  # Only check unused imports
                "--output-format=json",
                str(src_dir),
            ],
            capture_output=True,
            text=True,
            cwd=backend_dir,
            check=False,
        )

        # Parse JSON output
        import json

        if result.stdout.strip():
            violations = json.loads(result.stdout)
            if violations:
                # Format violation messages for better error reporting
                violation_messages = []
                for violation in violations:
                    file_path = violation.get("filename", "unknown")
                    line = violation.get("location", {}).get("row", "?")
                    message = violation.get("message", "")
                    violation_messages.append(f"{file_path}:{line} - {message}")

                pytest.fail(
                    f"Found {len(violations)} unused import(s):\n" + "\n".join(violation_messages)
                )

    def test_no_star_imports_in_source(self) -> None:
        """
        Test that source code does not use star imports (from X import *).

        Star imports make code harder to understand and maintain.
        """
        backend_dir = Path(__file__).parent.parent.parent
        src_dir = backend_dir / "src"

        # Use Ruff to check for star imports (F403, F405)
        result = subprocess.run(
            [
                "poetry",
                "run",
                "ruff",
                "check",
                "--select=F403,F405",  # Star import rules
                "--output-format=json",
                str(src_dir),
            ],
            capture_output=True,
            text=True,
            cwd=backend_dir,
            check=False,
        )

        import json

        if result.stdout.strip():
            violations = json.loads(result.stdout)
            if violations:
                violation_messages = []
                for violation in violations:
                    file_path = violation.get("filename", "unknown")
                    line = violation.get("location", {}).get("row", "?")
                    message = violation.get("message", "")
                    violation_messages.append(f"{file_path}:{line} - {message}")

                pytest.fail(
                    f"Found {len(violations)} star import(s):\n" + "\n".join(violation_messages)
                )


class TestBlackFormattingCompliance:
    """
    Test suite for Black code formatting compliance.

    These tests verify that all Python source files follow Black's
    formatting standards, ensuring consistent code style across the project.
    """

    def test_black_is_available(self) -> None:
        """Test that Black formatter is installed and accessible."""
        result = subprocess.run(
            ["poetry", "run", "black", "--version"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, "Black should be installed"
        assert "black" in result.stdout.lower()

    def test_black_configuration_exists(self) -> None:
        """Test that Black configuration exists in pyproject.toml."""
        backend_dir = Path(__file__).parent.parent.parent
        pyproject_path = backend_dir / "pyproject.toml"

        assert pyproject_path.exists(), "pyproject.toml should exist"
        content = pyproject_path.read_text()
        assert "[tool.black]" in content, "Black configuration should exist"

    def test_source_files_are_black_formatted(self) -> None:
        """
        Test that all source files comply with Black formatting.

        This test will fail if any files need reformatting, preventing
        unformatted code from being merged.
        """
        backend_dir = Path(__file__).parent.parent.parent
        src_dir = backend_dir / "src"

        result = subprocess.run(
            [
                "poetry",
                "run",
                "black",
                "--check",
                "--diff",
                "--exclude",
                "migrations",
                str(src_dir),
            ],
            capture_output=True,
            text=True,
            cwd=backend_dir,
            check=False,
        )

        if result.returncode != 0:
            # Extract file names that need formatting from output
            output_lines = result.stdout.split("\n")
            files_needing_format = [
                line for line in output_lines if line.startswith("would reformat")
            ]

            if files_needing_format:
                pytest.fail(
                    "Source files are not Black formatted:\n"
                    + "\n".join(files_needing_format)
                    + "\n\nRun 'make format' to fix formatting issues."
                )

    def test_line_length_compliance(self) -> None:
        """Test that configured line length is respected."""
        backend_dir = Path(__file__).parent.parent.parent
        pyproject_path = backend_dir / "pyproject.toml"

        content = pyproject_path.read_text()

        # Verify Black and Ruff line lengths match
        import re

        black_line_length = re.search(
            r"\[tool\.black\].*?line-length\s*=\s*(\d+)", content, re.DOTALL
        )
        ruff_line_length = re.search(
            r"\[tool\.ruff\].*?line-length\s*=\s*(\d+)", content, re.DOTALL
        )

        assert black_line_length, "Black line-length should be configured"
        assert ruff_line_length, "Ruff line-length should be configured"

        black_length = int(black_line_length.group(1))
        ruff_length = int(ruff_line_length.group(1))

        assert (
            black_length == ruff_length
        ), f"Black ({black_length}) and Ruff ({ruff_length}) line lengths should match"


class TestRuffCodeQualityChecks:
    """
    Test suite for Ruff code quality checks.

    These tests run Ruff linter to detect common code quality issues such as:
    - Undefined variables
    - Syntax errors
    - Import ordering issues
    - Complexity issues
    - Security vulnerabilities
    """

    def test_ruff_is_available(self) -> None:
        """Test that Ruff linter is installed and accessible."""
        result = subprocess.run(
            ["poetry", "run", "ruff", "--version"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, "Ruff should be installed"
        assert "ruff" in result.stdout.lower()

    def test_no_undefined_variables(self) -> None:
        """
        Test that code does not contain undefined variables.

        Uses Ruff's F821 rule to detect undefined names.
        """
        backend_dir = Path(__file__).parent.parent.parent
        src_dir = backend_dir / "src"

        result = subprocess.run(
            [
                "poetry",
                "run",
                "ruff",
                "check",
                "--select=F821",  # Undefined name
                "--output-format=json",
                str(src_dir),
            ],
            capture_output=True,
            text=True,
            cwd=backend_dir,
            check=False,
        )

        import json

        if result.stdout.strip():
            violations = json.loads(result.stdout)
            if violations:
                violation_messages = []
                for violation in violations:
                    file_path = violation.get("filename", "unknown")
                    line = violation.get("location", {}).get("row", "?")
                    message = violation.get("message", "")
                    violation_messages.append(f"{file_path}:{line} - {message}")

                pytest.fail(
                    f"Found {len(violations)} undefined variable(s):\n"
                    + "\n".join(violation_messages)
                )

    def test_no_syntax_errors(self) -> None:
        """
        Test that all Python files have valid syntax.

        Uses Ruff's E999 rule to detect syntax errors.
        """
        backend_dir = Path(__file__).parent.parent.parent
        src_dir = backend_dir / "src"

        result = subprocess.run(
            [
                "poetry",
                "run",
                "ruff",
                "check",
                "--select=E999",  # Syntax errors
                "--output-format=json",
                str(src_dir),
            ],
            capture_output=True,
            text=True,
            cwd=backend_dir,
            check=False,
        )

        import json

        if result.stdout.strip():
            violations = json.loads(result.stdout)
            if violations:
                violation_messages = []
                for violation in violations:
                    file_path = violation.get("filename", "unknown")
                    line = violation.get("location", {}).get("row", "?")
                    message = violation.get("message", "")
                    violation_messages.append(f"{file_path}:{line} - {message}")

                pytest.fail(
                    f"Found {len(violations)} syntax error(s):\n" + "\n".join(violation_messages)
                )

    def test_import_ordering_isort_compliance(self) -> None:
        """
        Test that imports are properly ordered according to isort rules.

        Uses Ruff's I001 rule (isort) to check import ordering.
        """
        backend_dir = Path(__file__).parent.parent.parent
        src_dir = backend_dir / "src"

        result = subprocess.run(
            [
                "poetry",
                "run",
                "ruff",
                "check",
                "--select=I",  # isort rules
                "--output-format=json",
                str(src_dir),
            ],
            capture_output=True,
            text=True,
            cwd=backend_dir,
            check=False,
        )

        import json

        if result.stdout.strip():
            violations = json.loads(result.stdout)
            if violations:
                violation_messages = []
                for violation in violations:
                    file_path = violation.get("filename", "unknown")
                    line = violation.get("location", {}).get("row", "?")
                    message = violation.get("message", "")
                    violation_messages.append(f"{file_path}:{line} - {message}")

                pytest.fail(
                    f"Found {len(violations)} import ordering issue(s):\n"
                    + "\n".join(violation_messages)
                    + "\n\nRun 'make format' to fix import ordering."
                )

    def test_no_unused_variables(self) -> None:
        """
        Test that code does not contain unused local variables.

        Uses Ruff's F841 rule to detect unused variables.
        """
        backend_dir = Path(__file__).parent.parent.parent
        src_dir = backend_dir / "src"

        result = subprocess.run(
            [
                "poetry",
                "run",
                "ruff",
                "check",
                "--select=F841",  # Unused variable
                "--output-format=json",
                str(src_dir),
            ],
            capture_output=True,
            text=True,
            cwd=backend_dir,
            check=False,
        )

        import json

        if result.stdout.strip():
            violations = json.loads(result.stdout)
            if violations:
                violation_messages = []
                for violation in violations:
                    file_path = violation.get("filename", "unknown")
                    line = violation.get("location", {}).get("row", "?")
                    message = violation.get("message", "")
                    violation_messages.append(f"{file_path}:{line} - {message}")

                pytest.fail(
                    f"Found {len(violations)} unused variable(s):\n" + "\n".join(violation_messages)
                )

    def test_no_mutable_default_arguments(self) -> None:
        """
        Test that functions do not use mutable default arguments.

        Uses Ruff's B006 rule to detect mutable default arguments like
        def func(x=[]) which can lead to bugs.
        """
        backend_dir = Path(__file__).parent.parent.parent
        src_dir = backend_dir / "src"

        result = subprocess.run(
            [
                "poetry",
                "run",
                "ruff",
                "check",
                "--select=B006",  # Mutable default argument
                "--output-format=json",
                str(src_dir),
            ],
            capture_output=True,
            text=True,
            cwd=backend_dir,
            check=False,
        )

        import json

        if result.stdout.strip():
            violations = json.loads(result.stdout)
            if violations:
                violation_messages = []
                for violation in violations:
                    file_path = violation.get("filename", "unknown")
                    line = violation.get("location", {}).get("row", "?")
                    message = violation.get("message", "")
                    violation_messages.append(f"{file_path}:{line} - {message}")

                pytest.fail(
                    f"Found {len(violations)} mutable default argument(s):\n"
                    + "\n".join(violation_messages)
                )

    def test_comprehensive_code_quality_check(self) -> None:
        """
        Comprehensive test that runs all configured Ruff rules.

        This test validates the entire codebase against all enabled Ruff rules
        as configured in pyproject.toml.
        """
        backend_dir = Path(__file__).parent.parent.parent
        src_dir = backend_dir / "src"

        result = subprocess.run(
            [
                "poetry",
                "run",
                "ruff",
                "check",
                "--output-format=json",
                str(src_dir),
            ],
            capture_output=True,
            text=True,
            cwd=backend_dir,
            check=False,
        )

        import json

        if result.stdout.strip():
            violations = json.loads(result.stdout)
            if violations:
                # Group violations by type for better reporting
                violations_by_code: dict[str, list[Any]] = {}
                for violation in violations:
                    code = violation.get("code", "UNKNOWN")
                    if code not in violations_by_code:
                        violations_by_code[code] = []
                    violations_by_code[code].append(violation)

                # Format error message
                error_lines = [f"Found {len(violations)} code quality violation(s):\n"]
                for code, code_violations in sorted(violations_by_code.items()):
                    error_lines.append(f"\n{code} ({len(code_violations)} issue(s)):")
                    for violation in code_violations[:5]:  # Show first 5 per code
                        file_path = violation.get("filename", "unknown")
                        line = violation.get("location", {}).get("row", "?")
                        message = violation.get("message", "")
                        error_lines.append(f"  {file_path}:{line} - {message}")
                    if len(code_violations) > 5:
                        error_lines.append(f"  ... and {len(code_violations) - 5} more")

                error_lines.append("\n\nRun 'make lint' for full details.")
                error_lines.append("Run 'make format' to auto-fix some issues.")

                pytest.fail("\n".join(error_lines))


class TestCodeQualityConfiguration:
    """
    Test suite for code quality tool configuration.

    These tests verify that all quality tools are properly configured
    and consistent with each other.
    """

    def test_pyproject_toml_exists(self) -> None:
        """Test that pyproject.toml configuration file exists."""
        backend_dir = Path(__file__).parent.parent.parent
        pyproject_path = backend_dir / "pyproject.toml"
        assert pyproject_path.exists(), "pyproject.toml should exist"

    def test_ruff_configuration_complete(self) -> None:
        """Test that Ruff configuration includes essential rules."""
        backend_dir = Path(__file__).parent.parent.parent
        pyproject_path = backend_dir / "pyproject.toml"
        content = pyproject_path.read_text()

        # Check for essential rule categories
        assert "[tool.ruff.lint]" in content, "Ruff lint configuration should exist"
        assert "select" in content, "Ruff should have selected rules"

        # Check for critical rule categories
        essential_rules = ["F", "E", "W", "I"]  # Pyflakes, pycodestyle, isort
        for rule in essential_rules:
            assert (
                f'"{rule}"' in content or f"'{rule}'" in content
            ), f"Rule category {rule} should be enabled"

    def test_test_markers_configured(self) -> None:
        """Test that pytest markers for regression tests are configured."""
        backend_dir = Path(__file__).parent.parent.parent
        pyproject_path = backend_dir / "pyproject.toml"
        content = pyproject_path.read_text()

        assert "markers" in content, "pytest markers should be configured"
        assert "regression" in content, "regression marker should be defined"

    def test_coverage_excludes_migrations(self) -> None:
        """Test that coverage configuration excludes migrations."""
        backend_dir = Path(__file__).parent.parent.parent
        pyproject_path = backend_dir / "pyproject.toml"
        content = pyproject_path.read_text()

        assert "[tool.coverage" in content, "Coverage configuration should exist"
        assert "migrations" in content, "Migrations should be excluded from coverage"


@pytest.mark.regression
class TestOriginalBugRegression:
    """
    Regression tests for the original bug: unused imports passing through CI.

    This test class specifically validates that the bug described in
    github-issue-47 cannot recur.
    """

    def test_unused_imports_are_detected_in_ci(self) -> None:
        """
        Test that unused imports would be caught in CI pipeline.

        This test simulates the original bug scenario where unused imports
        were not detected, ensuring our current setup prevents this.
        """
        # Create a temporary file with an unused import
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(
                """
import os  # This import is unused
import sys  # This import is used

def example():
    return sys.version
"""
            )
            temp_file = Path(f.name)

        try:
            # Run Ruff on the temporary file
            result = subprocess.run(
                [
                    "poetry",
                    "run",
                    "ruff",
                    "check",
                    "--select=F401",
                    str(temp_file),
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            # Should detect the unused import
            assert (
                result.returncode != 0
            ), "Ruff should detect unused imports and return non-zero exit code"
            assert (
                "F401" in result.stdout or "imported but unused" in result.stdout.lower()
            ), "Should report F401 unused import violation"

        finally:
            # Clean up
            temp_file.unlink()

    def test_ci_pipeline_includes_lint_step(self) -> None:
        """
        Test that Makefile includes lint command for CI.

        Ensures that the lint step exists and would be run in CI.
        """
        backend_dir = Path(__file__).parent.parent.parent
        makefile_path = backend_dir / "Makefile"

        assert makefile_path.exists(), "Makefile should exist"

        content = makefile_path.read_text()
        assert "lint:" in content, "Makefile should have lint target"
        assert "ruff check" in content, "Lint target should run Ruff"

    def test_format_command_available_for_developers(self) -> None:
        """
        Test that developers have easy access to formatting tools.

        Ensures that 'make format' command exists and works.
        """
        backend_dir = Path(__file__).parent.parent.parent
        makefile_path = backend_dir / "Makefile"

        content = makefile_path.read_text()
        assert "format:" in content, "Makefile should have format target"
        assert "black" in content, "Format should include Black"
        assert "ruff" in content, "Format should include Ruff"
