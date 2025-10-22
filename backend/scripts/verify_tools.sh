#!/usr/bin/env bash

# Script to verify code quality tools are properly configured and working
# This script should be run after setting up the development environment

set -e  # Exit on error

echo "=================================================="
echo "Code Quality Tools Verification Script"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running in virtual environment
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo -e "${RED}ERROR: Virtual environment not activated!${NC}"
    echo "Please activate the virtual environment first:"
    echo "  source venv/bin/activate"
    exit 1
fi

echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo "  Location: $VIRTUAL_ENV"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to verify tool
verify_tool() {
    local tool_name=$1
    local command=$2
    local expected_pattern=$3

    echo "Checking $tool_name..."

    if ! command_exists "$command"; then
        echo -e "${RED}✗ $tool_name not found${NC}"
        echo "  Install with: pip install $tool_name"
        return 1
    fi

    local version=$($command --version 2>&1 | head -1)
    echo -e "${GREEN}✓ $tool_name installed${NC}"
    echo "  Version: $version"
    return 0
}

echo "=================================================="
echo "1. Checking Tool Installation"
echo "=================================================="
echo ""

# Track overall status
all_passed=true

# Check Python version
echo "Checking Python version..."
python_version=$(python --version 2>&1)
echo -e "${GREEN}✓ $python_version${NC}"
echo ""

# Check Black
if verify_tool "Black" "black" "black"; then
    echo ""
else
    all_passed=false
    echo ""
fi

# Check isort
if verify_tool "isort" "isort" "isort"; then
    echo ""
else
    all_passed=false
    echo ""
fi

# Check Flake8
if verify_tool "Flake8" "flake8" "flake8"; then
    echo ""
else
    all_passed=false
    echo ""
fi

# Check mypy
if verify_tool "mypy" "mypy" "mypy"; then
    echo ""
else
    all_passed=false
    echo ""
fi

# Check pytest
if verify_tool "pytest" "pytest" "pytest"; then
    echo ""
else
    all_passed=false
    echo ""
fi

# Check pre-commit
if verify_tool "pre-commit" "pre-commit" "pre-commit"; then
    echo ""
else
    all_passed=false
    echo ""
fi

echo "=================================================="
echo "2. Checking Configuration Files"
echo "=================================================="
echo ""

# Check configuration files
config_files=(
    "pyproject.toml"
    ".flake8"
    "pytest.ini"
    ".pre-commit-config.yaml"
    ".editorconfig"
)

for file in "${config_files[@]}"; do
    if [[ -f "$file" ]]; then
        echo -e "${GREEN}✓ $file exists${NC}"
    else
        echo -e "${RED}✗ $file missing${NC}"
        all_passed=false
    fi
done

echo ""

echo "=================================================="
echo "3. Running Tool Verification Tests"
echo "=================================================="
echo ""

# Create a temporary test file
test_file=$(mktemp --suffix=.py)
cat > "$test_file" << 'EOF'
"""Test file for code quality verification."""
import os
import sys
from typing import List


def test_function(items: List[str]) -> int:
    """Test function with proper type annotations."""
    return len(items)


def untyped_function():
    """Function without type annotations."""
    pass
EOF

echo "Created test file: $test_file"
echo ""

# Test Black
echo "Testing Black (code formatter)..."
if black --check "$test_file" 2>&1; then
    echo -e "${GREEN}✓ Black check passed${NC}"
else
    echo -e "${YELLOW}⚠ Black would reformat (this is expected)${NC}"
    black "$test_file" 2>&1 > /dev/null
    echo -e "${GREEN}✓ Black formatting successful${NC}"
fi
echo ""

# Test isort
echo "Testing isort (import sorter)..."
if isort --check-only "$test_file" 2>&1; then
    echo -e "${GREEN}✓ isort check passed${NC}"
else
    echo -e "${YELLOW}⚠ isort would reformat (this is expected)${NC}"
    isort "$test_file" 2>&1 > /dev/null
    echo -e "${GREEN}✓ isort sorting successful${NC}"
fi
echo ""

# Test Flake8
echo "Testing Flake8 (linter)..."
if flake8 "$test_file" 2>&1; then
    echo -e "${GREEN}✓ Flake8 check passed${NC}"
else
    echo -e "${YELLOW}⚠ Flake8 found issues (expected for test file)${NC}"
    flake8 "$test_file" 2>&1 | head -5
fi
echo ""

# Test mypy
echo "Testing mypy (type checker)..."
mypy_output=$(mypy "$test_file" 2>&1 || true)
if echo "$mypy_output" | grep -q "Success"; then
    echo -e "${GREEN}✓ mypy check passed${NC}"
else
    echo -e "${YELLOW}⚠ mypy found type issues:${NC}"
    echo "$mypy_output" | head -5
fi
echo ""

# Clean up test file
rm -f "$test_file"

echo "=================================================="
echo "4. Checking Pre-commit Hooks"
echo "=================================================="
echo ""

if [[ -f ".git/hooks/pre-commit" ]]; then
    echo -e "${GREEN}✓ Pre-commit hooks installed${NC}"
    echo "  Location: .git/hooks/pre-commit"
else
    echo -e "${YELLOW}⚠ Pre-commit hooks not installed${NC}"
    echo "  Install with: make pre-commit"
    echo "  Or: pre-commit install"
fi
echo ""

# Check pre-commit configuration
echo "Checking pre-commit configuration..."
if pre-commit validate-config 2>&1; then
    echo -e "${GREEN}✓ Pre-commit configuration valid${NC}"
else
    echo -e "${RED}✗ Pre-commit configuration invalid${NC}"
    all_passed=false
fi
echo ""

echo "=================================================="
echo "5. Testing Project Files"
echo "=================================================="
echo ""

# Test formatting on actual project files (non-destructive)
echo "Running Black on project (check only)..."
if black --check apps/ config/ tests/ 2>&1 | tail -5; then
    echo -e "${GREEN}✓ All project files properly formatted${NC}"
else
    echo -e "${YELLOW}⚠ Some files need formatting (run: make format)${NC}"
fi
echo ""

# Test linting on actual project files
echo "Running Flake8 on project..."
flake8_output=$(flake8 apps/ config/ tests/ 2>&1 || true)
if [[ -z "$flake8_output" ]]; then
    echo -e "${GREEN}✓ No linting issues found${NC}"
else
    echo -e "${YELLOW}⚠ Flake8 found issues:${NC}"
    echo "$flake8_output" | head -10
    echo ""
    echo "Run 'make lint' for full output"
fi
echo ""

echo "=================================================="
echo "Summary"
echo "=================================================="
echo ""

if $all_passed; then
    echo -e "${GREEN}✓ All code quality tools are properly configured!${NC}"
    echo ""
    echo "You can now:"
    echo "  - Run 'make format' to format code"
    echo "  - Run 'make lint' to check for issues"
    echo "  - Run 'make type-check' to verify types"
    echo "  - Run 'make quality' to run all checks"
    echo "  - Run 'make pre-commit' to install hooks"
    echo ""
    exit 0
else
    echo -e "${RED}✗ Some tools or configurations are missing${NC}"
    echo ""
    echo "Please install missing dependencies:"
    echo "  make install"
    echo ""
    exit 1
fi
