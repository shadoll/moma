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
    def bold_green(text: str) -> str:
        """Deprecated: Use [TextFormatter.bold, TextFormatter.green] instead"""
        import warnings
        warnings.warn(
            "TextFormatter.bold_green is deprecated. Use [TextFormatter.bold, TextFormatter.green] instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return f"[bold green]{text}[/bold green]"

    @staticmethod
    def bold_cyan(text: str) -> str:
        """Deprecated: Use [TextFormatter.bold, TextFormatter.cyan] instead"""
        import warnings
        warnings.warn(
            "TextFormatter.bold_cyan is deprecated. Use [TextFormatter.bold, TextFormatter.cyan] instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return f"[bold cyan]{text}[/bold cyan]"

    @staticmethod
    def bold_magenta(text: str) -> str:
        """Deprecated: Use [TextFormatter.bold, TextFormatter.magenta] instead"""
        import warnings
        warnings.warn(
            "TextFormatter.bold_magenta is deprecated. Use [TextFormatter.bold, TextFormatter.magenta] instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return f"[bold magenta]{text}[/bold magenta]"

    @staticmethod
    def bold_yellow(text: str) -> str:
        """Deprecated: Use [TextFormatter.bold, TextFormatter.yellow] instead"""
        import warnings
        warnings.warn(
            "TextFormatter.bold_yellow is deprecated. Use [TextFormatter.bold, TextFormatter.yellow] instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return f"[bold yellow]{text}[/bold yellow]"

    @staticmethod
    def green(text: str) -> str:
        return f"[green]{text}[/green]"

    @staticmethod
    def yellow(text: str) -> str:
        return f"[yellow]{text}[/yellow]"

    @staticmethod
    def orange(text: str) -> str:
        return f"[orange]{text}[/orange]"

    @staticmethod
    def magenta(text: str) -> str:
        return f"[magenta]{text}[/magenta]"

    @staticmethod
    def cyan(text: str) -> str:
        return f"[cyan]{text}[/cyan]"

    @staticmethod
    def red(text: str) -> str:
        return f"[red]{text}[/red]"
    
    @staticmethod
    def blue(text: str) -> str:
        return f"[blue]{text}[/blue]"

    @staticmethod
    def grey(text: str) -> str:
        return f"[grey]{text}[/grey]"

    @staticmethod
    def dim(text: str) -> str:
        return f"[dim]{text}[/dim]"

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