class TextFormatter:
    """Class for formatting text with colors and styles using Textual markup"""

    @staticmethod
    def bold(text: str) -> str:
        return f"[bold]{text}[/bold]"

    @staticmethod
    def italic(text: str) -> str:
        return f"[italic]{text}[/italic]"

    @staticmethod
    def underline(text: str) -> str:
        return f"[underline]{text}[/underline]"

    @staticmethod
    def uppercase(text: str) -> str:
        return text.upper()

    @staticmethod
    def lowercase(text: str) -> str:
        return text.lower()

    @staticmethod
    def camelcase(text: str) -> str:
        """Convert text to CamelCase (first letter of each word capitalized)"""
        return ''.join(word.capitalize() for word in text.split())

    @staticmethod
    def colour(colour_name: str, text: str) -> str:
        """Generic method to color text with given colour name."""
        return f"[{colour_name}]{text}[/{colour_name}]"

    @staticmethod
    def green(text: str) -> str:
        return TextFormatter.colour("green", text)

    @staticmethod
    def yellow(text: str) -> str:
        return TextFormatter.colour("yellow", text)

    @staticmethod
    def orange(text: str) -> str:
        return TextFormatter.colour("orange", text)

    @staticmethod
    def magenta(text: str) -> str:
        return TextFormatter.colour("magenta", text)

    @staticmethod
    def cyan(text: str) -> str:
        return TextFormatter.colour("cyan", text)

    @staticmethod
    def red(text: str) -> str:
        return TextFormatter.colour("red", text)

    @staticmethod
    def blue(text: str) -> str:
        return TextFormatter.colour("blue", text)

    @staticmethod
    def grey(text: str) -> str:
        return TextFormatter.colour("grey", text)

    @staticmethod
    def dim(text: str) -> str:
        return TextFormatter.colour("dimgray", text)

    @staticmethod
    def link(url: str, text: str | None = None) -> str:
        """Create a clickable link. If text is None, uses the URL as text."""
        if text is None:
            text = url
        return f"[link={url}]{text}[/link]"

    @staticmethod
    def format_url(url: str) -> str:
        """Format a URL as a clickable link using OSC 8 if it's a valid URL, otherwise return as-is."""
        if url and url != "<None>" and url.startswith("http"):
            # Use OSC 8 hyperlink escape sequence for clickable links
            return f"\x1b]8;;{url}\x1b\\Open in TMDB\x1b]8;;\x1b\\"
        return url
