# Tasks: Button Station Cycle

**Input**: Design documents from `/specs/004-button-station-cycle/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md

**Tests**: Not explicitly requested - minimal test coverage for button registration

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: No setup needed - this feature adds to existing codebase

*No tasks - existing project structure is sufficient*

---

## Phase 2: Foundational - Expose Board Property

**Purpose**: Add board property to Display class (required before button registration)

- [X] T001 Add `board` property to Display class in src/display.py

**Checkpoint**: Display.board returns WhisPlayBoard instance (or None for MockDisplay)

---

## Phase 3: User Story 1 - Button Press Detection (Priority: P1) 🎯 MVP

**Goal**: Register button callback with WhisPlayBoard to detect button presses

**Independent Test**: Press button on device, see "Button pressed" in logs

### Implementation for User Story 1

- [X] T002 [US1] Add `_on_button_pressed()` method to WeatherApp in src/app.py
- [X] T003 [US1] Add `cycle_time` as instance attribute in WeatherApp.__init__() in src/app.py
- [X] T004 [US1] Register button callback in WeatherApp.__init__() after display setup in src/app.py
- [X] T005 [US1] Add logging for button press event in src/app.py

**Checkpoint**: Button press detected and logged

---

## Phase 4: User Story 2 - Station Cycling (Priority: P2)

**Goal**: Button press triggers station cycling and timer reset

**Independent Test**: Press button, verify station changes and timer resets

### Implementation for User Story 2

- [X] T006 [US2] Call `cycle_station()` in `_on_button_pressed()` in src/app.py
- [X] T007 [US2] Reset `cycle_time` in `_on_button_pressed()` to prevent immediate auto-cycle in src/app.py
- [X] T008 [US2] Update main loop to use `self.cycle_time` instead of local variable in src/app.py

**Checkpoint**: Button cycles station and resets auto-cycle timer

---

## Phase 5: User Story 3 - Graceful Degradation (Priority: P3)

**Goal**: Application works without button if board is unavailable

**Independent Test**: Run with mock display, verify no errors and app continues

### Implementation for User Story 3

- [X] T009 [US3] Add try/except around button registration in src/app.py
- [X] T010 [US3] Log warning if button registration fails in src/app.py
- [X] T011 [US3] Ensure app continues without button support in src/app.py

**Checkpoint**: App works with both real and mock display

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validation and cleanup

- [X] T012 Run ruff linter on modified files
- [ ] T013 Verify button works on hardware (manual test on Pi)
- [X] T014 Verify app works with mock display (no button errors)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: Skipped - no setup needed
- **Phase 2 (Foundational)**: Must complete before user stories
- **Phase 3 (US1 - Detection)**: Depends on Phase 2
- **Phase 4 (US2 - Cycling)**: Depends on Phase 3
- **Phase 5 (US3 - Graceful)**: Depends on Phase 2, can parallel with US1/US2
- **Phase 6 (Polish)**: Depends on all user stories

### User Story Dependencies

- **User Story 1 (Detection)**: Depends on Foundational (board property)
- **User Story 2 (Cycling)**: Depends on US1 (button callback)
- **User Story 3 (Graceful)**: Independent, can start after Foundational

### Parallel Opportunities

- T009, T010, T011 (US3) can run in parallel with US1/US2 tasks
- All involve the same file (app.py), so sequential is safer

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 2: Board property
2. Complete Phase 3: Button detection
3. **STOP and VALIDATE**: Test button press on hardware
4. Proceed to Phase 4

### Full Implementation

1. Complete Foundational (board property)
2. Complete US1 (detection) → Test button logs
3. Complete US2 (cycling) → Test station changes
4. Complete US3 (graceful) → Test mock display
5. Complete Polish → Final validation

---

## Notes

- This is a minimal feature with 14 tasks
- Two files modified: `src/display.py` and `src/app.py`
- Button callback uses WhisPlay's `on_button_press()` API
- Direct callback call chosen over flag-based (cycle_station is fast)
- Timer reset prevents immediate auto-cycle after manual press
