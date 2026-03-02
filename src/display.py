"""Display driver for ST7789-based displays."""

import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)

try:
    import ST7789
    import RPi.GPIO as GPIO
    DISPLAY_AVAILABLE = True
except ImportError as e:
    DISPLAY_AVAILABLE = False
    logger.error(f"Display import failed: {e}")


class Display:
    """ST7789 display controller for PiSugar Whisplay HAT."""
    
    def __init__(
        self,
        width: int = 240,
        height: int = 280,
        rotation: int = 0,
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
        import time
        
        # First, manually control backlight to ensure display is lit
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(18, GPIO.OUT)
        GPIO.output(18, GPIO.HIGH)  # Turn on backlight
        
        # Reset the display
        GPIO.setup(27, GPIO.OUT)
        GPIO.output(27, GPIO.LOW)
        time.sleep(0.1)
        GPIO.output(27, GPIO.HIGH)
        time.sleep(0.2)
        
        try:
            self._display = ST7789.ST7789(
                port=0,
                cs=0,
                dc=25,
                rst=27,
                width=self.width,
                height=self.height,
                rotation=self.rotation
            )
            logger.info("Display initialized successfully")
        except Exception as e:
            logger.error(f"ST7789 init failed: {e}")
            # Try without reset pin
            self._display = ST7789.ST7789(
                port=0,
                cs=0,
                dc=25,
                rst=None,
                width=self.width,
                height=self.height,
                rotation=self.rotation
            )
            logger.info("Display initialized (no reset)")
    
    def show_image(self, image) -> None:
        """Display an image on the screen.
        
        Args:
            image: PIL Image to display.
        """
        if self._display is None:
            logger.warning("Display not available")
            return
        
        try:
            from PIL import Image
            
            # Convert image to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            logger.info(f"Displaying image size: {image.size}")
            
            # First, show a solid color test
            solid_color = Image.new('RGB', (self.width, self.height), (255, 0, 0))  # Red
            self._display.display(solid_color)
            time.sleep(1)
            
            solid_color = Image.new('RGB', (self.width, self.height), (0, 255, 0))  # Green
            self._display.display(solid_color)
            time.sleep(1)
            
            solid_color = Image.new('RGB', (self.width, self.height), (0, 0, 255))  # Blue
            self._display.display(solid_color)
            time.sleep(1)
            
            # Now show the actual image
            self._display.display(image)
            
            logger.info("Image displayed successfully")
        except Exception as e:
            import traceback
            logger.error(f"Failed to show image: {e}")
            logger.error(traceback.format_exc())
    
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
