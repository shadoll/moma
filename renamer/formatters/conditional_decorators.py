"""Conditional formatting decorators.

Provides decorators for conditional formatting (wrap, replace_slashes, default):

    @conditional_decorators.wrap("[", "]")
    def get_order(self):
        return self.extractor.get('order')
"""

from functools import wraps
from typing import Callable, Any


class ConditionalDecorators:
    """Conditional formatting decorators (wrap, replace_slashes, default)."""

    @staticmethod
    def wrap(left: str, right: str = "") -> Callable:
        """Decorator to wrap value with delimiters if it exists.

        Can be used for prefix-only (right=""), suffix-only (left=""), or both.

        Usage:
            @conditional_decorators.wrap("[", "]")
            def get_order(self):
                return self.extractor.get('order')

            # Prefix only
            @conditional_decorators.wrap(" ")
            def get_source(self):
                return self.extractor.get('source')

            # Suffix only
            @conditional_decorators.wrap("", ",")
            def get_hdr(self):
                return self.extractor.get('hdr')
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> str:
                result = func(*args, **kwargs)
                return f"{left}{result}{right}" if result else ""
            return wrapper
        return decorator

    @staticmethod
    def replace_slashes() -> Callable:
        """Decorator to replace forward and back slashes with dashes.

        Usage:
            @conditional_decorators.replace_slashes()
            def get_title(self):
                return self.extractor.get('title')
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> str:
                result = func(*args, **kwargs)
                if result:
                    return str(result).replace("/", "-").replace("\\", "-")
                return result or ""
            return wrapper
        return decorator

    @staticmethod
    def default(default_value: Any) -> Callable:
        """Decorator to provide a default value if result is None or empty.

        NOTE: It's better to handle defaults in the extractor itself rather than
        using this decorator. This decorator should only be used when the extractor
        cannot provide a sensible default.

        Usage:
            @conditional_decorators.default("Unknown")
            def get_value(self):
                return self.extractor.get('value')
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                result = func(*args, **kwargs)
                return result if result else default_value
            return wrapper
        return decorator


# Singleton instance
conditional_decorators = ConditionalDecorators()
