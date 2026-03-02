"""Reusable UI components for display."""

import os
from typing import Optional, Tuple

from PIL import Image, ImageDraw, ImageFont


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
BLUE = (0, 100, 255)
YELLOW = (255, 200, 0)
GREEN = (0, 180, 0)
RED = (200, 0, 0)


class DisplayCanvas:
    """Canvas for drawing UI elements."""
    
    def __init__(self, width: int, height: int, background: Tuple[int, int, int] = WHITE):
        """Initialize canvas.
        
        Args:
            width: Canvas width in pixels.
            height: Canvas height in pixels.
            background: Background color as RGB tuple.
        """
        self.width = width
        self.height = height
        self.image = Image.new("RGB", (width, height), background)
        self.draw = ImageDraw.Draw(self.image)
    
    def get_image(self) -> Image.Image:
        """Get the final image."""
        return self.image
    
    def rectangle(
        self,
        xy: Tuple[int, int, int, int],
        fill: Optional[Tuple[int, int, int]] = None,
        outline: Optional[Tuple[int, int, int]] = None,
        width: int = 1
    ) -> None:
        """Draw a rectangle."""
        self.draw.rectangle(xy, fill=fill, outline=outline, width=width)
    
    def text(
        self,
        xy: Tuple[int, int],
        text: str,
        font: ImageFont,
        fill: Tuple[int, int, int] = BLACK,
        anchor: str = "lt"
    ) -> None:
        """Draw text at position."""
        self.draw.text(xy, text, font=font, fill=fill, anchor=anchor)
    
    def centered_text(
        self,
        y: int,
        text: str,
        font: ImageFont,
        fill: Tuple[int, int, int] = BLACK
    ) -> None:
        """Draw centered text."""
        bbox = self.draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        x = (self.width - text_width) // 2
        self.draw.text((x, y), text, font=font, fill=fill)
    
    def image_at(
        self,
        xy: Tuple[int, int],
        image: Image.Image,
        anchor: str = "lt"
    ) -> None:
        """Paste an image at position."""
        self.image.paste(image, xy)


class TextElement:
    """Text display element."""
    
    def __init__(
        self,
        x: int,
        y: int,
        font: ImageFont,
        color: Tuple[int, int, int] = BLACK
    ):
        self.x = x
        self.y = y
        self.font = font
        self.color = color
        self._text = ""
    
    def set_text(self, text: str) -> None:
        self._text = text
    
    def render(self, canvas: DisplayCanvas) -> None:
        canvas.text((self.x, self.y), self._text, self.font, self.color)


class IconElement:
    """Icon display element."""
    
    def __init__(self, x: int, y: int, size: int = 48):
        self.x = x
        self.y = y
        self.size = size
        self._image: Optional[Image.Image] = None
    
    def set_icon(self, image: Image.Image) -> None:
        # Resize icon to expected size
        self._image = image.resize((self.size, self.size), Image.Resampling.LANCZOS)
    
    def render(self, canvas: DisplayCanvas) -> None:
        if self._image:
            canvas.image_at((self.x, self.y), self._image)


class ProgressBar:
    """Simple progress bar element."""
    
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int = 8,
        fill_color: Tuple[int, int, int] = BLUE,
        bg_color: Tuple[int, int, int] = LIGHT_GRAY
    ):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.fill_color = fill_color
        self.bg_color = bg_color
        self._progress = 0.0
    
    def set_progress(self, progress: float) -> None:
        self._progress = max(0.0, min(1.0, progress))
    
    def render(self, canvas: DisplayCanvas) -> None:
        # Background
        canvas.rectangle(
            (self.x, self.y, self.x + self.width, self.y + self.height),
            fill=self.bg_color
        )
        
        # Fill
        if self._progress > 0:
            fill_width = int(self.width * self._progress)
            canvas.rectangle(
                (self.x, self.y, self.x + fill_width, self.y + self.height),
                fill=self.fill_color
            )
