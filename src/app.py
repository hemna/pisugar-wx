"""Main application entry point for PiSugar Weather Display."""

import argparse
import logging
import os
import sys
import time
from datetime import datetime
from typing import Optional

# Setup path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.config import load_config, AppConfig
from src.display import Display, MockDisplay
from src.weather.api import WeatherAPI
from src.weather.cache import WeatherCacheManager
from src.weather.models import CurrentConditions, Forecast
from src.ui.screens import CurrentWeatherScreen, OfflineScreen, ErrorScreen

# Import PIL Image for landscape rotation
try:
    from PIL import Image
except ImportError:
    Image = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class WeatherApp:
    """Main weather display application."""
    
    def __init__(self, config: AppConfig, mock_display: bool = False):
        """Initialize application.
        
        Args:
            config: Application configuration.
            mock_display: Use mock display for testing.
        """
        self.config = config
        self.api = WeatherAPI(user_agent=config.settings.user_agent)
        self.cache_manager = WeatherCacheManager(config.settings.cache_dir)
        
        # Initialize display
        if mock_display:
            self.display = MockDisplay()
        else:
            self.display = Display(brightness=config.settings.display_brightness)
            if not self.display.is_available:
                logger.warning("Display not available, using mock display")
                self.display = MockDisplay()
        
        self.current_station_index = 0
        self.last_fetch_time: Optional[datetime] = None
        self.current_weather: Optional[CurrentConditions] = None
        self.current_forecasts: list[Forecast] = []
    
    def fetch_weather(self) -> bool:
        """Fetch weather data for current station.
        
        Returns:
            True if fetch succeeded, False otherwise.
        """
        if not self.config.stations:
            logger.error("No stations configured")
            return False
        
        station = self.config.stations[self.current_station_index]
        
        try:
            cache = self.api.get_weather_with_cache(station, self.cache_manager)
            self.current_weather = cache.current
            self.current_forecasts = cache.forecasts
            self.last_fetch_time = datetime.now()
            logger.info(f"Fetched weather for {station.name}: "
                       f"{self.current_weather.temperature}°{self.config.settings.temperature_unit}, "
                       f"Dewpoint: {self.current_weather.dewpoint}, "
                       f"{self.current_weather.condition}, "
                       f"Humidity: {self.current_weather.humidity}%, "
                       f"Wind: {self.current_weather.wind_speed} {self.current_weather.wind_direction}, "
                       f"Pressure: {self.current_weather.pressure}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to fetch weather: {e}")
            return False
    
    def update_display(self) -> None:
        """Update display with current weather data."""
        if not self.config.stations:
            return
        
        station = self.config.stations[self.current_station_index]
        orientation = self.config.settings.orientation
        
        # Check if we have weather data
        if not self.current_weather:
            # Show error or offline screen
            offline_screen = OfflineScreen()
            image = offline_screen.render()
            self.display.show_image(image)
            logger.debug("Showing offline screen")
            return
        
        # Render current weather screen
        try:
            icon_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "assets", "icons"
            )
            screen = CurrentWeatherScreen(
                icon_dir=icon_dir,
                temperature_unit=self.config.settings.temperature_unit,
                orientation=orientation
            )
            image = screen.render(
                station=station,
                conditions=self.current_weather,
                is_cached=False,
                last_updated=self.last_fetch_time
            )
            
            # For landscape mode, rotate the image 90° before display
            # The display is physically 240x280, so landscape renders at 280x240
            # and must be rotated to fit
            if orientation == "landscape" and Image is not None:
                image = image.transpose(Image.Transpose.ROTATE_90)
            
            self.display.show_image(image)
            logger.debug(f"Displayed weather for {station.name} ({orientation} mode)")
        except Exception as e:
            logger.error(f"Failed to update display: {e}")
            # Try to show error screen
            try:
                error_screen = ErrorScreen()
                image = error_screen.render(str(e)[:30], station.name)
                self.display.show_image(image)
            except:
                pass
    
    def should_refresh(self) -> bool:
        """Check if weather data should be refreshed.
        
        Returns:
            True if refresh is needed.
        """
        if not self.last_fetch_time:
            return True
        
        elapsed = (datetime.now() - self.last_fetch_time).total_seconds()
        refresh_seconds = self.config.settings.refresh_interval_minutes * 60
        
        return elapsed >= refresh_seconds
    
    def cycle_station(self) -> None:
        """Move to next station in rotation."""
        if len(self.config.stations) > 1:
            self.current_station_index = (
                self.current_station_index + 1
            ) % len(self.config.stations)
            logger.info(f"Cycled to station {self.current_station_index}")
            # Fetch weather for the new station
            self.fetch_weather()
    
    def run(self) -> None:
        """Main application loop."""
        logger.info("Starting weather display application")
        
        # Initial fetch
        self.fetch_weather()
        
        cycle_time = time.time()
        
        try:
            while True:
                # Check if refresh needed
                if self.should_refresh():
                    self.fetch_weather()
                
                # Update display
                self.update_display()
                
                # Cycle station
                current_time = time.time()
                if current_time - cycle_time >= self.config.settings.cycle_interval_seconds:
                    self.cycle_station()
                    cycle_time = current_time
                
                # Sleep briefly
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Shutting down...")
        except Exception as e:
            logger.error(f"Fatal error: {e}")
            raise


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="PiSugar Weather Display")
    parser.add_argument(
        "--config",
        help="Path to configuration file",
        default=None
    )
    parser.add_argument(
        "--mock-display",
        action="store_true",
        help="Use mock display for testing"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Load configuration
    config = load_config(args.config)
    
    if not config.stations:
        logger.error("No stations configured. Please edit config/stations.json")
        sys.exit(1)
    
    # Run application
    app = WeatherApp(config, mock_display=args.mock_display)
    app.run()


if __name__ == "__main__":
    main()
