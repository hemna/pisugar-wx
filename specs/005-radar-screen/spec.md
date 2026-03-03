# Specification: Radar Display Screen

**Feature ID**: 005-radar-screen
**Date**: 2026-03-02
**Status**: Draft

## Overview

Add a radar screen that displays between weather station cycles. Each station shows its weather conditions, then a radar image for that location before moving to the next station. The radar displays NOAA CREF (Composite Reflectivity) overlaid on an OpenStreetMap base map, covering approximately 100 miles around each station.

## User Stories

### US1: View Radar After Weather (Priority: P1) MVP
**As a** user viewing weather information
**I want** to see a radar image for each station after its weather display
**So that** I can see precipitation patterns in the area

**Acceptance Criteria:**
- After weather displays for configured duration (30s), radar screen appears
- Radar shows ~100 mile radius around station location
- Radar displays for 15 seconds before cycling to next station
- Radar includes base map (OpenStreetMap) with radar overlay
- Station name shown at top of radar screen

### US2: Skip Radar With Button (Priority: P2)
**As a** user who wants to quickly browse stations
**I want** to skip the radar screen by pressing the button
**So that** I can move faster through the station list

**Acceptance Criteria:**
- Button press during radar skips to next station's weather
- Timer resets for next station's cycle
- Same behavior as button during weather (immediate response)

### US3: Radar for Random Cities (Priority: P2)
**As a** user viewing random US cities
**I want** to see radar for random cities too
**So that** I have a consistent experience across all stations

**Acceptance Criteria:**
- Random cities show radar screen after weather (same as configured stations)
- Same 15-second duration
- Same button skip behavior

### US4: Disable Radar Option (Priority: P3)
**As a** user who prefers weather-only display
**I want** to disable radar screens via configuration
**So that** I can customize my display experience

**Acceptance Criteria:**
- `radar_enabled` setting in config (default: true)
- When disabled, display cycles weather→weather without radar
- No performance impact when disabled (no radar fetching)

## Functional Requirements

### FR1: Radar Data Source
- Use NOAA GeoServer WMS for CREF (Composite Reflectivity)
- Endpoint: `https://opengeo.ncep.noaa.gov/geoserver/conus/conus_cref_qcd/ows`
- Request parameters: WMS 1.3.0, PNG format, transparent background
- Coverage: CONUS (Continental US) only

### FR2: Base Map
- Use OpenStreetMap tiles for base map
- Endpoint: `https://tile.openstreetmap.org/{z}/{x}/{y}.png`
- Composite multiple tiles to cover radar area
- Cache tiles to reduce network requests

### FR3: Radar Area Calculation
- Calculate bounding box based on station lat/lon
- Default radius: 100 miles (~1.45° latitude)
- Adjust longitude span based on latitude (cos correction)
- Support configurable radius via `radar_radius_miles` setting

### FR4: Display Timing
- Radar duration: 15 seconds (configurable via `radar_duration_seconds`)
- Weather duration: existing `cycle_interval_seconds` (default 30s)
- Sequence: Weather → Radar → Next Station Weather → Radar → ...

### FR5: Caching
- Cache base map tiles indefinitely (maps rarely change)
- Cache radar images for 2 minutes (radar updates ~every 2 min)
- Cache location: `~/.cache/pisugar-weather/tiles/` and `radar/`

### FR6: Error Handling
- If radar fetch fails: skip radar screen, continue to next station
- If tile fetch fails: show radar on solid dark background
- Log warnings but don't crash application

## Non-Functional Requirements

### NFR1: Performance
- Radar image fetch should complete within 5 seconds
- Tile fetching should be parallelized where possible
- Caching should minimize network requests

### NFR2: Network Usage
- Respect OpenStreetMap usage policy (include User-Agent)
- Don't fetch radar/tiles when display is disabled
- Use appropriate cache headers

### NFR3: Display Quality
- Radar overlay should use transparency to show base map
- Text overlay should be readable against map background
- Support both portrait and landscape orientations

## Configuration Schema

```json
{
  "settings": {
    "radar_enabled": true,
    "radar_duration_seconds": 15,
    "radar_radius_miles": 100
  }
}
```

## Out of Scope

- Animated radar (multiple frames)
- Radar for locations outside CONUS
- User-selectable radar products (only CREF)
- Pinch/zoom on radar
- Custom color scales for radar

## Dependencies

- `requests` library (already in project)
- `PIL/Pillow` library (already in project)
- Network connectivity to NOAA GeoServer and OpenStreetMap

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| NOAA WMS unavailable | No radar display | Skip radar, show warning in logs |
| OpenStreetMap rate limiting | No base map | Fall back to solid background |
| Slow network on Pi Zero | Delayed radar | Aggressive caching, timeout handling |
| Memory usage from images | App crash | Limit image sizes, cleanup after display |
