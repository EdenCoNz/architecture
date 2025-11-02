# Data migration to update existing 'football' records to 'soccer'
# Generated manually for Feature #21 Story 21.2

from django.db import migrations


def migrate_football_to_soccer(apps, schema_editor):
    """
    Update all assessment records with sport='football' to sport='soccer'.

    This migration is idempotent and can be run multiple times safely.
    """
    Assessment = apps.get_model("assessments", "Assessment")

    # Update all football records to soccer
    updated_count = Assessment.objects.filter(sport="football").update(sport="soccer")

    # Log the number of updated records (will appear in migration output)
    if updated_count > 0:
        print(f"Updated {updated_count} assessment(s) from 'football' to 'soccer'")


def reverse_migrate_soccer_to_football(apps, schema_editor):
    """
    Reverse migration: Update all assessment records with sport='soccer' back to sport='football'.

    This allows the migration to be reversed if needed.

    IMPORTANT: This function temporarily modifies the database CHECK constraint to allow
    "football" values before updating the data. The constraint will be properly restored
    when migration 0002 is reversed (which changes the field choices back).
    """
    Assessment = apps.get_model("assessments", "Assessment")

    # Step 1: Temporarily drop the CHECK constraint to allow "football" values
    # This is necessary because migration 0002 changed the valid choices to ["soccer", "cricket"]
    # and we need to revert data before reverting the constraint
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            "ALTER TABLE assessments DROP CONSTRAINT IF EXISTS assessments_sport_valid_choice"
        )

    # Step 2: Update all soccer records back to football
    updated_count = Assessment.objects.filter(sport="soccer").update(sport="football")

    if updated_count > 0:
        print(f"Reverted {updated_count} assessment(s) from 'soccer' to 'football'")

    # Step 3: Re-add the CHECK constraint to allow both "football" and "soccer"
    # This temporary constraint allows the data to be in a valid state until migration 0002 is reversed
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            "ALTER TABLE assessments ADD CONSTRAINT assessments_sport_valid_choice "
            "CHECK (sport IN ('football', 'soccer', 'cricket'))"
        )


class Migration(migrations.Migration):

    dependencies = [
        ("assessments", "0002_update_sport_to_soccer"),
    ]

    operations = [
        migrations.RunPython(
            migrate_football_to_soccer,
            reverse_code=reverse_migrate_soccer_to_football,
        ),
    ]
