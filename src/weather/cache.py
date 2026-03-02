"""File-based caching for weather data."""

import json
import os
from datetime import datetime, timedelta
from typing import Optional, List, Tuple

from .models import WeatherCache, CurrentConditions, Forecast


DEFAULT_CACHE_TTL_MINUTES = 30
# Pressure history settings
PRESSURE_HISTORY_MAX_ENTRIES = 12  # Keep last 12 readings (6 hours at 30min intervals)
PRESSURE_TREND_THRESHOLD = 0.02  # inHg change threshold to consider significant


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
                    pressure=current_data.get("pressure"),
                    pressure_value=current_data.get("pressure_value"),
                    pressure_trend=current_data.get("pressure_trend")
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
                "pressure": cache.current.pressure,
                "pressure_value": cache.current.pressure_value,
                "pressure_trend": cache.current.pressure_trend
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
    
    def _get_pressure_history_path(self, station_id: str) -> str:
        """Get pressure history file path for a station."""
        return os.path.join(self.cache_dir, f"{station_id}_pressure_history.json")
    
    def get_pressure_history(self, station_id: str) -> List[Tuple[str, float]]:
        """Get pressure history for a station.
        
        Args:
            station_id: Station identifier.
            
        Returns:
            List of (timestamp_iso, pressure_inhg) tuples, oldest first.
        """
        history_path = self._get_pressure_history_path(station_id)
        
        if not os.path.exists(history_path):
            return []
        
        try:
            with open(history_path, "r") as f:
                data = json.load(f)
            return [(entry["timestamp"], entry["pressure"]) for entry in data.get("history", [])]
        except (json.JSONDecodeError, KeyError, ValueError):
            return []
    
    def add_pressure_reading(self, station_id: str, timestamp: datetime, pressure_inhg: float) -> None:
        """Add a pressure reading to history.
        
        Args:
            station_id: Station identifier.
            timestamp: Observation timestamp.
            pressure_inhg: Pressure in inches of mercury.
        """
        history = self.get_pressure_history(station_id)
        
        # Add new reading
        history.append((timestamp.isoformat(), pressure_inhg))
        
        # Keep only the last N entries
        if len(history) > PRESSURE_HISTORY_MAX_ENTRIES:
            history = history[-PRESSURE_HISTORY_MAX_ENTRIES:]
        
        # Save history
        history_path = self._get_pressure_history_path(station_id)
        data = {
            "station_id": station_id,
            "history": [{"timestamp": ts, "pressure": p} for ts, p in history]
        }
        with open(history_path, "w") as f:
            json.dump(data, f)
    
    def calculate_pressure_trend(self, station_id: str, current_pressure: float) -> Optional[str]:
        """Calculate pressure trend based on history.
        
        Compares current pressure to the oldest reading in history.
        
        Args:
            station_id: Station identifier.
            current_pressure: Current pressure reading in inHg.
            
        Returns:
            "rising" if pressure is increasing, "falling" if decreasing,
            None if change is below threshold or insufficient history.
        """
        history = self.get_pressure_history(station_id)
        
        if not history:
            return None
        
        # Get the oldest reading for comparison
        oldest_pressure = history[0][1]
        
        # Calculate difference
        diff = current_pressure - oldest_pressure
        
        if diff > PRESSURE_TREND_THRESHOLD:
            return "rising"
        elif diff < -PRESSURE_TREND_THRESHOLD:
            return "falling"
        else:
            return None  # Steady (change below threshold)
