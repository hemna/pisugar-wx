"""Tests for weather data models."""

import pytest
from datetime import datetime

from src.weather.models import (
    CurrentConditions,
    Forecast,
    WeatherData,
    WeatherCache,
    fahrenheit_to_celsius,
    celsius_to_fahrenheit
)


class TestTemperatureConversion:
    """Tests for temperature conversion functions."""
    
    def test_fahrenheit_to_celsius_freezing(self):
        assert fahrenheit_to_celsius(32) == 0
    
    def test_fahrenheit_to_celsius_boiling(self):
        assert fahrenheit_to_celsius(212) == 100
    
    def test_fahrenheit_to_celsius_room(self):
        assert abs(fahrenheit_to_celsius(68) - 20) < 0.1
    
    def test_celsius_to_fahrenheit_freezing(self):
        assert celsius_to_fahrenheit(0) == 32
    
    def test_celsius_to_fahrenheit_boiling(self):
        assert celsius_to_fahrenheit(100) == 212


class TestCurrentConditions:
    """Tests for CurrentConditions model."""
    
    def test_create_current_conditions(self):
        conditions = CurrentConditions(
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
        
        assert conditions.station_id == "home"
        assert conditions.temperature == 72.0
        assert conditions.humidity == 65
    
    def test_humidity_validation(self):
        with pytest.raises(ValueError):
            CurrentConditions(
                station_id="home",
                timestamp=datetime.now(),
                temperature=72.0,
                temperature_celsius=22.2,
                humidity=150,  # Invalid - over 100
                wind_speed="10 mph",
                wind_direction="NW",
                condition="Clear",
                feels_like=70.0
            )


class TestForecast:
    """Tests for Forecast model."""
    
    def test_create_forecast(self):
        forecast = Forecast(
            station_id="home",
            period_name="Today",
            start_time=datetime.now(),
            end_time=datetime.now(),
            temperature=75,
            temperature_unit="F",
            wind_speed="15 mph",
            wind_direction="S",
            condition="Sunny",
            is_daytime=True,
            precipitation_probability=10,
            detailed_forecast="Sunny with highs around 75"
        )
        
        assert forecast.period_name == "Today"
        assert forecast.temperature == 75
        assert forecast.is_daytime is True


class TestWeatherCache:
    """Tests for WeatherCache model."""
    
    def test_create_weather_cache(self):
        cache = WeatherCache(
            station_id="home",
            cached_at=datetime.now(),
            is_stale=False
        )
        
        assert cache.station_id == "home"
        assert cache.is_stale is False
