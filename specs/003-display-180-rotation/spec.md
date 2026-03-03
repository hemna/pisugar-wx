# Feature Specification: Display 180° Rotation Setting

**Feature ID**: 003-display-180-rotation
**Date**: 2026-03-02
**Status**: Draft

## Overview

Add a configuration setting that allows the display to be rotated 180 degrees. This is useful when the physical device is mounted upside-down or in a different orientation than expected.

## Requirements

### Functional Requirements

1. **New Setting**: Add `display_rotation` setting to AppSettings
   - Valid values: 0, 90, 180, 270 (degrees)
   - Default: 0 (no rotation)
   - Configurable via `stations.json` settings

2. **Image Rotation**: Apply rotation to rendered images before displaying
   - Rotation should be applied after orientation-based rendering
   - Should work with both portrait and landscape orientations

3. **Backward Compatibility**: Existing configurations without this setting should continue to work (default to 0)

### Non-Functional Requirements

1. **Performance**: Rotation should not noticeably impact display refresh time
2. **Memory**: No significant memory increase from rotation operations

## Success Criteria

1. Setting `display_rotation: 180` rotates the display content 180 degrees
2. All rotation values (0, 90, 180, 270) work correctly
3. Rotation works in combination with portrait/landscape orientation
4. Existing configurations without the setting continue to work

## Technical Approach

1. Add `display_rotation` field to `AppSettings` dataclass in `config.py`
2. Update `load_config()` and `save_config()` to handle the new setting
3. Apply PIL Image rotation in `app.py` before `display.show_image()`
4. Use `Image.Transpose.ROTATE_180` etc. for efficient rotation
