import pytest
from pathlib import Path
from renamer.extractors.mediainfo_extractor import MediaInfoExtractor


class TestMediaInfoExtractor:
    @pytest.fixture
    def extractor(self):
        return MediaInfoExtractor()

    @pytest.fixture
    def test_file(self):
        """Use the filenames.txt file for testing"""
        return Path(__file__).parent / "filenames.txt"

    def test_extract_resolution(self, extractor, test_file):
        """Test extracting resolution from media info"""
        resolution = extractor.extract_resolution(test_file)
        # Text files don't have video resolution
        assert resolution is None

    def test_extract_hdr(self, extractor, test_file):
        """Test extracting HDR info"""
        hdr = extractor.extract_hdr(test_file)
        # Text files don't have HDR
        assert hdr is None

    def test_extract_audio_langs(self, extractor, test_file):
        """Test extracting audio languages"""
        langs = extractor.extract_audio_langs(test_file)
        # Text files don't have audio tracks
        assert langs == ''