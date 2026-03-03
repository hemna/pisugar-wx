# Data Model: Display 180° Rotation Setting

**Feature**: 003-display-180-rotation
**Date**: 2026-03-02

## Entities

### AppSettings (Modified)

**Location**: `src/config.py`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| refresh_interval_minutes | int | 15 | Weather data refresh interval |
| cycle_interval_seconds | int | 30 | Station cycling interval |
| temperature_unit | str | "F" | Temperature unit (F or C) |
| display_brightness | int | 100 | Display brightness (0-100) |
| orientation | str | "portrait" | Content layout (portrait/landscape) |
| random_city_enabled | bool | True | Show random city after cycle |
| **display_rotation** | **int** | **0** | **Physical rotation (0/90/180/270)** |
| user_agent | str | "pisugar-weather/0.1.0" | API user agent |
| cache_dir | str | "~/.cache/pisugar-weather" | Cache directory |

### Validation Rules

| Field | Rule | Error Handling |
|-------|------|----------------|
| display_rotation | Must be in [0, 90, 180, 270] | Log warning, default to 0 |

## Configuration Schema

### stations.json Settings Section

```json
{
  "settings": {
    "refresh_interval_minutes": 15,
    "cycle_interval_seconds": 30,
    "temperature_unit": "F",
    "display_brightness": 100,
    "orientation": "landscape",
    "random_city_enabled": true,
    "display_rotation": 180
  }
}
```

## State Transitions

N/A - This is a static configuration setting with no state machine.

## Relationships

- `display_rotation` is independent of `orientation`
- Both can be combined: landscape + 180° rotation = upside-down landscape
