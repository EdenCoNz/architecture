"""Tests to verify code quality tools are properly configured.

This test module demonstrates that the testing infrastructure works
and that code quality tools can analyze the codebase.
"""

from typing import List

import pytest


@pytest.mark.unit
def test_code_quality_tools_configured() -> None:
    """Verify that code quality tools can run on properly formatted code.

    This test verifies:
    - pytest is working
    - Type annotations are recognized
    - Test discovery works
    - Basic assertions work
    """
    # Test basic functionality
    result = calculate_sum([1, 2, 3, 4, 5])
    assert result == 15

    # Test with empty list
    result = calculate_sum([])
    assert result == 0

    # Test with negative numbers
    result = calculate_sum([-1, -2, -3])
    assert result == -6


def calculate_sum(numbers: List[int]) -> int:
    """Calculate the sum of a list of numbers.

    Args:
        numbers: List of integers to sum

    Returns:
        The sum of all numbers in the list

    Examples:
        >>> calculate_sum([1, 2, 3])
        6
        >>> calculate_sum([])
        0
    """
    return sum(numbers)


@pytest.mark.unit
def test_type_annotations() -> None:
    """Verify that type annotations are working correctly.

    This test demonstrates proper use of type annotations
    that mypy can verify.
    """
    # Test string operations
    result: str = format_name("john", "doe")
    assert result == "John Doe"

    # Test with empty strings
    result = format_name("", "")
    assert result == " "


def format_name(first_name: str, last_name: str) -> str:
    """Format a full name from first and last name.

    Args:
        first_name: Person's first name
        last_name: Person's last name

    Returns:
        Formatted full name with title case

    Examples:
        >>> format_name("john", "doe")
        'John Doe'
    """
    return f"{first_name.title()} {last_name.title()}"


@pytest.mark.unit
def test_configuration_values() -> None:
    """Test that demonstrates checking configuration values.

    This shows how to test configuration-dependent functionality.
    """
    # Test basic Python functionality
    test_dict = {"key1": "value1", "key2": "value2"}
    assert "key1" in test_dict
    assert test_dict["key1"] == "value1"

    # Test list operations
    test_list = [1, 2, 3, 4, 5]
    assert len(test_list) == 5
    assert max(test_list) == 5
    assert min(test_list) == 1
