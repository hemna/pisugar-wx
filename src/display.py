"""Display driver for PiSugar Whisplay HAT using WhisPlayBoard."""

import logging
import os
import sys

# Add WhisPlay driver to path
whisplay_driver_path = os.path.expanduser("~/Whisplay/Driver")
if os.path.exists(whisplay_driver_path):
    sys.path.insert(0, whisplay_driver_path)

logger = logging.getLogger(__name__)

try:
    from WhisPlay import WhisPlayBoard
    WHISPLAY_AVAILABLE = True
except ImportError as e:
    WHISPLAY_AVAILABLE = False
    logger.error(f"WhisPlay import failed: {e}")


class Display:
    """WhisPlay display controller for PiSugar Whisplay HAT."""
    
    def __init__(
        self,
        width: int = 240,
        height: int = 280,
        rotation: int = 0,
        brightness: int = 100
    ):
        self.width = width
        self.height = height
        self.rotation = rotation
        self.brightness = brightness
        self._board = None
        
        if WHISPLAY_AVAILABLE:
            try:
                self._initialize_display()
            except Exception as e:
                logger.error(f"Failed to initialize display: {e}")
                self._board = None
        else:
            logger.warning("WhisPlay library not available")
    
    def _initialize_display(self) -> None:
        """Initialize the WhisPlay display."""
        self._board = WhisPlayBoard()
        self._board.set_backlight(self.brightness)
        logger.info("Display initialized successfully")
    
    def show_image(self, image) -> None:
        """Display an image on the screen.
        
        Args:
            image: PIL Image to display.
        """
        if self._board is None:
            logger.warning("Display not available")
            return
        
        try:
            # Resize image to display size if needed
            if image.size != (self.width, self.height):
                image = image.resize((self.width, self.height))
            
            # Convert PIL image to RGB565 format for WhisPlay
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convert RGB to RGB565 (16-bit color) as byte array
            # WhisPlayBoard expects two bytes per pixel (high byte, low byte)
            pixels = list(image.getdata())
            rgb565_data = []
            for r, g, b in pixels:
                # Convert 8-bit RGB to RGB565 format (matches working example)
                rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
                # Append as two bytes (high byte first, then low byte)
                rgb565_data.extend([(rgb565 >> 8) & 0xFF, rgb565 & 0xFF])
            
            # Display using WhisPlay
            self._board.draw_image(0, 0, self.width, self.height, rgb565_data)
            logger.debug("Image displayed")
        except Exception as e:
            logger.error(f"Failed to show image: {e}")
    
    def clear(self) -> None:
        """Clear the display."""
        if self._board:
            self._board.fill_screen(0)
    
    def set_brightness(self, brightness: int) -> None:
        """Set display brightness.
        
        Args:
            brightness: Brightness level (0-100).
        """
        self.brightness = max(0, min(100, brightness))
        
        if self._board:
            self._board.set_backlight(self.brightness)
    
    @property
    def is_available(self) -> bool:
        """Check if display is available."""
        return self._board is not None

    @property
    def board(self):
        """Get the underlying WhisPlayBoard instance.
        
        Returns:
            WhisPlayBoard instance or None if not available.
        """
        return self._board


class MockDisplay:
    """Mock display for testing without hardware."""
    
    def __init__(self, width: int = 240, height: int = 280):
        self.width = width
        self.height = height
        self.brightness = 100
        logger.info("Mock display initialized")
    
    def show_image(self, image) -> None:
        logger.debug("Mock display: image received")
    
    def clear(self) -> None:
        pass
    
    def set_brightness(self, brightness: int) -> None:
        self.brightness = brightness
    
    @property
    def is_available(self) -> bool:
        return True

    @property
    def board(self):
        """Mock display has no board.
        
        Returns:
            None (no hardware board available).
        """
        return None
