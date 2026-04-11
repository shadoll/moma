import pytest
import json
from pathlib import Path
from src.extractors.metadata_extractor import MetadataExtractor


class TestMetadataExtractor:
    """
    Note: MetadataExtractor requires actual media files with embedded metadata.
    Since we don't have real media files in the repository, these tests verify
    the extractor handles missing/empty metadata gracefully.

    Real integration tests with actual media files should be done manually.
    """

    @pytest.fixture
    def dataset(self):
        """Load filename patterns dataset for test data"""
        dataset_file = Path(__file__).parent / "datasets" / "filenames" / "filename_patterns.json"
        with open(dataset_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    @pytest.fixture
    def test_file(self):
        """Use the dataset JSON file (has no media metadata)"""
        return Path(__file__).parent / "datasets" / "filenames" / "filename_patterns.json"

    @pytest.fixture
    def extractor(self, test_file):
        return MetadataExtractor(test_file)

    def test_extract_title(self, extractor):
        """Test extracting title from metadata - should return None for non-media files"""
        title = extractor.extract_title()
        assert title is None

    def test_extract_duration(self, extractor):
        """Test extracting duration from metadata - should return None for non-media files"""
        duration = extractor.extract_duration()
        assert duration is None

    def test_extract_artist(self, extractor):
        """Test extracting artist from metadata - should return None for non-media files"""
        artist = extractor.extract_artist()
        assert artist is None

    def test_extract_meta_type(self, extractor):
        """Test extracting meta type - should detect file type"""
        meta_type = extractor.extract_meta_type()
        # Should return some string describing file type
        assert isinstance(meta_type, str)

    def test_handles_missing_metadata(self, test_file):
        """Test that extractor doesn't crash on files without metadata"""
        extractor = MetadataExtractor(test_file)
        # Should not raise exceptions
        assert extractor.extract_title() is None
        assert extractor.extract_duration() is None
        assert extractor.extract_artist() is None

    def test_handles_nonexistent_file(self):
        """Test that extractor handles nonexistent files gracefully"""
        fake_file = Path("/nonexistent/file.mkv")
        extractor = MetadataExtractor(fake_file)
        # Should return None instead of crashing
        assert extractor.extract_title() is None

    def test_dataset_available(self, dataset):
        """Verify test dataset is available and valid"""
        assert 'test_cases' in dataset
        assert len(dataset['test_cases']) > 0
        # Verify dataset has expected structure
        first_case = dataset['test_cases'][0]
        assert 'filename' in first_case
        assert 'expected' in first_case


# Note: Full integration tests with real media files should include:
# - Extracting metadata from actual MKV/MP4 files
# - Testing with files that have metadata tags
# - Verifying metadata extraction accuracy
# These tests require actual media files which are not in the repository.
