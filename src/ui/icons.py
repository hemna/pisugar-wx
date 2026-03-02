"""Weather icon mapping from NWS condition codes to icon files."""

import os
from typing import Dict, Optional


# NWS weather condition codes mapped to icon filenames
# These map to the WMO weather codes used in NWS API responses
WEATHER_ICON_MAP: Dict[str, str] = {
    # Clear/Sunny
    "clear": "sunny.png",
    "sunny": "sunny.png",
    
    # Partly Cloudy
    "partly cloudy": "partly_cloudy.png",
    "partly_cloudy": "partly_cloudy.png",
    
    # Cloudy
    "cloudy": "cloudy.png",
    "mostly cloudy": "cloudy.png",
    "mostly_cloudy": "cloudy.png",
    "overcast": "cloudy.png",
    
    # Rain
    "rain": "rain.png",
    "showers": "rain.png",
    "light rain": "rain_light.png",
    "heavy rain": "rain_heavy.png",
    "drizzle": "rain_light.png",
    
    # Thunderstorms
    "thunderstorms": "thunderstorm.png",
    "thunderstorm": "thunderstorm.png",
    "scattered thunderstorms": "thunderstorm.png",
    
    # Snow
    "snow": "snow.png",
    "light snow": "snow_light.png",
    "heavy snow": "snow_heavy.png",
    "blizzard": "snow_heavy.png",
    "sleet": "sleet.png",
    "freezing rain": "freezing_rain.png",
    "ice": "ice.png",
    
    # Fog/Mist
    "fog": "fog.png",
    "mist": "fog.png",
    "haze": "fog.png",
    "smoke": "fog.png",
    
    # Wind
    "windy": "windy.png",
    "breezy": "windy.png",
}

# Default icon for unknown conditions
DEFAULT_ICON = "unknown.png"


def get_icon_filename(condition: str) -> str:
    """Get icon filename for a weather condition.
    
    Args:
        condition: Weather condition string from NWS API.
        
    Returns:
        Icon filename to look for in assets/icons/.
    """
    condition_lower = condition.lower()
    
    # Try exact match first
    if condition_lower in WEATHER_ICON_MAP:
        return WEATHER_ICON_MAP[condition_lower]
    
    # Try partial match
    for key, value in WEATHER_ICON_MAP.items():
        if key in condition_lower:
            return value
    
    return DEFAULT_ICON


def get_icon_path(icon_dir: str, condition: str) -> Optional[str]:
    """Get full path to icon file.
    
    Args:
        icon_dir: Directory containing icon files.
        condition: Weather condition string.
        
    Returns:
        Full path to icon file if exists, None otherwise.
    """
    icon_filename = get_icon_filename(condition)
    icon_path = os.path.join(icon_dir, icon_filename)
    
    if os.path.exists(icon_path):
        return icon_path
    
    return None


def get_all_available_icons(icon_dir: str) -> list[str]:
    """Get list of available icon files.
    
    Args:
        icon_dir: Directory containing icon files.
        
    Returns:
        List of icon filenames.
    """
    if not os.path.exists(icon_dir):
        return []
    
    return [f for f in os.listdir(icon_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
