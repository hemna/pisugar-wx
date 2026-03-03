# Quickstart: Display 180° Rotation Setting

**Feature**: 003-display-180-rotation
**Date**: 2026-03-02

## Configuration

Add `display_rotation` to your `config/stations.json` settings:

```json
{
  "settings": {
    "orientation": "landscape",
    "display_rotation": 180
  }
}
```

## Valid Values

| Value | Effect |
|-------|--------|
| 0 | No rotation (default) |
| 90 | Rotate 90° clockwise |
| 180 | Rotate 180° (upside-down) |
| 270 | Rotate 270° clockwise (or 90° counter-clockwise) |

## Common Use Cases

### Upside-down mounting
```json
"display_rotation": 180
```

### Landscape mode, rotated for right-side mounting
```json
"orientation": "landscape",
"display_rotation": 90
```

## Restart Required

After changing `display_rotation`, restart the service:

```bash
sudo systemctl restart pisugar-weather.service
```
