from .text_formatter import TextFormatter
import os


class CatalogFormatter:
    """Formatter for catalog mode display"""

    def __init__(self, extractor, settings=None):
        self.extractor = extractor
        self.settings = settings

    def format_catalog_info(self) -> str:
        """Format catalog information for display"""
        lines = []
        poster_output = None

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

        # Poster - check settings for display mode
        poster_mode = self.settings.get("poster", "no") if self.settings else "no"
        poster_image_path = self.extractor.tmdb_extractor.extract_poster_image_path()

        if poster_mode != "no" and poster_image_path:
            lines.append(f"{TextFormatter.bold('Poster:')}")
            poster_output = self._display_poster(poster_image_path, poster_mode)
        elif poster_mode == "no":
            # Don't show poster at all
            poster_output = None
        else:
            # Poster path not cached yet
            poster_path = self.extractor.get("poster_path", "TMDB")
            if poster_path:
                lines.append(f"{TextFormatter.bold('Poster:')} {poster_path} (not cached yet)")
            poster_output = None

        # Render text content with Rich markup
        text_content = "\n\n".join(lines) if lines else "No catalog information available"

        from rich.console import Console
        from io import StringIO

        console = Console(file=StringIO(), width=120, legacy_windows=False)
        console.print(text_content, markup=True)
        rendered_text = console.file.getvalue()

        # Append poster output if available
        # Don't process ASCII art through console - just append it directly
        if poster_output:
            return rendered_text + "\n" + poster_output
        else:
            return rendered_text

    def _display_poster(self, image_path: str, mode: str) -> str:
        """Display poster image based on mode setting.

        Args:
            image_path: Path to the poster image
            mode: Display mode - "pseudo" for ASCII art, "viu" for viu rendering

        Returns:
            Rendered poster as string
        """
        if not os.path.exists(image_path):
            return f"Image file not found: {image_path}"

        if mode == "viu":
            return self._display_poster_viu(image_path)
        elif mode == "pseudo":
            return self._display_poster_pseudo(image_path)
        else:
            return f"Unknown poster mode: {mode}"

    def _display_poster_viu(self, image_path: str) -> str:
        """Display poster using viu (not working in Textual, only in terminal)"""
        import subprocess
        import shutil

        # Check if viu is available
        if not shutil.which('viu'):
            return f"viu not installed. Install with: cargo install viu\nPoster at: {image_path}"

        try:
            # Run viu to render the image
            # -w 40: width in characters
            # -t: transparent background
            result = subprocess.run(
                ['viu', '-w', '40', '-t', image_path],
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

    def _display_poster_pseudo(self, image_path: str) -> str:
        """Display poster image using ASCII art (pseudo graphics)"""
        try:
            from PIL import Image, ImageEnhance

            # Open image
            img = Image.open(image_path)

            # Enhance contrast for better detail
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.3)

            # Convert to grayscale and resize
            # Compact size for ASCII art (35x35 -> 35x17 after row averaging)
            img = img.convert('L').resize((35, 35), Image.Resampling.LANCZOS)

            # Extended ASCII characters from darkest to lightest (more gradient levels)
            # Using characters with different visual density for better detail
            ascii_chars = '$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,"^`\'. '

            # Convert to ASCII
            pixels = img.getdata()
            width, height = img.size

            ascii_art = []
            for y in range(0, height, 2):  # Skip every other row for aspect ratio correction
                row = []
                for x in range(width):
                    # Average of two rows for better aspect ratio
                    pixel1 = pixels[y * width + x] if y < height else 255
                    pixel2 = pixels[(y + 1) * width + x] if y + 1 < height else 255
                    avg = (pixel1 + pixel2) // 2

                    # Map pixel brightness to character
                    # Invert: 0 (black) -> dark char, 255 (white) -> light char
                    char_index = (255 - avg) * (len(ascii_chars) - 1) // 255
                    char = ascii_chars[char_index]
                    row.append(char)
                ascii_art.append(''.join(row))

            return '\n'.join(ascii_art)

        except ImportError:
            return f"PIL not available for pseudo graphics\nPoster at: {image_path}"
        except Exception as e:
            return f"Failed to display image: {e}\nPoster at: {image_path}"