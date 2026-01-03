"""Text formatting decorators.

Provides decorator versions of TextFormatter methods:

    @text_decorators.bold()
    def get_title(self):
        return self.title
"""

from functools import wraps
from typing import Callable
from .text_formatter import TextFormatter


class TextDecorators:
    """Text styling and color decorators."""

    @staticmethod
    def bold() -> Callable:
        """Decorator to make text bold."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> str:
                result = func(*args, **kwargs)
                if result == "":
                    return ""
                return TextFormatter.bold(str(result))
            return wrapper
        return decorator

    @staticmethod
    def italic() -> Callable:
        """Decorator to make text italic."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> str:
                result = func(*args, **kwargs)
                if result == "":
                    return ""
                return TextFormatter.italic(str(result))
            return wrapper
        return decorator

    @staticmethod
    def green() -> Callable:
        """Decorator to color text green."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> str:
                result = func(*args, **kwargs)
                if result == "":
                    return ""
                return TextFormatter.green(str(result))
            return wrapper
        return decorator

    @staticmethod
    def yellow() -> Callable:
        """Decorator to color text yellow."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> str:
                result = func(*args, **kwargs)
                if not result:
                    return ""
                return TextFormatter.yellow(str(result))
            return wrapper
        return decorator

    @staticmethod
    def cyan() -> Callable:
        """Decorator to color text cyan."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> str:
                result = func(*args, **kwargs)
                if not result:
                    return ""
                return TextFormatter.cyan(str(result))
            return wrapper
        return decorator

    @staticmethod
    def magenta() -> Callable:
        """Decorator to color text magenta."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> str:
                result = func(*args, **kwargs)
                if not result:
                    return ""
                return TextFormatter.magenta(str(result))
            return wrapper
        return decorator

    @staticmethod
    def red() -> Callable:
        """Decorator to color text red."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> str:
                result = func(*args, **kwargs)
                if not result:
                    return ""
                return TextFormatter.red(str(result))
            return wrapper
        return decorator

    @staticmethod
    def orange() -> Callable:
        """Decorator to color text orange."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> str:
                result = func(*args, **kwargs)
                if not result:
                    return ""
                return TextFormatter.orange(str(result))
            return wrapper
        return decorator

    @staticmethod
    def blue() -> Callable:
        """Decorator to color text blue."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> str:
                result = func(*args, **kwargs)
                if not result:
                    return ""
                return TextFormatter.blue(str(result))
            return wrapper
        return decorator

    @staticmethod
    def grey() -> Callable:
        """Decorator to color text grey."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> str:
                result = func(*args, **kwargs)
                if not result:
                    return ""
                return TextFormatter.grey(str(result))
            return wrapper
        return decorator

    @staticmethod
    def uppercase() -> Callable:
        """Decorator to convert text to uppercase."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> str:
                result = func(*args, **kwargs)
                if not result:
                    return ""
                return TextFormatter.uppercase(str(result))
            return wrapper
        return decorator

    @staticmethod
    def lowercase() -> Callable:
        """Decorator to convert text to lowercase."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> str:
                result = func(*args, **kwargs)
                if not result:
                    return ""
                return TextFormatter.lowercase(str(result))
            return wrapper
        return decorator

    @staticmethod
    def url() -> Callable:
        """Decorator to format text as a clickable URL."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> str:
                result = func(*args, **kwargs)
                if not result:
                    return ""
                return TextFormatter.format_url(str(result))
            return wrapper
        return decorator

    @staticmethod
    def escape() -> Callable:
        """Decorator to escape rich markup in text."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> str:
                from rich.markup import escape
                result = func(*args, **kwargs)
                if not result:
                    return ""
                return escape(str(result))
            return wrapper
        return decorator


# Singleton instance
text_decorators = TextDecorators()
