"""Base class for poster renderers."""

from abc import ABC, abstractmethod
from typing import Any
import os


class PosterRenderer(ABC):
    """Abstract base class for poster rendering implementations."""

    @abstractmethod
    def render(self, image_path: str, width: int = 40) -> Any:
        """Render a poster image.

        Args:
            image_path: Path to the poster image file
            width: Desired width in characters

        Returns:
            Rendered poster as a string or Rich Renderable
        """
        pass

    def validate_image(self, image_path: str) -> tuple[bool, str]:
        """Validate that image file exists.

        Args:
            image_path: Path to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not os.path.exists(image_path):
            return False, f"Image file not found: {image_path}"
        return True, ""

    @abstractmethod
    def is_available(self) -> tuple[bool, str]:
        """Check if this renderer is available on the system.

        Returns:
            Tuple of (is_available, message)
        """
        pass
