"""Weather data models for NWS API responses."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


@dataclass
class CurrentConditions:
    """Current weather observation for a station."""
    station_id: str
    timestamp: datetime
    temperature: float  # Fahrenheit
    temperature_celsius: float
    humidity: int  # 0-100%
    wind_speed: str  # e.g., "10 mph"
    wind_direction: str  # e.g., "NW"
    condition: str  # e.g., "Partly Cloudy"
    condition_code: Optional[str] = None
    feels_like: float = 0.0
    visibility: Optional[str] = None
    pressure: Optional[str] = None
    pressure_value: Optional[float] = None  # Raw pressure in inHg for trend calculation
    pressure_trend: Optional[str] = None  # "rising", "falling", or None (steady/unknown)
    dewpoint: Optional[float] = None  # Fahrenheit
    dewpoint_celsius: Optional[float] = None


@dataclass
class Forecast:
    """A forecast period from NWS API."""
    station_id: str
    period_name: str  # e.g., "Today", "Tonight", "Wednesday"
    start_time: datetime
    end_time: datetime
    temperature: int
    temperature_unit: str  # "F" or "C"
    wind_speed: str
    wind_direction: str
    condition: str
    is_daytime: bool
    precipitation_probability: Optional[int] = None  # 0-100
    detailed_forecast: str = ""


@dataclass
class WeatherData:
    """Complete weather data for a station."""
    station_id: str
    current: Optional[CurrentConditions] = None
    forecasts: List[Forecast] = field(default_factory=list)
    last_updated: Optional[datetime] = None


@dataclass
class WeatherCache:
    """Cached weather data for offline support."""
    station_id: str
    cached_at: datetime
    current: Optional[CurrentConditions] = None
    forecasts: List[Forecast] = field(default_factory=list)
    is_stale: bool = False


def fahrenheit_to_celsius(f: float) -> float:
    """Convert Fahrenheit to Celsius."""
    return (f - 32) * 5 / 9


def celsius_to_fahrenheit(c: float) -> float:
    """Convert Celsius to Fahrenheit."""
    return c * 9 / 5 + 32
