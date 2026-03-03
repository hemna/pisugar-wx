# Feature Specification: Button Station Cycle

**Feature ID**: 004-button-station-cycle
**Date**: 2026-03-02
**Status**: Draft

## Overview

Add support for the PiSugar Whisplay's physical button. When pressed, the display should immediately cycle to the next weather station, providing a manual way to switch between stations without waiting for the automatic cycle timer.

## Requirements

### Functional Requirements

1. **Button Press Detection**: Register a callback with the WhisPlayBoard for button press events
   - Use `board.on_button_press(callback)` API from WhisPlay driver
   - Callback should trigger station cycling

2. **Immediate Station Cycle**: When button is pressed:
   - Immediately cycle to the next station (same as automatic cycling)
   - Reset the cycle timer to prevent immediate auto-cycle after manual press
   - Fetch and display weather for the new station

3. **Graceful Degradation**: If button setup fails (e.g., on mock display), continue without button support

### Non-Functional Requirements

1. **Responsiveness**: Button press should trigger station change within 500ms
2. **Thread Safety**: Button callback runs in separate thread - ensure safe interaction with main loop
3. **No Blocking**: Button callback should not block the WhisPlay driver

## Success Criteria

1. Pressing the physical button cycles to the next station
2. Display updates immediately after button press
3. Application continues to work if button initialization fails
4. Button works alongside automatic cycling (doesn't interfere)

## Technical Approach

1. Expose the WhisPlayBoard instance from Display class via property
2. In WeatherApp, register button callback after display initialization
3. Button callback calls `cycle_station()` and resets cycle timer
4. Handle thread safety with proper synchronization if needed

## Reference

WhisPlay button API (from test.py example):
```python
board.on_button_press(on_button_pressed)
```
