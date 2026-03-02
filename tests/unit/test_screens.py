"""Tests for screen orientation support."""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from src.weather.models import CurrentConditions
from src.config import WeatherStation


class TestScreenOrientation:
    """Tests for display screen orientation support."""
    
    @pytest.fixture
    def sample_conditions(self):
        """Sample weather conditions for testing."""
        return CurrentConditions(
            station_id="home",
            timestamp=datetime.now(),
            temperature=72.0,
            temperature_celsius=22.2,
            humidity=65,
            wind_speed="10 mph",
            wind_direction="NW",
            condition="Partly Cloudy",
            feels_like=70.0
        )
    
    @pytest.fixture
    def sample_station(self):
        """Sample weather station for testing."""
        return WeatherStation(
            id="home",
            name="Home",
            latitude=39.7456,
            longitude=-97.0892
        )


class TestPortraitLayout:
    """Tests for portrait mode layout (User Story 1)."""
    
    def test_portrait_screen_dimensions(self):
        """Test that portrait mode uses 240x280 dimensions."""
        from src.ui.screens import CurrentWeatherScreen
        
        screen = CurrentWeatherScreen(orientation="portrait")
        assert screen.width == 240
        assert screen.height == 280
    
    def test_portrait_layout_config_exists(self):
        """Test that _get_portrait_layout() method exists and returns layout config."""
        from src.ui.screens import CurrentWeatherScreen
        
        screen = CurrentWeatherScreen(orientation="portrait")
        layout = screen._get_portrait_layout()
        
        # Verify layout has required attributes
        assert layout.width == 240
        assert layout.height == 280
        assert hasattr(layout, 'icon_x')
        assert hasattr(layout, 'icon_y')
        assert hasattr(layout, 'temp_x')
        assert hasattr(layout, 'temp_y')
        assert hasattr(layout, 'compass_x')
        assert hasattr(layout, 'compass_y')
        assert hasattr(layout, 'compass_size')
        assert hasattr(layout, 'condition_y')
    
    def test_portrait_default_orientation(self):
        """Test that default orientation is portrait."""
        from src.ui.screens import CurrentWeatherScreen
        
        screen = CurrentWeatherScreen()
        assert screen.orientation == "portrait"
        assert screen.width == 240
        assert screen.height == 280


class TestLandscapeLayout:
    """Tests for landscape mode layout (User Story 2)."""
    
    def test_landscape_screen_dimensions(self):
        """Test that landscape mode uses 280x240 dimensions."""
        from src.ui.screens import CurrentWeatherScreen
        
        screen = CurrentWeatherScreen(orientation="landscape")
        assert screen.width == 280
        assert screen.height == 240
    
    def test_landscape_layout_config_exists(self):
        """Test that _get_landscape_layout() method exists and returns layout config."""
        from src.ui.screens import CurrentWeatherScreen
        
        screen = CurrentWeatherScreen(orientation="landscape")
        layout = screen._get_landscape_layout()
        
        # Verify layout has required attributes
        assert layout.width == 280
        assert layout.height == 240
        assert hasattr(layout, 'icon_x')
        assert hasattr(layout, 'icon_y')
        assert hasattr(layout, 'temp_x')
        assert hasattr(layout, 'temp_y')
        assert hasattr(layout, 'compass_x')
        assert hasattr(layout, 'compass_y')
        assert hasattr(layout, 'compass_size')
        assert hasattr(layout, 'condition_y')
    
    def test_landscape_render_method(self):
        """Test that landscape mode has _render_landscape() method."""
        from src.ui.screens import CurrentWeatherScreen
        
        screen = CurrentWeatherScreen(orientation="landscape")
        assert hasattr(screen, '_render_landscape')
        assert callable(screen._render_landscape)
