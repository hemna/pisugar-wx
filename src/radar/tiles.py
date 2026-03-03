"""OpenStreetMap tile fetching and compositing for radar base maps."""

import io
import logging
from math import asinh, atan, cos, degrees, pi, radians, sinh, tan
from typing import Dict, List, Optional, Tuple

import requests
from PIL import Image

from .cache import TileCache

logger = logging.getLogger(__name__)

# OpenStreetMap tile server URL
OSM_TILE_URL = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"

# Tile size in pixels
TILE_SIZE = 256

# User agent for OSM requests (required by usage policy)
USER_AGENT = "pisugar-weather/0.1.0 (https://github.com/hemna/pisugar-wx)"


def lat_lon_to_tile(lat: float, lon: float, zoom: int) -> Tuple[int, int]:
    """Convert latitude/longitude to tile coordinates.
    
    Args:
        lat: Latitude in degrees.
        lon: Longitude in degrees.
        zoom: Zoom level (0-19).
        
    Returns:
        Tuple of (tile_x, tile_y).
    """
    n = 2 ** zoom
    x = int((lon + 180.0) / 360.0 * n)
    y = int((1.0 - asinh(tan(radians(lat))) / pi) / 2.0 * n)
    return (x, y)


def tile_to_lat_lon(x: int, y: int, zoom: int) -> Tuple[float, float]:
    """Convert tile coordinates to latitude/longitude (NW corner of tile).
    
    Args:
        x: Tile X coordinate.
        y: Tile Y coordinate.
        zoom: Zoom level.
        
    Returns:
        Tuple of (latitude, longitude) for NW corner of tile.
    """
    n = 2 ** zoom
    lon = x / n * 360.0 - 180.0
    lat = degrees(atan(sinh(pi * (1 - 2 * y / n))))
    return (lat, lon)


def tile_to_bbox(x: int, y: int, zoom: int) -> Tuple[float, float, float, float]:
    """Get bounding box for a tile.
    
    Args:
        x: Tile X coordinate.
        y: Tile Y coordinate.
        zoom: Zoom level.
        
    Returns:
        Tuple of (south, west, north, east).
    """
    north, west = tile_to_lat_lon(x, y, zoom)
    south, east = tile_to_lat_lon(x + 1, y + 1, zoom)
    return (south, west, north, east)


class TileFetcher:
    """Fetches and composites OpenStreetMap tiles."""
    
    def __init__(self, cache_dir: Optional[str] = None):
        """Initialize tile fetcher.
        
        Args:
            cache_dir: Directory for tile cache. Uses default if None.
        """
        if cache_dir:
            self.cache = TileCache(cache_dir)
        else:
            self.cache = TileCache()
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
    
    def fetch_tile(self, x: int, y: int, zoom: int) -> Optional[Image.Image]:
        """Fetch a single tile, using cache if available.
        
        Args:
            x: Tile X coordinate.
            y: Tile Y coordinate.
            zoom: Zoom level.
            
        Returns:
            PIL Image or None if fetch failed.
        """
        # Check cache first
        cached = self.cache.get_tile(x, y, zoom)
        if cached:
            logger.debug(f"Using cached tile {zoom}/{x}/{y}")
            return cached
        
        # Fetch from OSM
        url = OSM_TILE_URL.format(z=zoom, x=x, y=y)
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            image = Image.open(io.BytesIO(response.content))
            
            # Cache for future use
            self.cache.save_tile(x, y, zoom, image)
            
            logger.debug(f"Fetched tile {zoom}/{x}/{y}")
            return image
            
        except Exception as e:
            logger.warning(f"Failed to fetch tile {zoom}/{x}/{y}: {e}")
            return None
    
    def get_required_tiles(
        self,
        bbox: Tuple[float, float, float, float],
        zoom: int
    ) -> List[Tuple[int, int]]:
        """Get list of tiles needed to cover a bounding box.
        
        Args:
            bbox: Tuple of (south, west, north, east).
            zoom: Zoom level.
            
        Returns:
            List of (x, y) tile coordinates.
        """
        south, west, north, east = bbox
        
        # Get tile coordinates for corners
        nw_x, nw_y = lat_lon_to_tile(north, west, zoom)
        se_x, se_y = lat_lon_to_tile(south, east, zoom)
        
        # Generate all tiles in the range
        tiles = []
        for x in range(nw_x, se_x + 1):
            for y in range(nw_y, se_y + 1):
                tiles.append((x, y))
        
        return tiles
    
    def composite_tiles(
        self,
        tiles: Dict[Tuple[int, int], Image.Image],
        bbox: Tuple[float, float, float, float],
        zoom: int,
        width: int,
        height: int
    ) -> Image.Image:
        """Composite tiles into a single image covering the bounding box.
        
        Args:
            tiles: Dictionary mapping (x, y) to tile images.
            bbox: Target bounding box (south, west, north, east).
            zoom: Zoom level used for tiles.
            width: Output image width.
            height: Output image height.
            
        Returns:
            Composited PIL Image.
        """
        south, west, north, east = bbox
        
        # Find the tile range
        min_x = min(t[0] for t in tiles.keys())
        min_y = min(t[1] for t in tiles.keys())
        max_x = max(t[0] for t in tiles.keys())
        max_y = max(t[1] for t in tiles.keys())
        
        # Calculate pixel dimensions of tile mosaic
        mosaic_width = (max_x - min_x + 1) * TILE_SIZE
        mosaic_height = (max_y - min_y + 1) * TILE_SIZE
        
        # Create mosaic image
        mosaic = Image.new("RGB", (mosaic_width, mosaic_height), (128, 128, 128))
        
        # Paste tiles into mosaic
        for (x, y), tile in tiles.items():
            px = (x - min_x) * TILE_SIZE
            py = (y - min_y) * TILE_SIZE
            mosaic.paste(tile, (px, py))
        
        # Calculate pixel coordinates of bbox within mosaic
        nw_lat, nw_lon = tile_to_lat_lon(min_x, min_y, zoom)
        se_lat, se_lon = tile_to_lat_lon(max_x + 1, max_y + 1, zoom)
        
        # Map bbox to pixel coordinates
        lon_range = se_lon - nw_lon
        lat_range = nw_lat - se_lat
        
        px_west = int((west - nw_lon) / lon_range * mosaic_width)
        px_east = int((east - nw_lon) / lon_range * mosaic_width)
        px_north = int((nw_lat - north) / lat_range * mosaic_height)
        px_south = int((nw_lat - south) / lat_range * mosaic_height)
        
        # Crop to bbox
        cropped = mosaic.crop((px_west, px_north, px_east, px_south))
        
        # Resize to target dimensions
        result = cropped.resize((width, height), Image.Resampling.LANCZOS)
        
        return result


def get_base_map(
    lat: float,
    lon: float,
    radius_miles: int,
    width: int,
    height: int,
    cache_dir: Optional[str] = None
) -> Optional[Image.Image]:
    """Get a base map image centered on a location.
    
    Args:
        lat: Center latitude.
        lon: Center longitude.
        radius_miles: Approximate radius to show in miles.
        width: Output image width.
        height: Output image height.
        cache_dir: Optional cache directory.
        
    Returns:
        PIL Image of base map, or None if failed.
    """
    # Calculate bounding box
    # 1 degree latitude ≈ 69 miles
    lat_delta = radius_miles / 69.0
    lon_delta = radius_miles / (69.0 * cos(radians(lat)))
    
    bbox = (
        lat - lat_delta,  # south
        lon - lon_delta,  # west
        lat + lat_delta,  # north
        lon + lon_delta   # east
    )
    
    # Choose zoom level based on radius
    # Zoom 7 gives good coverage for ~100mi radius
    # Each zoom level doubles the detail
    if radius_miles <= 50:
        zoom = 8
    elif radius_miles <= 100:
        zoom = 7
    elif radius_miles <= 200:
        zoom = 6
    else:
        zoom = 5
    
    fetcher = TileFetcher(cache_dir)
    
    # Get required tiles
    tile_coords = fetcher.get_required_tiles(bbox, zoom)
    logger.debug(f"Need {len(tile_coords)} tiles for {lat:.2f},{lon:.2f} r={radius_miles}mi")
    
    # Fetch all tiles
    tiles = {}
    for x, y in tile_coords:
        tile = fetcher.fetch_tile(x, y, zoom)
        if tile:
            tiles[(x, y)] = tile
    
    if not tiles:
        logger.error("Failed to fetch any tiles")
        return None
    
    # Composite into final image
    try:
        result = fetcher.composite_tiles(tiles, bbox, zoom, width, height)
        logger.info(f"Created base map for {lat:.2f},{lon:.2f}")
        return result
    except Exception as e:
        logger.error(f"Failed to composite tiles: {e}")
        return None
