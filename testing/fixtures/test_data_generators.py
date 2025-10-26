"""
Test Data Generation Utilities for Integration Tests.

This module provides utilities to generate realistic test data for users and assessments
for use in integration and end-to-end tests.

This is a wrapper module that imports from the backend test utilities to maintain
consistency across unit tests and integration tests.

Usage Examples:
    # In integration tests
    from fixtures.test_data_generators import (
        UserDataGenerator,
        AssessmentDataGenerator,
        EdgeCaseDataGenerator,
        TestDataGenerator
    )

    # Generate test users
    user_gen = UserDataGenerator()
    user = user_gen.generate_user()

    # Generate test assessments
    assessment_gen = AssessmentDataGenerator()
    assessments = assessment_gen.generate_assessments(count=10)

    # Generate edge cases
    edge_gen = EdgeCaseDataGenerator()
    min_age = edge_gen.generate_minimum_age_assessment()

    # Generate complete scenarios
    test_gen = TestDataGenerator()
    scenario = test_gen.generate_realistic_scenario()
"""

import os
import sys

# Add backend to path to import from backend tests
backend_path = os.path.join(os.path.dirname(__file__), "..", "..", "backend")
sys.path.insert(0, backend_path)

# Import and re-export the generators
from tests.test_data_generators import (  # noqa: E402
    AssessmentDataGenerator,
    EdgeCaseDataGenerator,
    TestDataGenerator,
    UserDataGenerator,
)

__all__ = [
    "UserDataGenerator",
    "AssessmentDataGenerator",
    "EdgeCaseDataGenerator",
    "TestDataGenerator",
]
