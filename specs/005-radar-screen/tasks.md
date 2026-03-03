# Tasks: Radar Display Screen

**Input**: Design documents from `/specs/005-radar-screen/`
**Tests**: Minimal - mock API responses for radar/tile fetching

## Format: `[ID] [P?] [Story] Description`

---

## Phase 1: Configuration Setup

**Purpose**: Add radar settings to configuration

- [X] T001 Add `radar_enabled: bool = True` to AppSettings in src/config.py
- [X] T002 Add `radar_duration_seconds: int = 15` to AppSettings in src/config.py
- [X] T003 Add `radar_radius_miles: int = 100` to AppSettings in src/config.py

**Checkpoint**: Config loads with radar settings, defaults work

---

## Phase 2: Tile System

**Purpose**: Fetch and composite OpenStreetMap tiles for base map

- [X] T004 Create src/radar/__init__.py with package exports
- [X] T005 Create src/radar/tiles.py with TileFetcher class skeleton
- [X] T006 Implement `lat_lon_to_tile(lat, lon, zoom)` conversion in tiles.py
- [X] T007 Implement `tile_to_bbox(x, y, zoom)` reverse conversion in tiles.py
- [X] T008 Implement `fetch_tile(x, y, zoom)` with requests in tiles.py
- [X] T009 Implement `get_required_tiles(bbox, zoom)` to list needed tiles in tiles.py
- [X] T010 Implement `composite_tiles()` to merge tiles into single image in tiles.py
- [X] T011 Implement `get_base_map(lat, lon, radius_miles, width, height)` main entry in tiles.py

**Checkpoint**: Can fetch and composite OSM tiles into single image

---

## Phase 3: Tile Caching

**Purpose**: Cache tiles to reduce network requests

- [X] T012 Create src/radar/cache.py with TileCache class
- [X] T013 Implement tile cache directory setup in cache.py
- [X] T014 Implement `get_cached_tile(x, y, zoom)` in cache.py
- [X] T015 Implement `save_tile(x, y, zoom, image_data)` in cache.py
- [X] T016 Integrate caching into TileFetcher.fetch_tile() in tiles.py

**Checkpoint**: Tiles cached on disk, subsequent fetches use cache

---

## Phase 4: Radar API

**Purpose**: Fetch NOAA CREF radar via WMS

- [X] T017 Create src/radar/api.py with RadarFetcher class
- [X] T018 Implement `get_radar_bbox(lat, lon, radius_miles)` in api.py
- [X] T019 Implement `build_wms_url(bbox, width, height)` in api.py
- [X] T020 Implement `fetch_radar(lat, lon, radius_miles, width, height)` in api.py
- [X] T021 Add radar image caching (2 minute TTL) to cache.py
- [X] T022 Integrate radar caching into RadarFetcher in api.py

**Checkpoint**: Can fetch radar image for given lat/lon

---

## Phase 5: Radar Screen UI

**Purpose**: Create RadarScreen class for rendering

- [X] T023 Add RadarScreen class to src/ui/screens.py
- [X] T024 Implement RadarScreen.__init__ with orientation support
- [X] T025 Implement RadarScreen.render(station, base_map, radar_image)
- [X] T026 Add station name text overlay at top of radar screen
- [X] T027 Handle orientation rotation (portrait/landscape) in RadarScreen

**Checkpoint**: RadarScreen renders base map + radar + text

---

## Phase 6: App Integration

**Purpose**: Integrate radar into display cycle

- [X] T028 Add `showing_radar: bool = False` state to WeatherApp in app.py
- [X] T029 Add `radar_time: float` timer attribute to WeatherApp in app.py
- [X] T030 Import and instantiate radar modules in WeatherApp
- [X] T031 Add `fetch_radar_image()` method to WeatherApp in app.py
- [X] T032 Add `update_radar_display()` method to WeatherApp in app.py
- [X] T033 Modify run() loop to toggle between weather and radar in app.py
- [X] T034 Modify _on_button_pressed() to skip radar to next station in app.py
- [X] T035 Add radar_enabled check to skip radar when disabled in app.py

**Checkpoint**: Full weather→radar→weather cycle working

---

## Phase 7: Polish

**Purpose**: Error handling, logging, testing

- [X] T036 Add try/except around radar fetch with graceful fallback in app.py
- [X] T037 Add try/except around tile fetch with fallback in tiles.py
- [X] T038 Add logging throughout radar module
- [X] T039 Test with mock display (--mock-display flag)
- [X] T040 Run ruff linter on all modified/new files

**Checkpoint**: App handles errors gracefully, passes linting

---

## Dependencies & Execution Order

### Phase Dependencies
- Phase 1 (Config): Independent, do first
- Phase 2 (Tiles): Independent, can parallel with Phase 1
- Phase 3 (Cache): Depends on Phase 2
- Phase 4 (Radar): Depends on Phase 3 (for caching)
- Phase 5 (Screen): Depends on Phases 2, 4
- Phase 6 (Integration): Depends on all previous phases
- Phase 7 (Polish): Depends on Phase 6

---

## Implementation Notes

1. **Zoom Level**: Use zoom 7 for ~100mi radius view
2. **OSM User-Agent**: Must include app name per OSM policy
3. **Image Memory**: Close PIL images after display to free memory
4. **CONUS Only**: Radar only available for continental US
5. **Transparency**: Radar PNG uses alpha channel for overlay
