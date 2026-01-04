from .text_formatter import TextFormatter
from renamer.views.posters import AsciiPosterRenderer, ViuPosterRenderer, RichPixelsPosterRenderer
from typing import Union
import os


class CatalogFormatter:
    """Formatter for catalog mode display"""

    def __init__(self, extractor, settings=None):
        self.extractor = extractor
        self.settings = settings

    def format_catalog_info(self) -> tuple[str, Union[str, object]]:
        """Format catalog information for display.

        Returns:
            Tuple of (info_text, poster_content)
            poster_content can be a string or Rich Renderable object
        """
        lines = []

        # Title
        title = self.extractor.get("title", "TMDB")
        if title:
            lines.append(f"{TextFormatter.bold('Title:')} {title}")

        # Year
        year = self.extractor.get("year", "TMDB")
        if year:
            lines.append(f"{TextFormatter.bold('Year:')} {year}")

        # Duration
        duration = self.extractor.get("duration", "TMDB")
        if duration:
            lines.append(f"{TextFormatter.bold('Duration:')} {duration} minutes")

        # Rates
        popularity = self.extractor.get("popularity", "TMDB")
        vote_average = self.extractor.get("vote_average", "TMDB")
        if popularity or vote_average:
            rates = []
            if popularity:
                rates.append(f"Popularity: {popularity}")
            if vote_average:
                rates.append(f"Rating: {vote_average}/10")
            lines.append(f"{TextFormatter.bold('Rates:')} {', '.join(rates)}")

        # Overview
        overview = self.extractor.get("overview", "TMDB")
        if overview:
            lines.append(f"{TextFormatter.bold('Overview:')}")
            lines.append(overview)

        # Genres
        genres = self.extractor.get("genres", "TMDB")
        if genres:
            lines.append(f"{TextFormatter.bold('Genres:')} {genres}")

        # Countries
        countries = self.extractor.get("production_countries", "TMDB")
        if countries:
            lines.append(f"{TextFormatter.bold('Countries:')} {countries}")

        # Render text content with Rich markup
        text_content = "\n\n".join(lines) if lines else "No catalog information available"

        from rich.console import Console
        from io import StringIO

        console = Console(file=StringIO(), width=120, legacy_windows=False)
        console.print(text_content, markup=True)
        rendered_text = console.file.getvalue()

        # Get poster separately
        poster_content = self.get_poster()

        return rendered_text, poster_content

    def get_poster(self) -> Union[str, object]:
        """Get poster content for separate display.

        Returns:
            Poster content (string or Rich Renderable) or empty string if no poster
        """
        poster_mode = self.settings.get("poster", "no") if self.settings else "no"

        if poster_mode == "no":
            return ""

        poster_image_path = self.extractor.tmdb_extractor.extract_poster_image_path()

        if poster_image_path:
            return self._display_poster(poster_image_path, poster_mode)
        else:
            # Poster path not cached yet
            poster_path = self.extractor.get("poster_path", "TMDB")
            if poster_path:
                return f"{TextFormatter.bold('Poster:')} {poster_path} (not cached yet)"
            return ""

    def _display_poster(self, image_path: str, mode: str) -> Union[str, object]:
        """Display poster image based on mode setting.

        Args:
            image_path: Path to the poster image
            mode: Display mode - "pseudo" for ASCII art, "viu", "richpixels"

        Returns:
            Rendered poster (string or Rich Renderable object)
        """
        if not os.path.exists(image_path):
            return f"Image file not found: {image_path}"

        # Select renderer based on mode
        if mode == "viu":
            renderer = ViuPosterRenderer()
        elif mode == "pseudo":
            renderer = AsciiPosterRenderer()
        elif mode == "richpixels":
            renderer = RichPixelsPosterRenderer()
        else:
            return f"Unknown poster mode: {mode}"

        # Render the poster
        return renderer.render(image_path, width=40)