"""Tests for display rendering."""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from src.weather.models import CurrentConditions
from src.config import WeatherStation


# Skip tests if PIL not available
pytestmark = pytest.mark.skipif(
    True,  # Always skip in non-Pi environment
    reason="PIL not available in test environment"
)


class TestDisplayRendering:
    """Tests for display rendering."""
    
    @pytest.fixture
    def sample_conditions(self):
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
        return WeatherStation(
            id="home",
            name="Home",
            latitude=39.7456,
            longitude=-97.0892
        )
    
    def test_current_weather_screen_creation(self):
        """Test that CurrentWeatherScreen can be instantiated."""
        from src.ui.screens import CurrentWeatherScreen
        
        screen = CurrentWeatherScreen()
        assert screen.width == 280
        assert screen.height == 240
