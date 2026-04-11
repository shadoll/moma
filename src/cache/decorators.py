"""Cache decorators for easy method caching.

Provides decorators that can be applied to methods for automatic caching
with different strategies.
"""

from functools import wraps
from pathlib import Path
from typing import Callable, Optional, Any
import logging
import json

from .strategies import (
    CacheKeyStrategy,
    FilepathMethodStrategy,
    APIRequestStrategy,
    SimpleKeyStrategy
)

logger = logging.getLogger(__name__)

# Sentinel object to distinguish "not in cache" from "cached value is None"
_CACHE_MISS = object()


def cached(
    strategy: Optional[CacheKeyStrategy] = None,
    ttl: Optional[int] = None,
    key_prefix: Optional[str] = None
):
    """Generic cache decorator with strategy pattern.

    This is the main caching decorator that supports different strategies
    for generating cache keys based on the use case.

    Args:
        strategy: Cache key generation strategy (defaults to FilepathMethodStrategy)
        ttl: Time-to-live in seconds (defaults to settings value or 21600)
        key_prefix: Optional prefix for cache key

    Returns:
        Decorated function with caching

    Usage:
        @cached(strategy=FilepathMethodStrategy(), ttl=3600)
        def extract_title(self):
            # Expensive operation
            return title

        @cached(strategy=APIRequestStrategy(), ttl=21600)
        def fetch_tmdb_data(self, movie_id):
            # API call
            return data

        @cached(ttl=7200)  # Uses FilepathMethodStrategy by default
        def extract_year(self):
            return year

    Note:
        The instance must have a `cache` attribute for caching to work.
        If no cache is found, the function executes without caching.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Get cache from instance
            cache = getattr(self, 'cache', None)
            if not cache:
                logger.debug(f"No cache found on {self.__class__.__name__}, executing uncached")
                return func(self, *args, **kwargs)

            # Determine strategy
            actual_strategy = strategy or FilepathMethodStrategy()

            # Generate cache key based on strategy type
            try:
                cache_key = _generate_cache_key(
                    actual_strategy, self, func, args, kwargs, key_prefix
                )
            except Exception as e:
                logger.warning(f"Failed to generate cache key: {e}, executing uncached")
                return func(self, *args, **kwargs)

            # Check cache (use sentinel to distinguish "not in cache" from "cached None")
            cached_value = cache.get(cache_key, _CACHE_MISS)
            if cached_value is not _CACHE_MISS:
                logger.debug(f"Cache hit for {func.__name__}: {cache_key} (value={cached_value!r})")
                return cached_value

            # Execute function
            logger.debug(f"Cache miss for {func.__name__}: {cache_key}")
            result = func(self, *args, **kwargs)

            # Determine TTL
            actual_ttl = _determine_ttl(self, ttl)

            # Cache result (including None - None is valid data meaning "not found")
            cache.set(cache_key, result, actual_ttl)
            logger.debug(f"Cached {func.__name__}: {cache_key} (TTL: {actual_ttl}s, value={result!r})")

            return result

        return wrapper
    return decorator


def _generate_cache_key(
    strategy: CacheKeyStrategy,
    instance: Any,
    func: Callable,
    args: tuple,
    kwargs: dict,
    key_prefix: Optional[str]
) -> str:
    """Generate cache key based on strategy type.

    Args:
        strategy: Cache key strategy
        instance: Instance the method is called on
        func: Function being cached
        args: Positional arguments
        kwargs: Keyword arguments
        key_prefix: Optional key prefix

    Returns:
        Generated cache key
    """
    if isinstance(strategy, FilepathMethodStrategy):
        # Extractor pattern: needs file_path attribute
        file_path = getattr(instance, 'file_path', None)
        if not file_path:
            raise ValueError(f"{instance.__class__.__name__} missing file_path attribute")

        # Cache by file_path + method_name only (no instance_id)
        # This allows cache hits across different extractor instances for the same file
        return strategy.generate_key(file_path, func.__name__)

    elif isinstance(strategy, APIRequestStrategy):
        # API pattern: expects service name in args or uses function name
        if args:
            service = str(args[0]) if len(args) >= 1 else func.__name__
            url = str(args[1]) if len(args) >= 2 else ""
            params = args[2] if len(args) >= 3 else kwargs
        else:
            service = func.__name__
            url = ""
            params = kwargs

        return strategy.generate_key(service, url, params)

    elif isinstance(strategy, SimpleKeyStrategy):
        # Simple pattern: uses prefix and first arg as identifier
        prefix = key_prefix or func.__name__
        identifier = str(args[0]) if args else str(kwargs.get('id', 'default'))
        return strategy.generate_key(prefix, identifier)

    else:
        # Custom strategy: pass instance and all args
        return strategy.generate_key(instance, *args, **kwargs)


def _determine_ttl(instance: Any, ttl: Optional[int]) -> int:
    """Determine TTL from explicit value or instance settings.

    Args:
        instance: Instance the method is called on
        ttl: Explicit TTL value (takes precedence)

    Returns:
        TTL in seconds
    """
    if ttl is not None:
        return ttl

    # Try to get from settings
    settings = getattr(instance, 'settings', None)
    if settings:
        return settings.get('cache_ttl_extractors', 21600)

    # Default to 6 hours
    return 21600


def cached_method(ttl: Optional[int] = None):
    """Decorator for extractor methods (legacy/convenience).

    This is an alias for cached() with FilepathMethodStrategy.
    Provides backward compatibility with existing code.

    Args:
        ttl: Time-to-live in seconds

    Returns:
        Decorated function

    Usage:
        @cached_method(ttl=3600)
        def extract_title(self):
            return title

    Note:
        This is equivalent to:
        @cached(strategy=FilepathMethodStrategy(), ttl=3600)
    """
    return cached(strategy=FilepathMethodStrategy(), ttl=ttl)


def cached_api(service: str, ttl: Optional[int] = None):
    """Decorator for API response caching.

    Specialized decorator for caching API responses. Generates keys
    based on service name and request parameters.

    Args:
        service: Service name (e.g., "tmdb", "imdb", "omdb")
        ttl: Time-to-live in seconds (defaults to cache_ttl_{service})

    Returns:
        Decorated function

    Usage:
        @cached_api("tmdb", ttl=21600)
        def search_movie(self, title, year=None):
            # Make API request
            response = requests.get(...)
            return response.json()

        @cached_api("imdb")
        def get_movie_details(self, movie_id):
            return api_response

    Note:
        The function args/kwargs are automatically included in the cache key.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            cache = getattr(self, 'cache', None)
            if not cache:
                logger.debug(f"No cache on {self.__class__.__name__}, executing uncached")
                return func(self, *args, **kwargs)

            # Build cache key from service + function name + args/kwargs
            args_repr = json.dumps({
                'args': [str(a) for a in args],
                'kwargs': {k: str(v) for k, v in sorted(kwargs.items())}
            }, sort_keys=True)

            strategy = APIRequestStrategy()
            cache_key = strategy.generate_key(service, func.__name__, {'params': args_repr})

            # Check cache (use sentinel to distinguish "not in cache" from "cached None")
            cached_value = cache.get(cache_key, _CACHE_MISS)
            if cached_value is not _CACHE_MISS:
                logger.debug(f"API cache hit for {service}.{func.__name__} (value={cached_value!r})")
                return cached_value

            # Execute function
            logger.debug(f"API cache miss for {service}.{func.__name__}")
            result = func(self, *args, **kwargs)

            # Determine TTL (service-specific or default)
            actual_ttl = ttl
            if actual_ttl is None:
                settings = getattr(self, 'settings', None)
                if settings:
                    # Try service-specific TTL first
                    actual_ttl = settings.get(f'cache_ttl_{service}',
                                             settings.get('cache_ttl_api', 21600))
                else:
                    actual_ttl = 21600  # Default 6 hours

            # Cache result (including None - None is valid data)
            cache.set(cache_key, result, actual_ttl)
            logger.debug(f"API cached {service}.{func.__name__} (TTL: {actual_ttl}s, value={result!r})")

            return result

        return wrapper
    return decorator


def cached_property(ttl: Optional[int] = None):
    """Decorator for caching property-like methods.

    Similar to @property but with caching support.

    Args:
        ttl: Time-to-live in seconds

    Returns:
        Decorated function

    Usage:
        @cached_property(ttl=3600)
        def metadata(self):
            # Expensive computation
            return complex_metadata

    Note:
        Unlike @property, this still requires parentheses: obj.metadata()
        For true property behavior, use @property with manual caching.
    """
    return cached(strategy=FilepathMethodStrategy(), ttl=ttl)
