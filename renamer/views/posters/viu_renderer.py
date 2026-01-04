"""Viu terminal image viewer renderer."""

import subprocess
import shutil
from .base import PosterRenderer


class ViuPosterRenderer(PosterRenderer):
    """Render posters using viu terminal image viewer."""

    def render(self, image_path: str, width: int = 40) -> str:
        """Render poster using viu.

        Args:
            image_path: Path to the poster image
            width: Width in characters (default: 40)

        Returns:
            Viu-rendered image with ANSI escape sequences
        """
        is_valid, error_msg = self.validate_image(image_path)
        if not is_valid:
            return error_msg

        is_available, msg = self.is_available()
        if not is_available:
            return msg

        try:
            # Run viu to render the image
            # -w <width>: width in characters
            # -t: transparent background
            result = subprocess.run(
                ['viu', '-w', str(width), '-t', image_path],
                capture_output=True,
                check=True
            )
            # Decode bytes output, preserving ANSI escape sequences
            return result.stdout.decode('utf-8', errors='replace')

        except subprocess.CalledProcessError as e:
            stderr_msg = e.stderr.decode('utf-8', errors='replace') if e.stderr else 'Unknown error'
            return f"Failed to render image with viu: {stderr_msg}\nPoster at: {image_path}"
        except Exception as e:
            return f"Failed to display image: {e}\nPoster at: {image_path}"

    def is_available(self) -> tuple[bool, str]:
        """Check if viu is installed.

        Returns:
            Tuple of (is_available, message)
        """
        if shutil.which('viu'):
            return True, ""
        return False, "viu not installed. Install with: cargo install viu"
