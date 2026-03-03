# Research: Button Station Cycle

**Feature**: 004-button-station-cycle
**Date**: 2026-03-02

## Research Tasks

### 1. WhisPlay Button API

**Decision**: Use `board.on_button_press(callback)` method
**Rationale**:
- Official API from WhisPlay driver
- Used in the example test.py from PiSugar/Whisplay repository
- Callback is called when button is pressed

**API Usage** (from test.py):
```python
def on_button_pressed():
    print("Button pressed!")
    # ... do something

board.on_button_press(on_button_pressed)
```

### 2. Thread Safety Considerations

**Decision**: Button callback runs in driver's thread - keep callback lightweight
**Rationale**:
- The WhisPlay driver likely uses GPIO edge detection which runs callbacks in a separate thread
- Long-running operations in the callback could block the driver
- Solution: Set a flag in the callback, check flag in main loop

**Implementation Approach**:
```python
# Option A: Direct call (simple, may block briefly)
def on_button_pressed(self):
    self.cycle_station()
    self.cycle_time = time.time()  # Reset timer

# Option B: Flag-based (more thread-safe)
self.button_pressed = False

def on_button_pressed(self):
    self.button_pressed = True

# In main loop:
if self.button_pressed:
    self.button_pressed = False
    self.cycle_station()
    cycle_time = time.time()
```

**Chosen**: Option A (direct call) - `cycle_station()` is fast (just updates state and fetches from cache), and the display update happens in the main loop anyway.

### 3. Exposing WhisPlayBoard from Display Class

**Decision**: Add `board` property to Display class
**Rationale**:
- Keep Display class as the single point of access to WhisPlayBoard
- App doesn't need to import WhisPlay directly
- Allows graceful handling when display is unavailable

**Implementation**:
```python
@property
def board(self):
    """Get the underlying WhisPlayBoard instance."""
    return self._board
```

### 4. Graceful Degradation

**Decision**: Skip button setup if board is None (MockDisplay)
**Rationale**:
- MockDisplay doesn't have a WhisPlayBoard
- Application should continue working without button support
- Log warning if button setup fails

**Implementation**:
```python
if hasattr(self.display, 'board') and self.display.board is not None:
    try:
        self.display.board.on_button_press(self._on_button_pressed)
        logger.info("Button handler registered")
    except Exception as e:
        logger.warning(f"Failed to register button handler: {e}")
```

## Resolved Items

| Item | Resolution |
|------|------------|
| Button API | `board.on_button_press(callback)` |
| Thread safety | Direct callback call (fast enough) |
| Board access | Add `board` property to Display class |
| Graceful degradation | Check for board existence, skip if None |
| Timer reset | Reset `cycle_time` after button press |
