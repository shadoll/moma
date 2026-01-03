"""Size formatting decorators.

Provides decorator versions of SizeFormatter methods.
"""

from functools import wraps
from typing import Callable
from .size_formatter import SizeFormatter


class SizeDecorators:
    """Size formatting decorators."""

    @staticmethod
    def size_full() -> Callable:
        """Decorator to format file size in full format."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                result = func(*args, **kwargs)
                if result is None:
                    return ""
                return SizeFormatter.format_size_full(result)
            return wrapper
        return decorator

    @staticmethod
    def size_short() -> Callable:
        """Decorator to format file size in short format."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                result = func(*args, **kwargs)
                if result is None:
                    return ""
                return SizeFormatter.format_size_short(result)
            return wrapper
        return decorator


# Singleton instance
size_decorators = SizeDecorators()
