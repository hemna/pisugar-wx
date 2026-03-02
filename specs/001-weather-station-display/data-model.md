# Data Model: Weather Station Display

**Feature**: 001-weather-station-display

## Entities

### WeatherStation

Represents a configured weather location.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | Yes | Unique identifier (e.g., "home", "work") |
| name | string | Yes | Display name (e.g., "Home", "Office") |
| latitude | float | Yes | Latitude (-90 to 90) |
| longitude | float | Yes | Longitude (-180 to 180) |
| grid_id | string | No | NWS grid ID (cached after first lookup) |
| grid_x | int | No | NWS grid X coordinate (cached) |
| grid_y | int | No | NWS grid Y coordinate (cached) |
| forecast_office | string | No | NWS forecast office code (cached) |

**Validation Rules**:
- `latitude` must be between -90 and 90
- `longitude` must be between -180 and 180
- `name` must be non-empty and max 50 characters

**Relationships**:
- Has many `CurrentConditions` (one per refresh)
- Has many `Forecast` periods

---

### CurrentConditions

Current weather observation for a station.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| station_id | string | Yes | Reference to WeatherStation |
| timestamp | datetime | Yes | When observation was made |
| temperature | float | Yes | Temperature in Fahrenheit |
| temperature_celsius | float | Yes | Temperature in Celsius |
| humidity | int | Yes | Relative humidity (0-100%) |
| wind_speed | string | Yes | Wind speed with unit (e.g., "10 mph") |
| wind_direction | string | Yes | Compass direction (e.g., "NW") |
| condition | string | Yes | Weather condition text |
| condition_code | string | No | NWS weather code |
| feels_like | float | Yes | Apparent temperature |
| visibility | string | No | Visibility distance |
| pressure | string | No | Barometric pressure |

**Validation Rules**:
- `temperature` must be between -100 and 150°F
- `humidity` must be between 0 and 100
- `timestamp` must be valid ISO 8601 datetime

---

### Forecast

A forecast period from NWS API.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| station_id | string | Yes | Reference to WeatherStation |
| period_name | string | Yes | Period name (e.g., "Today", "Tonight", "Wednesday") |
| start_time | datetime | Yes | When period begins |
| end_time | datetime | Yes | When period ends |
| temperature | int | Yes | Temperature value |
| temperature_unit | string | Yes | "F" or "C" |
| wind_speed | string | Yes | Wind speed text |
| wind_direction | string | Yes | Wind direction text |
| condition | string | Yes | Weather condition |
| is_daytime | bool | Yes | True if daytime period |
| precipitation_probability | int | No | Precipitation chance (0-100) |
| detailed_forecast | string | Yes | Full forecast text |

**Validation Rules**:
- `temperature` must be reasonable (-50 to 130°F)
- `precipitation_probability` must be 0-100 if present

---

### WeatherCache

Cached weather data for offline support.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| station_id | string | Yes | Reference to WeatherStation |
| cached_at | datetime | Yes | When data was cached |
| current_conditions | CurrentConditions | Yes | Cached current weather |
| forecasts | Forecast[] | Yes | Cached forecast data |
| is_stale | bool | Yes | True if cache exceeded TTL |

**Validation Rules**:
- `cached_at` must be in the past
- Cache TTL recommended: 15-30 minutes

---

### AppConfig

Application configuration.

| Field | Type | Required | Default |
|-------|------|----------|---------|
| stations | WeatherStation[] | Yes | [] |
| refresh_interval_minutes | int | No | 15 |
| cycle_interval_seconds | int | No | 30 |
| temperature_unit | string | No | "F" |
| display_brightness | int | No | 100 |
| user_agent | string | No | "pisugar-weather" |
| cache_dir | string | No | "~/.cache/pisugar-weather" |

**Validation Rules**:
- `refresh_interval_minutes` must be 5-60
- `cycle_interval_seconds` must be 10-300
- `display_brightness` must be 0-100

---

### DisplayState

Current state of the display.

| Field | Type | Description |
|-------|------|-------------|
| current_station_index | int | Index of currently displayed station |
| last_update | datetime | Last successful data fetch |
| is_error | bool | True if currently showing error |
| error_message | string | Error description if is_error=True |
| is_fetching | bool | True if currently fetching data |

---

## State Transitions

### Station Configuration Flow

```
[Empty] → Add Station → [Station Added] → Validate Coordinates → [Valid] or [Invalid]
```

### Weather Fetch Flow

```
[Idle] → Fetch Data → [Fetching] → Success → [Update Cache] → [Display New]
                                         ↓
                                   Error → [Log Error] → [Show Cached/Stale]
```

### Display Cycle Flow

```
[Station 0] → Wait cycle_interval → [Station 1] → ... → [Station N] → [Station 0]
```

---

## File Storage

### Configuration File: `config/stations.json`

```json
{
  "version": 1,
  "stations": [
    {
      "id": "home",
      "name": "Home",
      "latitude": 39.7456,
      "longitude": -97.0892
    }
  ],
  "settings": {
    "refresh_interval_minutes": 15,
    "cycle_interval_seconds": 30,
    "temperature_unit": "F",
    "display_brightness": 100
  }
}
```

### Cache File: `~/.cache/pisugar-weather/cache.json`

```json
{
  "stations": {
    "home": {
      "cached_at": "2026-03-01T15:30:00Z",
      "current": { ... },
      "forecast": [ ... ]
    }
  }
}
```
