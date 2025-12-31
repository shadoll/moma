import pytest
from pathlib import Path
from unittest.mock import MagicMock
from renamer.extractors.mediainfo_extractor import MediaInfoExtractor
import json


class TestMediaInfoExtractor:
    @pytest.fixture
    def extractor(self, test_file):
        return MediaInfoExtractor(test_file)

    @pytest.fixture
    def test_file(self):
        """Use the filenames.txt file for testing"""
        return Path(__file__).parent / "filenames.txt"

    @pytest.fixture
    def frame_class_cases(self):
        """Load test cases for frame class extraction"""
        # Try the expected file first, fallback to the main frame class test file
        cases_file = Path(__file__).parent / "test_mediainfo_frame_class_cases.json"
        if not cases_file.exists():
            cases_file = Path(__file__).parent / "test_mediainfo_frame_class.json"

        if not cases_file.exists():
            pytest.skip(f"Test case file not found: {cases_file}")

        with open(cases_file, 'r') as f:
            return json.load(f)

    def test_extract_resolution(self, extractor, test_file):
        """Test extracting resolution from media info"""
        resolution = extractor.extract_resolution()
        # Text files don't have video resolution
        assert resolution is None

    def test_extract_hdr(self, extractor, test_file):
        """Test extracting HDR info"""
        hdr = extractor.extract_hdr()
        # Text files don't have HDR
        assert hdr is None

    def test_extract_audio_langs(self, extractor, test_file):
        """Test extracting audio languages"""
        langs = extractor.extract_audio_langs()
        # Text files don't have audio tracks
        assert langs is None

    def test_extract_anamorphic(self, extractor, test_file):
        """Test extracting anamorphic info"""
        anamorphic = extractor.extract_anamorphic()
        # Text files don't have video tracks
        assert anamorphic is None

    def test_extract_extension(self, extractor, test_file):
        """Test extracting extension"""
        extension = extractor.extract_extension()
        # For text file, should return None since no media info
        assert extension is None

    def test_is_3d(self, extractor, test_file):
        """Test checking if video is 3D"""
        is_3d = extractor.is_3d()
        # Text files don't have video tracks
        assert is_3d is False

    def test_extract_frame_class_parametrized(self, frame_class_cases):
        """Test extracting frame class from various resolutions using fixture"""
        for case in frame_class_cases:
            # Create a mock extractor with the test resolution
            extractor = MagicMock(spec=MediaInfoExtractor)
            extractor.file_path = Path(f"test_{case['testname']}")

            # Mock the video_tracks with proper attributes
            mock_track = MagicMock()
            mock_track.height = case["resolution"][1]
            mock_track.width = case["resolution"][0]
            mock_track.interlaced = 'Yes' if case["interlaced"] else 'No'

            extractor.video_tracks = [mock_track]

            # Call the actual method
            result = MediaInfoExtractor.extract_frame_class(extractor)
            assert result == case["expected_frame_class"], f"Failed for {case['testname']}: expected {case['expected_frame_class']}, got {result}"