# Migration to add database-level CHECK constraint for sport field
# Generated manually for Feature #21 Story 21.8

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("assessments", "0003_migrate_football_to_soccer"),
    ]

    operations = [
        # Remove any existing constraint with the same name (e.g., from migration 0003 reverse)
        # Use RunSQL because the constraint may have been created directly via SQL and not tracked in Django's state
        migrations.RunSQL(
            sql="ALTER TABLE assessments DROP CONSTRAINT IF EXISTS assessments_sport_valid_choice;",
            reverse_sql=migrations.RunSQL.noop,
        ),
        # Add the new constraint that only allows current terminology
        migrations.AddConstraint(
            model_name="assessment",
            constraint=models.CheckConstraint(
                condition=models.Q(sport__in=["soccer", "cricket"]),
                name="assessments_sport_valid_choice",
            ),
        ),
    ]
