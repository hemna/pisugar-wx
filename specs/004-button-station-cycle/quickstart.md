# Quickstart: Button Station Cycle

**Feature**: 004-button-station-cycle
**Date**: 2026-03-02

## Usage

The physical button on the PiSugar Whisplay HAT now cycles through weather stations:

1. **Press the button** on the Whisplay display
2. Display immediately shows the next station's weather
3. Auto-cycle timer resets (prevents immediate auto-advance)

## Behavior

| Action | Result |
|--------|--------|
| Button press | Cycle to next station, reset timer |
| Button during random city | Returns to first configured station |
| Button on mock display | No effect (graceful degradation) |

## Logs

When button is pressed, you'll see:
```
INFO - Button pressed - cycling to next station
INFO - Cycled to station 1
INFO - Fetched weather for ...
```

## Troubleshooting

**Button not working?**

1. Check logs for "Button handler registered"
2. If you see "Failed to register button handler", check WhisPlay driver
3. Mock display doesn't have button support (expected behavior)

## No Configuration Required

Button support is automatic when running on hardware with WhisPlayBoard.
