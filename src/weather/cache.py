"""File-based caching for weather data."""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from .models import WeatherCache, CurrentConditions, Forecast


DEFAULT_CACHE_TTL_MINUTES = 30


class WeatherCacheManager:
    """Manages local file-based cache for weather data."""
    
    def __init__(self, cache_dir: str = "~/.cache/pisugar-weather"):
        """Initialize cache manager.
        
        Args:
            cache_dir: Directory to store cache files.
        """
        self.cache_dir = os.path.expanduser(cache_dir)
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def _get_cache_path(self, station_id: str) -> str:
        """Get cache file path for a station."""
        return os.path.join(self.cache_dir, f"{station_id}.json")
    
    def get(self, station_id: str, ttl_minutes: int = DEFAULT_CACHE_TTL_MINUTES) -> Optional[WeatherCache]:
        """Get cached weather data for a station.
        
        Args:
            station_id: Station identifier.
            ttl_minutes: Maximum age of cache in minutes.
            
        Returns:
            WeatherCache if valid cache exists, None otherwise.
        """
        cache_path = self._get_cache_path(station_id)
        
        if not os.path.exists(cache_path):
            return None
        
        try:
            with open(cache_path, "r") as f:
                data = json.load(f)
            
            cached_at = datetime.fromisoformat(data["cached_at"])
            age = datetime.now() - cached_at
            is_stale = age > timedelta(minutes=ttl_minutes)
            
            current_data = data.get("current")
            current = None
            if current_data:
                current = CurrentConditions(
                    station_id=current_data["station_id"],
                    timestamp=datetime.fromisoformat(current_data["timestamp"]),
                    temperature=current_data["temperature"],
                    temperature_celsius=current_data["temperature_celsius"],
                    humidity=current_data["humidity"],
                    wind_speed=current_data["wind_speed"],
                    wind_direction=current_data["wind_direction"],
                    condition=current_data["condition"],
                    condition_code=current_data.get("condition_code"),
                    feels_like=current_data.get("feels_like", 0.0),
                    visibility=current_data.get("visibility"),
                    pressure=current_data.get("pressure")
                )
            
            forecasts = []
            for f in data.get("forecasts", []):
                forecasts.append(Forecast(
                    station_id=f["station_id"],
                    period_name=f["period_name"],
                    start_time=datetime.fromisoformat(f["start_time"]),
                    end_time=datetime.fromisoformat(f["end_time"]),
                    temperature=f["temperature"],
                    temperature_unit=f["temperature_unit"],
                    wind_speed=f["wind_speed"],
                    wind_direction=f["wind_direction"],
                    condition=f["condition"],
                    is_daytime=f["is_daytime"],
                    precipitation_probability=f.get("precipitation_probability"),
                    detailed_forecast=f.get("detailed_forecast", "")
                ))
            
            return WeatherCache(
                station_id=data["station_id"],
                cached_at=cached_at,
                current=current,
                forecasts=forecasts,
                is_stale=is_stale
            )
            
        except (json.JSONDecodeError, KeyError, ValueError):
            return None
    
    def set(self, cache: WeatherCache) -> None:
        """Save weather data to cache.
        
        Args:
            cache: WeatherCache to save.
        """
        cache_path = self._get_cache_path(cache.station_id)
        
        current_data = None
        if cache.current:
            current_data = {
                "station_id": cache.current.station_id,
                "timestamp": cache.current.timestamp.isoformat(),
                "temperature": cache.current.temperature,
                "temperature_celsius": cache.current.temperature_celsius,
                "humidity": cache.current.humidity,
                "wind_speed": cache.current.wind_speed,
                "wind_direction": cache.current.wind_direction,
                "condition": cache.current.condition,
                "condition_code": cache.current.condition_code,
                "feels_like": cache.current.feels_like,
                "visibility": cache.current.visibility,
                "pressure": cache.current.pressure
            }
        
        forecasts_data = []
        for f in cache.forecasts:
            forecasts_data.append({
                "station_id": f.station_id,
                "period_name": f.period_name,
                "start_time": f.start_time.isoformat(),
                "end_time": f.end_time.isoformat(),
                "temperature": f.temperature,
                "temperature_unit": f.temperature_unit,
                "wind_speed": f.wind_speed,
                "wind_direction": f.wind_direction,
                "condition": f.condition,
                "is_daytime": f.is_daytime,
                "precipitation_probability": f.precipitation_probability,
                "detailed_forecast": f.detailed_forecast
            })
        
        data = {
            "station_id": cache.station_id,
            "cached_at": cache.cached_at.isoformat(),
            "current": current_data,
            "forecasts": forecasts_data
        }
        
        with open(cache_path, "w") as f:
            json.dump(data, f)
    
    def clear(self, station_id: Optional[str] = None) -> None:
        """Clear cache for a station or all stations.
        
        Args:
            station_id: If provided, clear cache for this station only.
                       If None, clear all caches.
        """
        if station_id:
            cache_path = self._get_cache_path(station_id)
            if os.path.exists(cache_path):
                os.remove(cache_path)
        else:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith(".json"):
                    os.remove(os.path.join(self.cache_dir, filename))
