import pytest
from pathlib import Path
from renamer.extractors.metadata_extractor import MetadataExtractor


class TestMetadataExtractor:
    @pytest.fixture
    def test_file(self):
        """Use the filenames.txt file for testing"""
        return Path(__file__).parent / "filenames.txt"

    def test_extract_title(self, test_file):
        """Test extracting title from metadata"""
        title = MetadataExtractor.extract_title(test_file)
        # Text files don't have metadata, so should be None
        assert title is None

    def test_extract_duration(self, test_file):
        """Test extracting duration from metadata"""
        duration = MetadataExtractor.extract_duration(test_file)
        # Text files don't have duration
        assert duration is None

    def test_extract_artist(self, test_file):
        """Test extracting artist from metadata"""
        artist = MetadataExtractor.extract_artist(test_file)
        # Text files don't have artist
        assert artist is None

    def test_extract_all_metadata(self, test_file):
        """Test extracting all metadata"""
        metadata = MetadataExtractor.extract_all_metadata(test_file)
        expected = {
            'title': None,
            'duration': None,
            'artist': None
        }
        assert metadata == expected