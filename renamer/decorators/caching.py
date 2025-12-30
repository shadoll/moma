"""Caching decorators for extractors."""

import hashlib
import json
from pathlib import Path
from typing import Any, Callable, Optional
from renamer.cache import Cache


# Global cache instance
_cache = Cache()


def cached_method(ttl_seconds: int = 3600) -> Callable:
    """Decorator to cache method results with TTL.

    Caches the result of a method call using a global file-based cache.
    The cache key includes class name, method name, instance identifier, and parameters hash.

    Args:
        ttl_seconds: Time to live for cached results in seconds (default 1 hour)

    Returns:
        The decorated method with caching
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(self, *args, **kwargs) -> Any:
            # Generate cache key: class_name.method_name.instance_id.param_hash
            class_name = self.__class__.__name__
            method_name = func.__name__
            
            # Use instance identifier (file_path for extractors)
            instance_id = getattr(self, 'file_path', str(id(self)))
            # If instance_id contains path separators, hash it to avoid creating subdirs
            if '/' in str(instance_id) or '\\' in str(instance_id):
                instance_id = hashlib.md5(str(instance_id).encode('utf-8')).hexdigest()
            
            # Create hash from args and kwargs only if they exist (excluding self)
            if args or kwargs:
                param_str = json.dumps((args, kwargs), sort_keys=True, default=str)
                param_hash = hashlib.md5(param_str.encode('utf-8')).hexdigest()
                cache_key = f"{class_name}.{method_name}.{instance_id}.{param_hash}"
            else:
                cache_key = f"{class_name}.{method_name}.{instance_id}"
            
            # Try to get from cache
            cached_result = _cache.get_object(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Compute result and cache it
            result = func(self, *args, **kwargs)
            _cache.set_object(cache_key, result, ttl_seconds)
            return result
        
        return wrapper
    return decorator