# Research: Weather Station Display for PiSugar Whisplay

**Date**: 2026-03-01  
**Feature**: 001-weather-station-display

## 1. NWS API Research

### Decision: Use National Weather Service API

**Rationale**: 
- Free and open source - no API key required
- Comprehensive US weather data (forecasts, alerts, observations)
- Generous rate limits suitable for personal use
- Official US government source - reliable and accurate

**Alternatives Considered**:
- OpenWeatherMap: Requires API key, more complex for US-only use
- WeatherAPI: Has free tier but limits apply
- Dark Sky (now Apple): No longer accepting new users

### API Endpoints Required

1. **Points Endpoint** (`/points/{latitude},{longitude}`)
   - Converts lat/long to NWS grid location
   - Returns forecast office and grid coordinates
   - One-time lookup per station (cache results)

2. **Forecast Endpoint** (`/gridpoints/{office}/{gridX},{gridY}/forecast`)
   - Returns 7-day forecast in 12-hour periods
   - Contains temperature, conditions, precipitation probability

3. **Alerts Endpoint** (`/alerts/active?point={lat},{long}`)
   - Returns active weather alerts for the location

### API Usage Requirements

- **User-Agent Header**: Required - must identify application
  - Example: `User-Agent: pisugar-weather (contact@example.com)`
- **Caching**: Essential - NWS requests cache-friendly responses
- **Rate Limits**: Generous but not published; implement exponential backoff

### Example API Response Flow

```
1. GET https://api.weather.gov/points/39.7456,-97.0892
   → Returns: gridX, gridY, forecast office (e.g., "TOP")

2. GET https://api.weather.gov/gridpoints/TOP/31,80/forecast
   → Returns: forecast periods with temperature, conditions, etc.
```

---

## 2. PiSugar Whisplay HAT Research

### Decision: Use ST7789 display driver with Pillow for rendering

**Hardware Specifications**:
- Display: 1.69" IPS LCD
- Resolution: 240x280 pixels
- Interface: SPI
- Color depth: 65K (16-bit RGB)

**Alternatives Considered**:
- Direct framebuffer access: Too low-level, harder to use
- pygame: Overkill for simple display, high memory usage

### Display Driver

**Library**: `st7789` Python library
- Lightweight SPI driver for ST7789 displays
- Supports Raspberry Pi GPIO SPI
- Works with Pi Zero (ARMv6)

**Installation**:
```bash
pip install st7789
```

### Rendering

**Library**: Pillow (PIL)
- Python Imaging Library
- Create text, draw shapes, render to framebuffer
- Font rendering with ImageFont

### Display Layout

```
+------------------------+
|  [Station Name]    🌡  |  <- Header (station name, status icon)
+------------------------+
|                        |
|      72°F              |  <- Large temperature (main feature)
|   Partly Cloudy        |  <- Current conditions
|                        |
+------------------------+
|  H: 78°F  L: 65°F      |  <- High/Low
|  💧 20%                |  <- Precipitation
+------------------------+
|  [Last updated: 3:45]  |  <- Footer (timestamp)
+------------------------+
```

### GPIO Configuration

- SPI MOSI: GPIO 10 (Pi Zero pin 19)
- SPI MISO: GPIO 9 (pin 21)  
- SPI SCLK: GPIO 11 (pin 23)
- DC: GPIO 25 (pin 22)
- RST: GPIO 27 (pin 13)
- BL: GPIO 18 (pin 12) - Backlight

---

## 3. Raspberry Pi Zero 2 W Considerations

### Hardware Constraints
- **CPU**: ARMv6 single-core @ 1GHz
- **RAM**: 512MB (shared with GPU)
- **Storage**: MicroSD card
- **Power**: Micro USB, 5V/1A recommended

### Software Constraints
- **OS**: Raspberry Pi OS Lite (recommended for minimal footprint)
- **Python**: 3.11 available via pyenv or bullseye backports
- **Memory**: Keep total usage under 200MB for headroom

### Performance Targets
- Boot to display: < 60 seconds
- Memory usage: < 100MB
- API refresh: Every 15 minutes (balance freshness vs. rate limits)
- Display cycle: Every 30 seconds for multiple stations

---

## 4. Configuration Management

### Decision: JSON configuration file

**Rationale**:
- Simple, human-readable
- No external dependencies
- Easy to edit on Pi (nano/vim)
- Version control friendly

### Configuration Schema

```json
{
  "stations": [
    {
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

---

## 5. Service/Deployment

### Decision: systemd service for auto-start

**Rationale**:
- Native to Raspberry Pi OS
- Handles auto-restart on failure
- Standard service management

### Service Configuration

```ini
[Unit]
Description=PiSugar Weather Display
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/pisugar-wx
ExecStart=/usr/bin/python3 src/app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## Summary

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Weather API | NWS api.weather.gov | Free, open, US-focused |
| Display Driver | st7789 | Native support for Whisplay |
| Rendering | Pillow | Standard Python imaging |
| Config | JSON file | Simple, no dependencies |
| Auto-start | systemd | Native Raspberry Pi OS |
| Testing | pytest | Python standard |
