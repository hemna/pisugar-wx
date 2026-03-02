"""National Weather Service API client."""

import logging
from datetime import datetime
from typing import List, Optional, Tuple

import requests

from ..config import WeatherStation
from .models import CurrentConditions, Forecast, WeatherCache, fahrenheit_to_celsius


logger = logging.getLogger(__name__)

NWS_API_BASE = "https://api.weather.gov"


def pascals_to_inhg(pa: float) -> float:
    """Convert Pascals to inches of mercury (inHg)."""
    return pa * 0.00029530


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
    
    def get_point_metadata(self, station: WeatherStation) -> dict:
        """Get NWS point metadata including observation stations URL.
        
        Args:
            station: WeatherStation with latitude/longitude.
            
        Returns:
            Dict with grid info and observation stations URL.
            
        Raises:
            NWSAPIError: If API request fails.
        """
        url = f"{NWS_API_BASE}/points/{station.latitude},{station.longitude}"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            properties = data.get("properties", {})
            return {
                "office": properties.get("gridId"),
                "grid_x": properties.get("gridX"),
                "grid_y": properties.get("gridY"),
                "observation_stations_url": properties.get("observationStations"),
                "forecast_url": properties.get("forecast"),
            }
            
        except requests.RequestException as e:
            logger.error(f"Failed to get point metadata: {e}")
            raise NWSAPIError(f"Failed to get point metadata: {e}")
    
    def get_nearest_observation_station(self, observation_stations_url: str) -> Optional[str]:
        """Get the nearest observation station ID.
        
        Args:
            observation_stations_url: URL to observation stations endpoint.
            
        Returns:
            Station ID of nearest observation station, or None.
        """
        try:
            response = self.session.get(observation_stations_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            features = data.get("features", [])
            if features:
                # First station is nearest
                station_id = features[0].get("properties", {}).get("stationIdentifier")
                logger.debug(f"Nearest observation station: {station_id}")
                return station_id
            return None
            
        except requests.RequestException as e:
            logger.warning(f"Failed to get observation stations: {e}")
            return None
    
    def get_current_observation(self, station_id: str) -> Optional[dict]:
        """Get latest observation from a weather station.
        
        Args:
            station_id: NWS station identifier (e.g., "KORD").
            
        Returns:
            Dict with observation data, or None if unavailable.
        """
        url = f"{NWS_API_BASE}/stations/{station_id}/observations/latest"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            properties = data.get("properties", {})
            
            # Extract values - NWS returns nested objects with value/unitCode
            def get_value(obj, default=None):
                if obj is None:
                    return default
                if isinstance(obj, dict):
                    return obj.get("value", default)
                return obj
            
            # Temperature is in Celsius from observations
            temp_c = get_value(properties.get("temperature"))
            dewpoint_c = get_value(properties.get("dewpoint"))
            humidity = get_value(properties.get("relativeHumidity"))
            pressure_pa = get_value(properties.get("barometricPressure"))
            wind_speed_ms = get_value(properties.get("windSpeed"))  # m/s
            wind_direction_deg = get_value(properties.get("windDirection"))
            visibility_m = get_value(properties.get("visibility"))
            text_description = properties.get("textDescription", "")
            
            # Convert units
            temp_f = None
            if temp_c is not None:
                temp_f = temp_c * 9/5 + 32
            
            dewpoint_f = None
            if dewpoint_c is not None:
                dewpoint_f = dewpoint_c * 9/5 + 32
            
            pressure_inhg = None
            if pressure_pa is not None:
                pressure_inhg = pascals_to_inhg(pressure_pa)
            
            wind_speed_mph = None
            if wind_speed_ms is not None:
                wind_speed_mph = wind_speed_ms * 2.237  # m/s to mph
            
            wind_dir_str = ""
            if wind_direction_deg is not None:
                # Convert degrees to compass direction
                directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                             "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
                idx = round(wind_direction_deg / 22.5) % 16
                wind_dir_str = directions[idx]
            
            return {
                "temperature_f": temp_f,
                "temperature_c": temp_c,
                "dewpoint_f": dewpoint_f,
                "dewpoint_c": dewpoint_c,
                "humidity": int(humidity) if humidity is not None else None,
                "pressure_inhg": pressure_inhg,
                "pressure_pa": pressure_pa,
                "wind_speed_mph": wind_speed_mph,
                "wind_direction": wind_dir_str,
                "visibility_m": visibility_m,
                "condition": text_description,
                "timestamp": properties.get("timestamp"),
            }
            
        except requests.RequestException as e:
            logger.warning(f"Failed to get observation from {station_id}: {e}")
            return None
        except (KeyError, TypeError) as e:
            logger.warning(f"Failed to parse observation: {e}")
            return None
    
    def get_grid_location(self, station: WeatherStation) -> Tuple[str, int, int]:
        """Get NWS grid location for coordinates.
        
        Args:
            station: WeatherStation with latitude/longitude.
            
        Returns:
            Tuple of (office, grid_x, grid_y).
            
        Raises:
            NWSAPIError: If API request fails.
        """
        metadata = self.get_point_metadata(station)
        office = metadata.get("office")
        grid_x = metadata.get("grid_x")
        grid_y = metadata.get("grid_y")
        
        if not office or grid_x is None or grid_y is None:
            raise NWSAPIError("Invalid grid location response")
        
        return office, grid_x, grid_y
    
    def get_forecast(self, station: WeatherStation) -> Tuple[Optional[CurrentConditions], List[Forecast]]:
        """Get weather forecast and current observations for a station.
        
        Args:
            station: WeatherStation with coordinates (grid info if cached).
            
        Returns:
            Tuple of (current_conditions, forecasts).
            
        Raises:
            NWSAPIError: If API request fails.
        """
        # Get point metadata (includes observation stations URL)
        metadata = self.get_point_metadata(station)
        
        office = metadata.get("office")
        grid_x = metadata.get("grid_x")
        grid_y = metadata.get("grid_y")
        obs_stations_url = metadata.get("observation_stations_url")
        
        if not office or grid_x is None or grid_y is None:
            raise NWSAPIError("Invalid grid location response")
        
        # Get current observation from nearest station
        observation = None
        if obs_stations_url:
            obs_station_id = self.get_nearest_observation_station(obs_stations_url)
            if obs_station_id:
                observation = self.get_current_observation(obs_station_id)
                if observation:
                    logger.info(f"Got observation from station {obs_station_id}")
        
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
                    # Use real observation data if available, otherwise fall back to forecast
                    if observation and observation.get("temperature_f") is not None:
                        temp = observation["temperature_f"]
                        temp_c = observation["temperature_c"]
                        dewpoint_f = observation.get("dewpoint_f")
                        dewpoint_c = observation.get("dewpoint_c")
                        humidity = observation.get("humidity") or 50
                        wind_speed = f"{int(observation['wind_speed_mph'])} mph" if observation.get("wind_speed_mph") else forecast.wind_speed
                        wind_dir = observation.get("wind_direction") or forecast.wind_direction
                        condition = observation.get("condition") or forecast.condition
                        pressure = f"{observation['pressure_inhg']:.2f} inHg" if observation.get("pressure_inhg") else None
                    else:
                        temp = forecast.temperature
                        temp_c = fahrenheit_to_celsius(temp)
                        dewpoint_f = None
                        dewpoint_c = None
                        humidity = 50
                        wind_speed = forecast.wind_speed
                        wind_dir = forecast.wind_direction
                        condition = forecast.condition
                        pressure = None
                    
                    current = CurrentConditions(
                        station_id=station.id,
                        timestamp=datetime.now(),
                        temperature=temp,
                        temperature_celsius=temp_c,
                        humidity=humidity,
                        wind_speed=wind_speed,
                        wind_direction=wind_dir,
                        condition=condition,
                        feels_like=temp,  # Simplified
                        pressure=pressure,
                        dewpoint=dewpoint_f,
                        dewpoint_celsius=dewpoint_c
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
