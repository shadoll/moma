"""Custom widget for rendering poster images."""

from textual.widget import Widget
from textual.widgets import Static
from rich.console import RenderableType
from typing import Union


class PosterWidget(Static):
    """Widget optimized for displaying poster images with Rich renderables.

    This widget properly handles both string content and Rich renderables
    (like Pixels from rich-pixels) without escaping or markup processing.
    """

    def __init__(self, *args, **kwargs):
        """Initialize poster widget with markup disabled."""
        # Force markup=False to prevent text processing
        kwargs['markup'] = False
        super().__init__(*args, **kwargs)

    def update_poster(self, renderable: Union[str, RenderableType]) -> None:
        """Update poster display with new content.

        Args:
            renderable: String or Rich Renderable object to display
        """
        # Directly update with the renderable - Textual handles Rich renderables natively
        self.update(renderable if renderable else "")
