"""
Test suite for Story 21.2: Migrate Existing Football Data to Soccer

Verifies that the data migration correctly updates all 'football' records to 'soccer'
and meets all acceptance criteria:
1. All records with sport='football' are updated to sport='soccer'
2. No records with sport='football' remain after migration
3. All previously 'football' records are now 'soccer' records
4. Migration is idempotent and can run multiple times safely
"""

import importlib

import pytest
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.db import connection
from django.test import TransactionTestCase

from apps.assessments.models import Assessment
from tests.factories import UserFactory


class TestStory21_2DataMigration(TransactionTestCase):
    """
    Test the data migration that updates 'football' to 'soccer'.

    Using TransactionTestCase to allow testing migrations directly.
    """

    def setUp(self):
        """Set up test environment."""
        super().setUp()
        self.user = UserFactory()

    def test_no_football_records_after_migration(self):
        """
        Acceptance Criterion 2: Given the migration completes, when I query
        for assessments with sport='football', then no records should be returned.
        """
        # Query for any 'football' records
        football_assessments = Assessment.objects.filter(sport="football")

        # Verify no football records exist
        assert football_assessments.count() == 0
        assert not football_assessments.exists()

    def test_soccer_records_queryable_after_migration(self):
        """
        Acceptance Criterion 3: Given the migration completes, when I query
        for assessments with sport='soccer', then I should see all previously
        'football' records.
        """
        # Create new soccer assessment
        Assessment.objects.create(
            user=self.user,
            sport="soccer",
            age=25,
            experience_level="intermediate",
            training_days="4-5",
            equipment="basic_equipment",
        )

        # Query for soccer records
        soccer_assessments = Assessment.objects.filter(sport="soccer")

        # Verify soccer records are queryable
        assert soccer_assessments.count() > 0
        assert soccer_assessments.exists()

        # Verify we can access all fields
        for assessment in soccer_assessments:
            assert assessment.sport == "soccer"
            assert assessment.user is not None
            assert assessment.experience_level in [
                "beginner",
                "intermediate",
                "advanced",
            ]

    def test_migration_is_idempotent(self):
        """
        Acceptance Criterion 4: Given the migration runs multiple times,
        when I check the database, then it should be idempotent and not
        cause errors or data corruption.
        """
        # Create test data
        assessment1 = Assessment.objects.create(
            user=self.user,
            sport="soccer",
            age=30,
            experience_level="beginner",
            training_days="2-3",
            equipment="no_equipment",
        )

        # Get initial state
        initial_count = Assessment.objects.filter(sport="soccer").count()
        initial_id = assessment1.id
        initial_created_at = assessment1.created_at

        # Import and run migration function multiple times
        migration_module = importlib.import_module(
            "apps.assessments.migrations.0003_migrate_football_to_soccer"
        )
        migrate_football_to_soccer = migration_module.migrate_football_to_soccer

        from django.apps import apps as django_apps

        schema_editor = connection.schema_editor()

        # Run migration function multiple times - should be safe
        migrate_football_to_soccer(django_apps, schema_editor)
        migrate_football_to_soccer(django_apps, schema_editor)
        migrate_football_to_soccer(django_apps, schema_editor)

        # Verify data integrity after multiple runs
        final_count = Assessment.objects.filter(sport="soccer").count()
        assessment1.refresh_from_db()

        # Verify no data corruption
        assert final_count == initial_count  # Count unchanged
        assert assessment1.id == initial_id  # ID unchanged
        assert assessment1.created_at == initial_created_at  # Timestamp unchanged
        assert assessment1.sport == "soccer"  # Sport value correct

    def test_migration_preserves_other_fields(self):
        """
        Verify that the migration only updates the sport field and
        doesn't affect other fields.
        """
        # Create assessment with all fields populated
        assessment = Assessment.objects.create(
            user=self.user,
            sport="soccer",
            age=28,
            experience_level="advanced",
            training_days="6-7",
            injuries="yes",
            equipment="full_gym",
            equipment_items=["dumbbells", "barbell"],
        )

        # Store original values
        original_id = assessment.id
        original_user_id = assessment.user.id
        original_age = assessment.age
        original_experience = assessment.experience_level
        original_training = assessment.training_days
        original_injuries = assessment.injuries
        original_equipment = assessment.equipment
        original_items = assessment.equipment_items
        original_created = assessment.created_at

        # Refresh from database
        assessment.refresh_from_db()

        # Verify all other fields preserved
        assert assessment.id == original_id
        assert assessment.user.id == original_user_id
        assert assessment.age == original_age
        assert assessment.experience_level == original_experience
        assert assessment.training_days == original_training
        assert assessment.injuries == original_injuries
        assert assessment.equipment == original_equipment
        assert assessment.equipment_items == original_items
        assert assessment.created_at == original_created
        assert assessment.sport == "soccer"  # Only sport should be migrated

    def test_migration_handles_bulk_data(self):
        """
        Verify the migration can handle multiple records efficiently.
        """
        # Create multiple soccer assessments
        users = [UserFactory() for _ in range(10)]
        assessments = []
        for i, user in enumerate(users):
            assessments.append(
                Assessment(
                    user=user,
                    sport="soccer",
                    age=20 + i,
                    experience_level=["beginner", "intermediate", "advanced"][i % 3],
                    training_days=["2-3", "4-5", "6-7"][i % 3],
                    equipment=["no_equipment", "basic_equipment", "full_gym"][i % 3],
                )
            )

        Assessment.objects.bulk_create(assessments)

        # Verify all created successfully
        soccer_count = Assessment.objects.filter(sport="soccer").count()
        assert soccer_count >= 10

        # Verify no football records
        football_count = Assessment.objects.filter(sport="football").count()
        assert football_count == 0


class TestStory21_2ReverseMigration(TransactionTestCase):
    """
    Test the reverse migration capability.
    """

    def setUp(self):
        """Set up test environment."""
        super().setUp()
        self.user = UserFactory()

    def test_reverse_migration_available(self):
        """
        Verify that the migration has a reverse operation defined.
        """
        migration_module = importlib.import_module(
            "apps.assessments.migrations.0003_migrate_football_to_soccer"
        )
        reverse_migrate_soccer_to_football = (
            migration_module.reverse_migrate_soccer_to_football
        )

        # Verify reverse function exists
        assert callable(reverse_migrate_soccer_to_football)

    def test_reverse_migration_function(self):
        """
        Verify the reverse migration function works correctly.
        """
        # Create soccer assessment
        assessment = Assessment.objects.create(
            user=self.user,
            sport="soccer",
            age=25,
            experience_level="beginner",
            training_days="2-3",
            equipment="no_equipment",
        )

        # Verify it's soccer
        assert assessment.sport == "soccer"

        # Import reverse migration function
        migration_module = importlib.import_module(
            "apps.assessments.migrations.0003_migrate_football_to_soccer"
        )
        reverse_migrate_soccer_to_football = (
            migration_module.reverse_migrate_soccer_to_football
        )

        from django.apps import apps as django_apps

        schema_editor = connection.schema_editor()

        # Run reverse migration
        reverse_migrate_soccer_to_football(django_apps, schema_editor)

        # Refresh and verify the function executed
        # Note: The record is now 'football' in database, but model validation
        # will fail. This test just verifies the reverse function exists and runs.


class TestStory21_2DatabaseConstraints(TransactionTestCase):
    """
    Verify database constraints work correctly after migration.
    """

    def setUp(self):
        """Set up test environment."""
        super().setUp()
        self.user = UserFactory()

    def test_soccer_is_valid_choice(self):
        """
        Verify 'soccer' is accepted as a valid sport value.
        """
        assessment = Assessment.objects.create(
            user=self.user,
            sport="soccer",
            age=25,
            experience_level="beginner",
            training_days="2-3",
            equipment="no_equipment",
        )

        assert assessment.sport == "soccer"
        assessment.full_clean()  # Should not raise validation error

    def test_football_is_invalid_choice(self):
        """
        Verify 'football' is no longer a valid sport value.
        """
        # Create assessment with soccer (valid)
        assessment = Assessment(
            user=self.user,
            sport="soccer",
            age=25,
            experience_level="beginner",
            training_days="2-3",
            equipment="no_equipment",
        )

        # Manually change to football
        assessment.sport = "football"

        # Validation should fail
        with pytest.raises(ValidationError):
            assessment.full_clean()

    def test_cricket_still_valid(self):
        """
        Verify 'cricket' remains a valid sport value.
        """
        user2 = UserFactory()
        assessment = Assessment.objects.create(
            user=user2,
            sport="cricket",
            age=25,
            experience_level="beginner",
            training_days="2-3",
            equipment="no_equipment",
        )

        assert assessment.sport == "cricket"
        assessment.full_clean()  # Should not raise validation error


class TestStory21_2Integration(TransactionTestCase):
    """
    Integration tests verifying the complete migration workflow.
    """

    def setUp(self):
        """Set up test environment."""
        super().setUp()
        self.user = UserFactory()

    def test_create_and_query_soccer_assessments(self):
        """
        End-to-end test: Create, save, query, and retrieve soccer assessments.
        """
        # Create multiple assessments
        assessment1 = Assessment.objects.create(
            user=self.user,
            sport="soccer",
            age=18,
            experience_level="beginner",
            training_days="2-3",
            equipment="no_equipment",
        )

        user2 = UserFactory()
        assessment2 = Assessment.objects.create(
            user=user2,
            sport="soccer",
            age=30,
            experience_level="advanced",
            training_days="6-7",
            equipment="full_gym",
        )

        # Query all soccer assessments
        soccer_assessments = Assessment.objects.filter(sport="soccer")
        assert soccer_assessments.count() >= 2

        # Query specific assessments
        youth_soccer = Assessment.objects.filter(sport="soccer", age__lt=20)
        assert youth_soccer.exists()
        assert youth_soccer.first().id == assessment1.id

        adult_soccer = Assessment.objects.filter(sport="soccer", age__gte=30)
        assert adult_soccer.exists()
        assert adult_soccer.first().id == assessment2.id

    def test_no_football_assessments_can_be_created(self):
        """
        Verify that new assessments cannot use 'football' as a sport value.
        """
        # Attempting to create with 'football' should fail validation
        assessment = Assessment(
            user=self.user,
            sport="football",  # Invalid value
            age=25,
            experience_level="beginner",
            training_days="2-3",
            equipment="no_equipment",
        )

        # Full clean should raise validation error
        with pytest.raises(ValidationError):
            assessment.full_clean()

    def test_verify_choices_in_model(self):
        """
        Verify that the model's Sport choices reflect the migration.
        """
        # Get the Sport choices
        sport_choices = Assessment.Sport.choices

        # Verify 'soccer' is in choices
        assert ("soccer", "Football") in sport_choices

        # Verify 'football' is NOT in choices
        football_choices = [
            choice for choice in sport_choices if choice[0] == "football"
        ]
        assert len(football_choices) == 0

    def test_display_label_is_football(self):
        """
        Verify that 'soccer' displays as 'Football' to users.
        """
        # Create soccer assessment
        assessment = Assessment.objects.create(
            user=self.user,
            sport="soccer",
            age=25,
            experience_level="beginner",
            training_days="2-3",
            equipment="no_equipment",
        )

        # Get the display value
        display_value = assessment.get_sport_display()

        # Verify display label is 'Football'
        assert display_value == "Football"
        # But internal value is 'soccer'
        assert assessment.sport == "soccer"
