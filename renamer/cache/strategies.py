"""Cache key generation strategies.

Provides different strategies for generating cache keys based on use case.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional, Callable
import hashlib
import json
import logging

logger = logging.getLogger(__name__)


class CacheKeyStrategy(ABC):
    """Base class for cache key generation strategies."""

    @abstractmethod
    def generate_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments.

        Returns:
            Cache key string
        """
        pass


class FilepathMethodStrategy(CacheKeyStrategy):
    """Generate key from filepath + method name.

    Format: extractor_{hash(filepath)}_{method_name}
    Usage: Extractor methods that operate on files

    Examples:
        extractor_a1b2c3d4e5f6_extract_title
        extractor_a1b2c3d4e5f6_12345_extract_year  (with instance_id)
    """

    def generate_key(
        self,
        file_path: Path,
        method_name: str,
        instance_id: str = ""
    ) -> str:
        """Generate cache key from file path and method name.

        Args:
            file_path: Path to the file being processed
            method_name: Name of the method being cached
            instance_id: Optional instance identifier for uniqueness

        Returns:
            Cache key string
        """
        # Hash the file path for consistent key length
        path_hash = hashlib.md5(str(file_path).encode()).hexdigest()[:12]

        if instance_id:
            return f"extractor_{path_hash}_{instance_id}_{method_name}"
        return f"extractor_{path_hash}_{method_name}"


class APIRequestStrategy(CacheKeyStrategy):
    """Generate key from API request parameters.

    Format: api_{service}_{hash(url+params)}
    Usage: API responses (TMDB, IMDB, etc.)

    Examples:
        api_tmdb_a1b2c3d4e5f6
        api_imdb_b2c3d4e5f6a1
    """

    def generate_key(
        self,
        service: str,
        url: str,
        params: Optional[Dict] = None
    ) -> str:
        """Generate cache key from API request parameters.

        Args:
            service: Service name (e.g., "tmdb", "imdb")
            url: API endpoint URL or path
            params: Optional request parameters dictionary

        Returns:
            Cache key string
        """
        # Sort params for consistent hashing
        params_str = json.dumps(params or {}, sort_keys=True)
        request_data = f"{url}{params_str}"
        request_hash = hashlib.md5(request_data.encode()).hexdigest()[:12]

        return f"api_{service}_{request_hash}"


class SimpleKeyStrategy(CacheKeyStrategy):
    """Generate key from simple string prefix + identifier.

    Format: {prefix}_{identifier}
    Usage: Posters, images, simple data

    Examples:
        poster_movie_12345
        image_actor_67890
    """

    def generate_key(self, prefix: str, identifier: str) -> str:
        """Generate cache key from prefix and identifier.

        Args:
            prefix: Key prefix (e.g., "poster", "image")
            identifier: Unique identifier

        Returns:
            Cache key string
        """
        # Sanitize identifier for filesystem safety
        clean_id = identifier.replace('/', '_').replace('\\', '_').replace('..', '_')
        return f"{prefix}_{clean_id}"


class CustomStrategy(CacheKeyStrategy):
    """User-provided custom key generation.

    Format: User-defined via callable
    Usage: Special cases requiring custom logic

    Example:
        def my_key_generator(obj, *args):
            return f"custom_{obj.id}_{args[0]}"

        strategy = CustomStrategy(my_key_generator)
    """

    def __init__(self, key_func: Callable[..., str]):
        """Initialize with custom key generation function.

        Args:
            key_func: Callable that returns cache key string
        """
        self.key_func = key_func

    def generate_key(self, *args, **kwargs) -> str:
        """Generate cache key using custom function.

        Returns:
            Cache key string from custom function
        """
        return self.key_func(*args, **kwargs)
