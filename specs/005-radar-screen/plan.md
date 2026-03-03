# Implementation Plan: Radar Display Screen

**Branch**: `005-radar-screen` | **Date**: 2026-03-02 | **Spec**: spec.md

## Summary

Add radar screen between weather displays using NOAA CREF WMS overlaid on OpenStreetMap tiles. Weather shows 30s, radar shows 15s, then cycles to next station.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: requests, PIL/Pillow (existing)
**External APIs**: NOAA GeoServer WMS, OpenStreetMap tiles
**Testing**: pytest with mock responses
**Performance Goals**: Radar fetch < 5 seconds

## Project Structure

### New Files
```
src/radar/
├── __init__.py          # Package init
├── tiles.py             # OpenStreetMap tile fetching/compositing  
├── api.py               # NOAA WMS radar fetching
└── cache.py             # Tile and radar caching
```

### Modified Files
```
src/config.py            # Add radar settings
src/app.py               # Add radar state management and display logic
src/ui/screens.py        # Add RadarScreen class
```

## Data Flow

1. Station lat/lon → Calculate bounding box (100mi radius)
2. Bounding box → Fetch OSM tiles → Composite base map
3. Bounding box → Fetch NOAA WMS radar → PNG with transparency
4. Base map + Radar → Overlay composition
5. Add station name text → Final image
6. Display for 15 seconds → Cycle to next station

## Key Algorithms

### Bounding Box Calculation
```python
def get_radar_bbox(lat: float, lon: float, radius_miles: int = 100):
    lat_delta = radius_miles / 69.0
    lon_delta = radius_miles / (69.0 * cos(radians(lat)))
    return (lat - lat_delta, lon - lon_delta, lat + lat_delta, lon + lon_delta)
```

### Tile Coordinate Calculation
```python
def lat_lon_to_tile(lat, lon, zoom):
    n = 2 ** zoom
    x = int((lon + 180) / 360 * n)
    y = int((1 - asinh(tan(radians(lat))) / pi) / 2 * n)
    return (x, y)
```

### Display Cycle Logic
```
if showing_radar:
    if elapsed >= radar_duration:
        showing_radar = False
        cycle_station()
else:
    if elapsed >= cycle_interval:
        showing_radar = True
        fetch_radar()
```

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Code Quality | ✅ PASS | Follow existing patterns, add docstrings |
| II. Testing Standards | ✅ PASS | Add mock tests for API calls |
| III. UX Consistency | ✅ PASS | Same text style, button behavior |
| IV. Performance | ✅ PASS | Caching minimizes network calls |
