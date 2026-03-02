# Data Model: Display Orientation Support

**Feature**: 002-display-orientation-support  
**Date**: 2026-03-02

## Entities

### DisplayOrientation (Enum)

Represents the display orientation mode.

| Value | Description |
|-------|-------------|
| `portrait` | Default mode, 240 width × 280 height |
| `landscape` | Rotated mode, 280 width × 240 height (rendered then rotated 90°) |

**Validation Rules**:
- Must be one of: "portrait", "landscape"
- Case-insensitive comparison
- Defaults to "portrait" if not specified or invalid

### AppSettings (Extended)

Extended to include orientation configuration.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| refresh_interval_minutes | int | 15 | Weather data refresh interval |
| cycle_interval_seconds | int | 30 | Station cycling interval |
| temperature_unit | str | "F" | Temperature unit (F or C) |
| display_brightness | int | 100 | Display brightness (0-100) |
| **orientation** | str | "portrait" | Display orientation ("portrait" or "landscape") |
| user_agent | str | "pisugar-weather/0.1.0" | HTTP user agent for NWS API |
| cache_dir | str | "~/.cache/pisugar-weather" | Cache directory path |

### LayoutConfig (New)

Configuration for screen element positioning based on orientation.

| Field | Type | Description |
|-------|------|-------------|
| width | int | Canvas width in pixels |
| height | int | Canvas height in pixels |
| station_name_y | int | Y position for station name |
| icon_x | int | X position for weather icon |
| icon_y | int | Y position for weather icon |
| temp_x | int | X center position for temperature |
| temp_y | int | Y position for temperature |
| compass_x | int | X center position for wind compass |
| compass_y | int | Y center position for wind compass |
| compass_size | int | Diameter of wind compass |
| condition_y | int | Y position for condition text |
| humidity_y | int | Y position for humidity text |
| footer_y | int | Y position for footer text |

**Portrait Layout Values** (current):
```python
LayoutConfig(
    width=240, height=280,
    station_name_y=8,
    icon_x=46, icon_y=35,  # left_center=70, icon centered
    temp_x=70, temp_y=90,
    compass_x=180, compass_y=75, compass_size=55,
    condition_y=165,
    humidity_y=195,  # dynamic based on condition lines
    footer_y=265
)
```

**Landscape Layout Values** (new):
```python
LayoutConfig(
    width=280, height=240,
    station_name_y=8,
    icon_x=26, icon_y=35,  # left section center=50
    temp_x=140, temp_y=45,  # center section
    compass_x=230, compass_y=70, compass_size=50,  # right section
    condition_y=100,  # center section, below temp
    humidity_y=210,  # bottom
    footer_y=225
)
```

## State Transitions

### Orientation Loading

```
App Start
    ↓
Load Config (stations.json)
    ↓
Parse orientation setting
    ↓
[Valid orientation?]
    ├─ Yes → Use specified orientation
    └─ No → Log warning, use "portrait" default
    ↓
Initialize Display with dimensions
    ↓
Create Screen with orientation
    ↓
Render loop (orientation fixed at startup)
```

## Relationships

```
AppConfig
    └── AppSettings
            └── orientation (str) ──→ DisplayOrientation enum

CurrentWeatherScreen
    └── orientation (str)
            └── LayoutConfig (derived from orientation)

Display
    └── width, height (derived from orientation)
```

## Configuration File Schema

**stations.json** (updated settings section):

```json
{
  "version": 1,
  "stations": [...],
  "settings": {
    "refresh_interval_minutes": 15,
    "cycle_interval_seconds": 30,
    "temperature_unit": "F",
    "display_brightness": 100,
    "orientation": "portrait"
  }
}
```
