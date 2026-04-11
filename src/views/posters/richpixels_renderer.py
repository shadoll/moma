"""Rich-pixels renderer for high-quality terminal image display."""

from .base import PosterRenderer
from typing import Union


class RichPixelsPosterRenderer(PosterRenderer):
    """Render posters using rich-pixels library for high-quality display."""

    def render(self, image_path: str, width: int = 40) -> Union[str, object]:
        """Render poster using rich-pixels.

        Args:
            image_path: Path to the poster image
            width: Width in characters (default: 40)

        Returns:
            Rich Pixels object (Renderable) or error string
        """
        is_valid, error_msg = self.validate_image(image_path)
        if not is_valid:
            return error_msg

        is_available, msg = self.is_available()
        if not is_available:
            return msg

        try:
            from rich_pixels import Pixels

            # Create a Pixels object from the image
            # Return the Pixels object directly - it's a Rich Renderable
            # that Textual can display natively
            pixels = Pixels.from_image_path(image_path, resize=(width * 2, width * 2))

            return pixels

        except Exception as e:
            return f"Failed to display image with rich-pixels: {e}\nPoster at: {image_path}"

    def is_available(self) -> tuple[bool, str]:
        """Check if rich-pixels is installed.

        Returns:
            Tuple of (is_available, message)
        """
        try:
            import rich_pixels
            return True, ""
        except ImportError:
            return False, "rich-pixels not installed. Install with: pip install rich-pixels"
