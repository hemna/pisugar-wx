# Implementation Plan: Button Station Cycle

**Branch**: `004-button-station-cycle` | **Date**: 2026-03-02 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-button-station-cycle/spec.md`

## Summary

Add physical button support for the PiSugar Whisplay HAT. When the button is pressed, immediately cycle to the next weather station. The button callback uses `board.on_button_press()` API and triggers the existing `cycle_station()` logic while resetting the auto-cycle timer.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: WhisPlayBoard driver (button handling), threading (callback safety)
**Storage**: N/A - no new configuration needed
**Testing**: pytest (with mock button callbacks)
**Target Platform**: Raspberry Pi Zero W with PiSugar Whisplay HAT
**Project Type**: Embedded display application
**Performance Goals**: Button response < 500ms
**Constraints**: Button callback runs in separate thread, must be thread-safe
**Scale/Scope**: Single device deployment

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Code Quality | ✅ PASS | Will follow existing patterns, add docstrings |
| II. Testing Standards | ✅ PASS | Will add tests for button registration logic |
| III. UX Consistency | ✅ PASS | Button provides consistent station cycling |
| IV. Performance | ✅ PASS | Button callback is lightweight, just triggers cycle |

## Project Structure

### Documentation (this feature)

```text
specs/004-button-station-cycle/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
src/
├── display.py           # Add board property to expose WhisPlayBoard
├── app.py               # Register button callback, handle button press
└── ...
```

**Structure Decision**: Single project structure - this adds button handling to existing Display and WeatherApp classes.

## Complexity Tracking

No constitution violations - this is a straightforward feature addition.
