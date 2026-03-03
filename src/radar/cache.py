"""Tile caching for radar base maps and radar images."""

import hashlib
import logging
import os
import time
from pathlib import Path
from typing import Optional

from PIL import Image

logger = logging.getLogger(__name__)


class TileCache:
    """Cache for OpenStreetMap tiles.
    
    Tiles are cached indefinitely since map data rarely changes.
    """
    
    def __init__(self, cache_dir: str = "~/.cache/pisugar-weather/tiles"):
        """Initialize tile cache.
        
        Args:
            cache_dir: Directory to store cached tiles.
        """
        self.cache_dir = Path(os.path.expanduser(cache_dir))
        self._ensure_cache_dir()
    
    def _ensure_cache_dir(self) -> None:
        """Create cache directory if it doesn't exist."""
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_tile_path(self, x: int, y: int, zoom: int) -> Path:
        """Get path for cached tile.
        
        Args:
            x: Tile X coordinate.
            y: Tile Y coordinate.
            zoom: Zoom level.
            
        Returns:
            Path to cached tile file.
        """
        return self.cache_dir / f"{zoom}_{x}_{y}.png"
    
    def get_tile(self, x: int, y: int, zoom: int) -> Optional[Image.Image]:
        """Get tile from cache.
        
        Args:
            x: Tile X coordinate.
            y: Tile Y coordinate.
            zoom: Zoom level.
            
        Returns:
            PIL Image if cached, None otherwise.
        """
        tile_path = self._get_tile_path(x, y, zoom)
        if tile_path.exists():
            try:
                return Image.open(tile_path)
            except Exception as e:
                logger.warning(f"Failed to load cached tile {tile_path}: {e}")
                return None
        return None
    
    def save_tile(self, x: int, y: int, zoom: int, image: Image.Image) -> None:
        """Save tile to cache.
        
        Args:
            x: Tile X coordinate.
            y: Tile Y coordinate.
            zoom: Zoom level.
            image: PIL Image to cache.
        """
        tile_path = self._get_tile_path(x, y, zoom)
        try:
            image.save(tile_path, "PNG")
            logger.debug(f"Cached tile {zoom}/{x}/{y}")
        except Exception as e:
            logger.warning(f"Failed to cache tile {tile_path}: {e}")


class RadarCache:
    """Cache for radar images with TTL.
    
    Radar images are cached for a short duration since data updates frequently.
    """
    
    def __init__(
        self,
        cache_dir: str = "~/.cache/pisugar-weather/radar",
        ttl_seconds: int = 120
    ):
        """Initialize radar cache.
        
        Args:
            cache_dir: Directory to store cached radar images.
            ttl_seconds: Time-to-live for cached images in seconds.
        """
        self.cache_dir = Path(os.path.expanduser(cache_dir))
        self.ttl_seconds = ttl_seconds
        self._ensure_cache_dir()
    
    def _ensure_cache_dir(self) -> None:
        """Create cache directory if it doesn't exist."""
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_key(self, lat: float, lon: float, radius: int) -> str:
        """Generate cache key from parameters.
        
        Args:
            lat: Latitude.
            lon: Longitude.
            radius: Radius in miles.
            
        Returns:
            Cache key string.
        """
        # Round to reduce cache misses from minor coordinate differences
        key_str = f"{lat:.2f}_{lon:.2f}_{radius}"
        return hashlib.md5(key_str.encode()).hexdigest()[:12]
    
    def _get_radar_path(self, lat: float, lon: float, radius: int) -> Path:
        """Get path for cached radar image.
        
        Args:
            lat: Latitude.
            lon: Longitude.
            radius: Radius in miles.
            
        Returns:
            Path to cached radar file.
        """
        key = self._get_cache_key(lat, lon, radius)
        return self.cache_dir / f"radar_{key}.png"
    
    def _get_timestamp_path(self, lat: float, lon: float, radius: int) -> Path:
        """Get path for cache timestamp file.
        
        Args:
            lat: Latitude.
            lon: Longitude.
            radius: Radius in miles.
            
        Returns:
            Path to timestamp file.
        """
        key = self._get_cache_key(lat, lon, radius)
        return self.cache_dir / f"radar_{key}.ts"
    
    def get_radar(self, lat: float, lon: float, radius: int) -> Optional[Image.Image]:
        """Get radar image from cache if not expired.
        
        Args:
            lat: Latitude.
            lon: Longitude.
            radius: Radius in miles.
            
        Returns:
            PIL Image if cached and valid, None otherwise.
        """
        radar_path = self._get_radar_path(lat, lon, radius)
        ts_path = self._get_timestamp_path(lat, lon, radius)
        
        if not radar_path.exists() or not ts_path.exists():
            return None
        
        try:
            # Check if cache is expired
            with open(ts_path, "r") as f:
                cached_time = float(f.read().strip())
            
            if time.time() - cached_time > self.ttl_seconds:
                logger.debug(f"Radar cache expired for {lat:.2f},{lon:.2f}")
                return None
            
            return Image.open(radar_path)
        except Exception as e:
            logger.warning(f"Failed to load cached radar: {e}")
            return None
    
    def save_radar(
        self,
        lat: float,
        lon: float,
        radius: int,
        image: Image.Image
    ) -> None:
        """Save radar image to cache.
        
        Args:
            lat: Latitude.
            lon: Longitude.
            radius: Radius in miles.
            image: PIL Image to cache.
        """
        radar_path = self._get_radar_path(lat, lon, radius)
        ts_path = self._get_timestamp_path(lat, lon, radius)
        
        try:
            image.save(radar_path, "PNG")
            with open(ts_path, "w") as f:
                f.write(str(time.time()))
            logger.debug(f"Cached radar for {lat:.2f},{lon:.2f}")
        except Exception as e:
            logger.warning(f"Failed to cache radar: {e}")
