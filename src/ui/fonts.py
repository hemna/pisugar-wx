"""Font utilities for display rendering."""

import os
from typing import Optional

from PIL import ImageFont


DEFAULT_FONT_SIZE = 16
LARGE_FONT_SIZE = 36
SMALL_FONT_SIZE = 12


class FontLoader:
    """Manages font loading for display."""
    
    def __init__(self, font_path: Optional[str] = None):
        """Initialize font loader.
        
        Args:
            font_path: Path to font directory. Uses default if None.
        """
        if font_path is None:
            # Try common font locations
            font_path = self._find_default_font_path()
        
        self.font_path = font_path
    
    def _find_default_font_path(self) -> Optional[str]:
        """Find default font path."""
        # Check for bundled fonts
        paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        ]
        
        for path in paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def get_font(self, size: int = DEFAULT_FONT_SIZE) -> ImageFont.FreeTypeFont:
        """Load font at specified size.
        
        Args:
            size: Font size in points.
            
        Returns:
            PIL ImageFont.
        """
        if self.font_path and os.path.exists(self.font_path):
            return ImageFont.truetype(self.font_path, size)
        
        # Fall back to default font
        return ImageFont.load_default()
    
    def get_large_font(self) -> ImageFont.FreeTypeFont:
        """Get large font for temperature display."""
        return self.get_font(LARGE_FONT_SIZE)
    
    def get_default_font(self) -> ImageFont.FreeTypeFont:
        """Get default font for regular text."""
        return self.get_font(DEFAULT_FONT_SIZE)
    
    def get_small_font(self) -> ImageFont.FreeTypeFont:
        """Get small font for labels."""
        return self.get_font(SMALL_FONT_SIZE)
