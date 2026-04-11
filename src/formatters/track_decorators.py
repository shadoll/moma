"""Track formatting decorators.

Provides decorator versions of TrackFormatter methods.
"""

from functools import wraps
from typing import Callable
from .track_formatter import TrackFormatter


class TrackDecorators:
    """Track formatting decorators."""

    @staticmethod
    def video_track() -> Callable:
        """Decorator to format video track data."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                result = func(*args, **kwargs)
                if not result:
                    return ""
                return TrackFormatter.format_video_track(result)
            return wrapper
        return decorator

    @staticmethod
    def audio_track() -> Callable:
        """Decorator to format audio track data."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                result = func(*args, **kwargs)
                if not result:
                    return ""
                return TrackFormatter.format_audio_track(result)
            return wrapper
        return decorator

    @staticmethod
    def subtitle_track() -> Callable:
        """Decorator to format subtitle track data."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                result = func(*args, **kwargs)
                if not result:
                    return ""
                return TrackFormatter.format_subtitle_track(result)
            return wrapper
        return decorator


# Singleton instance
track_decorators = TrackDecorators()
