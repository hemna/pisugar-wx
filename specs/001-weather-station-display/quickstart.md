# Quickstart: PiSugar Weather Display

**Feature**: 001-weather-station-display  
**Platform**: Raspberry Pi Zero 2 W with PiSugar Whisplay HAT

## Prerequisites

### Hardware
- Raspberry Pi Zero 2 W
- PiSugar Whisplay HAT (or compatible ST7789 240x280 display)
- MicroSD card with Raspberry Pi OS Lite (32GB recommended)
- Power supply (5V/2A recommended)

### Software
- Raspberry Pi OS Lite (latest stable)
- Python 3.11+
- Git

---

## Installation

### 1. Set up Raspberry Pi

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3-pip python3-venv git

# Enable SPI interface
sudo raspi-config
# Navigate to Interface Options → SPI → Enable
# Reboot after
```

### 2. Clone and Install Application

```bash
# Clone repository
cd ~
git clone https://github.com/yourusername/pisugar-wx.git
cd pisugar-wx

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Weather Stations

Edit `config/stations.json`:

```json
{
  "version": 1,
  "stations": [
    {
      "id": "home",
      "name": "Home",
      "latitude": 39.7456,
      "longitude": -97.0892
    },
    {
      "id": "work",
      "name": "Office",
      "latitude": 39.8283,
      "longitude": -98.5795
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

**Finding your coordinates**:
- Use Google Maps: Right-click location → "What's here?" → coordinates
- Or visit: https://www.latlong.net

### 4. Test Display (Optional)

```bash
# Run display test
python -m src.display.test
```

### 5. Run Application

```bash
# Activate virtual environment
source venv/bin/activate

# Run application
python -m src.app
```

You should see weather data displayed on the Whisplay HAT.

---

## Auto-Start on Boot

### Using systemd

```bash
# Copy service file
sudo cp pisugar-weather.service /etc/systemd/system/

# Edit service file to correct paths
sudo nano /etc/systemd/system/pisugar-weather.service
# Update User, WorkingDirectory, and ExecStart paths

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable pisugar-weather.service
sudo systemctl start pisugar-weather.service

# Check status
sudo systemctl status pisugar-weather.service
```

### Service File Template

```ini
[Unit]
Description=PiSugar Weather Display
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/pisugar-wx
ExecStart=/home/pi/pisugar-wx/venv/bin/python -m src.app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

---

## Troubleshooting

### Display not showing anything
- Check SPI is enabled: `raspi-config` → Interface Options → SPI
- Verify wiring connections
- Try increasing brightness in config

### "No data" or "Offline" message
- Verify internet connectivity: `ping api.weather.gov`
- Check station coordinates are valid
- Review logs: `journalctl -u pisugar-weather -f`

### API errors
- NWS API may be temporarily unavailable; app will show cached data
- Check rate limiting; reduce refresh interval

### Display too dim
- Adjust `display_brightness` in config (0-100)
- Check backlight GPIO connection

---

## Configuration Reference

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| refresh_interval_minutes | int | 15 | How often to fetch new weather data |
| cycle_interval_seconds | int | 30 | Time to display each station |
| temperature_unit | string | "F" | "F" for Fahrenheit, "C" for Celsius |
| display_brightness | int | 100 | Display brightness (0-100) |

---

## Development

### Running Tests

```bash
# Activate venv
source venv/bin/activate

# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_weather.py

# Run with coverage
pytest --cov=src tests/
```

### Project Structure

```
src/
├── app.py              # Main entry point
├── config.py           # Configuration loading
├── weather/
│   ├── api.py          # NWS API client
│   ├── models.py       # Data models
│   └── cache.py        # Caching logic
└── ui/
    ├── screens.py      # Display screens
    └── elements.py     # UI components
```

---

## License

MIT License - See LICENSE file for details
