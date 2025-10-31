"""
Management command to migrate existing equipment data from multiple-selection to
single-selection format.

This command handles conversion of existing assessment data where equipment field
may contain multiple selections (from before Story 19.4) to the new
single-selection format.

Acceptance Criteria Implementation:
1. When existing assessment data has multiple equipment selections, the most
   specific or advanced option should be retained
2. When existing equipment data indicates "basic equipment" without specific
   items, it should be flagged for user re-assessment
3. When existing equipment data is migrated, users should not lose their
   original assessment
4. When users with migrated data log in, they should see their updated
   equipment selection
"""

import json
from typing import Any, Dict, List, Optional, Tuple

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.assessments.models import Assessment


class EquipmentMigrator:
    """Handles conversion of equipment data from multiple-selection to single-selection format."""

    # Equipment hierarchy: more specific/advanced options override less specific ones
    EQUIPMENT_HIERARCHY = {
        "full_gym": 3,  # Most advanced
        "basic_equipment": 2,  # Mid-level
        "no_equipment": 1,  # Least advanced
    }

    VALID_EQUIPMENT_OPTIONS = {"no_equipment", "basic_equipment", "full_gym"}

    def __init__(self):
        """Initialize the migrator."""
        self.migrated_count = 0
        self.flagged_count = 0
        self.skipped_count = 0
        self.error_count = 0
        self.migration_details: List[Dict[str, Any]] = []

    def migrate_equipment_field(self, assessment: Assessment) -> Tuple[bool, Optional[str]]:
        """
        Migrate a single assessment's equipment data.

        Args:
            assessment: Assessment instance to migrate

        Returns:
            Tuple of (success, message)
        """
        original_equipment = assessment.equipment
        original_items = assessment.equipment_items

        try:
            # Determine if migration is needed
            if isinstance(original_equipment, str):
                # Already a string - validate it's a valid option
                if original_equipment not in self.VALID_EQUIPMENT_OPTIONS:
                    error_msg = f"Invalid equipment option: {original_equipment}"
                    self.error_count += 1
                    self.migration_details.append(
                        {
                            "user_id": assessment.user.id,
                            "user_email": assessment.user.email,
                            "status": "error",
                            "reason": error_msg,
                            "original_equipment": original_equipment,
                        }
                    )
                    return False, error_msg

                # Valid string equipment - check if re-assessment needed
                if original_equipment == "basic_equipment" and (
                    not original_items or len(original_items) == 0
                ):
                    # Flag for re-assessment
                    self.flagged_count += 1
                    self.migration_details.append(
                        {
                            "user_id": assessment.user.id,
                            "user_email": assessment.user.email,
                            "status": "flagged",
                            "reason": (
                                "Basic equipment without specific items - "
                                "user needs to re-assess"
                            ),
                            "original_equipment": original_equipment,
                            "original_items": original_items,
                        }
                    )
                    return True, "Flagged for re-assessment"

                # Already valid single selection with proper items
                self.skipped_count += 1
                self.migration_details.append(
                    {
                        "user_id": assessment.user.id,
                        "user_email": assessment.user.email,
                        "status": "skipped",
                        "reason": "Already valid single selection",
                        "equipment": original_equipment,
                    }
                )
                return True, "Already valid"

            elif isinstance(original_equipment, list):
                # Multiple selections - convert to single selection
                converted_equipment = self._convert_multiple_to_single(original_equipment)

                if converted_equipment is None:
                    error_msg = "Could not determine valid equipment from multiple selections"
                    self.error_count += 1
                    self.migration_details.append(
                        {
                            "user_id": assessment.user.id,
                            "user_email": assessment.user.email,
                            "status": "error",
                            "reason": error_msg,
                            "original_equipment": original_equipment,
                        }
                    )
                    return False, error_msg

                # Update assessment with converted equipment
                assessment.equipment = converted_equipment

                # Clear items if not basic equipment
                if converted_equipment != "basic_equipment":
                    assessment.equipment_items = []

                assessment.save()
                self.migrated_count += 1
                self.migration_details.append(
                    {
                        "user_id": assessment.user.id,
                        "user_email": assessment.user.email,
                        "status": "migrated",
                        "original_equipment": original_equipment,
                        "new_equipment": converted_equipment,
                        "items_cleared": converted_equipment != "basic_equipment",
                    }
                )
                return True, f"Migrated from {original_equipment} to {converted_equipment}"

            else:
                # Unknown format
                error_msg = f"Unknown equipment data type: {type(original_equipment)}"
                self.error_count += 1
                self.migration_details.append(
                    {
                        "user_id": assessment.user.id,
                        "user_email": assessment.user.email,
                        "status": "error",
                        "reason": error_msg,
                        "equipment_type": str(type(original_equipment)),
                    }
                )
                return False, error_msg

        except Exception as e:
            error_msg = f"Exception during migration: {str(e)}"
            self.error_count += 1
            self.migration_details.append(
                {
                    "user_id": assessment.user.id,
                    "user_email": assessment.user.email,
                    "status": "error",
                    "reason": error_msg,
                    "exception": str(e),
                }
            )
            return False, error_msg

    def _convert_multiple_to_single(self, equipment_list: List[str]) -> Optional[str]:
        """
        Convert multiple equipment selections to single selection.

        Uses hierarchy: full_gym > basic_equipment > no_equipment
        More specific/advanced options override less specific ones.

        Args:
            equipment_list: List of equipment selections

        Returns:
            Single equipment selection or None if conversion not possible
        """
        if not equipment_list:
            return None

        # Filter to valid options only
        valid_selections = [e for e in equipment_list if e in self.VALID_EQUIPMENT_OPTIONS]

        if not valid_selections:
            return None

        # Find option with highest hierarchy value
        selected = max(valid_selections, key=lambda x: self.EQUIPMENT_HIERARCHY.get(x, 0))
        return selected

    def generate_report(self) -> Dict[str, Any]:
        """
        Generate migration report.

        Returns:
            Dictionary containing migration statistics
        """
        total_count = (
            self.migrated_count + self.flagged_count + self.skipped_count + self.error_count
        )
        return {
            "summary": {
                "total_processed": total_count,
                "migrated": self.migrated_count,
                "flagged": self.flagged_count,
                "skipped": self.skipped_count,
                "errors": self.error_count,
            },
            "details": self.migration_details,
        }


class Command(BaseCommand):
    """
    Django management command to migrate equipment data.

    Usage:
        python manage.py migrate_equipment_data
        python manage.py migrate_equipment_data --dry-run
        python manage.py migrate_equipment_data --save-report migration_report.json
    """

    help = "Migrate existing equipment data from multiple-selection to single-selection format"

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be migrated without making changes",
        )
        parser.add_argument(
            "--save-report",
            type=str,
            help="Save migration report to JSON file",
        )

    def handle(self, *args, **options):
        """Execute the migration command."""
        dry_run = options.get("dry_run", False)
        report_file = options.get("save_report")

        self.stdout.write(self.style.SUCCESS("Starting equipment data migration..."))

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No changes will be saved"))

        migrator = EquipmentMigrator()

        try:
            assessments = Assessment.objects.all()
            total = assessments.count()

            if total == 0:
                self.stdout.write(self.style.WARNING("No assessments found to migrate"))
                return

            self.stdout.write(f"Found {total} assessments to process")

            # Process each assessment
            with transaction.atomic():
                for assessment in assessments:
                    success, message = migrator.migrate_equipment_field(assessment)

                    if not success:
                        self.stdout.write(
                            self.style.ERROR(f"Error for user {assessment.user.email}: {message}")
                        )

                # If dry run, roll back changes
                if dry_run:
                    transaction.set_rollback(True)
                    self.stdout.write(self.style.WARNING("Rolling back changes (dry run mode)"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Migration failed: {str(e)}"))
            raise CommandError(f"Migration failed: {str(e)}")

        # Generate and display report
        report = migrator.generate_report()
        self._display_report(report)

        # Save report if requested
        if report_file:
            self._save_report(report, report_file)

        # Final status
        if migrator.error_count > 0:
            self.stdout.write(
                self.style.ERROR(
                    f"Migration complete with {migrator.error_count} errors. "
                    f"Review errors above."
                )
            )
        else:
            self.stdout.write(self.style.SUCCESS("Migration completed successfully!"))

    def _display_report(self, report: Dict[str, Any]) -> None:
        """Display migration report to stdout."""
        summary = report["summary"]

        self.stdout.write(self.style.SUCCESS("\n--- Migration Report ---"))
        self.stdout.write(f"Total Processed: {summary['total_processed']}")
        self.stdout.write(self.style.SUCCESS(f"Migrated: {summary['migrated']}"))
        self.stdout.write(self.style.WARNING(f"Flagged for Re-assessment: {summary['flagged']}"))
        self.stdout.write(f"Skipped (Already Valid): {summary['skipped']}")

        if summary["errors"] > 0:
            self.stdout.write(self.style.ERROR(f"Errors: {summary['errors']}"))

    def _save_report(self, report: Dict[str, Any], filename: str) -> None:
        """Save migration report to JSON file."""
        try:
            with open(filename, "w") as f:
                json.dump(report, f, indent=2, default=str)
            self.stdout.write(self.style.SUCCESS(f"Report saved to: {filename}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to save report: {str(e)}"))
