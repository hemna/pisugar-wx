# Quickstart: Display Orientation Support

**Feature**: 002-display-orientation-support  
**Date**: 2026-03-02

## Overview

This feature adds support for both portrait (240x280) and landscape (280x240) display orientations for the PiSugar weather display.

## Configuration

### Setting Display Orientation

Edit `config/stations.json` and add or modify the `orientation` setting:

```json
{
  "version": 1,
  "stations": [...],
  "settings": {
    "refresh_interval_minutes": 15,
    "cycle_interval_seconds": 30,
    "temperature_unit": "F",
    "display_brightness": 100,
    "orientation": "landscape"
  }
}
```

**Valid values**:
- `"portrait"` - Default, 240x280 pixels (taller than wide)
- `"landscape"` - Rotated, 280x240 pixels (wider than tall)

### Default Behavior

If `orientation` is not specified, the display defaults to portrait mode for backward compatibility.

## Layout Differences

### Portrait Mode (240x280)

```
┌──────────────────────────────────┐
│         Station Name             │
├────────────────┬─────────────────┤
│                │                 │
│   [Weather     │    [Wind        │
│    Icon]       │    Compass]     │
│                │                 │
│   Temperature  │    Speed        │
│                │                 │
├────────────────┴─────────────────┤
│     Condition Text Line 1        │
│     Condition Text Line 2        │
├──────────────────────────────────┤
│         Humidity: XX%            │
├──────────────────────────────────┤
│         Updated: HH:MM           │
└──────────────────────────────────┘
```

### Landscape Mode (280x240)

```
┌────────────────────────────────────────────┐
│              Station Name                   │
├─────────────┬───────────────┬──────────────┤
│             │               │              │
│  [Weather   │  Temperature  │  [Wind       │
│   Icon]     │               │  Compass]    │
│             │  Condition    │              │
│             │  Text         │  Speed       │
│             │               │              │
├─────────────┴───────────────┴──────────────┤
│    Humidity: XX%        Updated: HH:MM     │
└────────────────────────────────────────────┘
```

## Testing

### Unit Tests

Run orientation-related tests:

```bash
python -m pytest tests/unit/test_config.py -v
python -m pytest tests/unit/test_screens.py -v
```

### Manual Testing

1. Set orientation in config:
   ```bash
   # Edit config/stations.json
   nano config/stations.json
   ```

2. Run the application:
   ```bash
   python -m src.app
   ```

3. Verify display renders correctly for the selected orientation.

## Troubleshooting

### Display appears rotated incorrectly

Ensure the `orientation` value is spelled correctly ("portrait" or "landscape"). Invalid values default to portrait mode with a warning in the logs.

### Elements overlap or are cut off

This may indicate a layout calculation issue. Check the logs for any warnings and ensure you're running the latest version.

## Implementation Files

| File | Purpose |
|------|---------|
| `src/config.py` | Loads orientation from config with validation |
| `src/app.py` | Passes orientation to screens and rotates image for landscape |
| `src/display.py` | Handles display output (no orientation-specific changes) |
| `src/ui/screens.py` | Renders layouts based on orientation using LayoutConfig |
| `tests/unit/test_config.py` | Tests for orientation config parsing |
| `tests/unit/test_screens.py` | Tests for orientation-aware screen rendering |
