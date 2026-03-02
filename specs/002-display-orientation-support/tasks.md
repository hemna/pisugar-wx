# Tasks: Display Orientation Support

**Input**: Design documents from `/specs/002-display-orientation-support/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Unit tests requested in constitution check (plan.md). Tests will be included.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root (as per plan.md)

---

## Phase 1: Setup

**Purpose**: Prepare codebase for orientation feature

- [X] T001 Create test file for screen orientation tests in tests/unit/test_screens.py
- [X] T002 [P] Create test file for config orientation tests in tests/unit/test_config.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core orientation infrastructure that MUST be complete before user story implementation

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 Add orientation field to AppSettings dataclass in src/config.py
- [X] T004 Update load_config() to parse orientation from JSON in src/config.py
- [X] T005 Update save_config() to include orientation field in src/config.py
- [X] T006 Add orientation validation with default fallback and warning logging in src/config.py

**Checkpoint**: Configuration infrastructure ready - user story implementation can begin

---

## Phase 3: User Story 1 - Portrait Mode Display (Priority: P1) 🎯 MVP

**Goal**: Preserve existing portrait mode functionality (240x280) while adding orientation awareness

**Independent Test**: Run app with `"orientation": "portrait"` in config and verify current layout works correctly

### Tests for User Story 1

- [X] T007 [P] [US1] Unit test for portrait layout dimensions in tests/unit/test_screens.py
- [X] T008 [P] [US1] Unit test for portrait config parsing in tests/unit/test_config.py

### Implementation for User Story 1

- [X] T009 [US1] Add orientation parameter to CurrentWeatherScreen.__init__() in src/ui/screens.py
- [X] T010 [US1] Create _get_portrait_layout() method returning LayoutConfig values in src/ui/screens.py
- [X] T011 [US1] Update render() to use layout config for portrait mode in src/ui/screens.py
- [X] T012 [US1] Update app.py to pass orientation from config to CurrentWeatherScreen in src/app.py

**Checkpoint**: Portrait mode works with explicit orientation config - existing functionality preserved

---

## Phase 4: User Story 2 - Landscape Mode Display (Priority: P1)

**Goal**: Add landscape mode (280x240) with optimized three-section layout

**Independent Test**: Run app with `"orientation": "landscape"` in config and verify all elements display correctly

### Tests for User Story 2

- [X] T013 [P] [US2] Unit test for landscape layout dimensions in tests/unit/test_screens.py
- [X] T014 [P] [US2] Unit test for landscape config parsing in tests/unit/test_config.py

### Implementation for User Story 2

- [X] T015 [US2] Create _get_landscape_layout() method with three-section layout values in src/ui/screens.py
- [X] T016 [US2] Implement _render_landscape() method for landscape-specific rendering in src/ui/screens.py
- [X] T017 [US2] Update render() to choose layout based on orientation in src/ui/screens.py
- [X] T018 [US2] Add image rotation for landscape mode (transpose 90°) in src/app.py before display
- [X] T019 [US2] Update Display class to handle rotated image dimensions in src/display.py (N/A - Display already handles any image size)

**Checkpoint**: Landscape mode renders correctly with proper rotation

---

## Phase 5: User Story 3 - Configuration-Based Orientation (Priority: P2)

**Goal**: Enable user configuration of orientation via stations.json

**Independent Test**: Modify config/stations.json orientation value, restart app, verify orientation changes

### Tests for User Story 3

- [X] T020 [P] [US3] Unit test for default orientation when not specified in tests/unit/test_config.py
- [X] T021 [P] [US3] Unit test for invalid orientation fallback with warning in tests/unit/test_config.py

### Implementation for User Story 3

- [X] T022 [US3] Update config/stations.json to include orientation setting in config/stations.json
- [X] T023 [US3] Add case-insensitive orientation comparison in src/config.py
- [X] T024 [US3] Ensure backward compatibility when orientation is missing in src/config.py

**Checkpoint**: Orientation fully configurable via JSON file

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements and documentation

- [X] T025 [P] Update quickstart.md with orientation configuration examples in specs/002-display-orientation-support/quickstart.md
- [X] T026 [P] Add docstrings to all new orientation-related functions in src/ui/screens.py
- [X] T027 Run all tests and verify no regressions with pytest tests/
- [ ] T028 Test on Pi hardware in both orientations via SSH

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - US1 and US2 are both P1 priority but US1 should complete first (preserves existing functionality)
  - US3 can proceed after US1/US2 or in parallel
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after US1 or in parallel - Independent but builds on same codebase
- **User Story 3 (P2)**: Can start after Foundational - Primarily config-focused, independent

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Layout config before render methods
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- T001, T002: Setup tests can run in parallel
- T007, T008: US1 tests can run in parallel
- T013, T014: US2 tests can run in parallel
- T020, T021: US3 tests can run in parallel
- T025, T026: Polish tasks can run in parallel

---

## Parallel Example: User Story 2

```bash
# Launch all tests for User Story 2 together:
Task: "Unit test for landscape layout dimensions in tests/unit/test_screens.py"
Task: "Unit test for landscape config parsing in tests/unit/test_config.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test portrait mode with explicit orientation config
5. Existing functionality preserved, ready for landscape addition

### Incremental Delivery

1. Complete Setup + Foundational → Configuration ready
2. Add User Story 1 → Portrait works with orientation awareness → Deploy/Demo (MVP!)
3. Add User Story 2 → Landscape mode working → Deploy/Demo
4. Add User Story 3 → Full config support → Deploy/Demo
5. Each story adds value without breaking previous stories

### Recommended Execution Order

Since this is a single-developer embedded project:

1. T001-T002 (Setup) → T003-T006 (Foundational)
2. T007-T008 (US1 Tests) → T009-T012 (US1 Implementation) → Verify portrait
3. T013-T014 (US2 Tests) → T015-T019 (US2 Implementation) → Verify landscape
4. T020-T021 (US3 Tests) → T022-T024 (US3 Implementation) → Verify config
5. T025-T028 (Polish) → Deploy to Pi

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Portrait mode (US1) should complete first to ensure no regression
- Landscape rotation happens in app.py after render, before display
- Test on actual Pi hardware after local development
- Commit after each task or logical group
