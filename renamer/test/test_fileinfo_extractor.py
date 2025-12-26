import pytest
from pathlib import Path
from renamer.extractors.fileinfo_extractor import FileInfoExtractor


class TestFileInfoExtractor:
    @pytest.fixture
    def extractor(self, test_file):
        return FileInfoExtractor(test_file)

    @pytest.fixture
    def test_file(self):
        """Use the filenames.txt file for testing"""
        return Path(__file__).parent / "filenames.txt"

    def test_extract_size(self, extractor):
        """Test extracting file size"""
        size = extractor.extract_size()
        assert isinstance(size, int)
        assert size > 0

    def test_extract_modification_time(self, extractor):
        """Test extracting modification time"""
        mtime = extractor.extract_modification_time()
        assert isinstance(mtime, float)
        assert mtime > 0

    def test_extract_file_name(self, extractor):
        """Test extracting file name"""
        name = extractor.extract_file_name()
        assert isinstance(name, str)
        assert name == "filenames.txt"

    def test_extract_file_path(self, extractor):
        """Test extracting file path"""
        path = extractor.extract_file_path()
        assert isinstance(path, str)
        assert "filenames.txt" in path