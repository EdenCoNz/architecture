# Migration to add database-level CHECK constraint for sport field
# Generated manually for Feature #21 Story 21.8

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("assessments", "0003_migrate_football_to_soccer"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="assessment",
            constraint=models.CheckConstraint(
                condition=models.Q(sport__in=["soccer", "cricket"]),
                name="assessments_sport_valid_choice",
            ),
        ),
    ]
