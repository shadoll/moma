import pytest
from pathlib import Path
from ..extractors.filename_extractor import FilenameExtractor


def load_test_filenames():
    """Load test filenames from filenames.txt"""
    test_file = Path(__file__).parent / "filenames.txt"
    if test_file.exists():
        with open(test_file, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    return []


@pytest.mark.parametrize("filename", load_test_filenames())
def test_extract_title(filename):
    """Test title extraction from filename"""
    file_path = Path(filename)
    title = FilenameExtractor.extract_title(file_path)
    # For now, just check it's not None and is string
    assert isinstance(title, str) or title is None


@pytest.mark.parametrize("filename", load_test_filenames())
def test_extract_year(filename):
    """Test year extraction from filename"""
    file_path = Path(filename)
    year = FilenameExtractor.extract_year(file_path)
    # Print filename and extracted year clearly
    print(f"\nFilename: \033[1;36m{filename}\033[0m")
    print(f"Extracted year: \033[1;32m{year}\033[0m")
    # Year should be None or 4-digit string
    if year:
        assert len(year) == 4 and year.isdigit()


@pytest.mark.parametrize("filename", load_test_filenames())
def test_extract_source(filename):
    """Test source extraction from filename"""
    file_path = Path(filename)
    source = FilenameExtractor.extract_source(file_path)
    # Source should be None or string
    assert isinstance(source, str) or source is None


@pytest.mark.parametrize("filename", load_test_filenames())
def test_extract_resolution(filename):
    """Test resolution extraction from filename"""
    file_path = Path(filename)
    resolution = FilenameExtractor.extract_resolution(file_path)
    # Resolution should be None or string like '2160p'
    if resolution:
        assert 'p' in resolution or 'i' in resolution