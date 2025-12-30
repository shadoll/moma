import json
import os
import time
import hashlib
import pickle
from pathlib import Path
from typing import Any, Optional


class Cache:
    """File-based cache with TTL support."""

    def __init__(self, cache_dir: Optional[Path] = None):
        # Always use the default cache dir to avoid creating cache in scan dir
        cache_dir = Path.home() / ".cache" / "renamer"
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._memory_cache = {}  # In-memory cache for faster access

    def _get_cache_file(self, key: str) -> Path:
        """Get cache file path with hashed filename and subdirs."""
        import logging
        logging.info(f"Cache _get_cache_file called with key: {key!r}")
        # Parse key format: ClassName.method_name.param_hash
        if '.' in key:
            parts = key.split('.')
            if len(parts) >= 3:
                class_name = parts[0]
                method_name = parts[1]
                param_hash = parts[2]
                
                # Use class name as subdir, but if it contains '/', use general to avoid creating nested dirs
                if '/' in class_name or '\\' in class_name:
                    subdir = "general"
                    subkey = key
                    file_ext = "json"
                else:
                    subdir = class_name
                    file_ext = "pkl"
                
                # Use class name as subdir
                cache_subdir = self.cache_dir / subdir
                logging.info(f"Cache parsed key, class_name: {class_name!r}, cache_subdir: {cache_subdir!r}")
                cache_subdir.mkdir(parents=True, exist_ok=True)
                
                if file_ext == "pkl":
                    # Use method_name.param_hash as filename
                    return cache_subdir / f"{method_name}.{param_hash}.pkl"
                else:
                    # Hash the subkey for filename
                    key_hash = hashlib.md5(subkey.encode('utf-8')).hexdigest()
                    return cache_subdir / f"{key_hash}.json"
        
        # Fallback for old keys (tmdb_, poster_, etc.)
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
            subdir = "general"
            subkey = key
        
        # Create subdir
        cache_subdir = self.cache_dir / subdir
        logging.info(f"Cache fallback, subdir: {subdir!r}, cache_subdir: {cache_subdir!r}")
        cache_subdir.mkdir(parents=True, exist_ok=True)
        
        # Hash the subkey for filename
        key_hash = hashlib.md5(subkey.encode('utf-8')).hexdigest()
        return cache_subdir / f"{key_hash}.json"

    def get(self, key: str) -> Optional[Any]:
        """Get cached value if not expired."""
        # Check memory cache first
        if key in self._memory_cache:
            data = self._memory_cache[key]
            if time.time() > data.get('expires', 0):
                del self._memory_cache[key]
                return None
            return data.get('value')
        
        cache_file = self._get_cache_file(key)
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
            
            if time.time() > data.get('expires', 0):
                # Expired, remove file
                cache_file.unlink(missing_ok=True)
                return None
            
            # Store in memory cache
            self._memory_cache[key] = data
            return data.get('value')
        except (json.JSONDecodeError, IOError):
            # Corrupted, remove
            cache_file.unlink(missing_ok=True)
            return None

    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        """Set cached value with TTL."""
        data = {
            'value': value,
            'expires': time.time() + ttl_seconds
        }
        # Store in memory cache
        self._memory_cache[key] = data
        
        cache_file = self._get_cache_file(key)
        try:
            with open(cache_file, 'w') as f:
                json.dump(data, f)
        except IOError:
            pass  # Silently fail

    def invalidate(self, key: str) -> None:
        """Remove cache entry."""
        cache_file = self._get_cache_file(key)
        cache_file.unlink(missing_ok=True)

    def get_image(self, key: str) -> Optional[Path]:
        """Get cached image path if not expired."""
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
                return None
            
            image_path = data.get('image_path')
            if image_path and Path(image_path).exists():
                return Path(image_path)
            return None
        except (json.JSONDecodeError, IOError):
            cache_file.unlink(missing_ok=True)
            return None

    def set_image(self, key: str, image_data: bytes, ttl_seconds: int) -> Optional[Path]:
        """Set cached image and return path."""
        # Determine subdir and subkey
        if key.startswith("poster_"):
            subdir = "posters"
            subkey = key[7:]
        else:
            subdir = "images"
            subkey = key
        
        # Create subdir
        image_dir = self.cache_dir / subdir
        image_dir.mkdir(parents=True, exist_ok=True)
        
        # Hash for filename
        key_hash = hashlib.md5(subkey.encode('utf-8')).hexdigest()
        image_path = image_dir / f"{key_hash}.jpg"
        
        try:
            with open(image_path, 'wb') as f:
                f.write(image_data)
            
            # Cache metadata
            data = {
                'image_path': str(image_path),
                'expires': time.time() + ttl_seconds
            }
            cache_file = self._get_cache_file(key)
            with open(cache_file, 'w') as f:
                json.dump(data, f)
            
            return image_path
        except IOError:
            return None

    def get_object(self, key: str) -> Optional[Any]:
        """Get pickled object from cache if not expired."""
        # Check memory cache first
        if key in self._memory_cache:
            data = self._memory_cache[key]
            if time.time() > data.get('expires', 0):
                del self._memory_cache[key]
                return None
            return data.get('value')
        
        cache_file = self._get_cache_file(key)
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'rb') as f:
                data = pickle.load(f)
            
            if time.time() > data.get('expires', 0):
                # Expired, remove file
                cache_file.unlink(missing_ok=True)
                return None
            
            # Store in memory cache
            self._memory_cache[key] = data
            return data.get('value')
        except (pickle.PickleError, IOError):
            # Corrupted, remove
            cache_file.unlink(missing_ok=True)
            return None

    def set_object(self, key: str, obj: Any, ttl_seconds: int) -> None:
        """Pickle and cache object with TTL."""
        data = {
            'value': obj,
            'expires': time.time() + ttl_seconds
        }
        # Store in memory cache
        self._memory_cache[key] = data
        
        cache_file = self._get_cache_file(key)
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(data, f)
        except IOError:
            pass  # Silently fail