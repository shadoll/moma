"""Poster rendering views.

This package provides different rendering engines for movie posters:
- ASCII art (pseudo graphics)
- viu (terminal image viewer)
- rich-pixels (Rich library integration)
"""

from .base import PosterRenderer
from .ascii_renderer import AsciiPosterRenderer
from .viu_renderer import ViuPosterRenderer
from .richpixels_renderer import RichPixelsPosterRenderer

__all__ = [
    'PosterRenderer',
    'AsciiPosterRenderer',
    'ViuPosterRenderer',
    'RichPixelsPosterRenderer',
]
