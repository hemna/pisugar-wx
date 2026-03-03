# PiSugar Weather Station Display

Weather display application for Raspberry Pi Zero 2 W with PiSugar Whisplay HAT.

![PiSugar Weather Display](pisugar-wx.png)

## Overview

This application fetches weather data from the National Weather Service (NWS) API and displays current conditions on the PiSugar Whisplay HAT (240x280 pixel LCD). It also shows NOAA weather radar overlaid on OpenStreetMap base maps.

## Features

- **Current Weather Display**: Temperature, conditions, humidity, wind, pressure, and dewpoint
- **Weather Radar**: NOAA composite reflectivity radar overlaid on map tiles
- **Multiple Stations**: Configure multiple locations with automatic cycling
- **Random City**: Optionally displays weather for a random US city after cycling through configured stations
- **Physical Button Control**: Press to skip between weather and radar views
- **Flexible Display Options**: Portrait/landscape orientation, 180-degree rotation support
- **Offline Support**: Local caching for network interruptions
- **Auto-refresh**: Configurable refresh intervals for weather data

## Hardware Requirements

- Raspberry Pi Zero 2 W (or other Raspberry Pi with GPIO)
- [PiSugar Whisplay HAT](https://www.pisugar.com/) (240x280 LCD + button)

## Software Requirements

- Raspberry Pi OS Lite (Bookworm or later recommended)
- Python 3.11+
- WhisPlay Driver (from PiSugar)

## Installation

### 1. Install WhisPlay Driver

Follow PiSugar's instructions to install the WhisPlay driver:

```bash
cd ~
git clone https://github.com/PiSugar/Whisplay.git
cd Whisplay/Driver
pip3 install .
```

### 2. Install PiSugar Weather Display

```bash
# Clone repository
git clone https://github.com/yourusername/pisugar-wx.git
cd pisugar-wx

# Install dependencies (system-wide for RPi.GPIO compatibility)
sudo pip3 install -r requirements.txt
```

### 3. Configure Stations

Edit `config/stations.json` to add your weather stations:

```json
{
  "version": 1,
  "stations": [
    {
      "id": "home",
      "name": "My City, ST",
      "latitude": 39.7456,
      "longitude": -97.0892
    }
  ],
  "settings": {
    "refresh_interval_minutes": 15,
    "cycle_interval_seconds": 30,
    "temperature_unit": "F",
    "display_brightness": 100,
    "orientation": "landscape",
    "display_rotation": 0,
    "random_city_enabled": true,
    "radar_enabled": true,
    "radar_duration_seconds": 15,
    "radar_radius_miles": 100
  }
}
```

### Configuration Options

| Setting | Description | Default |
|---------|-------------|---------|
| `refresh_interval_minutes` | How often to fetch new weather data | 15 |
| `cycle_interval_seconds` | Time to display each station's weather | 30 |
| `temperature_unit` | `F` for Fahrenheit, `C` for Celsius | F |
| `display_brightness` | LCD brightness (0-100) | 100 |
| `orientation` | `portrait` or `landscape` | landscape |
| `display_rotation` | Physical rotation: 0, 90, 180, or 270 | 0 |
| `random_city_enabled` | Show random US city after configured stations | true |
| `radar_enabled` | Show radar between weather displays | true |
| `radar_duration_seconds` | How long to display radar | 15 |
| `radar_radius_miles` | Radar coverage radius | 100 |

## Usage

### Manual Run

```bash
python3 -m src.app
```

### Command Line Options

```bash
python3 -m src.app --help
python3 -m src.app --config /path/to/config.json
python3 -m src.app --mock-display  # Test without hardware
python3 -m src.app --debug         # Enable debug logging
```

### Button Controls

- **During weather display**: Press button to skip to radar
- **During radar display**: Press button to skip to next station's weather

## Auto-start on Boot

Install as a systemd service:

```bash
# Edit the service file to match your username and paths
sudo cp pisugar-weather.service /etc/systemd/system/

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable pisugar-weather.service
sudo systemctl start pisugar-weather.service

# Check status
sudo systemctl status pisugar-weather.service

# View logs
journalctl -u pisugar-weather.service -f
```

## Display Cycle

The application cycles through displays in this order:

1. **Weather** (Station 1) - 30 seconds
2. **Radar** (Station 1) - 15 seconds
3. **Weather** (Station 2) - 30 seconds
4. **Radar** (Station 2) - 15 seconds
5. ... continues for all stations ...
6. **Weather** (Random City) - if enabled
7. **Radar** (Random City) - if enabled
8. Back to Station 1

Radar is prefetched while weather is displayed for seamless transitions.

## Data Sources

- **Weather Data**: [National Weather Service API](https://www.weather.gov/documentation/services-web-api)
- **Radar Images**: [NOAA GeoServer WMS](https://opengeo.ncep.noaa.gov/geoserver/) (Composite Reflectivity)
- **Base Maps**: [OpenStreetMap](https://www.openstreetmap.org/)

## Development

```bash
# Create virtual environment (for development only)
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run tests
pytest

# Run with coverage
pytest --cov=src tests/

# Lint
ruff check .
```

## Troubleshooting

### Display not working
- Ensure WhisPlay driver is installed correctly
- Check SPI is enabled: `sudo raspi-config` > Interface Options > SPI
- Verify GPIO permissions

### Weather data not loading
- Check internet connectivity
- NWS API requires a User-Agent header (configured automatically)
- Some locations may not have NWS coverage (US only)

### Service won't start
- Check logs: `journalctl -u pisugar-weather.service -e`
- Verify paths in service file match your installation
- Ensure Python can find RPi.GPIO (may need system Python, not venv)

## License

MIT License
