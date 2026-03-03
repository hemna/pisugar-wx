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

from src.config import load_config, AppConfig, WeatherStation
from src.display import Display, MockDisplay
from src.weather.api import WeatherAPI
from src.weather.cache import WeatherCacheManager
from src.weather.models import CurrentConditions, Forecast
from src.ui.screens import CurrentWeatherScreen, OfflineScreen, ErrorScreen, RadarScreen
from src.random_city import get_random_city
from src.radar import get_base_map, fetch_radar_image

# Import PIL Image for landscape rotation
try:
    from PIL import Image
except ImportError:
    Image = None

# Map display_rotation degrees to PIL Transpose values
ROTATION_MAP = {
    90: Image.Transpose.ROTATE_90 if Image else None,
    180: Image.Transpose.ROTATE_180 if Image else None,
    270: Image.Transpose.ROTATE_270 if Image else None,
}

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
        
        # Timer for station cycling (can be reset by button press)
        self.cycle_time: float = time.time()
        
        # Random city tracking
        self.showing_random_city = False
        self.random_city_station: Optional[WeatherStation] = None
        
        # Radar display state
        self.showing_radar = False
        self.radar_time: float = 0.0
        self.current_base_map = None  # PIL Image
        self.current_radar_image = None  # PIL Image
        self.radar_prefetched = False  # True if radar already fetched for current station
        
        # Register button callback if board is available
        self._register_button_callback()
    
    def _register_button_callback(self) -> None:
        """Register button press callback with the WhisPlayBoard.
        
        Gracefully handles cases where board is not available (mock display).
        """
        board = self.display.board
        if board is None:
            logger.info("No hardware board available, button support disabled")
            return
        
        try:
            board.on_button_press(self._on_button_pressed)
            logger.info("Button callback registered successfully")
        except Exception as e:
            logger.warning(f"Failed to register button callback: {e}")
    
    def _on_button_pressed(self) -> None:
        """Handle button press event.
        
        If showing radar, skip to next station's weather.
        If showing weather, skip to radar (if enabled) or cycle to next station.
        Called from WhisPlayBoard's button handler thread.
        """
        if self.showing_radar:
            # Skip radar, go to next station's weather
            logger.info("Button pressed during radar - skipping to next station")
            self.showing_radar = False
            self.cycle_station()
            self.cycle_time = time.time()
        else:
            # Showing weather - skip to radar if enabled
            if self.config.settings.radar_enabled:
                logger.info("Button pressed during weather - skipping to radar")
                self.showing_radar = True
                self.radar_time = time.time()
            else:
                # Radar disabled, cycle to next station
                logger.info("Button pressed - cycling station")
                self.cycle_station()
                self.cycle_time = time.time()
    
    def fetch_weather(self) -> bool:
        """Fetch weather data for current station.
        
        Returns:
            True if fetch succeeded, False otherwise.
        """
        if not self.config.stations and not self.showing_random_city:
            logger.error("No stations configured")
            return False
        
        # Get the appropriate station
        if self.showing_random_city and self.random_city_station:
            station = self.random_city_station
        else:
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
        if not self.config.stations and not self.showing_random_city:
            return
        
        # Get the appropriate station
        if self.showing_random_city and self.random_city_station:
            station = self.random_city_station
        else:
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
            
            # Apply display_rotation setting for physical mounting adjustments
            display_rotation = self.config.settings.display_rotation
            if display_rotation != 0 and Image is not None and display_rotation in ROTATION_MAP:
                image = image.transpose(ROTATION_MAP[display_rotation])
                logger.debug(f"Applied display rotation: {display_rotation}°")
            
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
    
    def fetch_radar(self) -> bool:
        """Fetch radar image for current station.
        
        Returns:
            True if fetch succeeded, False otherwise.
        """
        # Get the appropriate station
        if self.showing_random_city and self.random_city_station:
            station = self.random_city_station
        else:
            station = self.config.stations[self.current_station_index]
        
        orientation = self.config.settings.orientation
        
        # Determine image dimensions based on orientation
        if orientation == "landscape":
            width, height = 280, 240
        else:
            width, height = 240, 280
        
        radius = self.config.settings.radar_radius_miles
        cache_dir = self.config.settings.cache_dir
        
        try:
            # Fetch base map
            logger.debug(f"Fetching base map for {station.name}")
            self.current_base_map = get_base_map(
                station.latitude,
                station.longitude,
                radius,
                width,
                height,
                cache_dir
            )
            
            if self.current_base_map is None:
                logger.warning(f"Failed to fetch base map for {station.name}")
                return False
            
            # Fetch radar image
            logger.debug(f"Fetching radar for {station.name}")
            self.current_radar_image = fetch_radar_image(
                station.latitude,
                station.longitude,
                radius,
                width,
                height,
                cache_dir
            )
            
            if self.current_radar_image is None:
                logger.warning(f"Failed to fetch radar for {station.name}")
                return False
            
            logger.info(f"Fetched radar for {station.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to fetch radar: {e}")
            return False
    
    def update_radar_display(self) -> None:
        """Update display with radar image."""
        # Get the appropriate station
        if self.showing_random_city and self.random_city_station:
            station = self.random_city_station
        else:
            station = self.config.stations[self.current_station_index]
        
        orientation = self.config.settings.orientation
        
        # Check if we have radar data
        if self.current_base_map is None or self.current_radar_image is None:
            # Show error screen
            try:
                screen = RadarScreen(orientation=orientation)
                image = screen.render_error(station.name)
                
                # Apply rotations
                if orientation == "landscape" and Image is not None:
                    image = image.transpose(Image.Transpose.ROTATE_90)
                
                display_rotation = self.config.settings.display_rotation
                if display_rotation != 0 and Image is not None and display_rotation in ROTATION_MAP:
                    image = image.transpose(ROTATION_MAP[display_rotation])
                
                self.display.show_image(image)
            except Exception as e:
                logger.error(f"Failed to show radar error screen: {e}")
            return
        
        # Render radar screen
        try:
            screen = RadarScreen(orientation=orientation)
            image = screen.render(
                station_name=station.name,
                base_map=self.current_base_map,
                radar_image=self.current_radar_image
            )
            
            # For landscape mode, rotate the image 90° before display
            if orientation == "landscape" and Image is not None:
                image = image.transpose(Image.Transpose.ROTATE_90)
            
            # Apply display_rotation setting for physical mounting adjustments
            display_rotation = self.config.settings.display_rotation
            if display_rotation != 0 and Image is not None and display_rotation in ROTATION_MAP:
                image = image.transpose(ROTATION_MAP[display_rotation])
                logger.debug(f"Applied display rotation: {display_rotation}°")
            
            self.display.show_image(image)
            logger.debug(f"Displayed radar for {station.name} ({orientation} mode)")
        except Exception as e:
            logger.error(f"Failed to update radar display: {e}")
    
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
        """Move to next station in rotation.
        
        After cycling through all configured stations, shows a random US city
        if random_city_enabled is True, then restarts the cycle.
        """
        num_stations = len(self.config.stations)
        
        # Reset radar prefetch flag for new station
        self.radar_prefetched = False
        
        # If currently showing random city, go back to first configured station
        if self.showing_random_city:
            self.showing_random_city = False
            self.random_city_station = None
            self.current_station_index = 0
            logger.info("Returning to configured stations")
            self.fetch_weather()
            return
        
        # Move to next station
        next_index = self.current_station_index + 1
        
        # Check if we've completed a full cycle through configured stations
        if next_index >= num_stations:
            # If random city is enabled, show one before restarting
            if self.config.settings.random_city_enabled:
                city_name, state, lat, lon = get_random_city()
                self.random_city_station = WeatherStation(
                    id=f"random_{city_name.lower().replace(' ', '_')}",
                    name=f"{city_name}, {state}",
                    latitude=lat,
                    longitude=lon
                )
                self.showing_random_city = True
                logger.info(f"Showing random city: {self.random_city_station.name}")
                self.fetch_weather()
            else:
                # Just wrap around to first station
                self.current_station_index = 0
                logger.info("Cycled back to station 0")
                self.fetch_weather()
        else:
            # Normal cycling to next station
            self.current_station_index = next_index
            logger.info(f"Cycled to station {self.current_station_index}")
            self.fetch_weather()
    
    def run(self) -> None:
        """Main application loop.
        
        Display cycle: Weather (30s) → Radar (15s) → Next Station Weather → Radar → ...
        Radar is prefetched while weather is displayed for seamless transitions.
        """
        logger.info("Starting weather display application")
        radar_enabled = self.config.settings.radar_enabled
        radar_duration = self.config.settings.radar_duration_seconds
        weather_duration = self.config.settings.cycle_interval_seconds
        
        # Initial fetch
        self.fetch_weather()
        
        # Reset cycle time at start
        self.cycle_time = time.time()
        self.showing_radar = False
        self.radar_prefetched = False
        
        try:
            while True:
                current_time = time.time()
                
                # Check if refresh needed (for weather data)
                if self.should_refresh():
                    self.fetch_weather()
                
                if self.showing_radar:
                    # Currently showing radar
                    self.update_radar_display()
                    
                    # Check if radar duration has elapsed
                    elapsed = current_time - self.radar_time
                    if elapsed >= radar_duration:
                        # Radar done, cycle to next station
                        self.showing_radar = False
                        self.cycle_station()
                        self.cycle_time = current_time
                else:
                    # Currently showing weather
                    self.update_display()
                    
                    # Prefetch radar while weather is displayed (if not already fetched)
                    if radar_enabled and not self.radar_prefetched:
                        logger.debug("Prefetching radar while showing weather")
                        self.fetch_radar()
                        self.radar_prefetched = True
                    
                    # Check if weather duration has elapsed
                    elapsed = current_time - self.cycle_time
                    if elapsed >= weather_duration:
                        if radar_enabled:
                            # Switch to radar for current station (already prefetched)
                            self.showing_radar = True
                            self.radar_time = current_time
                        else:
                            # Radar disabled, just cycle to next station
                            self.cycle_station()
                            self.cycle_time = current_time
                
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
