# Implementation Plan: Display 180° Rotation Setting

**Branch**: `003-display-180-rotation` | **Date**: 2026-03-02 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-display-180-rotation/spec.md`

## Summary

Add a `display_rotation` configuration setting that allows users to rotate the display output by 0, 90, 180, or 270 degrees. This is useful when the physical device is mounted in a different orientation. The rotation is applied to the final rendered image before sending to the display hardware.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: PIL/Pillow (image rotation), WhisPlayBoard driver (display hardware)
**Storage**: JSON configuration file (`config/stations.json`)
**Testing**: pytest
**Target Platform**: Raspberry Pi Zero W with PiSugar Whisplay HAT
**Project Type**: Embedded display application
**Performance Goals**: Rotation must complete within display refresh cycle (<100ms)
**Constraints**: Limited memory on RPi Zero W, must work with existing orientation setting
**Scale/Scope**: Single device deployment

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Code Quality | ✅ PASS | Will follow existing code patterns, add docstrings |
| II. Testing Standards | ✅ PASS | Will add unit tests for rotation logic |
| III. UX Consistency | ✅ PASS | Follows existing settings pattern |
| IV. Performance | ✅ PASS | PIL rotation is O(1) transpose operation |

## Project Structure

### Documentation (this feature)

```text
specs/003-display-180-rotation/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
src/
├── config.py            # Add display_rotation to AppSettings
├── app.py               # Apply rotation before display.show_image()
└── ...

tests/
├── unit/
│   └── test_config.py   # Add tests for display_rotation setting
└── ...
```

**Structure Decision**: Single project structure - this is a simple configuration addition to the existing codebase with minimal changes to 2 files.

## Complexity Tracking

No constitution violations - this is a straightforward feature addition.
