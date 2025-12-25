class ColorFormatter:
    """Class for formatting text with colors using Textual markup"""

    @staticmethod
    def bold_blue(text: str) -> str:
        return f"[bold blue]{text}[/bold blue]"

    @staticmethod
    def bold_green(text: str) -> str:
        return f"[bold green]{text}[/bold green]"

    @staticmethod
    def bold_cyan(text: str) -> str:
        return f"[bold cyan]{text}[/bold cyan]"

    @staticmethod
    def bold_magenta(text: str) -> str:
        return f"[bold magenta]{text}[/bold magenta]"

    @staticmethod
    def bold_yellow(text: str) -> str:
        return f"[bold yellow]{text}[/bold yellow]"

    @staticmethod
    def bold_red(text: str) -> str:
        return f"[bold red]{text}[/bold red]"

    @staticmethod
    def green(text: str) -> str:
        return f"[green]{text}[/green]"

    @staticmethod
    def yellow(text: str) -> str:
        return f"[yellow]{text}[/yellow]"

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
    def grey(text: str) -> str:
        return f"[grey]{text}[/grey]"

    @staticmethod
    def dim(text: str) -> str:
        return f"[dim]{text}[/dim]"