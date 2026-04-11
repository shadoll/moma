#!/usr/bin/env python3
"""Test script for MediaInfo frame class detection by resolution"""

import json
import pytest
from unittest.mock import MagicMock
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from renamer.extractors.mediainfo_extractor import MediaInfoExtractor
from pathlib import Path

# Load test cases from dataset using context manager
test_cases_file = Path(__file__).parent / 'datasets' / 'mediainfo' / 'frame_class_tests.json'
with open(test_cases_file, 'r', encoding='utf-8') as f:
    test_cases = json.load(f)

@pytest.mark.parametrize("test_case", test_cases, ids=[tc['testname'] for tc in test_cases])
def test_frame_class_detection(test_case):
    """Test frame class detection for various resolutions"""

    testname = test_case['testname']
    width, height = test_case['resolution']
    interlaced = test_case['interlaced']
    expected = test_case['expected_frame_class']

    # Create a mock MediaInfoExtractor
    extractor = MagicMock(spec=MediaInfoExtractor)
    from pathlib import Path
    extractor.file_path = Path(f"test_{testname}")  # Set a unique file_path for caching

    # Mock the video_tracks
    mock_track = MagicMock()
    mock_track.height = height
    mock_track.width = width
    mock_track.interlaced = 'Yes' if interlaced else 'No'

    extractor.video_tracks = [mock_track]
    extractor.extract_resolution.return_value = (height, width)
    extractor._video_tracks.return_value = [mock_track]
    extractor.extract_interlaced.return_value = interlaced

    # Test the method
    actual = MediaInfoExtractor.extract_frame_class(extractor)

    assert actual == expected, f"{testname}: expected {expected}, got {actual}"
