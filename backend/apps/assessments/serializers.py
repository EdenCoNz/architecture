"""
Serializers for Assessment models.
Handles serialization, deserialization, and validation of assessment data.
"""

from typing import Any, Dict, Union

from rest_framework import serializers

from apps.assessments.models import Assessment


class EquipmentField(serializers.Field):
    """
    Custom field for equipment that accepts both strings and lists
    to validate single equipment selection.
    """

    default_error_messages = {
        "required": "Equipment level is required",
        "null": "Equipment level is required",
        "blank": "Equipment level is required",
    }

    def to_representation(self, value: str) -> str:
        """Convert model value to JSON-serializable representation."""
        return str(value) if value else ""

    def to_internal_value(self, data: Any) -> str:
        """Convert input data to internal value."""
        # Accept lists and strings, pass to validation
        return data


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

    # Override equipment field with custom field to accept lists and strings
    equipment = EquipmentField(
        required=True,
    )

    # Equipment items for basic equipment selection
    equipment_items = serializers.ListField(
        child=serializers.CharField(
            max_length=100,
            allow_blank=False,
        ),
        required=False,
        allow_empty=True,
        default=list,
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
            "equipment_items",
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
                "allow_blank": True,
                "allow_null": False,
                "error_messages": {
                    "required": "Equipment level is required",
                    "null": "Equipment level is required",
                    "blank": "Equipment level is required",
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

    def validate_equipment(self, value: Any) -> str:
        """
        Custom validation for equipment field.
        Ensures only one equipment level is selected.

        Args:
            value: The equipment value to validate (can be str or list)

        Returns:
            str: The validated equipment value

        Raises:
            serializers.ValidationError: If equipment validation fails
        """
        # Check if value is a list (multiple selections)
        if isinstance(value, list):
            if len(value) > 1:
                raise serializers.ValidationError("Please select only one equipment level")
            elif len(value) == 0:
                raise serializers.ValidationError("Equipment level is required")
            # If it's a single-item list, extract the value
            value = value[0]

        # Check if value is empty or None
        if not value or value == "":
            raise serializers.ValidationError("Equipment level is required")

        # Validate against choices
        valid_equipment = [choice[0] for choice in Assessment.Equipment.choices]
        if value not in valid_equipment:
            raise serializers.ValidationError(
                "Please select a valid equipment option "
                "(no_equipment, basic_equipment, or full_gym)"
            )

        return value

    def validate_equipment_items(self, value: Any) -> list:
        """
        Custom validation for equipment_items field.

        Args:
            value: The equipment items list to validate

        Returns:
            list: The validated equipment items list

        Raises:
            serializers.ValidationError: If validation fails
        """
        # Allow empty list for non-basic equipment
        if value is None:
            return []

        # Validate each item is a non-empty string
        if not isinstance(value, list):
            raise serializers.ValidationError("Equipment items must be a list")

        for item in value:
            if not isinstance(item, str) or not item.strip():
                raise serializers.ValidationError("Each equipment item must be a non-empty string")

        return value

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate the entire assessment data.

        Includes conditional validation for equipment items:
        - If equipment is 'basic_equipment', items must be provided
        - If equipment is not 'basic_equipment', items are cleared

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

        # Conditional validation for equipment items
        equipment = data.get("equipment")
        equipment_items = data.get("equipment_items", [])

        if equipment == "basic_equipment":
            # When equipment is basic_equipment, items must be provided
            if not equipment_items or len(equipment_items) == 0:
                raise serializers.ValidationError(
                    {"equipment_items": "Please specify at least one equipment item"}
                )
        else:
            # When equipment is not basic_equipment, clear the items
            data["equipment_items"] = []

        return data
