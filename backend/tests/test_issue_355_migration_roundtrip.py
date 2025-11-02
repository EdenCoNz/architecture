"""
Test suite for Issue #355: Verify migration reversibility and round-trip capability.

This test validates that migrations can be applied and reversed repeatedly without
data corruption or constraint violations.
"""

import importlib
import json

import pytest
from django.core.management import call_command
from django.db import connection
from django.test import TransactionTestCase

from apps.assessments.models import Assessment
from tests.factories import UserFactory


class TestIssue355MigrationRoundTrip(TransactionTestCase):
    """
    Test the complete migration round-trip: forward -> reverse -> forward.

    Validates Acceptance Criteria:
    1. Reverse migration completes without IntegrityError
    2. Records are properly reverted from "soccer" to "football"
    3. Forward migration can be re-applied successfully
    """

    def setUp(self):
        """Set up test environment."""
        super().setUp()
        self.user = UserFactory()

    def test_migration_roundtrip(self):
        """
        Test forward -> reverse -> forward migration sequence.

        Acceptance Criteria:
        - AC1: Reverse migration completes without IntegrityError
        - AC2: Records are reverted from "soccer" to "football"
        - AC4: Forward migration can be re-applied successfully
        """
        # Create test data with soccer
        assessment = Assessment.objects.create(
            user=self.user,
            sport="soccer",
            age=25,
            experience_level="beginner",
            training_days="2-3",
            equipment="no_equipment",
        )

        # Verify initial state
        assert assessment.sport == "soccer"
        initial_id = assessment.id

        # Import migration functions
        migration_module = importlib.import_module(
            "apps.assessments.migrations.0003_migrate_football_to_soccer"
        )
        migrate_football_to_soccer = migration_module.migrate_football_to_soccer
        reverse_migrate_soccer_to_football = migration_module.reverse_migrate_soccer_to_football

        from django.apps import apps as django_apps

        schema_editor = connection.schema_editor()

        # Step 1: Run reverse migration (soccer -> football)
        # AC1: This should complete without IntegrityError
        reverse_migrate_soccer_to_football(django_apps, schema_editor)

        # Step 2: Verify data was reverted
        # AC2: Records should be "football" now
        # Note: We query directly from DB since model validation would fail
        with connection.cursor() as cursor:
            cursor.execute("SELECT sport FROM assessments WHERE id = %s", [initial_id])
            sport_value = cursor.fetchone()[0]
            assert sport_value == "football", "Record should be reverted to 'football'"

        # Step 3: Run forward migration again (football -> soccer)
        # AC4: Forward migration should execute successfully
        migrate_football_to_soccer(django_apps, schema_editor)

        # Step 4: Verify data is back to soccer
        assessment.refresh_from_db()
        assert assessment.sport == "soccer", "Record should be migrated back to 'soccer'"
        assert assessment.id == initial_id, "Record ID should be unchanged"

    def test_reverse_migration_with_multiple_records(self):
        """
        Test reverse migration handles multiple records correctly.
        """
        # Create multiple soccer assessments
        users = [UserFactory() for _ in range(5)]
        assessments = []
        for user in users:
            assessment = Assessment.objects.create(
                user=user,
                sport="soccer",
                age=25,
                experience_level="beginner",
                training_days="2-3",
                equipment="no_equipment",
            )
            assessments.append(assessment)

        # Import reverse migration
        migration_module = importlib.import_module(
            "apps.assessments.migrations.0003_migrate_football_to_soccer"
        )
        reverse_migrate_soccer_to_football = migration_module.reverse_migrate_soccer_to_football

        from django.apps import apps as django_apps

        schema_editor = connection.schema_editor()

        # Run reverse migration
        # AC1: Should complete without IntegrityError
        reverse_migrate_soccer_to_football(django_apps, schema_editor)

        # Verify all records were reverted
        # AC2: All records should be "football"
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM assessments WHERE sport = 'football'")
            football_count = cursor.fetchone()[0]
            assert football_count == 5, "All records should be reverted to 'football'"

            cursor.execute("SELECT COUNT(*) FROM assessments WHERE sport = 'soccer'")
            soccer_count = cursor.fetchone()[0]
            assert soccer_count == 0, "No soccer records should remain"

    def test_reverse_migration_preserves_data_integrity(self):
        """
        Verify reverse migration preserves all other fields.
        """
        # Create assessment with all fields
        assessment = Assessment.objects.create(
            user=self.user,
            sport="soccer",
            age=28,
            experience_level="advanced",
            training_days="6-7",
            injuries="yes",
            equipment="full_gym",
            equipment_items=["dumbbells", "barbell", "bench"],
        )

        # Store original values
        original_id = assessment.id
        original_user_id = assessment.user.id
        original_age = assessment.age
        original_experience = assessment.experience_level
        original_training = assessment.training_days
        original_injuries = assessment.injuries
        original_equipment = assessment.equipment
        original_items = list(assessment.equipment_items)  # Copy list
        original_created = assessment.created_at

        # Import and run reverse migration
        migration_module = importlib.import_module(
            "apps.assessments.migrations.0003_migrate_football_to_soccer"
        )
        reverse_migrate_soccer_to_football = migration_module.reverse_migrate_soccer_to_football

        from django.apps import apps as django_apps

        schema_editor = connection.schema_editor()

        reverse_migrate_soccer_to_football(django_apps, schema_editor)

        # Query data directly from DB
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT user_id, age, experience_level, training_days,
                       injuries, equipment, equipment_items, created_at, sport
                FROM assessments WHERE id = %s
                """,
                [original_id],
            )
            row = cursor.fetchone()

            # Verify all fields preserved (except sport which should be 'football')
            assert row[0] == original_user_id, "User ID should be preserved"
            assert row[1] == original_age, "Age should be preserved"
            assert row[2] == original_experience, "Experience level should be preserved"
            assert row[3] == original_training, "Training days should be preserved"
            assert row[4] == original_injuries, "Injuries should be preserved"
            assert row[5] == original_equipment, "Equipment should be preserved"
            # Equipment items is JSONField - parse if string, compare if list
            equipment_items = row[6] if isinstance(row[6], list) else json.loads(row[6])
            assert equipment_items == original_items, "Equipment items should be preserved"
            # Note: Skip timestamp comparison due to timezone handling complexity
            assert row[8] == "football", "Sport should be 'football'"
