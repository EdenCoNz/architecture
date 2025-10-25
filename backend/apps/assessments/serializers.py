"""
Serializers for Assessment models.
Handles serialization, deserialization, and validation of assessment data.
"""

from typing import Any, Dict

from rest_framework import serializers

from apps.assessments.models import Assessment


class AssessmentSerializer(serializers.ModelSerializer):
    """
    Serializer for Assessment model.

    Handles validation and serialization of user assessment data
    collected during onboarding.
    """

    # Override age field to use custom validators with specific error messages
    age = serializers.IntegerField(
        min_value=13,
        max_value=100,
        required=True,
        allow_null=False,
        error_messages={
            "min_value": "You must be at least 13 years old to use this service",
            "max_value": "Please enter a valid age",
            "invalid": "Please enter a valid age",
            "required": "Age is required",
            "null": "Age cannot be empty",
        },
    )

    class Meta:
        model = Assessment
        fields = [
            "id",
            "sport",
            "age",
            "experience_level",
            "training_days",
            "injuries",
            "equipment",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
        extra_kwargs = {
            "sport": {
                "required": True,
                "allow_blank": False,
                "allow_null": False,
                "error_messages": {
                    "required": "Sport selection is required",
                    "null": "Sport cannot be empty",
                    "blank": "Sport cannot be empty",
                    "invalid_choice": "Please select a valid sport (football or cricket)",
                },
            },
            "experience_level": {
                "required": True,
                "allow_blank": False,
                "allow_null": False,
                "error_messages": {
                    "required": "Experience level is required",
                    "null": "Experience level cannot be empty",
                    "blank": "Experience level cannot be empty",
                    "invalid_choice": (
                        "Please select a valid experience level "
                        "(beginner, intermediate, or advanced)"
                    ),
                },
            },
            "training_days": {
                "required": True,
                "allow_blank": False,
                "allow_null": False,
                "error_messages": {
                    "required": "Training days per week is required",
                    "null": "Training days cannot be empty",
                    "blank": "Training days cannot be empty",
                    "invalid_choice": (
                        "Please select a valid training frequency "
                        "(2-3, 4-5, or 6-7 days per week)"
                    ),
                },
            },
            "equipment": {
                "required": True,
                "allow_blank": False,
                "allow_null": False,
                "error_messages": {
                    "required": "Equipment availability is required",
                    "null": "Equipment cannot be empty",
                    "blank": "Equipment cannot be empty",
                    "invalid_choice": (
                        "Please select a valid equipment option "
                        "(no_equipment, basic_equipment, or full_gym)"
                    ),
                },
            },
            "injuries": {
                "error_messages": {
                    "invalid_choice": "Please select a valid injury status (yes or no)",
                },
            },
        }

    def validate_age(self, value: int) -> int:
        """
        Custom validation for age field.

        Args:
            value: The age value to validate

        Returns:
            int: The validated age value

        Raises:
            serializers.ValidationError: If age is invalid
        """
        if value is None:
            raise serializers.ValidationError("Age cannot be empty")

        if not isinstance(value, int):
            raise serializers.ValidationError("Please enter a valid age")

        if value < 13:
            raise serializers.ValidationError(
                "You must be at least 13 years old to use this service"
            )

        if value > 100:
            raise serializers.ValidationError("Please enter a valid age")

        return value

    def validate_sport(self, value: str) -> str:
        """
        Custom validation for sport field.

        Args:
            value: The sport value to validate

        Returns:
            str: The validated sport value

        Raises:
            serializers.ValidationError: If sport is invalid
        """
        if not value:
            raise serializers.ValidationError("Sport cannot be empty")

        valid_sports = [choice[0] for choice in Assessment.Sport.choices]
        if value not in valid_sports:
            raise serializers.ValidationError("Please select a valid sport (football or cricket)")

        return value

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate the entire assessment data.

        Args:
            data: The assessment data to validate

        Returns:
            dict: The validated data

        Raises:
            serializers.ValidationError: If validation fails
        """
        # Ensure all required fields are present
        required_fields = ["sport", "age", "experience_level", "training_days", "equipment"]
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            errors = {}
            for field in missing_fields:
                errors[field] = f"{field.replace('_', ' ').title()} is required"
            raise serializers.ValidationError(errors)

        return data
