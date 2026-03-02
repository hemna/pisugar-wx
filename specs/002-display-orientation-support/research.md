# Research: Display Orientation Support

**Feature**: 002-display-orientation-support  
**Date**: 2026-03-02

## Research Questions

### 1. How to handle image rotation for landscape mode?

**Decision**: Use PIL Image.transpose() or rotate() to handle orientation at the rendering level, not the display driver level.

**Rationale**: 
- The ST7789 display controller and WhisPlayBoard driver expect data in a fixed format
- Rotating the rendered PIL Image before converting to RGB565 is simpler and more reliable
- This keeps display.py unchanged and puts orientation logic in the screen rendering

**Alternatives considered**:
- Hardware rotation via ST7789 MADCTL register: Rejected - would require modifying WhisPlayBoard driver
- Swapping width/height in display driver: Rejected - could cause issues with RGB565 conversion

### 2. Optimal landscape layout design

**Decision**: Use a three-section horizontal layout for landscape mode:
- Left section: Weather icon (larger, since we have more horizontal space)
- Center section: Temperature + condition text
- Right section: Wind compass + humidity

**Rationale**:
- Takes advantage of the wider aspect ratio (280px width vs 240px)
- Keeps related information grouped
- Similar information density to portrait mode
- Station name remains at top, spanning full width

**Alternatives considered**:
- Two-column layout similar to portrait: Rejected - doesn't optimize for landscape width
- Single column scrolling: Rejected - not suitable for always-on display

### 3. Configuration approach

**Decision**: Add `orientation` field to the `settings` section in stations.json with values "portrait" or "landscape".

**Rationale**:
- Consistent with existing configuration pattern
- Easy for users to modify
- Allows for future expansion (e.g., "auto" mode based on accelerometer)
- Default to "portrait" for backward compatibility

**Alternatives considered**:
- Command-line argument: Rejected - config file is more persistent
- Separate config file: Rejected - unnecessary complexity

### 4. Screen class architecture

**Decision**: Create separate render methods or use conditional logic within CurrentWeatherScreen based on orientation parameter.

**Rationale**:
- Portrait layout is already well-tested and working
- Landscape layout shares many elements but with different positioning
- Single class with orientation parameter keeps code DRY
- Pass orientation to screen constructor

**Alternatives considered**:
- Separate PortraitScreen/LandscapeScreen classes: Rejected - too much code duplication
- Abstract factory pattern: Rejected - over-engineering for two variants

## Technical Findings

### Display Dimensions
- Portrait: 240 width × 280 height
- Landscape: 280 width × 240 height
- The physical display is 240×280, so landscape requires rendering at 280×240 then rotating 90°

### Rotation Implementation
```python
# For landscape mode, render at 280x240 then rotate
image = screen.render(...)  # 280x240
if orientation == 'landscape':
    image = image.transpose(Image.Transpose.ROTATE_90)  # Now 240x280 for display
```

### Configuration Schema Addition
```json
{
  "settings": {
    "orientation": "portrait",  // or "landscape"
    ...
  }
}
```

## Resolved Clarifications

All technical context items have been resolved. No NEEDS CLARIFICATION items remain.
