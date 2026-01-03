from .text_formatter import TextFormatter
import os


class CatalogFormatter:
    """Formatter for catalog mode display"""

    def __init__(self, extractor):
        self.extractor = extractor

    def format_catalog_info(self) -> str:
        """Format catalog information for display"""
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

        # Poster
        poster_image_path = self.extractor.tmdb_extractor.extract_poster_image_path()
        if poster_image_path:
            lines.append(f"{TextFormatter.bold('Poster:')}")
            lines.append(self._display_poster(poster_image_path))
        else:
            poster_path = self.extractor.get("poster_path", "TMDB")
            if poster_path:
                lines.append(f"{TextFormatter.bold('Poster:')} {poster_path} (not cached yet)")

        full_text = "\n\n".join(lines) if lines else "No catalog information available"
        
        # Render markup to ANSI
        from rich.console import Console
        from io import StringIO
        console = Console(file=StringIO(), width=120, legacy_windows=False)
        console.print(full_text, markup=True)
        return console.file.getvalue()

    def _display_poster(self, image_path: str) -> str:
        """Display poster image in terminal using simple ASCII art"""
        try:
            from PIL import Image
            import os
            
            if not os.path.exists(image_path):
                return f"Image file not found: {image_path}"
            
            # Open and resize image
            img = Image.open(image_path).convert('L').resize((80, 40), Image.Resampling.LANCZOS)
            
            # ASCII characters from dark to light
            ascii_chars = '@%#*+=-:. '
            
            # Convert to ASCII
            pixels = img.getdata()
            width, height = img.size
            
            ascii_art = []
            for y in range(0, height, 2):  # Skip every other row for aspect ratio
                row = []
                for x in range(width):
                    # Average of two rows for better aspect
                    pixel1 = pixels[y * width + x] if y < height else 255
                    pixel2 = pixels[(y + 1) * width + x] if y + 1 < height else 255
                    avg = (pixel1 + pixel2) // 2
                    char = ascii_chars[avg * len(ascii_chars) // 256]
                    row.append(char)
                ascii_art.append(''.join(row))
            
            return '\n'.join(ascii_art)
            
        except ImportError:
            return f"Image at {image_path} (PIL not available)"
        except Exception as e:
            return f"Failed to display image at {image_path}: {e}"