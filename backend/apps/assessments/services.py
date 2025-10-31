"""
Business logic services for assessment management.

Provides high-level services for equipment configuration,
validation, and related operations.
"""

from typing import Any, Dict, List

from apps.assessments.config import PredefinedEquipmentConfig


class EquipmentService:
    """
    Service for managing equipment options and validation.

    Provides business logic for retrieving, validating, and managing
    predefined and custom equipment options.
    """

    @staticmethod
    def get_predefined_options() -> List[Dict[str, str]]:
        """
        Get all predefined equipment options.

        Returns:
            List[Dict[str, str]]: List of equipment options with value and label
        """
        return PredefinedEquipmentConfig.get_equipment_options()

    @staticmethod
    def validate_equipment_items(items: List[str]) -> bool:
        """
        Validate a list of equipment items.

        Checks that all items are either predefined options or valid custom entries.
        Custom entries must be non-empty strings.

        Args:
            items: List of equipment item values/names

        Returns:
            bool: True if all items are valid, False otherwise
        """
        if not isinstance(items, list):
            return False

        for item in items:
            if not isinstance(item, str) or not item.strip():
                return False

        return True

    @staticmethod
    def is_predefined(item: str) -> bool:
        """
        Check if an equipment item is in the predefined options.

        Args:
            item: Equipment item value

        Returns:
            bool: True if item is predefined, False if custom
        """
        return PredefinedEquipmentConfig.is_valid_equipment(item)

    @staticmethod
    def get_equipment_display_name(value: str) -> str:
        """
        Get the human-readable display name for an equipment value.

        Works for both predefined options and custom items.

        Args:
            value: Equipment value

        Returns:
            str: Display label for the equipment
        """
        labels = PredefinedEquipmentConfig.get_equipment_labels()
        if value in labels:
            return labels[value]

        # Custom items: beautify the value
        return value.replace("-", " ").title()
