"""Cache management and operations.

Provides high-level cache management functionality including
clearing, statistics, and maintenance operations.
"""

from pathlib import Path
from typing import Dict, Any, Optional
import logging
import time
import json
import pickle

from .types import CacheStats

logger = logging.getLogger(__name__)


class CacheManager:
    """High-level cache management and operations."""

    def __init__(self, cache):
        """Initialize manager with cache instance.

        Args:
            cache: Core Cache instance
        """
        self.cache = cache

    def clear_all(self) -> int:
        """Clear all cache entries (files and memory).

        Returns:
            Number of entries removed
        """
        count = 0

        # Clear all cache files
        for cache_file in self.cache.cache_dir.rglob('*'):
            if cache_file.is_file():
                try:
                    cache_file.unlink()
                    count += 1
                except (OSError, PermissionError) as e:
                    logger.warning(f"Failed to remove {cache_file}: {e}")

        # Clear memory cache
        with self.cache._lock:
            mem_count = len(self.cache._memory_cache)
            self.cache._memory_cache.clear()
            count += mem_count

        logger.info(f"Cleared all cache: {count} entries removed")
        return count

    def clear_by_prefix(self, prefix: str) -> int:
        """Clear cache entries matching prefix.

        Args:
            prefix: Cache key prefix (e.g., "tmdb", "extractor", "poster")

        Returns:
            Number of entries removed

        Examples:
            clear_by_prefix("tmdb_")  # Clear all TMDB cache
            clear_by_prefix("extractor_")  # Clear all extractor cache
        """
        count = 0

        # Remove trailing underscore if present
        subdir = prefix.rstrip('_')
        cache_subdir = self.cache.cache_dir / subdir

        # Clear files in subdirectory
        if cache_subdir.exists():
            for cache_file in cache_subdir.rglob('*'):
                if cache_file.is_file():
                    try:
                        cache_file.unlink()
                        count += 1
                    except (OSError, PermissionError) as e:
                        logger.warning(f"Failed to remove {cache_file}: {e}")

        # Clear from memory cache
        with self.cache._lock:
            keys_to_remove = [k for k in self.cache._memory_cache.keys()
                            if k.startswith(prefix)]
            for key in keys_to_remove:
                del self.cache._memory_cache[key]
                count += 1

        logger.info(f"Cleared cache with prefix '{prefix}': {count} entries removed")
        return count

    def clear_expired(self) -> int:
        """Clear all expired cache entries.

        Delegates to Cache.clear_expired() for implementation.

        Returns:
            Number of expired entries removed
        """
        return self.cache.clear_expired()

    def get_stats(self) -> CacheStats:
        """Get comprehensive cache statistics.

        Returns:
            Dictionary with cache statistics including:
            - cache_dir: Path to cache directory
            - subdirs: Per-subdirectory statistics
            - total_files: Total number of cached files
            - total_size_bytes: Total size in bytes
            - total_size_mb: Total size in megabytes
            - memory_cache_entries: Number of in-memory entries
        """
        stats: CacheStats = {
            'cache_dir': str(self.cache.cache_dir),
            'subdirs': {},
            'total_files': 0,
            'total_size_bytes': 0,
            'total_size_mb': 0.0,
            'memory_cache_entries': len(self.cache._memory_cache)
        }

        # Gather statistics for each subdirectory
        if self.cache.cache_dir.exists():
            for subdir in self.cache.cache_dir.iterdir():
                if subdir.is_dir():
                    files = list(subdir.rglob('*'))
                    file_list = [f for f in files if f.is_file()]
                    file_count = len(file_list)
                    size = sum(f.stat().st_size for f in file_list)

                    stats['subdirs'][subdir.name] = {
                        'files': file_count,
                        'size_bytes': size,
                        'size_mb': round(size / (1024 * 1024), 2)
                    }
                    stats['total_files'] += file_count
                    stats['total_size_bytes'] += size

        stats['total_size_mb'] = round(stats['total_size_bytes'] / (1024 * 1024), 2)
        return stats

    def clear_file_cache(self, file_path: Path) -> int:
        """Clear all cache entries for a specific file.

        Useful when file is renamed, moved, or modified.
        Removes all extractor cache entries associated with the file.

        Args:
            file_path: Path to file whose cache should be cleared

        Returns:
            Number of entries removed

        Example:
            After renaming a file, clear its old cache:
            manager.clear_file_cache(old_path)
        """
        count = 0
        import hashlib

        # Generate the same hash used in FilepathMethodStrategy
        path_hash = hashlib.md5(str(file_path).encode()).hexdigest()[:12]

        # Search in extractor subdirectory
        extractor_dir = self.cache.cache_dir / "extractors"
        if extractor_dir.exists():
            for cache_file in extractor_dir.rglob('*'):
                if cache_file.is_file() and path_hash in cache_file.name:
                    try:
                        cache_file.unlink()
                        count += 1
                    except (OSError, PermissionError) as e:
                        logger.warning(f"Failed to remove {cache_file}: {e}")

        # Clear from memory cache
        with self.cache._lock:
            keys_to_remove = [k for k in self.cache._memory_cache.keys()
                            if path_hash in k]
            for key in keys_to_remove:
                del self.cache._memory_cache[key]
                count += 1

        logger.info(f"Cleared cache for file {file_path}: {count} entries removed")
        return count

    def get_cache_age(self, key: str) -> Optional[float]:
        """Get the age of a cache entry in seconds.

        Args:
            key: Cache key

        Returns:
            Age in seconds, or None if not cached
        """
        cache_file = self.cache._get_cache_file(key)
        if not cache_file.exists():
            return None

        try:
            # Check if it's a JSON or pickle file
            if cache_file.suffix == '.json':
                with open(cache_file, 'r') as f:
                    data = json.load(f)
            else:  # .pkl
                with open(cache_file, 'rb') as f:
                    data = pickle.load(f)

            expires = data.get('expires', 0)
            age = time.time() - (expires - data.get('ttl', 0))  # Approximate
            return age if age >= 0 else None

        except (json.JSONDecodeError, pickle.PickleError, IOError, KeyError):
            return None

    def compact_cache(self) -> int:
        """Remove empty subdirectories and organize cache.

        Returns:
            Number of empty directories removed
        """
        count = 0

        if self.cache.cache_dir.exists():
            for subdir in self.cache.cache_dir.rglob('*'):
                if subdir.is_dir():
                    try:
                        # Try to remove if empty
                        subdir.rmdir()
                        count += 1
                        logger.debug(f"Removed empty directory: {subdir}")
                    except OSError:
                        # Directory not empty or other error
                        pass

        logger.info(f"Compacted cache: removed {count} empty directories")
        return count
