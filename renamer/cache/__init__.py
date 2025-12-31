"""Unified caching subsystem for Renamer.

This module provides a flexible caching system with:
- Multiple cache key generation strategies
- Decorators for easy method caching
- Cache management and statistics
- Thread-safe operations
- In-memory and file-based caching with TTL

Usage Examples:
    # Using decorators
    from renamer.cache import cached, cached_api

    class MyExtractor:
        def __init__(self, file_path, cache, settings):
            self.file_path = file_path
            self.cache = cache
            self.settings = settings

        @cached(ttl=3600)
        def extract_data(self):
            # Automatically cached using FilepathMethodStrategy
            return expensive_operation()

        @cached_api("tmdb", ttl=21600)
        def fetch_movie_data(self, movie_id):
            # Cached API response
            return api_call(movie_id)

    # Using cache manager
    from renamer.cache import Cache, CacheManager

    cache = Cache()
    manager = CacheManager(cache)

    # Get statistics
    stats = manager.get_stats()
    print(f"Total cache size: {stats['total_size_mb']} MB")

    # Clear all cache
    manager.clear_all()

    # Clear specific prefix
    manager.clear_by_prefix("tmdb_")
"""

from .core import Cache
from .managers import CacheManager
from .strategies import (
    CacheKeyStrategy,
    FilepathMethodStrategy,
    APIRequestStrategy,
    SimpleKeyStrategy,
    CustomStrategy
)
from .decorators import (
    cached,
    cached_method,
    cached_api,
    cached_property
)
from .types import CacheEntry, CacheStats

__all__ = [
    # Core cache
    'Cache',
    'CacheManager',

    # Strategies
    'CacheKeyStrategy',
    'FilepathMethodStrategy',
    'APIRequestStrategy',
    'SimpleKeyStrategy',
    'CustomStrategy',

    # Decorators
    'cached',
    'cached_method',
    'cached_api',
    'cached_property',

    # Types
    'CacheEntry',
    'CacheStats',

    # Convenience functions
    'create_cache',
]


def create_cache(cache_dir=None):
    """Create a Cache instance with Manager (convenience function).

    Args:
        cache_dir: Optional cache directory path

    Returns:
        tuple: (Cache instance, CacheManager instance)

    Example:
        cache, manager = create_cache()
        stats = manager.get_stats()
        print(f"Cache has {stats['total_files']} files")
    """
    cache = Cache(cache_dir)
    manager = CacheManager(cache)
    return cache, manager
