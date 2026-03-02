# Implementation Plan: Display Orientation Support

**Branch**: `002-display-orientation-support` | **Date**: 2026-03-02 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-display-orientation-support/spec.md`

## Summary

Add support for both portrait (240x280) and landscape (280x240) display orientations for the PiSugar weather display. The current portrait layout is working well with a two-column design (weather icon + temperature on left, wind compass on right). Landscape mode will require an optimized layout for the wider aspect ratio. Orientation will be configurable via the stations.json settings file.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: PIL/Pillow (image rendering), WhisPlayBoard driver (display hardware)  
**Storage**: JSON configuration file (stations.json)  
**Testing**: pytest (unit tests)  
**Target Platform**: Raspberry Pi Zero 2 W with PiSugar Whisplay HAT (1.69" IPS LCD, ST7789 controller)
**Project Type**: Embedded display application  
**Performance Goals**: Display render < 3 seconds, smooth transitions between stations  
**Constraints**: 240x280 or 280x240 pixel display, limited CPU/memory on Pi Zero  
**Scale/Scope**: Single-device embedded application

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Code Quality | PASS | Will follow existing code style, add docstrings for new functions |
| II. Testing Standards | PASS | Will add unit tests for orientation logic and layout calculations |
| III. UX Consistency | PASS | Both orientations will use consistent design patterns (dark theme, color-coded temp, wind compass) |
| IV. Performance Requirements | PASS | Layout calculations are lightweight, no performance concerns |

**Quality Gates Checklist**:
- [ ] Linting: Code will pass static analysis
- [ ] Tests: Unit tests for orientation config and layout selection
- [ ] Coverage: New code will have tests
- [ ] Performance: No regression expected
- [ ] Documentation: Orientation config option documented
- [ ] Review: PR review required

## Project Structure

### Documentation (this feature)

```text
specs/002-display-orientation-support/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
src/
├── __init__.py
├── app.py               # Main application (update for orientation)
├── config.py            # Configuration (add orientation setting)
├── display.py           # Display driver (update dimensions based on orientation)
├── weather/
│   ├── __init__.py
│   ├── api.py
│   ├── cache.py
│   └── models.py
└── ui/
    ├── __init__.py
    ├── elements.py
    ├── fonts.py
    ├── icons.py
    └── screens.py       # Screen layouts (add landscape layout)

config/
└── stations.json        # Add orientation setting

tests/
└── unit/
    ├── test_config.py   # Test orientation config parsing
    └── test_screens.py  # Test layout selection (new)
```

**Structure Decision**: Single project structure, extending existing codebase. Main changes in `config.py` (orientation setting), `display.py` (dimension handling), and `screens.py` (landscape layout).

## Complexity Tracking

No constitution violations - this is a straightforward feature addition with no architectural complexity.
