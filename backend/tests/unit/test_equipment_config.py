"""
Unit tests for equipment configuration management.

Tests predefined equipment options retrieval, validation,
and configuration management.
"""

import pytest
from django.conf import settings
from django.test import TestCase, override_settings

from apps.assessments.config import PredefinedEquipmentConfig
from apps.assessments.services import EquipmentService


class TestPredefinedEquipmentConfig(TestCase):
    """Tests for PredefinedEquipmentConfig class."""

    def setUp(self):
        """Reset configuration before each test."""
        # Reset the DEFAULT_EQUIPMENT_OPTIONS to known state
        PredefinedEquipmentConfig.DEFAULT_EQUIPMENT_OPTIONS = [
            {"value": "dumbbell", "label": "Dumbbell"},
            {"value": "barbell", "label": "Barbell"},
            {"value": "kettlebell", "label": "Kettlebell"},
            {"value": "resistance-bands", "label": "Resistance Bands"},
            {"value": "pull-up-bar", "label": "Pull-up Bar"},
            {"value": "bench", "label": "Bench"},
            {"value": "yoga-mat", "label": "Yoga Mat"},
        ]

    def tearDown(self):
        """Reset settings after each test."""
        # Reset PREDEFINED_EQUIPMENT_OPTIONS if it was set
        if hasattr(settings, "PREDEFINED_EQUIPMENT_OPTIONS"):
            delattr(settings, "PREDEFINED_EQUIPMENT_OPTIONS")

    def test_default_equipment_options_defined(self):
        """Test that default equipment options are properly defined."""
        defaults = PredefinedEquipmentConfig.DEFAULT_EQUIPMENT_OPTIONS
        assert len(defaults) == 7
        assert all("value" in opt and "label" in opt for opt in defaults)

    def test_default_options_include_required_items(self):
        """Test that default options include all required items from AC."""
        required_items = [
            "dumbbell",
            "barbell",
            "kettlebell",
            "resistance-bands",
            "pull-up-bar",
            "bench",
            "yoga-mat",
        ]
        defaults = PredefinedEquipmentConfig.DEFAULT_EQUIPMENT_OPTIONS
        default_values = [opt["value"] for opt in defaults]

        for item in required_items:
            assert item in default_values

    def test_get_equipment_options_returns_defaults(self):
        """Test that get_equipment_options returns default when not configured."""
        options = PredefinedEquipmentConfig.get_equipment_options()
        assert len(options) == 7
        assert options[0]["value"] == "dumbbell"

    @override_settings(
        PREDEFINED_EQUIPMENT_OPTIONS=[{"value": "custom-item", "label": "Custom Item"}]
    )
    def test_get_equipment_options_returns_configured_settings(self):
        """Test that get_equipment_options returns settings when configured."""
        options = PredefinedEquipmentConfig.get_equipment_options()
        assert len(options) == 1
        assert options[0]["value"] == "custom-item"

    def test_get_equipment_values_returns_list_of_values(self):
        """Test that get_equipment_values returns only the value strings."""
        values = PredefinedEquipmentConfig.get_equipment_values()
        assert isinstance(values, list)
        assert "dumbbell" in values
        assert "barbell" in values
        assert len(values) == 7

    def test_get_equipment_labels_returns_mapping(self):
        """Test that get_equipment_labels returns value->label mapping."""
        labels = PredefinedEquipmentConfig.get_equipment_labels()
        assert isinstance(labels, dict)
        assert labels["dumbbell"] == "Dumbbell"
        assert labels["pull-up-bar"] == "Pull-up Bar"
        assert labels["resistance-bands"] == "Resistance Bands"

    def test_is_valid_equipment_returns_true_for_predefined(self):
        """Test that is_valid_equipment returns True for predefined items."""
        assert PredefinedEquipmentConfig.is_valid_equipment("dumbbell")
        assert PredefinedEquipmentConfig.is_valid_equipment("barbell")
        assert PredefinedEquipmentConfig.is_valid_equipment("yoga-mat")

    def test_is_valid_equipment_returns_false_for_undefined(self):
        """Test that is_valid_equipment returns False for undefined items."""
        assert not PredefinedEquipmentConfig.is_valid_equipment("invalid-item")
        assert not PredefinedEquipmentConfig.is_valid_equipment("cable-machine")

    def test_add_option_adds_new_equipment_option(self):
        """Test that add_option successfully adds new equipment."""
        initial_values = PredefinedEquipmentConfig.get_equipment_values()
        initial_count = len(initial_values)

        PredefinedEquipmentConfig.add_option("cable-machine", "Cable Machine")

        updated_values = PredefinedEquipmentConfig.get_equipment_values()
        assert len(updated_values) == initial_count + 1
        assert "cable-machine" in updated_values

    def test_add_option_does_not_duplicate_existing(self):
        """Test that add_option doesn't add duplicates."""
        initial_options = PredefinedEquipmentConfig.get_equipment_options()
        initial_count = len(initial_options)

        # Add existing item
        PredefinedEquipmentConfig.add_option("dumbbell", "Dumbbell")

        updated_options = PredefinedEquipmentConfig.get_equipment_options()
        assert len(updated_options) == initial_count


class TestEquipmentService(TestCase):
    """Tests for EquipmentService class."""

    def test_get_predefined_options_returns_list(self):
        """Test that get_predefined_options returns list of options."""
        options = EquipmentService.get_predefined_options()
        assert isinstance(options, list)
        assert len(options) == 7

    def test_get_predefined_options_includes_required_items(self):
        """Test that predefined options include all required acceptance criteria items."""
        options = EquipmentService.get_predefined_options()
        values = [opt["value"] for opt in options]

        required = [
            "dumbbell",
            "barbell",
            "kettlebell",
            "resistance-bands",
            "pull-up-bar",
            "bench",
            "yoga-mat",
        ]
        for item in required:
            assert item in values

    def test_validate_equipment_items_accepts_list(self):
        """Test that validate_equipment_items accepts valid list."""
        items = ["dumbbell", "barbell"]
        assert EquipmentService.validate_equipment_items(items)

    def test_validate_equipment_items_accepts_custom_items(self):
        """Test that validate_equipment_items accepts custom items."""
        items = ["dumbbell", "custom-item"]
        assert EquipmentService.validate_equipment_items(items)

    def test_validate_equipment_items_rejects_non_list(self):
        """Test that validate_equipment_items rejects non-list input."""
        assert not EquipmentService.validate_equipment_items("dumbbell")
        assert not EquipmentService.validate_equipment_items(None)

    def test_validate_equipment_items_rejects_empty_strings(self):
        """Test that validate_equipment_items rejects empty strings in list."""
        items = ["dumbbell", ""]
        assert not EquipmentService.validate_equipment_items(items)

    def test_validate_equipment_items_rejects_whitespace_only(self):
        """Test that validate_equipment_items rejects whitespace-only items."""
        items = ["dumbbell", "   "]
        assert not EquipmentService.validate_equipment_items(items)

    def test_validate_equipment_items_rejects_non_string_items(self):
        """Test that validate_equipment_items rejects non-string items."""
        items = ["dumbbell", 123]
        assert not EquipmentService.validate_equipment_items(items)

    def test_is_predefined_returns_true_for_predefined(self):
        """Test that is_predefined returns True for predefined items."""
        assert EquipmentService.is_predefined("dumbbell")
        assert EquipmentService.is_predefined("yoga-mat")

    def test_is_predefined_returns_false_for_custom(self):
        """Test that is_predefined returns False for custom items."""
        assert not EquipmentService.is_predefined("cable-machine")
        assert not EquipmentService.is_predefined("custom-item")

    def test_get_equipment_display_name_returns_label_for_predefined(self):
        """Test that get_equipment_display_name returns label for predefined items."""
        assert EquipmentService.get_equipment_display_name("dumbbell") == "Dumbbell"
        assert EquipmentService.get_equipment_display_name("pull-up-bar") == "Pull-up Bar"

    def test_get_equipment_display_name_beautifies_custom_items(self):
        """Test that get_equipment_display_name beautifies custom item names."""
        assert EquipmentService.get_equipment_display_name("cable-machine") == "Cable Machine"
        assert EquipmentService.get_equipment_display_name("smith-machine") == "Smith Machine"
