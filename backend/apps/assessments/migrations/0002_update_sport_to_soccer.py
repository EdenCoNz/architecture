# Migration to update sport field from 'football' to 'soccer'
# Generated manually for Feature #21 Story 21.1

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("assessments", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="assessment",
            name="sport",
            field=models.CharField(
                choices=[("soccer", "Football"), ("cricket", "Cricket")],
                help_text="Primary sport for training focus",
                max_length=20,
                verbose_name="sport",
            ),
        ),
    ]
