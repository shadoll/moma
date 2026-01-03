"""Resolution formatting decorators.

Provides decorator versions of ResolutionFormatter methods.
"""

from functools import wraps
from typing import Callable
from .resolution_formatter import ResolutionFormatter


class ResolutionDecorators:
    """Resolution formatting decorators."""

    @staticmethod
    def resolution_dimensions() -> Callable:
        """Decorator to format resolution as dimensions (WxH)."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                result = func(*args, **kwargs)
                if not result:
                    return ""
                return ResolutionFormatter.format_resolution_dimensions(result)
            return wrapper
        return decorator


# Singleton instance
resolution_decorators = ResolutionDecorators()
