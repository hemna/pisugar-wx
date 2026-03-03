"""NOAA WMS radar image fetching."""

import io
import logging
from math import cos, radians
from typing import Optional, Tuple

import requests
from PIL import Image

from .cache import RadarCache

logger = logging.getLogger(__name__)

# NOAA GeoServer WMS endpoint for CREF (Composite Reflectivity)
NOAA_WMS_URL = "https://opengeo.ncep.noaa.gov/geoserver/conus/conus_cref_qcd/ows"

# User agent for requests
USER_AGENT = "pisugar-weather/0.1.0 (https://github.com/hemna/pisugar-wx)"


def get_radar_bbox(
    lat: float,
    lon: float,
    radius_miles: int = 100
) -> Tuple[float, float, float, float]:
    """Calculate bounding box for radar coverage.
    
    Args:
        lat: Center latitude.
        lon: Center longitude.
        radius_miles: Radius in miles.
        
    Returns:
        Tuple of (south, west, north, east).
    """
    # 1 degree latitude ≈ 69 miles
    lat_delta = radius_miles / 69.0
    # Longitude degrees vary with latitude
    lon_delta = radius_miles / (69.0 * cos(radians(lat)))
    
    return (
        lat - lat_delta,  # south
        lon - lon_delta,  # west
        lat + lat_delta,  # north
        lon + lon_delta   # east
    )


def build_wms_url(
    bbox: Tuple[float, float, float, float],
    width: int,
    height: int
) -> str:
    """Build WMS GetMap URL for radar image.
    
    Args:
        bbox: Bounding box (south, west, north, east).
        width: Image width in pixels.
        height: Image height in pixels.
        
    Returns:
        WMS GetMap URL.
    """
    south, west, north, east = bbox
    
    params = {
        "service": "WMS",
        "version": "1.3.0",
        "request": "GetMap",
        "layers": "conus_cref_qcd",
        "styles": "",
        "format": "image/png",
        "transparent": "true",
        "width": str(width),
        "height": str(height),
        "crs": "EPSG:4326",
        # WMS 1.3.0 uses lat,lon order for EPSG:4326
        "bbox": f"{south},{west},{north},{east}"
    }
    
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return f"{NOAA_WMS_URL}?{query}"


class RadarFetcher:
    """Fetches radar images from NOAA WMS."""
    
    def __init__(self, cache_dir: Optional[str] = None):
        """Initialize radar fetcher.
        
        Args:
            cache_dir: Directory for radar cache. Uses default if None.
        """
        if cache_dir:
            self.cache = RadarCache(cache_dir)
        else:
            self.cache = RadarCache()
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
    
    def fetch_radar(
        self,
        lat: float,
        lon: float,
        radius_miles: int,
        width: int,
        height: int
    ) -> Optional[Image.Image]:
        """Fetch radar image for a location.
        
        Args:
            lat: Center latitude.
            lon: Center longitude.
            radius_miles: Coverage radius in miles.
            width: Image width in pixels.
            height: Image height in pixels.
            
        Returns:
            PIL Image with RGBA (transparent background), or None if failed.
        """
        # Check cache first
        cached = self.cache.get_radar(lat, lon, radius_miles)
        if cached:
            logger.debug(f"Using cached radar for {lat:.2f},{lon:.2f}")
            return cached
        
        # Calculate bounding box and build URL
        bbox = get_radar_bbox(lat, lon, radius_miles)
        url = build_wms_url(bbox, width, height)
        
        logger.debug(f"Fetching radar from: {url[:100]}...")
        
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get("content-type", "")
            if "image" not in content_type:
                logger.warning(f"Unexpected content type: {content_type}")
                return None
            
            image = Image.open(io.BytesIO(response.content))
            
            # Ensure RGBA mode for transparency
            if image.mode != "RGBA":
                image = image.convert("RGBA")
            
            # Cache for future use
            self.cache.save_radar(lat, lon, radius_miles, image)
            
            logger.info(f"Fetched radar for {lat:.2f},{lon:.2f}")
            return image
            
        except requests.exceptions.Timeout:
            logger.warning(f"Radar fetch timeout for {lat:.2f},{lon:.2f}")
            return None
        except Exception as e:
            logger.warning(f"Failed to fetch radar for {lat:.2f},{lon:.2f}: {e}")
            return None


def fetch_radar_image(
    lat: float,
    lon: float,
    radius_miles: int = 100,
    width: int = 240,
    height: int = 280,
    cache_dir: Optional[str] = None
) -> Optional[Image.Image]:
    """Convenience function to fetch radar image.
    
    Args:
        lat: Center latitude.
        lon: Center longitude.
        radius_miles: Coverage radius in miles.
        width: Image width in pixels.
        height: Image height in pixels.
        cache_dir: Optional cache directory.
        
    Returns:
        PIL Image with radar data, or None if failed.
    """
    fetcher = RadarFetcher(cache_dir)
    return fetcher.fetch_radar(lat, lon, radius_miles, width, height)
