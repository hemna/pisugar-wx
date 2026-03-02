#!/bin/bash
# PiSugar Weather Station Display - Setup Script
# Run on Raspberry Pi: bash setup.sh

set -e

echo "=== PiSugar Weather Station Display Setup ==="

# Check if running on Raspberry Pi
if [ ! -f /proc/cpuinfo ]; then
    echo "Warning: This script is designed for Raspberry Pi"
fi

# Update system
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required packages
echo "Installing required packages..."
sudo apt install -y python3-pip python3-venv git python3-rpi.gpio

# Enable SPI interface
echo "Enabling SPI interface..."
if command -v raspi-config &> /dev/null; then
    sudo raspi-config nonint do_spi 0
    echo "SPI enabled"
else
    echo "Warning: raspi-config not found. Please enable SPI manually."
fi

# Clone or update repository
if [ -d "$HOME/pisugar-wx" ]; then
    echo "Updating existing installation..."
    cd "$HOME/pisugar-wx"
    git pull
else
    echo "Cloning repository..."
    cd "$HOME"
    git clone https://github.com/yourusername/pisugar-wx.git
    cd pisugar-wx
fi

# Create virtual environment
echo "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Copy systemd service
if [ -f pisugar-weather.service ]; then
    echo "Installing systemd service..."
    sudo cp pisugar-weather.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable pisugar-weather.service
    echo "Service installed. Start with: sudo systemctl start pisugar-weather"
fi

echo "=== Setup Complete ==="
echo "Configuration: Edit config/stations.json to add your weather stations"
echo "Run: source venv/bin/activate && python -m src.app"
