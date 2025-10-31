"""
Integration tests for equipment data migration command.

Tests the management command that converts existing multiple-selection equipment data
to single-selection format while preserving user assessments and flagging those needing
re-assessment.
"""

import json
import tempfile
from io import StringIO

import pytest
from django.core.management import call_command
from django.test import TestCase

from apps.assessments.management.commands.migrate_equipment_data import EquipmentMigrator
from apps.assessments.models import Assessment
from apps.users.models import User


@pytest.mark.django_db
class TestEquipmentMigrator:
    """Test EquipmentMigrator class."""

    def test_migrator_initialization(self):
        """Test migrator initializes with correct state."""
        migrator = EquipmentMigrator()
        assert migrator.migrated_count == 0
        assert migrator.flagged_count == 0
        assert migrator.skipped_count == 0
        assert migrator.error_count == 0
        assert migrator.migration_details == []

    def test_equipment_hierarchy_defined(self):
        """Test equipment hierarchy is properly defined."""
        migrator = EquipmentMigrator()
        assert "full_gym" in migrator.EQUIPMENT_HIERARCHY
        assert "basic_equipment" in migrator.EQUIPMENT_HIERARCHY
        assert "no_equipment" in migrator.EQUIPMENT_HIERARCHY
        assert (
            migrator.EQUIPMENT_HIERARCHY["full_gym"]
            > migrator.EQUIPMENT_HIERARCHY["basic_equipment"]
        )
        assert (
            migrator.EQUIPMENT_HIERARCHY["basic_equipment"]
            > migrator.EQUIPMENT_HIERARCHY["no_equipment"]
        )

    def test_valid_equipment_options_defined(self):
        """Test valid equipment options are defined."""
        migrator = EquipmentMigrator()
        assert len(migrator.VALID_EQUIPMENT_OPTIONS) == 3
        assert "no_equipment" in migrator.VALID_EQUIPMENT_OPTIONS
        assert "basic_equipment" in migrator.VALID_EQUIPMENT_OPTIONS
        assert "full_gym" in migrator.VALID_EQUIPMENT_OPTIONS

    def test_convert_multiple_to_single_empty_list(self):
        """Test conversion with empty list returns None."""
        migrator = EquipmentMigrator()
        result = migrator._convert_multiple_to_single([])
        assert result is None

    def test_convert_multiple_to_single_single_item(self):
        """Test conversion with single item returns that item."""
        migrator = EquipmentMigrator()
        result = migrator._convert_multiple_to_single(["full_gym"])
        assert result == "full_gym"

    def test_convert_multiple_to_single_multiple_items_hierarchy(self):
        """Test conversion selects item with highest hierarchy."""
        migrator = EquipmentMigrator()

        # full_gym should win
        result = migrator._convert_multiple_to_single(
            ["no_equipment", "full_gym", "basic_equipment"]
        )
        assert result == "full_gym"

        # basic_equipment should win
        result = migrator._convert_multiple_to_single(["no_equipment", "basic_equipment"])
        assert result == "basic_equipment"

        # no_equipment only
        result = migrator._convert_multiple_to_single(["no_equipment"])
        assert result == "no_equipment"

    def test_convert_multiple_to_single_invalid_options_ignored(self):
        """Test conversion ignores invalid options."""
        migrator = EquipmentMigrator()
        result = migrator._convert_multiple_to_single(["invalid_option", "full_gym"])
        assert result == "full_gym"

    def test_convert_multiple_to_single_all_invalid_returns_none(self):
        """Test conversion returns None if all options invalid."""
        migrator = EquipmentMigrator()
        result = migrator._convert_multiple_to_single(["invalid1", "invalid2"])
        assert result is None

    def test_migrate_valid_string_equipment_skipped(self):
        """Test migration skips already valid string equipment."""
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        assessment = Assessment.objects.create(
            user=user,
            sport="football",
            age=25,
            experience_level="intermediate",
            training_days="4-5",
            equipment="full_gym",
            equipment_items=[],
        )

        migrator = EquipmentMigrator()
        success, message = migrator.migrate_equipment_field(assessment)

        assert success is True
        assert "Already valid" in message
        assert migrator.skipped_count == 1
        assert migrator.migrated_count == 0

    def test_migrate_basic_equipment_without_items_flagged(self):
        """Test basic equipment without items is flagged for re-assessment."""
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        assessment = Assessment.objects.create(
            user=user,
            sport="football",
            age=25,
            experience_level="intermediate",
            training_days="4-5",
            equipment="basic_equipment",
            equipment_items=[],
        )

        migrator = EquipmentMigrator()
        success, message = migrator.migrate_equipment_field(assessment)

        assert success is True
        assert "Flagged" in message
        assert migrator.flagged_count == 1
        # Equipment should not be changed
        assessment.refresh_from_db()
        assert assessment.equipment == "basic_equipment"

    def test_migrate_basic_equipment_with_items_accepted(self):
        """Test basic equipment with items is accepted without flagging."""
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        assessment = Assessment.objects.create(
            user=user,
            sport="football",
            age=25,
            experience_level="intermediate",
            training_days="4-5",
            equipment="basic_equipment",
            equipment_items=["dumbbell", "barbell"],
        )

        migrator = EquipmentMigrator()
        success, message = migrator.migrate_equipment_field(assessment)

        assert success is True
        assert migrator.skipped_count == 1
        assert migrator.flagged_count == 0

    def test_migrate_multiple_selections_to_single(self):
        """Test migration converts multiple selections to single selection.

        Note: Since equipment field is CharField in current schema, this test
        simulates the migration logic directly rather than storing a list.
        """
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        assessment = Assessment.objects.create(
            user=user,
            sport="football",
            age=25,
            experience_level="intermediate",
            training_days="4-5",
            equipment="no_equipment",  # Will be manually set to list for testing
            equipment_items=[],
        )

        # Simulate legacy data with multiple selections by setting equipment field directly
        assessment.equipment = ["no_equipment", "basic_equipment"]

        migrator = EquipmentMigrator()
        success, message = migrator.migrate_equipment_field(assessment)

        assert success is True
        assert migrator.migrated_count == 1
        assessment.refresh_from_db()
        assert assessment.equipment == "basic_equipment"  # Higher hierarchy wins

    def test_migrate_multiple_selections_clears_items_when_needed(self):
        """Test migration clears items when not basic equipment."""
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        assessment = Assessment.objects.create(
            user=user,
            sport="football",
            age=25,
            experience_level="intermediate",
            training_days="4-5",
            equipment="no_equipment",
            equipment_items=["dumbbell"],  # Has items
        )

        # Simulate legacy data with multiple selections
        assessment.equipment = ["no_equipment", "basic_equipment", "full_gym"]

        migrator = EquipmentMigrator()
        success, message = migrator.migrate_equipment_field(assessment)

        assert success is True
        assessment.refresh_from_db()
        assert assessment.equipment == "full_gym"
        assert assessment.equipment_items == []  # Items cleared

    def test_migrate_invalid_equipment_returns_error(self):
        """Test migration with invalid equipment returns error."""
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        assessment = Assessment.objects.create(
            user=user,
            sport="football",
            age=25,
            experience_level="intermediate",
            training_days="4-5",
            equipment="invalid_equipment",
            equipment_items=[],
        )

        migrator = EquipmentMigrator()
        success, message = migrator.migrate_equipment_field(assessment)

        assert success is False
        assert "Invalid equipment" in message
        assert migrator.error_count == 1

    def test_migration_report_generation(self):
        """Test migration report is generated correctly."""
        migrator = EquipmentMigrator()
        migrator.migrated_count = 5
        migrator.flagged_count = 2
        migrator.skipped_count = 3
        migrator.error_count = 1

        report = migrator.generate_report()

        assert report["summary"]["migrated"] == 5
        assert report["summary"]["flagged"] == 2
        assert report["summary"]["skipped"] == 3
        assert report["summary"]["errors"] == 1
        assert report["summary"]["total_processed"] == 11

    def test_migration_details_tracking(self):
        """Test migration details are tracked for each assessment."""
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        assessment = Assessment.objects.create(
            user=user,
            sport="football",
            age=25,
            experience_level="intermediate",
            training_days="4-5",
            equipment="full_gym",
            equipment_items=[],
        )

        migrator = EquipmentMigrator()
        migrator.migrate_equipment_field(assessment)

        assert len(migrator.migration_details) == 1
        detail = migrator.migration_details[0]
        assert detail["user_id"] == user.id
        assert detail["user_email"] == user.email
        assert detail["status"] == "skipped"  # Already valid single selection
        assert detail["equipment"] == "full_gym"  # For skipped status, uses "equipment" key


@pytest.mark.django_db
class TestMigrateEquipmentDataCommand:
    """Test the migrate_equipment_data management command."""

    def test_command_with_no_assessments(self):
        """Test command when no assessments exist."""
        out = StringIO()
        call_command("migrate_equipment_data", stdout=out)
        output = out.getvalue()
        assert "No assessments found" in output

    def test_command_processes_all_assessments(self):
        """Test command processes all assessments."""
        # Create multiple assessments
        for i in range(3):
            user = User.objects.create_user(email=f"user{i}@example.com", password="testpass123")
            Assessment.objects.create(
                user=user,
                sport="football",
                age=25,
                experience_level="intermediate",
                training_days="4-5",
                equipment="full_gym",
                equipment_items=[],
            )

        out = StringIO()
        call_command("migrate_equipment_data", stdout=out)
        output = out.getvalue()

        assert "Found 3 assessments" in output
        assert "Migration completed successfully" in output

    def test_command_dry_run_mode(self):
        """Test command dry run mode doesn't save changes."""
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        assessment = Assessment.objects.create(
            user=user,
            sport="football",
            age=25,
            experience_level="intermediate",
            training_days="4-5",
            equipment="basic_equipment",
            equipment_items=[],  # No items - should be flagged
        )

        out = StringIO()
        call_command("migrate_equipment_data", "--dry-run", stdout=out)
        output = out.getvalue()

        assert "DRY RUN MODE" in output
        assert "Rolling back changes" in output

        # Verify data wasn't changed - equipment field remains basic_equipment
        assessment.refresh_from_db()
        assert assessment.equipment == "basic_equipment"
        assert assessment.equipment_items == []

    def test_command_save_report(self):
        """Test command saves report to file."""
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        Assessment.objects.create(
            user=user,
            sport="football",
            age=25,
            experience_level="intermediate",
            training_days="4-5",
            equipment="full_gym",
            equipment_items=[],
        )

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            report_file = f.name

        try:
            out = StringIO()
            call_command("migrate_equipment_data", f"--save-report={report_file}", stdout=out)

            # Verify report file was created and contains valid JSON
            with open(report_file, "r") as f:
                report = json.load(f)

            assert "summary" in report
            assert "details" in report
            assert report["summary"]["total_processed"] > 0
        finally:
            import os

            if os.path.exists(report_file):
                os.unlink(report_file)

    def test_command_displays_report_summary(self):
        """Test command displays migration report summary."""
        user1 = User.objects.create_user(email="user1@example.com", password="testpass123")
        user2 = User.objects.create_user(email="user2@example.com", password="testpass123")

        # Create different scenarios
        Assessment.objects.create(  # Will be skipped
            user=user1,
            sport="football",
            age=25,
            experience_level="intermediate",
            training_days="4-5",
            equipment="full_gym",
            equipment_items=[],
        )

        Assessment.objects.create(  # Will be flagged
            user=user2,
            sport="football",
            age=25,
            experience_level="intermediate",
            training_days="4-5",
            equipment="basic_equipment",
            equipment_items=[],
        )

        out = StringIO()
        call_command("migrate_equipment_data", stdout=out)
        output = out.getvalue()

        assert "Migration Report" in output
        assert "Total Processed:" in output
        assert "Skipped" in output
        assert "Flagged" in output

    def test_users_can_access_migrated_data_on_login(self):
        """Test that users with migrated data can access their updated equipment selection."""
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        assessment = Assessment.objects.create(
            user=user,
            sport="football",
            age=25,
            experience_level="intermediate",
            training_days="4-5",
            equipment="no_equipment",
            equipment_items=[],
        )

        # Simulate legacy data with multiple selections
        assessment.equipment = ["no_equipment", "basic_equipment"]

        # Perform migration
        migrator = EquipmentMigrator()
        migrator.migrate_equipment_field(assessment)

        # Verify user can access their updated assessment
        refreshed_assessment = Assessment.objects.get(user=user)
        assert refreshed_assessment.equipment == "basic_equipment"
        assert isinstance(refreshed_assessment.equipment, str)

    def test_migration_preserves_other_assessment_fields(self):
        """Test that migration doesn't affect other assessment fields."""
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        assessment = Assessment.objects.create(
            user=user,
            sport="cricket",
            age=30,
            experience_level="advanced",
            training_days="6-7",
            injuries="yes",
            equipment="no_equipment",
            equipment_items=[],
        )

        # Simulate legacy data with multiple selections
        assessment.equipment = ["no_equipment", "full_gym"]

        original_sport = assessment.sport
        original_age = assessment.age
        original_experience = assessment.experience_level
        original_training_days = assessment.training_days
        original_injuries = assessment.injuries

        # Perform migration
        migrator = EquipmentMigrator()
        migrator.migrate_equipment_field(assessment)

        # Verify other fields unchanged
        assessment.refresh_from_db()
        assert assessment.sport == original_sport
        assert assessment.age == original_age
        assert assessment.experience_level == original_experience
        assert assessment.training_days == original_training_days
        assert assessment.injuries == original_injuries

    def test_migration_handles_edge_cases(self):
        """Test migration handles edge cases correctly."""
        user = User.objects.create_user(email="test@example.com", password="testpass123")

        # Duplicate selections
        assessment1 = Assessment.objects.create(
            user=user,
            sport="football",
            age=25,
            experience_level="intermediate",
            training_days="4-5",
            equipment="full_gym",
            equipment_items=[],
        )

        # Simulate legacy data with duplicate selections
        assessment1.equipment = ["full_gym", "full_gym", "full_gym"]

        migrator = EquipmentMigrator()
        success, _ = migrator.migrate_equipment_field(assessment1)

        assert success is True
        assessment1.refresh_from_db()
        assert assessment1.equipment == "full_gym"


class TestEquipmentMigrationAcceptanceCriteria(TestCase):
    """Test that implementation meets all acceptance criteria."""

    @pytest.mark.django_db
    def test_criterion_1_multiple_selections_retains_advanced(self):
        """AC1: When existing assessment data has multiple equipment selections,
        the most specific or advanced option should be retained."""
        user = User.objects.create_user(email="test@example.com", password="testpass123")

        # Scenario: User selected both no_equipment and full_gym
        assessment = Assessment.objects.create(
            user=user,
            sport="football",
            age=25,
            experience_level="intermediate",
            training_days="4-5",
            equipment="no_equipment",
            equipment_items=[],
        )

        # Simulate legacy data with multiple selections
        assessment.equipment = ["no_equipment", "full_gym"]

        migrator = EquipmentMigrator()
        migrator.migrate_equipment_field(assessment)

        assessment.refresh_from_db()
        # Most advanced (full_gym) should be retained
        assert assessment.equipment == "full_gym"

    @pytest.mark.django_db
    def test_criterion_2_basic_equipment_without_items_flagged(self):
        """AC2: When existing equipment data indicates "basic equipment" without specific items,
        it should be flagged for user re-assessment."""
        user = User.objects.create_user(email="test@example.com", password="testpass123")

        assessment = Assessment.objects.create(
            user=user,
            sport="football",
            age=25,
            experience_level="intermediate",
            training_days="4-5",
            equipment="basic_equipment",
            equipment_items=[],  # No specific items
        )

        migrator = EquipmentMigrator()
        success, message = migrator.migrate_equipment_field(assessment)

        assert success is True
        assert migrator.flagged_count == 1
        assert "Flagged" in message or "re-assess" in message

    @pytest.mark.django_db
    def test_criterion_3_users_not_losing_assessment(self):
        """AC3: When existing equipment data is migrated, users should not lose
        their original assessment."""
        user = User.objects.create_user(email="test@example.com", password="testpass123")

        # Create assessment with multiple selections
        assessment = Assessment.objects.create(
            user=user,
            sport="cricket",
            age=32,
            experience_level="advanced",
            training_days="6-7",
            injuries="yes",
            equipment="no_equipment",
            equipment_items=[],
        )

        # Simulate legacy data with multiple selections
        assessment.equipment = ["no_equipment", "basic_equipment", "full_gym"]

        assessment_id = assessment.id

        migrator = EquipmentMigrator()
        migrator.migrate_equipment_field(assessment)

        # Verify assessment still exists and is accessible
        refreshed = Assessment.objects.get(id=assessment_id)
        assert refreshed is not None
        assert refreshed.user == user
        assert refreshed.sport == "cricket"
        assert refreshed.age == 32
        assert refreshed.experience_level == "advanced"

    @pytest.mark.django_db
    def test_criterion_4_migrated_data_visible_on_login(self):
        """AC4: When users with migrated data log in, they should see their
        updated equipment selection."""
        user = User.objects.create_user(email="test@example.com", password="testpass123")

        assessment = Assessment.objects.create(
            user=user,
            sport="football",
            age=25,
            experience_level="intermediate",
            training_days="4-5",
            equipment="basic_equipment",
            equipment_items=[],
        )

        # Simulate legacy data with multiple selections
        assessment.equipment = ["basic_equipment", "full_gym"]

        # Simulate migration
        migrator = EquipmentMigrator()
        migrator.migrate_equipment_field(assessment)

        # Simulate user login - fetch their assessment
        user_assessment = Assessment.objects.get(user=user)

        # User should see the updated (single) selection
        assert isinstance(user_assessment.equipment, str)
        assert user_assessment.equipment == "full_gym"
        assert user_assessment.equipment in Assessment.Equipment.values
