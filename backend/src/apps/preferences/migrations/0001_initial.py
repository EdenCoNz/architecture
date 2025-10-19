"""Initial migration for preferences app."""

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    """Create UserPreferences model."""

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="UserPreferences",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "theme",
                    models.CharField(
                        choices=[
                            ("light", "Light"),
                            ("dark", "Dark"),
                            ("auto", "Auto"),
                        ],
                        default="auto",
                        help_text="Preferred color theme (light, dark, or auto)",
                        max_length=10,
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="Timestamp when preferences were created",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True,
                        help_text="Timestamp when preferences were last updated",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        help_text="User who owns these preferences",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="preferences",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "User Preference",
                "verbose_name_plural": "User Preferences",
                "db_table": "user_preferences",
                "ordering": ["-updated_at"],
            },
        ),
    ]
