# Data Model: Button Station Cycle

**Feature**: 004-button-station-cycle
**Date**: 2026-03-02

## Entities

### Display Class (Modified)

**Location**: `src/display.py`

| Property | Type | Description |
|----------|------|-------------|
| board | WhisPlayBoard \| None | Underlying hardware board instance |

**New Property**:
```python
@property
def board(self):
    """Get the underlying WhisPlayBoard instance for button handling."""
    return self._board
```

### WeatherApp Class (Modified)

**Location**: `src/app.py`

| Attribute | Type | Description |
|-----------|------|-------------|
| cycle_time | float | Timestamp of last cycle (needs to be instance attribute) |

**New Method**:
```python
def _on_button_pressed(self) -> None:
    """Handle button press event - cycle to next station."""
    logger.info("Button pressed - cycling to next station")
    self.cycle_station()
    self.cycle_time = time.time()  # Reset auto-cycle timer
```

### MockDisplay Class (No Changes)

- No `board` property needed (returns None implicitly via `hasattr` check)
- Button functionality gracefully skipped

## State Transitions

Button press triggers:
1. `current_station_index` increments (via `cycle_station()`)
2. Weather fetched for new station
3. `cycle_time` reset to current time
4. Display updates on next loop iteration

## Relationships

- Display owns WhisPlayBoard instance
- WeatherApp registers callback with WhisPlayBoard via Display.board
- Button callback triggers WeatherApp.cycle_station()
