"""ASCII art poster renderer."""

from .base import PosterRenderer
from typing import Any


class AsciiPosterRenderer(PosterRenderer):
    """Render posters as ASCII art using PIL."""

    def render(self, image_path: str, width: int = 35) -> Any:
        """Render poster as ASCII art.

        Args:
            image_path: Path to the poster image
            width: Width in characters (default: 35)

        Returns:
            ASCII art representation of the poster
        """
        is_valid, error_msg = self.validate_image(image_path)
        if not is_valid:
            return error_msg

        is_available, msg = self.is_available()
        if not is_available:
            return msg

        try:
            from PIL import Image, ImageEnhance

            # Open image
            img: Any = Image.open(image_path)

            # Enhance contrast for better detail
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.3)

            # Convert to grayscale and resize
            # Using provided width, height calculated to maintain aspect ratio
            img = img.convert('L').resize((width, width), Image.Resampling.LANCZOS)

            # Extended ASCII characters from darkest to lightest (more gradient levels)
            # Using characters with different visual density for better detail
            ascii_chars = '$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,"^`\'. '

            # Convert to ASCII
            pixels = img.getdata()
            img_width, height = img.size

            ascii_art = []
            for y in range(0, height, 2):  # Skip every other row for aspect ratio correction
                row = []
                for x in range(img_width):
                    # Average of two rows for better aspect ratio
                    pixel1 = pixels[y * img_width + x] if y < height else 255
                    pixel2 = pixels[(y + 1) * img_width + x] if y + 1 < height else 255
                    avg = (pixel1 + pixel2) // 2

                    # Map pixel brightness to character
                    # Invert: 0 (black) -> dark char, 255 (white) -> light char
                    char_index = int((255 - avg) * (len(ascii_chars) - 1) // 255)
                    char = ascii_chars[char_index]
                    row.append(char)
                ascii_art.append(''.join(row))

            return '\n'.join(ascii_art)

        except Exception as e:
            return f"Failed to display image: {e}\nPoster at: {image_path}"

    def is_available(self) -> tuple[bool, str]:
        """Check if PIL is available.

        Returns:
            Tuple of (is_available, message)
        """
        try:
            import PIL
            return True, ""
        except ImportError:
            return False, "PIL not available for ASCII art rendering\nInstall with: pip install Pillow"
