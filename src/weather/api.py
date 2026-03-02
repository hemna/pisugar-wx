"""National Weather Service API client."""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import requests

from ..config import WeatherStation
from .models import CurrentConditions, Forecast, WeatherCache, fahrenheit_to_celsius


logger = logging.getLogger(__name__)

NWS_API_BASE = "https://api.weather.gov"


class NWSAPIError(Exception):
    """Exception raised for NWS API errors."""
    pass


class WeatherAPI:
    """Client for National Weather Service API."""
    
    def __init__(self, user_agent: str = "pisugar-weather/0.1.0"):
        """Initialize API client.
        
        Args:
            user_agent: User agent string for API requests.
        """
        self.session = requests.Session()
        self.session.headers["User-Agent"] = user_agent
        self.session.headers["Accept"] = "application/geo+json"
    
    def get_grid_location(self, station: WeatherStation) -> Tuple[str, int, int]:
        """Get NWS grid location for coordinates.
        
        Args:
            station: WeatherStation with latitude/longitude.
            
        Returns:
            Tuple of (office, grid_x, grid_y).
            
        Raises:
            NWSAPIError: If API request fails.
        """
        url = f"{NWS_API_BASE}/points/{station.latitude},{station.longitude}"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            properties = data.get("properties", {})
            office = properties.get("gridId")
            grid_x = properties.get("gridX")
            grid_y = properties.get("gridY")
            
            if not office or grid_x is None or grid_y is None:
                raise NWSAPIError("Invalid grid location response")
            
            return office, grid_x, grid_y
            
        except requests.RequestException as e:
            logger.error(f"Failed to get grid location: {e}")
            raise NWSAPIError(f"Failed to get grid location: {e}")
    
    def get_forecast(self, station: WeatherStation) -> Tuple[Optional[CurrentConditions], List[Forecast]]:
        """Get weather forecast for a station.
        
        Args:
            station: WeatherStation with coordinates (grid info if cached).
            
        Returns:
            Tuple of (current_conditions, forecasts).
            
        Raises:
            NWSAPIError: If API request fails.
        """
        # Get grid location if not cached
        if station.grid_id is None or station.grid_x is None or station.grid_y is None:
            office, grid_x, grid_y = self.get_grid_location(station)
        else:
            office = station.forecast_office or station.grid_id
            grid_x = station.grid_x
            grid_y = station.grid_y
        
        # Get forecast
        url = f"{NWS_API_BASE}/gridpoints/{office}/{grid_x},{grid_y}/forecast"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            properties = data.get("properties", {})
            periods = properties.get("periods", [])
            
            current = None
            forecasts = []
            
            for i, period in enumerate(periods):
                forecast = Forecast(
                    station_id=station.id,
                    period_name=period.get("name", ""),
                    start_time=datetime.fromisoformat(period.get("startTime", "").replace("Z", "+00:00")),
                    end_time=datetime.fromisoformat(period.get("endTime", "").replace("Z", "+00:00")),
                    temperature=int(period.get("temperature", 0)),
                    temperature_unit=period.get("temperatureUnit", "F"),
                    wind_speed=period.get("windSpeed", ""),
                    wind_direction=period.get("windDirection", ""),
                    condition=period.get("shortForecast", ""),
                    is_daytime=period.get("isDaytime", True),
                    precipitation_probability=period.get("probabilityOfPrecipitation", {}).get("value"),
                    detailed_forecast=period.get("detailedForecast", "")
                )
                
                if i == 0:
                    # First period is current conditions
                    temp = forecast.temperature
                    humidity = 50  # NWS forecast doesn't include humidity
                    
                    current = CurrentConditions(
                        station_id=station.id,
                        timestamp=datetime.now(),
                        temperature=temp,
                        temperature_celsius=fahrenheit_to_celsius(temp),
                        humidity=humidity,
                        wind_speed=forecast.wind_speed,
                        wind_direction=forecast.wind_direction,
                        condition=forecast.condition,
                        feels_like=temp  # Simplified - would need heat index calculation
                    )
                
                forecasts.append(forecast)
            
            return current, forecasts
            
        except requests.RequestException as e:
            logger.error(f"Failed to get forecast: {e}")
            raise NWSAPIError(f"Failed to get forecast: {e}")
        except (KeyError, ValueError) as e:
            logger.error(f"Failed to parse forecast: {e}")
            raise NWSAPIError(f"Failed to parse forecast: {e}")
    
    def get_weather_with_cache(self, station: WeatherStation, cache_manager) -> WeatherCache:
        """Get weather data with caching.
        
        Args:
            station: WeatherStation to get weather for.
            cache_manager: WeatherCacheManager instance.
            
        Returns:
            WeatherCache with current conditions and forecasts.
        """
        # Try to get from cache first
        cached = cache_manager.get(station.id)
        
        if cached and not cached.is_stale:
            logger.info(f"Using cached data for {station.id}")
            return cached
        
        # Fetch fresh data
        try:
            current, forecasts = self.get_forecast(station)
            
            weather_cache = WeatherCache(
                station_id=station.id,
                cached_at=datetime.now(),
                current=current,
                forecasts=forecasts,
                is_stale=False
            )
            
            # Save to cache
            cache_manager.set(weather_cache)
            logger.info(f"Fetched and cached fresh data for {station.id}")
            
            return weather_cache
            
        except NWSAPIError as e:
            logger.error(f"API error for {station.id}: {e}")
            
            # Return stale cache if available
            if cached:
                logger.info(f"Returning stale cache for {station.id}")
                cached.is_stale = True
                return cached
            
            raise
