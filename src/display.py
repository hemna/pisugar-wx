"""Display driver for ST7789-based displays."""

import logging
from typing import Optional

try:
    import ST7789
    import RPi.GPIO as GPIO
    DISPLAY_AVAILABLE = True
except ImportError:
    DISPLAY_AVAILABLE = False


logger = logging.getLogger(__name__)


class Display:
    """ST7789 display controller for PiSugar Whisplay HAT."""
    
    def __init__(
        self,
        width: int = 280,
        height: int = 240,
        rotation: int = 90,
        brightness: int = 100
    ):
        """Initialize display.
        
        Args:
            width: Display width in pixels.
            height: Display height in pixels.
            rotation: Display rotation (0, 90, 180, 270).
            brightness: Display brightness (0-100).
        """
        self.width = width
        self.height = height
        self.rotation = rotation
        self.brightness = brightness
        self._display = None
        self._image = None
        
        if DISPLAY_AVAILABLE:
            try:
                self._initialize_display()
                logger.info("Display initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize display: {e}")
                self._display = None
        else:
            logger.warning("Display libraries not available (not on Raspberry Pi)")
        
        logger.info(f"Display available: {self.is_available}")
    
    def _initialize_display(self) -> None:
        """Initialize the ST7789 display."""
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        self._display = ST7789.ST7789(
            port=0,
            cs=0,
            dc=25,
            rst=27,
            backlight=18,
            width=self.width,
            height=self.height,
            rotation=self.rotation
        )
        
        self._display.Setup()
        self._display.SetBacklight(self.brightness / 100.0)
        
        logger.info("Display initialized successfully")
    
    def show_image(self, image) -> None:
        """Display an image on the screen.
        
        Args:
            image: PIL Image to display.
        """
        if self._display is None:
            logger.warning("Display not available")
            return
        
        try:
            self._display.ShowImage(image)
        except Exception as e:
            logger.error(f"Failed to show image: {e}")
    
    def clear(self) -> None:
        """Clear the display."""
        if self._display is None:
            return
        
        # Will be implemented with PIL Image
        pass
    
    def set_brightness(self, brightness: int) -> None:
        """Set display brightness.
        
        Args:
            brightness: Brightness level (0-100).
        """
        self.brightness = max(0, min(100, brightness))
        
        if self._display:
            self._display.SetBacklight(self.brightness / 100.0)
    
    @property
    def is_available(self) -> bool:
        """Check if display is available."""
        return self._display is not None


class MockDisplay:
    """Mock display for testing without hardware."""
    
    def __init__(self, width: int = 280, height: int = 240):
        self.width = width
        self.height = height
        self.brightness = 100
        self._last_image = None
        logger.info("Mock display initialized")
    
    def show_image(self, image) -> None:
        """Store image for testing verification."""
        self._last_image = image
        logger.debug("Mock display: image received")
    
    def clear(self) -> None:
        self._last_image = None
    
    def set_brightness(self, brightness: int) -> None:
        self.brightness = max(0, min(100, brightness))
    
    @property
    def is_available(self) -> bool:
        return True
    
    @property
    def last_image(self):
        return self._last_image
