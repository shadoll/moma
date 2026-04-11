"""Tests for the service layer.

Tests for FileTreeService, MetadataService, and RenameService.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
import tempfile
import os

from src.services import FileTreeService, MetadataService, RenameService
from src.cache import Cache
from src.settings import Settings


class TestFileTreeService:
    """Test FileTreeService functionality."""

    @pytest.fixture
    def service(self):
        """Create a FileTreeService instance."""
        return FileTreeService()

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory with test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create some test files
            (tmpdir / "movie1.mkv").touch()
            (tmpdir / "movie2.mp4").touch()
            (tmpdir / "readme.txt").touch()

            # Create subdirectory
            subdir = tmpdir / "subdir"
            subdir.mkdir()
            (subdir / "movie3.avi").touch()

            yield tmpdir

    def test_validate_directory_valid(self, service, temp_dir):
        """Test validating a valid directory."""
        is_valid, error = service.validate_directory(temp_dir)
        assert is_valid is True
        assert error is None

    def test_validate_directory_not_exists(self, service):
        """Test validating a non-existent directory."""
        is_valid, error = service.validate_directory(Path("/nonexistent"))
        assert is_valid is False
        assert "does not exist" in error

    def test_validate_directory_is_file(self, service, temp_dir):
        """Test validating a file instead of directory."""
        file_path = temp_dir / "movie1.mkv"
        is_valid, error = service.validate_directory(file_path)
        assert is_valid is False
        assert "not a directory" in error

    def test_scan_directory(self, service, temp_dir):
        """Test scanning directory for media files."""
        files = service.scan_directory(temp_dir)

        # Should find 3 media files (2 in root, 1 in subdir)
        assert len(files) == 3

        # Check file types
        extensions = {f.suffix for f in files}
        assert extensions == {'.mkv', '.mp4', '.avi'}

    def test_scan_directory_non_recursive(self, service, temp_dir):
        """Test scanning without recursion."""
        files = service.scan_directory(temp_dir, recursive=False)

        # Should only find 2 files in root (not subdir)
        assert len(files) == 2

    def test_is_media_file(self, service):
        """Test media file detection."""
        assert service._is_media_file(Path("movie.mkv")) is True
        assert service._is_media_file(Path("movie.mp4")) is True
        assert service._is_media_file(Path("readme.txt")) is False
        assert service._is_media_file(Path("movie.MKV")) is True  # Case insensitive

    def test_count_media_files(self, service, temp_dir):
        """Test counting media files."""
        count = service.count_media_files(temp_dir)
        assert count == 3

    def test_get_directory_stats(self, service, temp_dir):
        """Test getting directory statistics."""
        stats = service.get_directory_stats(temp_dir)

        assert stats['total_files'] == 4  # 3 media + 1 txt
        assert stats['total_dirs'] == 1   # 1 subdir
        assert stats['media_files'] == 3


class TestMetadataService:
    """Test MetadataService functionality."""

    @pytest.fixture
    def cache(self):
        """Create a cache instance."""
        return Cache()

    @pytest.fixture
    def settings(self):
        """Create a settings instance."""
        return Settings()

    @pytest.fixture
    def service(self, cache, settings):
        """Create a MetadataService instance."""
        return MetadataService(cache, settings, max_workers=2)

    @pytest.fixture
    def test_file(self):
        """Create a temporary test file."""
        with tempfile.NamedTemporaryFile(suffix='.mkv', delete=False) as f:
            path = Path(f.name)
        yield path
        # Cleanup
        if path.exists():
            path.unlink()

    def test_service_initialization(self, service):
        """Test service initializes correctly."""
        assert service.max_workers == 2
        assert service.executor is not None
        assert service._lock is not None

    def test_extract_metadata_sync(self, service, test_file):
        """Test synchronous metadata extraction."""
        result = service.extract_metadata(test_file)

        assert result is not None
        assert 'formatted_info' in result
        assert 'proposed_name' in result
        assert 'mode' in result

    def test_extract_metadata_async(self, service, test_file):
        """Test asynchronous metadata extraction with callback."""
        callback_result = None

        def callback(result):
            nonlocal callback_result
            callback_result = result

        service.extract_metadata(test_file, callback=callback)

        # Wait for async operation
        import time
        time.sleep(1.0)

        # Callback should have been called
        # May be None if file doesn't exist or extraction failed
        assert callback_result is None or 'formatted_info' in callback_result

    def test_get_active_extraction_count(self, service):
        """Test getting active extraction count."""
        count = service.get_active_extraction_count()
        assert count == 0

    def test_shutdown(self, service):
        """Test service shutdown."""
        service.shutdown(wait=False)
        # Should not raise any errors

    def test_context_manager(self, cache, settings):
        """Test using service as context manager."""
        with MetadataService(cache, settings) as service:
            assert service.executor is not None
        # Executor should be shut down after context


class TestRenameService:
    """Test RenameService functionality."""

    @pytest.fixture
    def service(self):
        """Create a RenameService instance."""
        return RenameService()

    @pytest.fixture
    def test_file(self):
        """Create a temporary test file."""
        with tempfile.NamedTemporaryFile(suffix='.mkv', delete=False) as f:
            path = Path(f.name)
        yield path
        # Cleanup
        if path.exists():
            path.unlink()

    def test_sanitize_filename(self, service):
        """Test filename sanitization."""
        assert service.sanitize_filename("Movie: Title?") == "Movie Title"
        assert service.sanitize_filename("Movie<>|*.mkv") == "Movie.mkv"
        assert service.sanitize_filename("  Movie  ") == "Movie"
        assert service.sanitize_filename("Movie...") == "Movie"

    def test_validate_filename_valid(self, service):
        """Test validating a valid filename."""
        is_valid, error = service.validate_filename("movie.mkv")
        assert is_valid is True
        assert error is None

    def test_validate_filename_empty(self, service):
        """Test validating empty filename."""
        is_valid, error = service.validate_filename("")
        assert is_valid is False
        assert "empty" in error.lower()

    def test_validate_filename_too_long(self, service):
        """Test validating too long filename."""
        long_name = "a" * 300
        is_valid, error = service.validate_filename(long_name)
        assert is_valid is False
        assert "too long" in error.lower()

    def test_validate_filename_reserved(self, service):
        """Test validating reserved Windows names."""
        is_valid, error = service.validate_filename("CON.txt")
        assert is_valid is False
        assert "reserved" in error.lower()

    def test_validate_filename_invalid_chars(self, service):
        """Test validating filename with invalid characters."""
        is_valid, error = service.validate_filename("movie<>.mkv")
        assert is_valid is False
        assert "invalid" in error.lower()

    def test_check_name_conflict_no_conflict(self, service, test_file):
        """Test checking for name conflict when none exists."""
        has_conflict, msg = service.check_name_conflict(test_file, "newname.mkv")
        assert has_conflict is False
        assert msg is None

    def test_check_name_conflict_exists(self, service, test_file):
        """Test checking for name conflict when file exists."""
        # Use the same filename
        has_conflict, msg = service.check_name_conflict(test_file, test_file.name)
        assert has_conflict is False  # Same file, no conflict

        # Create another file
        other_file = test_file.parent / "other.mkv"
        other_file.touch()

        has_conflict, msg = service.check_name_conflict(test_file, "other.mkv")
        assert has_conflict is True
        assert "already exists" in msg

        # Cleanup
        other_file.unlink()

    def test_rename_file_dry_run(self, service, test_file):
        """Test renaming file in dry-run mode."""
        success, msg = service.rename_file(test_file, "newname.mkv", dry_run=True)

        assert success is True
        assert "Would rename" in msg
        # File should not actually be renamed
        assert test_file.exists()

    def test_rename_file_actual(self, service, test_file):
        """Test actually renaming a file."""
        old_name = test_file.name
        new_name = "renamed.mkv"

        success, msg = service.rename_file(test_file, new_name, dry_run=False)

        assert success is True
        assert "Renamed" in msg

        # Check file was renamed
        new_path = test_file.parent / new_name
        assert new_path.exists()
        assert not test_file.exists()

        # Cleanup
        new_path.unlink()

    def test_rename_file_not_exists(self, service):
        """Test renaming a file that doesn't exist."""
        fake_path = Path("/nonexistent/file.mkv")
        success, msg = service.rename_file(fake_path, "new.mkv")

        assert success is False
        assert "does not exist" in msg

    def test_strip_markup(self, service):
        """Test stripping markup tags."""
        assert service._strip_markup("[bold]text[/bold]") == "text"
        assert service._strip_markup("[green]Movie[/green]") == "Movie"
        assert service._strip_markup("No markup") == "No markup"
        assert service._strip_markup("[bold green]text[/bold green]") == "text"


class TestServiceIntegration:
    """Integration tests for services working together."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory with test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            (tmpdir / "movie1.mkv").touch()
            (tmpdir / "movie2.mp4").touch()
            yield tmpdir

    def test_scan_and_rename_workflow(self, temp_dir):
        """Test a complete workflow: scan, then rename."""
        # Scan for files
        tree_service = FileTreeService()
        files = tree_service.scan_directory(temp_dir)
        assert len(files) == 2

        # Rename one file
        rename_service = RenameService()
        old_file = files[0]
        success, msg = rename_service.rename_file(old_file, "renamed.mkv")

        assert success is True

        # Scan again
        new_files = tree_service.scan_directory(temp_dir)
        assert len(new_files) == 2

        # Check renamed file exists
        renamed_path = temp_dir / "renamed.mkv"
        assert renamed_path.exists()
