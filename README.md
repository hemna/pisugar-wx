# PiSugar Weather Station Display

Weather display application for Raspberry Pi Zero 2 W with PiSugar Whisplay HAT.

## Overview

This application fetches weather data from the National Weather Service (NWS) API and displays current conditions and forecasts on the PiSugar Whisplay HAT (240x280 pixel LCD).

## Features

- Current temperature, conditions, and humidity display
- 7-day weather forecast
- Support for multiple weather stations with automatic cycling
- Offline support with local caching
- Automatic data refresh
- Weather condition icons (bitmap graphics)

## Hardware Requirements

- Raspberry Pi Zero 2 W
- PiSugar Whisplay HAT

## Software Requirements

- Raspberry Pi OS Lite
- Python 3.11+

## Installation

```bash
# Clone repository
git clone https://github.com/yourusername/pisugar-wx.git
cd pisugar-wx

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Edit `config/stations.json` to add your weather stations:

```json
{
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
    "temperature_unit": "F"
  }
}
```

## Usage

```bash
# Run the application
python -m src.app
```

## Auto-start on Boot

Copy the systemd service file and enable:

```bash
sudo cp pisugar-weather.service /etc/systemd/system/
sudo systemctl enable pisugar-weather.service
sudo systemctl start pisugar-weather.service
```

## Development

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=src tests/
```

## License

MIT License
