"""Duration formatting decorators.

Provides decorator versions of DurationFormatter methods.
"""

from functools import wraps
from typing import Callable
from .duration_formatter import DurationFormatter


class DurationDecorators:
    """Duration formatting decorators."""

    @staticmethod
    def duration_full() -> Callable:
        """Decorator to format duration in full format (HH:MM:SS)."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                result = func(*args, **kwargs)
                if not result:
                    return ""
                return DurationFormatter.format_full(result)
            return wrapper
        return decorator

    @staticmethod
    def duration_short() -> Callable:
        """Decorator to format duration in short format."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                result = func(*args, **kwargs)
                if not result:
                    return ""
                return DurationFormatter.format_short(result)
            return wrapper
        return decorator


# Singleton instance
duration_decorators = DurationDecorators()
