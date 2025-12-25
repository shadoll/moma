import pytest
from pathlib import Path
from renamer.extractors.fileinfo_extractor import FileInfoExtractor


class TestFileInfoExtractor:
    @pytest.fixture
    def test_file(self):
        """Use the filenames.txt file for testing"""
        return Path(__file__).parent / "filenames.txt"

    def test_extract_size(self, test_file):
        """Test extracting file size"""
        size = FileInfoExtractor.extract_size(test_file)
        assert isinstance(size, int)
        assert size > 0

    def test_extract_modification_time(self, test_file):
        """Test extracting modification time"""
        mtime = FileInfoExtractor.extract_modification_time(test_file)
        assert isinstance(mtime, float)
        assert mtime > 0

    def test_extract_file_name(self, test_file):
        """Test extracting file name"""
        name = FileInfoExtractor.extract_file_name(test_file)
        assert isinstance(name, str)
        assert name == "filenames.txt"

    def test_extract_file_path(self, test_file):
        """Test extracting file path"""
        path = FileInfoExtractor.extract_file_path(test_file)
        assert isinstance(path, str)
        assert "filenames.txt" in path
        assert str(test_file) == path