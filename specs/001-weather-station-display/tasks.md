---

description: "Task list for PiSugar Weather Station Display implementation"
---

# Tasks: Weather Station Display

**Input**: Design documents from `specs/001-weather-station-display/`
**Prerequisites**: plan.md, spec.md, data-model.md, research.md

**Tests**: Included - spec requests testing standards per constitution

**Organization**: Tasks are grouped by user story to enable independent implementation and testing

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project structure per implementation plan in src/
- [X] T002 Create src/__init__.py with package metadata
- [X] T003 Create src/weather/__init__.py
- [X] T004 Create src/ui/__init__.py
- [X] T005 Create requirements.txt with dependencies (requests, st7789, Pillow, pytest)
- [X] T006 Create config/stations.json with default station configuration
- [X] T007 [P] Create README.md with project overview and setup instructions
- [X] T008 Create setup.sh installation script for Raspberry Pi
- [X] T009 Create assets/icons/ directory for weather icon bitmaps
- [X] T010 [P] Download or create weather condition icons (48x48 PNG format) in assets/icons/ (14 icons downloaded)

**Checkpoint**: Project structure ready - can begin foundational work

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [X] T011 Create src/config.py for configuration loading and validation
- [X] T012 [P] Create src/weather/models.py with WeatherStation, CurrentConditions, Forecast classes
- [X] T013 [P] Create src/weather/cache.py for file-based caching
- [X] T014 Create src/weather/api.py for NWS API client (points + forecast endpoints)
- [X] T015 Create tests/unit/test_weather_models.py with model validation tests
- [X] T016 Create tests/integration/test_api.py with mocked API tests
- [X] T017 Create src/display.py with ST7789 display initialization
- [X] T018 [P] Create src/ui/fonts.py with font loading utilities
- [X] T019 [P] Create src/ui/elements.py with reusable UI components (text, icons)
- [X] T020 Create src/app.py with main application entry point

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Display Current Weather (Priority: P1) 🎯 MVP

**Goal**: Display current temperature, conditions, and humidity on the Whisplay HAT with weather icons

**Independent Test**: Run app with single station, verify temperature, condition icon, humidity display

### Tests for User Story 1

- [X] T021 [P] [US1] Create tests/unit/test_display_rendering.py for display output validation
- [X] T022 [P] [US1] Create tests/unit/test_weather_icons.py for icon mapping validation

### Implementation for User Story 1

- [X] T023 [P] [US1] Create src/ui/icons.py with weather icon mapping (NWS codes to icon files)
- [X] T024 [P] [US1] Create src/ui/screens.py with CurrentWeatherScreen class
- [X] T025 [US1] Implement weather icon rendering in src/ui/screens.py (48x48 bitmap)
- [X] T026 [US1] Implement temperature rendering in large font in src/ui/screens.py
- [X] T027 [US1] Implement condition text rendering in src/ui/screens.py
- [X] T028 [US1] Implement humidity display in src/ui/screens.py
- [X] T029 [US1] Connect NWS API to display in src/app.py main loop
- [X] T030 [US1] Add error handling for API failures in src/weather/api.py

**Checkpoint**: Current weather displays on screen with icons - MVP complete

---

## Phase 4: User Story 2 - Display Weather Forecast (Priority: P2)

**Goal**: Show high/low temperatures and upcoming forecast periods with icons

**Independent Test**: Verify forecast data displays correctly with icons and matches API response

### Tests for User Story 2

- [ ] T031 [P] [US2] Add tests for forecast parsing in tests/unit/test_weather_models.py

### Implementation for User Story 2

- [ ] T032 [P] [US2] Extend Forecast model in src/weather/models.py with all fields
- [ ] T033 [US2] Update src/weather/api.py to fetch forecast endpoint
- [ ] T034 [US2] Create src/ui/screens.py ForecastScreen class
- [ ] T035 [US2] Implement high/low temperature display in src/ui/screens.py
- [ ] T036 [US2] Implement precipitation probability display in src/ui/screens.py
- [ ] T037 [US2] Add weather icons to forecast periods in src/ui/screens.py

**Checkpoint**: Forecast displays alongside current weather with icons

---

## Phase 5: User Story 3 - Support Multiple Stations (Priority: P3)

**Goal**: Monitor multiple weather stations with automatic cycling

**Independent Test**: Configure 2+ stations, verify cycling through all stations

### Tests for User Story 3

- [ ] T038 [P] [US3] Add tests for station cycling in tests/unit/test_display.py

### Implementation for User Story 3

- [ ] T039 [P] [US3] Create src/ui/screens.py with station cycling logic
- [ ] T040 [US3] Add station name rendering to all screens in src/ui/screens.py
- [ ] T041 [US3] Implement cycling timer in src/app.py
- [ ] T042 [US3] Add multi-station configuration support in src/config.py
- [ ] T043 [US3] Add graceful error handling when one station fails in src/weather/api.py

**Checkpoint**: Multiple stations cycle automatically

---

## Phase 6: User Story 4 - Handle Offline/Error States (Priority: P1)

**Goal**: Gracefully handle network failures and display cached data or error messages

**Independent Test**: Disconnect network, verify cached data or "Offline" message displays

### Tests for User Story 4

- [ ] T044 [P] [US4] Add tests for offline handling in tests/integration/test_api.py

### Implementation for User Story 4

- [ ] T045 [P] [US4] Enhance src/weather/cache.py with TTL and stale detection
- [ ] T046 [US4] Create src/ui/screens.py ErrorScreen for displaying errors
- [ ] T047 [US4] Implement "Last updated" timestamp display in src/ui/screens.py
- [ ] T048 [US4] Add "Offline" message display in src/ui/screens.py
- [ ] T049 [US4] Add rate limit handling with exponential backoff in src/weather/api.py

**Checkpoint**: App handles offline gracefully

---

## Phase 7: User Story 5 - Auto-Refresh and Cycling (Priority: P2)

**Goal**: Automatic data refresh and station cycling without user interaction

**Independent Test**: Wait for refresh intervals, verify automatic updates

### Implementation for User Story 5

- [ ] T050 [P] [US5] Implement refresh timer in src/app.py
- [ ] T051 [US5] Implement auto-start on boot in setup.sh systemd service
- [ ] T052 [US5] Add configurable intervals in src/config.py
- [ ] T053 [US5] Create pisugar-weather.service systemd unit file

**Checkpoint**: Fully automated hands-free operation

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T054 [P] Run linting and fix code style issues
- [ ] T055 [P] Update README.md with final documentation
- [ ] T056 Add memory usage validation (<100MB) test
- [ ] T057 Add display brightness control in src/config.py
- [ ] T058 Run full test suite and fix any failures
- [ ] T059 [P] Validate icon rendering on 240x280 display

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed) or sequentially in priority order

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational - Requires US1 for basic display
- **User Story 4 (P1)**: Can start after Foundational - Can be parallelized with US1
- **User Story 5 (P2)**: Can start after Foundational - Requires US1-US3 for full functionality

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Create tests/unit/test_display_rendering.py for display output validation"
Task: "Create tests/unit/test_weather_icons.py for icon mapping validation"

# Launch implementation tasks in parallel:
Task: "Create src/ui/icons.py with weather icon mapping"
Task: "Create src/ui/screens.py with CurrentWeatherScreen class"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 - Display Current Weather with Icons
4. **STOP and VALIDATE**: Test current weather display with icons independently
5. Deploy/demo if ready - This is the MVP!

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Add User Story 5 → Test independently → Deploy/Demo
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (MVP with icons)
   - Developer B: User Story 2 (Forecast)
   - Developer C: User Story 4 (Error handling)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- **NEW**: Icon assets are critical for US1 - ensure weather icons are acquired/created in Phase 1
