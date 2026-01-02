"""Special info formatting decorators.

Provides decorator versions of SpecialInfoFormatter methods:

    @special_info_decorators.special_info()
    def get_special_info(self):
        return self.extractor.get('special_info')
"""

from functools import wraps
from typing import Callable
from .special_info_formatter import SpecialInfoFormatter


class SpecialInfoDecorators:
    """Special info and database formatting decorators."""

    @staticmethod
    def special_info() -> Callable:
        """Decorator to format special info lists.

        Usage:
            @special_info_decorators.special_info()
            def get_special_info(self):
                return self.extractor.get('special_info')
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> str:
                result = func(*args, **kwargs)
                return SpecialInfoFormatter.format_special_info(result)
            return wrapper
        return decorator

    @staticmethod
    def database_info() -> Callable:
        """Decorator to format database info.

        Usage:
            @special_info_decorators.database_info()
            def get_db_info(self):
                return self.extractor.get('movie_db')
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> str:
                result = func(*args, **kwargs)
                return SpecialInfoFormatter.format_database_info(result)
            return wrapper
        return decorator


# Singleton instance
special_info_decorators = SpecialInfoDecorators()
