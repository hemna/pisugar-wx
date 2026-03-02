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
            logger.info(f"Fetched weather for {station.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to fetch weather: {e}")
            return False
    
    def update_display(self) -> None:
        """Update display with current weather data."""
        # Placeholder - will be implemented with screens
        logger.debug("Updating display...")
    
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
