"""Tests for weather icon mapping."""

import pytest

from src.ui.icons import (
    get_icon_filename,
    get_icon_path,
    WEATHER_ICON_MAP,
    DEFAULT_ICON
)


class TestWeatherIconMapping:
    """Tests for weather icon mapping functions."""
    
    def test_clear_weather(self):
        assert get_icon_filename("clear") == "sunny.png"
        assert get_icon_filename("sunny") == "sunny.png"
    
    def test_partly_cloudy(self):
        assert get_icon_filename("partly cloudy") == "partly_cloudy.png"
        assert get_icon_filename("partly_cloudy") == "partly_cloudy.png"
    
    def test_cloudy_conditions(self):
        assert get_icon_filename("cloudy") == "cloudy.png"
        assert get_icon_filename("mostly cloudy") == "cloudy.png"
        assert get_icon_filename("overcast") == "cloudy.png"
    
    def test_rain_conditions(self):
        assert get_icon_filename("rain") == "rain.png"
        assert get_icon_filename("showers") == "rain.png"
        assert get_icon_filename("light rain") == "rain_light.png"
        assert get_icon_filename("heavy rain") == "rain_heavy.png"
    
    def test_thunderstorm(self):
        assert get_icon_filename("thunderstorms") == "thunderstorm.png"
        assert get_icon_filename("thunderstorm") == "thunderstorm.png"
        assert get_icon_filename("scattered thunderstorms") == "thunderstorm.png"
    
    def test_snow_conditions(self):
        assert get_icon_filename("snow") == "snow.png"
        assert get_icon_filename("light snow") == "snow_light.png"
        assert get_icon_filename("heavy snow") == "snow_heavy.png"
        assert get_icon_filename("blizzard") == "snow_heavy.png"
        assert get_icon_filename("sleet") == "sleet.png"
    
    def test_fog_conditions(self):
        assert get_icon_filename("fog") == "fog.png"
        assert get_icon_filename("mist") == "fog.png"
        assert get_icon_filename("haze") == "fog.png"
    
    def test_wind_conditions(self):
        assert get_icon_filename("windy") == "windy.png"
        assert get_icon_filename("breezy") == "windy.png"
    
    def test_unknown_condition(self):
        assert get_icon_filename("unknown condition") == DEFAULT_ICON
    
    def test_case_insensitive(self):
        assert get_icon_filename("CLEAR") == "sunny.png"
        assert get_icon_filename("Rain") == "rain.png"
        assert get_icon_filename("PARTLY CLOUDY") == "partly_cloudy.png"
    
    def test_icon_map_has_valid_values(self):
        """Verify all mapped conditions have valid filenames."""
        for condition, icon in WEATHER_ICON_MAP.items():
            assert icon.endswith(".png"), f"Invalid icon: {icon}"
    
    def test_default_icon(self):
        assert DEFAULT_ICON == "unknown.png"


class TestIconPath:
    """Tests for icon path resolution."""
    
    def test_get_icon_path_nonexistent(self, tmp_path):
        """Test that None is returned for non-existent icon directory."""
        result = get_icon_path(str(tmp_path), "clear")
        assert result is None
    
    def test_get_icon_path_existing(self, tmp_path):
        """Test that path is returned for existing icon."""
        # Create mock icon
        icon_file = tmp_path / "sunny.png"
        icon_file.write_bytes(b"fake png")
        
        result = get_icon_path(str(tmp_path), "clear")
        assert result is not None
        assert result.endswith("sunny.png")
