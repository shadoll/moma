"""Extension formatting decorators.

Provides decorator versions of ExtensionFormatter methods.
"""

from functools import wraps
from typing import Callable
from .extension_formatter import ExtensionFormatter


class ExtensionDecorators:
    """Extension formatting decorators."""

    @staticmethod
    def extension_info() -> Callable:
        """Decorator to format extension information."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                result = func(*args, **kwargs)
                if not result:
                    return ""
                return ExtensionFormatter.format_extension_info(result)
            return wrapper
        return decorator


# Singleton instance
extension_decorators = ExtensionDecorators()
