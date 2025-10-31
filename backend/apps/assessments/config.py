"""
Configuration management for assessment options.

Provides centralized configuration for predefined equipment options
that can be customized via environment variables.
"""

from typing import Any, Dict, List

from django.conf import settings


class PredefinedEquipmentConfig:
    """
    Manages predefined equipment options configuration.

    Allows system to maintain a configurable list of equipment options
    that users can select during assessment. Options can be customized
    via environment variables while maintaining default values.
    """

    # Default predefined equipment options
    DEFAULT_EQUIPMENT_OPTIONS = [
        {"value": "dumbbell", "label": "Dumbbell"},
        {"value": "barbell", "label": "Barbell"},
        {"value": "kettlebell", "label": "Kettlebell"},
        {"value": "resistance-bands", "label": "Resistance Bands"},
        {"value": "pull-up-bar", "label": "Pull-up Bar"},
        {"value": "bench", "label": "Bench"},
        {"value": "yoga-mat", "label": "Yoga Mat"},
    ]

    @classmethod
    def get_equipment_options(cls) -> List[Dict[str, str]]:
        """
        Retrieve the current predefined equipment options.

        Returns equipment options from settings if configured,
        otherwise returns default options.

        Returns:
            List[Dict[str, str]]: List of equipment option dicts with 'value' and 'label' keys
        """
        # Check for PREDEFINED_EQUIPMENT_OPTIONS in settings
        equipment_options = getattr(settings, "PREDEFINED_EQUIPMENT_OPTIONS", None)

        if equipment_options is not None:
            return equipment_options

        return cls.DEFAULT_EQUIPMENT_OPTIONS

    @classmethod
    def get_equipment_values(cls) -> List[str]:
        """
        Get list of valid equipment option values.

        Useful for validation - checks if a provided equipment
        value is in the list of predefined options.

        Returns:
            List[str]: List of equipment option values
        """
        return [option["value"] for option in cls.get_equipment_options()]

    @classmethod
    def get_equipment_labels(cls) -> Dict[str, str]:
        """
        Get mapping of equipment values to labels.

        Returns:
            Dict[str, str]: Mapping of value -> label
        """
        return {option["value"]: option["label"] for option in cls.get_equipment_options()}

    @classmethod
    def is_valid_equipment(cls, value: str) -> bool:
        """
        Check if a value is a valid predefined equipment option.

        Args:
            value: Equipment option value to validate

        Returns:
            bool: True if value is in predefined options, False otherwise
        """
        return value in cls.get_equipment_values()

    @classmethod
    def add_option(cls, value: str, label: str) -> None:
        """
        Add a new equipment option to the configuration.

        This modifies the settings at runtime. In production,
        use environment variables for persistent configuration changes.

        Args:
            value: Unique identifier for the option
            label: Human-readable label for the option
        """
        current_options = list(cls.get_equipment_options())

        # Check if option already exists
        if not cls.is_valid_equipment(value):
            current_options.append({"value": value, "label": label})
            settings.PREDEFINED_EQUIPMENT_OPTIONS = current_options
