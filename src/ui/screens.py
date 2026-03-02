"""Display screens for weather information."""

import os
from typing import Optional

from PIL import Image, ImageDraw, ImageFont

from ..weather.models import CurrentConditions, Forecast
from ..config import WeatherStation
from .elements import DisplayCanvas, WHITE, BLACK, BLUE, GRAY
from .fonts import FontLoader
from .icons import get_icon_path


ICON_SIZE = 48
LAYOUT_PADDING = 10


class BaseScreen:
    """Base class for display screens."""
    
    def __init__(self, width: int = 280, height: int = 240):
        self.width = width
        self.height = height
        self.font_loader = FontLoader()
    
    def create_canvas(self, background=WHITE) -> DisplayCanvas:
        return DisplayCanvas(self.width, self.height, background)
    
    def render(self) -> Image.Image:
        """Render the screen and return the image."""
        raise NotImplementedError


class CurrentWeatherScreen(BaseScreen):
    """Screen displaying current weather conditions."""
    
    def __init__(
        self,
        width: int = 280,
        height: int = 240,
        icon_dir: str = "assets/icons",
        temperature_unit: str = "F"
    ):
        super().__init__(width, height)
        self.icon_dir = icon_dir
        self.temperature_unit = temperature_unit
    
    def render(
        self,
        station: WeatherStation,
        conditions: CurrentConditions,
        is_cached: bool = False,
        last_updated=None
    ) -> Image.Image:
        """Render current weather display.
        
        Args:
            station: Weather station information.
            conditions: Current weather conditions.
            is_cached: Whether data is from cache.
            last_updated: Last update timestamp.
            
        Returns:
            PIL Image for display.
        """
        canvas = self.create_canvas()
        
        # Station name (header)
        font_small = self.font_loader.get_small_font()
        font_medium = self.font_loader.get_default_font()
        font_large = self.font_loader.get_large_font()
        
        # Draw station name
        canvas.text(
            (LAYOUT_PADDING, LAYOUT_PADDING),
            station.name,
            font_small,
            BLACK
        )
        
        # Draw weather icon (top right area)
        icon_x = self.width - ICON_SIZE - LAYOUT_PADDING
        icon_y = LAYOUT_PADDING
        
        icon_path = get_icon_path(self.icon_dir, conditions.condition)
        if icon_path and os.path.exists(icon_path):
            icon_img = Image.open(icon_path)
            icon_img = icon_img.resize((ICON_SIZE, ICON_SIZE), Image.Resampling.LANCZOS)
            canvas.image_at((icon_x, icon_y), icon_img)
        else:
            # Draw placeholder rectangle if icon not found
            canvas.rectangle(
                (icon_x, icon_y, icon_x + ICON_SIZE, icon_y + ICON_SIZE),
                outline=GRAY
            )
        
        # Temperature (large, centered)
        temp_text = f"{int(conditions.temperature)}°{self.temperature_unit}"
        temp_bbox = canvas.draw.textbbox((0, 0), temp_text, font=font_large)
        temp_width = temp_bbox[2] - temp_bbox[0]
        temp_x = (self.width - temp_width) // 2
        canvas.text((temp_x, 50), temp_text, font=font_large, fill=BLACK)
        
        # Condition text
        condition_y = 110
        canvas.centered_text(condition_y, conditions.condition, font_medium, BLACK)
        
        # Humidity
        humidity_y = 140
        humidity_text = f"Humidity: {conditions.humidity}%"
        canvas.centered_text(humidity_y, humidity_text, font_small, GRAY)
        
        # Wind
        wind_y = 160
        wind_text = f"Wind: {conditions.wind_speed} {conditions.wind_direction}"
        canvas.centered_text(wind_y, wind_text, font_small, GRAY)
        
        # Footer - Last updated or cached indicator
        if is_cached:
            footer_text = "Cached Data"
        elif last_updated:
            footer_text = f"Updated: {last_updated.strftime('%H:%M')}"
        else:
            footer_text = ""
        
        if footer_text:
            canvas.centered_text(self.height - 20, footer_text, font_small, GRAY)
        
        return canvas.get_image()


class ForecastScreen(BaseScreen):
    """Screen displaying weather forecast."""
    
    def __init__(
        self,
        width: int = 280,
        height: int = 240,
        icon_dir: str = "assets/icons",
        temperature_unit: str = "F"
    ):
        super().__init__(width, height)
        self.icon_dir = icon_dir
        self.temperature_unit = temperature_unit
    
    def render(
        self,
        station: WeatherStation,
        forecasts: list[Forecast],
        is_cached: bool = False
    ) -> Image.Image:
        """Render forecast display.
        
        Args:
            station: Weather station information.
            forecasts: List of forecast periods.
            is_cached: Whether data is from cache.
            
        Returns:
            PIL Image for display.
        """
        canvas = self.create_canvas()
        
        font_small = self.font_loader.get_small_font()
        font_medium = self.font_loader.get_default_font()
        
        # Header - Station name
        canvas.text(
            (LAYOUT_PADDING, LAYOUT_PADDING),
            f"{station.name} - Forecast",
            font_small,
            BLACK
        )
        
        # Show first few forecast periods
        y_pos = 40
        
        for i, forecast in enumerate(forecasts[:4]):
            # Period name
            canvas.text(
                (LAYOUT_PADDING, y_pos),
                forecast.period_name,
                font_small,
                BLACK
            )
            
            # Temperature
            temp_text = f"{forecast.temperature}°{self.temperature_unit}"
            canvas.text(
                (120, y_pos),
                temp_text,
                font_medium,
                BLACK
            )
            
            # Condition
            canvas.text(
                (170, y_pos),
                forecast.condition[:15],
                font_small,
                GRAY
            )
            
            # Precipitation probability
            if forecast.precipitation_probability and forecast.precipitation_probability > 20:
                pop_text = f"{forecast.precipitation_probability}%"
                canvas.text(
                    (250, y_pos),
                    pop_text,
                    font_small,
                    BLUE
                )
            
            y_pos += 35
        
        # Footer
        if is_cached:
            canvas.centered_text(self.height - 20, "Cached Data", font_small, GRAY)
        
        return canvas.get_image()


class ErrorScreen(BaseScreen):
    """Screen displaying error messages."""
    
    def __init__(self, width: int = 280, height: int = 240):
        super().__init__(width, height)
    
    def render(self, message: str, station_name: str = "") -> Image.Image:
        """Render error display.
        
        Args:
            message: Error message to display.
            station_name: Optional station name.
            
        Returns:
            PIL Image for display.
        """
        canvas = self.create_canvas(background=(50, 0, 0))  # Dark red background
        
        font_small = self.font_loader.get_small_font()
        font_medium = self.font_loader.get_default_font()
        
        # Title
        canvas.centered_text(50, "Error", font_medium, WHITE)
        
        # Station name if provided
        if station_name:
            canvas.centered_text(80, station_name, font_small, WHITE)
        
        # Error message
        canvas.centered_text(120, message[:30], font_small, WHITE)
        
        return canvas.get_image()


class OfflineScreen(BaseScreen):
    """Screen displaying offline status."""
    
    def __init__(self, width: int = 280, height: int = 240):
        super().__init__(width, height)
    
    def render(self, last_updated=None) -> Image.Image:
        """Render offline display.
        
        Args:
            last_updated: Last successful update timestamp.
            
        Returns:
            PIL Image for display.
        """
        canvas = self.create_canvas(background=GRAY)
        
        font_medium = self.font_loader.get_default_font()
        font_small = self.font_loader.get_small_font()
        
        # Offline message
        canvas.centered_text(80, "OFFLINE", font_medium, WHITE)
        
        # Last update time if available
        if last_updated:
            time_str = f"Last update: {last_updated.strftime('%H:%M')}"
            canvas.centered_text(120, time_str, font_small, WHITE)
        
        return canvas.get_image()
