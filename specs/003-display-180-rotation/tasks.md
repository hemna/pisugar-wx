# Tasks: Display 180° Rotation Setting

**Input**: Design documents from `/specs/003-display-180-rotation/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md

**Tests**: Test tasks included per constitution (Testing Standards principle)

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: No setup needed - this feature adds to existing codebase

*No tasks - existing project structure is sufficient*

---

## Phase 2: Foundational

**Purpose**: No foundational tasks needed - feature uses existing infrastructure

*No tasks - PIL/Pillow already available, config system exists*

---

## Phase 3: User Story 1 - Configuration Setting (Priority: P1) 🎯 MVP

**Goal**: Add `display_rotation` setting to AppSettings and configuration loading/saving

**Independent Test**: Load a config file with `display_rotation: 180`, verify AppSettings has value 180

### Tests for User Story 1

- [X] T001 [P] [US1] Add unit test for display_rotation parsing in tests/unit/test_config.py
- [X] T002 [P] [US1] Add unit test for invalid display_rotation values in tests/unit/test_config.py

### Implementation for User Story 1

- [X] T003 [US1] Add `display_rotation: int = 0` field to AppSettings dataclass in src/config.py
- [X] T004 [US1] Add VALID_ROTATIONS constant `(0, 90, 180, 270)` in src/config.py
- [X] T005 [US1] Update `load_config()` to parse and validate display_rotation in src/config.py
- [X] T006 [US1] Update `save_config()` to include display_rotation in src/config.py

**Checkpoint**: Config can be loaded with display_rotation setting, validated, and saved

---

## Phase 4: User Story 2 - Apply Rotation to Display (Priority: P2)

**Goal**: Apply the configured rotation to images before displaying

**Independent Test**: Set `display_rotation: 180` and verify display shows upside-down content

### Implementation for User Story 2

- [X] T007 [US2] Add rotation_map dictionary mapping degrees to Image.Transpose values in src/app.py
- [X] T008 [US2] Add display rotation logic after orientation rotation in `update_display()` method in src/app.py
- [X] T009 [US2] Add logging for rotation being applied in src/app.py

**Checkpoint**: Display rotates content based on display_rotation setting

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Documentation and validation

- [X] T010 Verify all rotation values (0, 90, 180, 270) work correctly
- [X] T011 Verify rotation works with both portrait and landscape orientations
- [X] T012 Run ruff linter on modified files
- [X] T013 Run existing tests to ensure no regressions

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: Skipped - no setup needed
- **Phase 2 (Foundational)**: Skipped - no foundational work needed
- **Phase 3 (US1 - Config)**: Can start immediately
- **Phase 4 (US2 - Display)**: Depends on Phase 3 completion
- **Phase 5 (Polish)**: Depends on Phase 4 completion

### User Story Dependencies

- **User Story 1 (Config)**: No dependencies - can start immediately
- **User Story 2 (Display)**: Depends on US1 (needs config setting to read)

### Within Each User Story

- Tests written first (T001, T002 before T003-T006)
- Config changes before app changes
- Validation before use

### Parallel Opportunities

- T001 and T002 (tests) can run in parallel
- T003, T004 can run in parallel (different sections of same file, but sequential is safer)

---

## Parallel Example: User Story 1 Tests

```bash
# Launch all tests for User Story 1 together:
Task: "Add unit test for display_rotation parsing in tests/unit/test_config.py"
Task: "Add unit test for invalid display_rotation values in tests/unit/test_config.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 3: Config setting
2. **STOP and VALIDATE**: Verify config loads correctly
3. Proceed to Phase 4

### Full Implementation

1. Complete US1 (Config) → Test loading/saving
2. Complete US2 (Display) → Test rotation works
3. Complete Polish → Verify all combinations work

---

## Notes

- This is a minimal feature with only 13 tasks
- Two files modified: `src/config.py` and `src/app.py`
- One test file updated: `tests/unit/test_config.py`
- PIL Image.Transpose is efficient O(1) operation
- Default value 0 ensures backward compatibility
