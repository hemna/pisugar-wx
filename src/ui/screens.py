"""Display screens for weather information."""

import logging
import os
from typing import Optional

from PIL import Image, ImageDraw, ImageFont

from ..weather.models import CurrentConditions, Forecast
from ..config import WeatherStation
from .elements import DisplayCanvas, WHITE, BLACK, BLUE, GRAY, LIGHT_GRAY
from .fonts import FontLoader
from .icons import get_icon_path

logger = logging.getLogger(__name__)


ICON_SIZE = 48
LAYOUT_PADDING = 8

# Dark theme colors
BG_COLOR = BLACK
TEXT_COLOR = WHITE
TEXT_SECONDARY = LIGHT_GRAY


class BaseScreen:
    """Base class for display screens."""
    
    def __init__(self, width: int = 240, height: int = 280):
        self.width = width
        self.height = height
        self.font_loader = FontLoader()
    
    def create_canvas(self, background=BG_COLOR) -> DisplayCanvas:
        return DisplayCanvas(self.width, self.height, background)
    
    def render(self) -> Image.Image:
        """Render the screen and return the image."""
        raise NotImplementedError


class CurrentWeatherScreen(BaseScreen):
    """Screen displaying current weather conditions."""
    
    def __init__(
        self,
        width: int = 240,
        height: int = 280,
        icon_dir: str = "assets/icons",
        temperature_unit: str = "F"
    ):
        super().__init__(width, height)
        self.icon_dir = icon_dir
        self.temperature_unit = temperature_unit
    
    def _get_temp_color(self, temp: float) -> tuple:
        """Get color for temperature display (blue for cold, red for hot).
        
        Args:
            temp: Temperature in Fahrenheit
            
        Returns:
            RGB color tuple
        """
        # Define temperature range (in Fahrenheit)
        cold_temp = 20   # Blue
        hot_temp = 100   # Red
        
        # Clamp temperature to range
        t = max(cold_temp, min(hot_temp, temp))
        
        # Normalize to 0-1 range
        ratio = (t - cold_temp) / (hot_temp - cold_temp)
        
        # Gradient from blue (cold) -> cyan -> green -> yellow -> red (hot)
        if ratio < 0.25:
            # Blue to Cyan (0 - 0.25)
            r = 0
            g = int(255 * (ratio / 0.25))
            b = 255
        elif ratio < 0.5:
            # Cyan to Green (0.25 - 0.5)
            r = 0
            g = 255
            b = int(255 * (1 - (ratio - 0.25) / 0.25))
        elif ratio < 0.75:
            # Green to Yellow (0.5 - 0.75)
            r = int(255 * ((ratio - 0.5) / 0.25))
            g = 255
            b = 0
        else:
            # Yellow to Red (0.75 - 1.0)
            r = 255
            g = int(255 * (1 - (ratio - 0.75) / 0.25))
            b = 0
        
        return (r, g, b)
    
    def _direction_to_degrees(self, direction: str) -> float:
        """Convert compass direction to degrees (0 = North, clockwise).
        
        Args:
            direction: Compass direction string (N, NE, E, etc.)
            
        Returns:
            Degrees from North (0-360)
        """
        # Map compass directions to degrees
        direction_map = {
            'N': 0, 'NNE': 22.5, 'NE': 45, 'ENE': 67.5,
            'E': 90, 'ESE': 112.5, 'SE': 135, 'SSE': 157.5,
            'S': 180, 'SSW': 202.5, 'SW': 225, 'WSW': 247.5,
            'W': 270, 'WNW': 292.5, 'NW': 315, 'NNW': 337.5
        }
        # Extract direction from string (e.g., "5 mph NE" -> "NE")
        dir_upper = direction.upper().strip()
        for key in direction_map:
            if dir_upper == key or dir_upper.endswith(' ' + key):
                return direction_map[key]
        return 0  # Default to North if unknown
    
    def _draw_wind_compass(self, canvas: DisplayCanvas, x: int, y: int, size: int, 
                           direction: str, speed: str) -> None:
        """Draw a compass rose with wind direction indicator.
        
        Args:
            canvas: Canvas to draw on
            x: Center X position
            y: Center Y position  
            size: Diameter of compass
            direction: Wind direction (N, NE, E, etc.)
            speed: Wind speed string
        """
        import math
        
        radius = size // 2
        inner_radius = radius - 10  # Inner circle for arrow
        
        # Draw compass circle
        canvas.draw.ellipse(
            [x - radius, y - radius, x + radius, y + radius],
            outline=TEXT_SECONDARY,
            width=1
        )
        
        # Draw cardinal direction markers OUTSIDE the circle
        font_tiny = self.font_loader.get_font(10)
        markers = [('N', 0), ('E', 90), ('S', 180), ('W', 270)]
        for label, degrees in markers:
            angle_rad = math.radians(degrees - 90)  # Adjust so 0 = up
            marker_x = x + int((radius + 10) * math.cos(angle_rad))
            marker_y = y + int((radius + 10) * math.sin(angle_rad))
            # Center the text on the marker position
            bbox = canvas.draw.textbbox((0, 0), label, font=font_tiny)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
            canvas.draw.text(
                (marker_x - text_w // 2, marker_y - text_h // 2),
                label, font=font_tiny, fill=TEXT_SECONDARY
            )
        
        # Draw small tick marks on circle for cardinal directions
        for degrees in [0, 90, 180, 270]:
            angle_rad = math.radians(degrees - 90)
            inner_x = x + int((radius - 4) * math.cos(angle_rad))
            inner_y = y + int((radius - 4) * math.sin(angle_rad))
            outer_x = x + int(radius * math.cos(angle_rad))
            outer_y = y + int(radius * math.sin(angle_rad))
            canvas.draw.line([(inner_x, inner_y), (outer_x, outer_y)], fill=TEXT_SECONDARY, width=1)
        
        # Draw wind direction arrow
        degrees = self._direction_to_degrees(direction)
        angle_rad = math.radians(degrees - 90)  # Adjust so 0 = up (North)
        
        # Arrow points in the direction wind is coming FROM
        arrow_length = inner_radius - 2
        end_x = x + int(arrow_length * math.cos(angle_rad))
        end_y = y + int(arrow_length * math.sin(angle_rad))
        
        # Draw arrow line (thicker, more visible)
        canvas.draw.line([(x, y), (end_x, end_y)], fill=TEXT_COLOR, width=3)
        
        # Draw arrowhead
        arrow_head_size = 8
        angle1 = angle_rad + math.radians(150)
        angle2 = angle_rad - math.radians(150)
        head1_x = end_x + int(arrow_head_size * math.cos(angle1))
        head1_y = end_y + int(arrow_head_size * math.sin(angle1))
        head2_x = end_x + int(arrow_head_size * math.cos(angle2))
        head2_y = end_y + int(arrow_head_size * math.sin(angle2))
        canvas.draw.polygon([(end_x, end_y), (head1_x, head1_y), (head2_x, head2_y)], fill=TEXT_COLOR)
        
        # Draw wind speed below compass
        font_medium = self.font_loader.get_default_font()
        # Extract just the number from speed (e.g., "5 to 10 mph" -> "5-10 mph")
        speed_text = speed.replace(' to ', '-')
        bbox = canvas.draw.textbbox((0, 0), speed_text, font=font_medium)
        text_w = bbox[2] - bbox[0]
        canvas.draw.text(
            (x - text_w // 2, y + radius + 18),
            speed_text, font=font_medium, fill=TEXT_COLOR
        )
    
    def _invert_icon(self, icon: Image.Image) -> Image.Image:
        """Invert icon colors for dark theme (keep alpha channel)."""
        from PIL import ImageOps
        if icon.mode == 'RGBA':
            # Split into RGB and Alpha
            r, g, b, a = icon.split()
            # Invert RGB channels
            rgb = Image.merge('RGB', (r, g, b))
            rgb_inverted = ImageOps.invert(rgb)
            # Recombine with original alpha
            r2, g2, b2 = rgb_inverted.split()
            return Image.merge('RGBA', (r2, g2, b2, a))
        else:
            return ImageOps.invert(icon)
    
    def _paste_with_alpha(self, canvas: DisplayCanvas, icon: Image.Image, position: tuple) -> None:
        """Paste an RGBA image onto the canvas, handling transparency."""
        if icon.mode == 'RGBA':
            # Create a black background and composite the icon onto it
            bg = Image.new('RGB', icon.size, BG_COLOR)
            bg.paste(icon, mask=icon.split()[3])  # Use alpha channel as mask
            canvas.image.paste(bg, position)
        else:
            canvas.image.paste(icon, position)
    
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
        
        # Draw station name centered at top
        canvas.centered_text(LAYOUT_PADDING, station.name, font_medium, TEXT_COLOR)
        
        # Layout: Left side has icon + temp, right side has wind compass
        left_center = 70  # Center of left column
        right_center = 180  # Center of right column
        
        # Draw weather icon (left side)
        icon_x = left_center - ICON_SIZE // 2
        icon_y = 35
        
        icon_path = get_icon_path(self.icon_dir, conditions.condition)
        logger.debug(f"Icon lookup: condition='{conditions.condition}', path='{icon_path}', exists={icon_path and os.path.exists(icon_path)}")
        icon_loaded = False
        if icon_path and os.path.exists(icon_path):
            try:
                icon_img = Image.open(icon_path)
                # Convert to RGBA if not already, to handle transparency
                if icon_img.mode != 'RGBA':
                    icon_img = icon_img.convert('RGBA')
                icon_img = icon_img.resize((ICON_SIZE, ICON_SIZE), Image.Resampling.LANCZOS)
                # Invert colors for dark theme
                icon_img = self._invert_icon(icon_img)
                # Paste with transparency mask
                self._paste_with_alpha(canvas, icon_img, (icon_x, icon_y))
                icon_loaded = True
                logger.debug(f"Icon loaded successfully: {icon_path}")
            except Exception as e:
                logger.warning(f"Failed to load icon: {e}")
                icon_loaded = False
        else:
            logger.warning(f"Icon not found: icon_dir={self.icon_dir}, exists={os.path.exists(self.icon_dir)}")
        
        if not icon_loaded:
            # Draw placeholder rectangle if icon not found or failed to load
            canvas.rectangle(
                (icon_x, icon_y, icon_x + ICON_SIZE, icon_y + ICON_SIZE),
                outline=TEXT_SECONDARY
            )
        
        # Temperature (left side, below icon) with color based on temp
        temp_color = self._get_temp_color(conditions.temperature)
        temp_text = f"{int(conditions.temperature)}°{self.temperature_unit}"
        temp_bbox = canvas.draw.textbbox((0, 0), temp_text, font=font_large)
        temp_width = temp_bbox[2] - temp_bbox[0]
        temp_x = left_center - temp_width // 2
        canvas.text((temp_x, 90), temp_text, font=font_large, fill=temp_color)
        
        # Wind compass rose (right side)
        compass_size = 55
        compass_y = 75
        self._draw_wind_compass(
            canvas, right_center, compass_y, compass_size,
            conditions.wind_direction, conditions.wind_speed
        )
        
        # Condition text (full width, below icon/compass area)
        condition_y = 165
        condition_text = conditions.condition
        if len(condition_text) > 28:
            condition_text = condition_text[:25] + "..."
        canvas.centered_text(condition_y, condition_text, font_medium, TEXT_COLOR)
        
        # Humidity
        humidity_y = 195
        humidity_text = f"Humidity: {conditions.humidity}%"
        canvas.centered_text(humidity_y, humidity_text, font_medium, TEXT_SECONDARY)
        
        # Footer - Last updated or cached indicator
        if is_cached:
            footer_text = "Cached Data"
        elif last_updated:
            footer_text = f"Updated: {last_updated.strftime('%H:%M')}"
        else:
            footer_text = ""
        
        if footer_text:
            canvas.centered_text(self.height - 15, footer_text, font_small, TEXT_SECONDARY)
        
        return canvas.get_image()


class ForecastScreen(BaseScreen):
    """Screen displaying weather forecast."""
    
    def __init__(
        self,
        width: int = 240,
        height: int = 280,
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
    
    def __init__(self, width: int = 240, height: int = 280):
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
    
    def __init__(self, width: int = 240, height: int = 280):
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
