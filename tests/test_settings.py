"""
Unit tests for Settings configuration.
"""
import pytest
from stella.config.settings import Settings


@pytest.mark.unit
class TestSettings:
    """Tests for Settings class."""

    def test_settings_initialization(self):
        """Test that settings initialize with defaults."""
        settings = Settings()
        assert settings is not None
        assert isinstance(settings._settings, dict)

    def test_get_authentication_settings(self):
        """Test retrieving authentication settings."""
        settings = Settings()
        pin_length = settings.get('authentication.pin_length')
        assert pin_length == 6
        max_attempts = settings.get('authentication.max_pin_attempts')
        assert max_attempts == 3

    def test_get_system_settings(self):
        """Test retrieving system settings."""
        settings = Settings()
        unit_id = settings.get('system.unit_id')
        assert unit_id == 'UNIT_001'

    def test_get_with_default(self):
        """Test get with default value for non-existent key."""
        settings = Settings()
        value = settings.get('nonexistent.key', 'default_value')
        assert value == 'default_value'

    def test_set_configuration(self):
        """Test setting a configuration value."""
        settings = Settings()
        settings.set('test.key', 'test_value')
        assert settings.get('test.key') == 'test_value'

    def test_unit_pin_property(self):
        """Test unit_pin property."""
        settings = Settings()
        pin = settings.unit_pin
        assert isinstance(pin, str)
        assert len(pin) == 6
