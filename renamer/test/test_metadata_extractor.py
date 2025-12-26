import pytest
from pathlib import Path
from renamer.extractors.metadata_extractor import MetadataExtractor


class TestMetadataExtractor:
    @pytest.fixture
    def extractor(self, test_file):
        return MetadataExtractor(test_file)

    @pytest.fixture
    def test_file(self):
        """Use the filenames.txt file for testing"""
        return Path(__file__).parent / "filenames.txt"

    def test_extract_title(self, extractor):
        """Test extracting title from metadata"""
        title = extractor.extract_title()
        # Text files don't have metadata, so should be None
        assert title is None

    def test_extract_duration(self, extractor):
        """Test extracting duration from metadata"""
        duration = extractor.extract_duration()
        # Text files don't have duration
        assert duration is None

    def test_extract_artist(self, extractor):
        """Test extracting artist from metadata"""
        artist = extractor.extract_artist()
        # Text files don't have artist
        assert artist is None