"""Tests for the unified cache subsystem."""

import pytest
from pathlib import Path
from renamer.cache import (
    Cache,
    CacheManager,
    cached,
    cached_method,
    cached_api,
    FilepathMethodStrategy,
    APIRequestStrategy,
    SimpleKeyStrategy,
    CustomStrategy
)


class TestCacheBasicOperations:
    """Test basic cache operations."""

    @pytest.fixture
    def cache(self):
        """Create a cache instance for testing."""
        return Cache()

    @pytest.fixture
    def manager(self, cache):
        """Create a cache manager for testing."""
        return CacheManager(cache)

    def test_set_and_get_object(self, cache):
        """Test storing and retrieving an object."""
        cache.set_object("test_key", {"data": "value"}, ttl_seconds=3600)
        result = cache.get_object("test_key")
        assert result == {"data": "value"}

    def test_cache_manager_stats(self, manager):
        """Test getting cache statistics."""
        stats = manager.get_stats()
        assert 'total_files' in stats
        assert 'total_size_mb' in stats
        assert 'memory_cache_entries' in stats
        assert 'subdirs' in stats


class TestCacheStrategies:
    """Test cache key generation strategies."""

    def test_filepath_method_strategy(self):
        """Test FilepathMethodStrategy generates correct keys."""
        strategy = FilepathMethodStrategy()
        key = strategy.generate_key(Path("/test/file.mkv"), "extract_title")
        assert key.startswith("extractor_")
        assert "extract_title" in key

    def test_filepath_method_strategy_with_instance_id(self):
        """Test FilepathMethodStrategy with instance ID."""
        strategy = FilepathMethodStrategy()
        key = strategy.generate_key(
            Path("/test/file.mkv"),
            "extract_title",
            instance_id="12345"
        )
        assert key.startswith("extractor_")
        assert "12345" in key
        assert "extract_title" in key

    def test_api_request_strategy(self):
        """Test APIRequestStrategy generates correct keys."""
        strategy = APIRequestStrategy()
        key = strategy.generate_key("tmdb", "/movie/search", {"query": "test"})
        assert key.startswith("api_tmdb_")

    def test_api_request_strategy_no_params(self):
        """Test APIRequestStrategy without params."""
        strategy = APIRequestStrategy()
        key = strategy.generate_key("imdb", "/title/search")
        assert key.startswith("api_imdb_")

    def test_simple_key_strategy(self):
        """Test SimpleKeyStrategy generates correct keys."""
        strategy = SimpleKeyStrategy()
        key = strategy.generate_key("poster", "movie_123")
        assert key == "poster_movie_123"

    def test_simple_key_strategy_sanitizes_path_separators(self):
        """Test SimpleKeyStrategy sanitizes dangerous characters."""
        strategy = SimpleKeyStrategy()
        key = strategy.generate_key("poster", "path/to/file")
        assert "/" not in key
        assert key == "poster_path_to_file"

    def test_custom_strategy(self):
        """Test CustomStrategy with custom function."""
        def my_key_func(prefix, identifier):
            return f"custom_{prefix}_{identifier}"

        strategy = CustomStrategy(my_key_func)
        key = strategy.generate_key("test", "123")
        assert key == "custom_test_123"


class TestCacheDecorators:
    """Test cache decorators."""

    @pytest.fixture
    def cache(self):
        """Create a cache instance for testing."""
        return Cache()

    def test_cached_method_decorator(self, cache):
        """Test cached_method decorator caches results."""
        call_count = 0

        class TestExtractor:
            def __init__(self, file_path):
                self.file_path = file_path
                self.cache = cache

            @cached_method(ttl=3600)
            def extract_title(self):
                nonlocal call_count
                call_count += 1
                return "Test Movie"

        extractor = TestExtractor(Path("/test/movie.mkv"))

        # First call executes the method
        result1 = extractor.extract_title()
        assert result1 == "Test Movie"
        assert call_count == 1

        # Second call uses cache
        result2 = extractor.extract_title()
        assert result2 == "Test Movie"
        assert call_count == 1  # Should still be 1 (cached)

    def test_cached_method_without_cache_attribute(self):
        """Test cached_method executes without caching if no cache attribute."""
        call_count = 0

        class TestExtractor:
            def __init__(self, file_path):
                self.file_path = file_path
                # No cache attribute!

            @cached_method(ttl=3600)
            def extract_title(self):
                nonlocal call_count
                call_count += 1
                return "Test Movie"

        extractor = TestExtractor(Path("/test/movie.mkv"))

        # Both calls should execute since no cache
        result1 = extractor.extract_title()
        assert result1 == "Test Movie"
        assert call_count == 1

        result2 = extractor.extract_title()
        assert result2 == "Test Movie"
        assert call_count == 2  # Should increment (no caching)

    def test_cached_method_different_instances(self, cache):
        """Test cached_method creates different cache keys for different files."""
        call_count = 0

        class TestExtractor:
            def __init__(self, file_path):
                self.file_path = file_path
                self.cache = cache

            @cached_method(ttl=3600)
            def extract_title(self):
                nonlocal call_count
                call_count += 1
                return f"Title for {self.file_path.name}"

        extractor1 = TestExtractor(Path("/test/movie1.mkv"))
        extractor2 = TestExtractor(Path("/test/movie2.mkv"))

        result1 = extractor1.extract_title()
        result2 = extractor2.extract_title()

        assert result1 != result2
        assert call_count == 2  # Both should execute (different files)


class TestCacheManager:
    """Test cache manager operations."""

    @pytest.fixture
    def cache(self):
        """Create a cache instance for testing."""
        return Cache()

    @pytest.fixture
    def manager(self, cache):
        """Create a cache manager for testing."""
        return CacheManager(cache)

    def test_clear_by_prefix(self, cache, manager):
        """Test clearing cache by prefix."""
        # Add some test data with recognized prefixes
        cache.set_object("tmdb_movie_123", "data1", 3600)
        cache.set_object("tmdb_movie_456", "data2", 3600)
        cache.set_object("extractor_test_1", "data3", 3600)

        # Clear only tmdb_ prefix
        manager.clear_by_prefix("tmdb_")

        # tmdb_ entries should be gone
        assert cache.get_object("tmdb_movie_123") is None
        assert cache.get_object("tmdb_movie_456") is None

        # extractor_ entry should remain
        assert cache.get_object("extractor_test_1") == "data3"

    def test_clear_all(self, cache, manager):
        """Test clearing all cache."""
        # Add some test data
        cache.set_object("key1", "data1", 3600)
        cache.set_object("key2", "data2", 3600)

        # Clear all
        manager.clear_all()

        # All should be gone
        assert cache.get_object("key1") is None
        assert cache.get_object("key2") is None

    def test_compact_cache(self, manager):
        """Test cache compaction."""
        # Just verify it runs without error
        manager.compact_cache()


class TestBackwardCompatibility:
    """Test backward compatibility with old import paths."""

    def test_import_from_decorators(self):
        """Test importing from renamer.decorators still works."""
        from renamer.decorators import cached_method
        assert cached_method is not None

    def test_import_cache_from_package(self):
        """Test importing Cache from renamer.cache package."""
        from renamer.cache import Cache as PackageCache
        assert PackageCache is not None

    def test_create_cache_convenience_function(self):
        """Test the create_cache convenience function."""
        from renamer.cache import create_cache
        cache, manager = create_cache()
        assert cache is not None
        assert manager is not None
        assert isinstance(manager, CacheManager)
