"""Date formatting decorators.

Provides decorator versions of DateFormatter methods for cleaner code:

    @date_decorators.year()
    def get_year(self):
        return self.extractor.get('year')
"""

from functools import wraps
from typing import Callable
from .date_formatter import DateFormatter


class DateDecorators:
    """Date and time formatting decorators."""

    @staticmethod
    def modification_date() -> Callable:
        """Decorator to format modification dates.

        Usage:
            @date_decorators.modification_date()
            def get_mtime(self):
                return self.file_path.stat().st_mtime
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> str:
                result = func(*args, **kwargs)
                return DateFormatter.format_modification_date(result)
            return wrapper
        return decorator


# Singleton instance
date_decorators = DateDecorators()
