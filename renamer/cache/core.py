import json
import logging
import threading
import time
import hashlib
import pickle
from pathlib import Path
from typing import Any, Optional, Dict

# Configure logger
logger = logging.getLogger(__name__)


class Cache:
    """Thread-safe file-based cache with TTL support."""

    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize cache with optional custom directory.

        Args:
            cache_dir: Optional cache directory path. Defaults to ~/.cache/renamer/
        """
        # Always use the default cache dir to avoid creating cache in scan dir
        if cache_dir is None:
            cache_dir = Path.home() / ".cache" / "renamer"
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._memory_cache: Dict[str, Dict[str, Any]] = {}  # In-memory cache for faster access
        self._lock = threading.RLock()  # Reentrant lock for thread safety

    def _sanitize_key_component(self, component: str) -> str:
        """Sanitize a key component to prevent filesystem escaping.

        Args:
            component: Key component to sanitize

        Returns:
            Sanitized component safe for filesystem use
        """
        # Remove or replace dangerous characters
        dangerous_chars = ['/', '\\', '..', '\0']
        sanitized = component
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '_')
        return sanitized

    def _get_cache_file(self, key: str) -> Path:
        """Get cache file path with organized subdirectories.

        Supports two key formats:
        1. Prefixed keys: "tmdb_id123", "poster_xyz" -> subdirectories
        2. Plain keys: "anykey" -> general subdirectory

        Args:
            key: Cache key

        Returns:
            Path to cache file
        """
        # Determine subdirectory and subkey based on prefix
        if key.startswith("tmdb_"):
            subdir = "tmdb"
            subkey = key[5:]  # Remove "tmdb_" prefix
        elif key.startswith("poster_"):
            subdir = "posters"
            subkey = key[7:]  # Remove "poster_" prefix
        elif key.startswith("extractor_"):
            subdir = "extractors"
            subkey = key[10:]  # Remove "extractor_" prefix
        else:
            # Default to general subdirectory
            subdir = "general"
            subkey = key

        # Sanitize subdirectory name
        subdir = self._sanitize_key_component(subdir)

        # Create subdirectory
        cache_subdir = self.cache_dir / subdir
        cache_subdir.mkdir(parents=True, exist_ok=True)

        # Hash the subkey for filename (prevents filesystem issues with long/special names)
        key_hash = hashlib.md5(subkey.encode('utf-8')).hexdigest()

        # Use .json extension for all cache files (simplifies logic)
        return cache_subdir / f"{key_hash}.json"

    def get(self, key: str) -> Optional[Any]:
        """Get cached value if not expired (thread-safe).

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        with self._lock:
            # Check memory cache first
            if key in self._memory_cache:
                data = self._memory_cache[key]
                if time.time() <= data.get('expires', 0):
                    return data.get('value')
                else:
                    # Expired, remove from memory
                    del self._memory_cache[key]
                    logger.debug(f"Memory cache expired for key: {key}")

            # Check file cache
            cache_file = self._get_cache_file(key)
            if not cache_file.exists():
                return None

            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)

                if time.time() > data.get('expires', 0):
                    # Expired, remove file
                    cache_file.unlink(missing_ok=True)
                    logger.debug(f"File cache expired for key: {key}, removed {cache_file}")
                    return None

                # Store in memory cache for faster future access
                self._memory_cache[key] = data
                return data.get('value')

            except json.JSONDecodeError as e:
                # Corrupted JSON, remove file
                logger.warning(f"Corrupted cache file {cache_file}: {e}")
                cache_file.unlink(missing_ok=True)
                return None
            except IOError as e:
                # File read error
                logger.error(f"Failed to read cache file {cache_file}: {e}")
                return None

    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        """Set cached value with TTL (thread-safe).

        Args:
            key: Cache key
            value: Value to cache (must be JSON-serializable)
            ttl_seconds: Time-to-live in seconds
        """
        with self._lock:
            data = {
                'value': value,
                'expires': time.time() + ttl_seconds
            }

            # Store in memory cache
            self._memory_cache[key] = data

            # Store in file cache
            cache_file = self._get_cache_file(key)
            try:
                with open(cache_file, 'w') as f:
                    json.dump(data, f, indent=2)
                logger.debug(f"Cached key: {key} to {cache_file} (TTL: {ttl_seconds}s)")
            except (IOError, TypeError) as e:
                logger.error(f"Failed to write cache file {cache_file}: {e}")

    def invalidate(self, key: str) -> None:
        """Remove cache entry (thread-safe).

        Args:
            key: Cache key to invalidate
        """
        with self._lock:
            # Remove from memory cache
            if key in self._memory_cache:
                del self._memory_cache[key]

            # Remove from file cache
            cache_file = self._get_cache_file(key)
            if cache_file.exists():
                cache_file.unlink(missing_ok=True)
                logger.debug(f"Invalidated cache for key: {key}")

    def get_image(self, key: str) -> Optional[Path]:
        """Get cached image path if not expired (thread-safe).

        Args:
            key: Cache key

        Returns:
            Path to cached image or None if not found/expired
        """
        with self._lock:
            cache_file = self._get_cache_file(key)
            if not cache_file.exists():
                return None

            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)

                if time.time() > data.get('expires', 0):
                    # Expired, remove file and image
                    image_path = data.get('image_path')
                    if image_path and Path(image_path).exists():
                        Path(image_path).unlink(missing_ok=True)
                    cache_file.unlink(missing_ok=True)
                    logger.debug(f"Image cache expired for key: {key}")
                    return None

                image_path = data.get('image_path')
                if image_path and Path(image_path).exists():
                    return Path(image_path)
                else:
                    logger.warning(f"Image path in cache but file missing: {image_path}")
                    return None

            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to read image cache {cache_file}: {e}")
                cache_file.unlink(missing_ok=True)
                return None

    def set_image(self, key: str, image_data: bytes, ttl_seconds: int) -> Optional[Path]:
        """Set cached image and return path (thread-safe).

        Args:
            key: Cache key
            image_data: Image binary data
            ttl_seconds: Time-to-live in seconds

        Returns:
            Path to saved image or None if failed
        """
        with self._lock:
            # Determine subdirectory for image storage
            if key.startswith("poster_"):
                subdir = "posters"
                subkey = key[7:]
            else:
                subdir = "images"
                subkey = key

            # Create image directory
            image_dir = self.cache_dir / subdir
            image_dir.mkdir(parents=True, exist_ok=True)

            # Hash for filename
            key_hash = hashlib.md5(subkey.encode('utf-8')).hexdigest()
            image_path = image_dir / f"{key_hash}.jpg"

            try:
                # Write image data
                with open(image_path, 'wb') as f:
                    f.write(image_data)

                # Cache metadata
                data = {
                    'image_path': str(image_path),
                    'expires': time.time() + ttl_seconds
                }
                cache_file = self._get_cache_file(key)
                with open(cache_file, 'w') as f:
                    json.dump(data, f, indent=2)

                logger.debug(f"Cached image for key: {key} at {image_path} (TTL: {ttl_seconds}s)")
                return image_path

            except IOError as e:
                logger.error(f"Failed to cache image for key {key}: {e}")
                return None

    def get_object(self, key: str) -> Optional[Any]:
        """Get pickled object from cache if not expired (thread-safe).

        Note: This uses a separate .pkl file format for objects that can't be JSON-serialized.

        Args:
            key: Cache key

        Returns:
            Cached object or None if not found/expired
        """
        with self._lock:
            # Check memory cache first
            if key in self._memory_cache:
                data = self._memory_cache[key]
                if time.time() <= data.get('expires', 0):
                    return data.get('value')
                else:
                    del self._memory_cache[key]
                    logger.debug(f"Memory cache expired for pickled object: {key}")

            # Get cache file path but change extension to .pkl
            cache_file = self._get_cache_file(key).with_suffix('.pkl')
            if not cache_file.exists():
                return None

            try:
                with open(cache_file, 'rb') as f:
                    data = pickle.load(f)

                if time.time() > data.get('expires', 0):
                    # Expired, remove file
                    cache_file.unlink(missing_ok=True)
                    logger.debug(f"Pickled cache expired for key: {key}")
                    return None

                # Store in memory cache
                self._memory_cache[key] = data
                return data.get('value')

            except (pickle.PickleError, IOError) as e:
                # Corrupted or read error, remove
                logger.warning(f"Corrupted pickle cache {cache_file}: {e}")
                cache_file.unlink(missing_ok=True)
                return None

    def set_object(self, key: str, obj: Any, ttl_seconds: int) -> None:
        """Pickle and cache object with TTL (thread-safe).

        Note: This uses pickle format for objects that can't be JSON-serialized.

        Args:
            key: Cache key
            obj: Object to cache (must be picklable)
            ttl_seconds: Time-to-live in seconds
        """
        with self._lock:
            data = {
                'value': obj,
                'expires': time.time() + ttl_seconds
            }

            # Store in memory cache
            self._memory_cache[key] = data

            # Get cache file path but change extension to .pkl
            cache_file = self._get_cache_file(key).with_suffix('.pkl')
            try:
                with open(cache_file, 'wb') as f:
                    pickle.dump(data, f)
                logger.debug(f"Cached pickled object for key: {key} (TTL: {ttl_seconds}s)")
            except (IOError, pickle.PickleError) as e:
                logger.error(f"Failed to cache pickled object {cache_file}: {e}")

    def clear_expired(self) -> int:
        """Remove all expired cache entries.

        Returns:
            Number of entries removed
        """
        with self._lock:
            removed_count = 0
            current_time = time.time()

            # Clear expired from memory cache
            expired_keys = [k for k, v in self._memory_cache.items()
                          if current_time > v.get('expires', 0)]
            for key in expired_keys:
                del self._memory_cache[key]
                removed_count += 1

            # Clear expired from file cache
            for cache_file in self.cache_dir.rglob('*'):
                if cache_file.is_file() and cache_file.suffix in ['.json', '.pkl']:
                    try:
                        if cache_file.suffix == '.json':
                            with open(cache_file, 'r') as f:
                                data = json.load(f)
                        else:  # .pkl
                            with open(cache_file, 'rb') as f:
                                data = pickle.load(f)

                        if current_time > data.get('expires', 0):
                            cache_file.unlink(missing_ok=True)
                            removed_count += 1

                    except (json.JSONDecodeError, pickle.PickleError, IOError):
                        # Corrupted file, remove it
                        cache_file.unlink(missing_ok=True)
                        removed_count += 1

            logger.info(f"Cleared {removed_count} expired cache entries")
            return removed_count
