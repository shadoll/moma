"""Type definitions for cache subsystem."""

from typing import TypedDict, Any, Dict


class CacheEntry(TypedDict):
    """Type definition for cache entry structure.

    Attributes:
        value: The cached value (any JSON-serializable type)
        expires: Unix timestamp when entry expires
    """
    value: Any
    expires: float


class CacheStats(TypedDict):
    """Type definition for cache statistics.

    Attributes:
        cache_dir: Path to cache directory
        subdirs: Statistics for each subdirectory
        total_files: Total number of cache files
        total_size_bytes: Total size in bytes
        total_size_mb: Total size in megabytes
        memory_cache_entries: Number of entries in memory cache
    """
    cache_dir: str
    subdirs: Dict[str, Dict[str, Any]]
    total_files: int
    total_size_bytes: int
    total_size_mb: float
    memory_cache_entries: int
