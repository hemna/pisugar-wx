"""Configuration management for PiSugar Weather Display."""

import json
import logging
import os
from dataclasses import dataclass, field
from typing import List, Optional

logger = logging.getLogger(__name__)

# Valid orientation values
VALID_ORIENTATIONS = ("portrait", "landscape")

# Valid display rotation values (degrees)
VALID_ROTATIONS = (0, 90, 180, 270)


@dataclass
class WeatherStation:
    """Represents a configured weather location."""
    id: str
    name: str
    latitude: float
    longitude: float
    grid_id: Optional[str] = None
    grid_x: Optional[int] = None
    grid_y: Optional[int] = None
    forecast_office: Optional[str] = None


@dataclass
class AppSettings:
    """Application settings."""
    refresh_interval_minutes: int = 15
    cycle_interval_seconds: int = 30
    temperature_unit: str = "F"
    display_brightness: int = 100
    orientation: str = "portrait"
    display_rotation: int = 0  # Physical rotation: 0, 90, 180, or 270 degrees
    random_city_enabled: bool = True  # Show random US city after cycling through stations
    user_agent: str = "pisugar-weather/0.1.0"
    cache_dir: str = "~/.cache/pisugar-weather"


@dataclass
class AppConfig:
    """Complete application configuration."""
    version: int = 1
    stations: List[WeatherStation] = field(default_factory=list)
    settings: AppSettings = field(default_factory=AppSettings)


def load_config(config_path: Optional[str] = None) -> AppConfig:
    """Load configuration from JSON file.
    
    Args:
        config_path: Path to config file. If None, uses default location.
        
    Returns:
        AppConfig instance with loaded configuration.
    """
    if config_path is None:
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "config",
            "stations.json"
        )
    
    config_path = os.path.expanduser(config_path)
    
    if not os.path.exists(config_path):
        return AppConfig()
    
    with open(config_path, "r") as f:
        data = json.load(f)
    
    stations = [
        WeatherStation(
            id=s["id"],
            name=s["name"],
            latitude=s["latitude"],
            longitude=s["longitude"],
            grid_id=s.get("grid_id"),
            grid_x=s.get("grid_x"),
            grid_y=s.get("grid_y"),
            forecast_office=s.get("forecast_office")
        )
        for s in data.get("stations", [])
    ]
    
    settings_data = data.get("settings", {})
    
    # Parse orientation with validation and case-insensitivity
    raw_orientation = settings_data.get("orientation", "portrait")
    orientation = raw_orientation.lower() if isinstance(raw_orientation, str) else "portrait"
    if orientation not in VALID_ORIENTATIONS:
        logger.warning(
            f"Invalid orientation '{raw_orientation}', defaulting to 'portrait'. "
            f"Valid values: {VALID_ORIENTATIONS}"
        )
        orientation = "portrait"
    
    # Parse display_rotation with validation
    raw_rotation = settings_data.get("display_rotation", 0)
    display_rotation = raw_rotation if isinstance(raw_rotation, int) else 0
    if display_rotation not in VALID_ROTATIONS:
        logger.warning(
            f"Invalid display_rotation '{raw_rotation}', defaulting to 0. "
            f"Valid values: {VALID_ROTATIONS}"
        )
        display_rotation = 0
    
    settings = AppSettings(
        refresh_interval_minutes=settings_data.get("refresh_interval_minutes", 15),
        cycle_interval_seconds=settings_data.get("cycle_interval_seconds", 30),
        temperature_unit=settings_data.get("temperature_unit", "F"),
        display_brightness=settings_data.get("display_brightness", 100),
        orientation=orientation,
        display_rotation=display_rotation,
        random_city_enabled=settings_data.get("random_city_enabled", True)
    )
    
    return AppConfig(
        version=data.get("version", 1),
        stations=stations,
        settings=settings
    )


def save_config(config: AppConfig, config_path: str) -> None:
    """Save configuration to JSON file.
    
    Args:
        config: AppConfig instance to save.
        config_path: Path to save config file.
    """
    data = {
        "version": config.version,
        "stations": [
            {
                "id": s.id,
                "name": s.name,
                "latitude": s.latitude,
                "longitude": s.longitude,
                "grid_id": s.grid_id,
                "grid_x": s.grid_x,
                "grid_y": s.grid_y,
                "forecast_office": s.forecast_office
            }
            for s in config.stations
        ],
        "settings": {
            "refresh_interval_minutes": config.settings.refresh_interval_minutes,
            "cycle_interval_seconds": config.settings.cycle_interval_seconds,
            "temperature_unit": config.settings.temperature_unit,
            "display_brightness": config.settings.display_brightness,
            "orientation": config.settings.orientation,
            "display_rotation": config.settings.display_rotation,
            "random_city_enabled": config.settings.random_city_enabled
        }
    }
    
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    with open(config_path, "w") as f:
        json.dump(data, f, indent=2)
