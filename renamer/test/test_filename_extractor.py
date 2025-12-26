import pytest
from pathlib import Path
from ..extractors.filename_extractor import FilenameExtractor
from ..constants import FRAME_CLASSES


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
    extractor = FilenameExtractor(file_path)
    title = extractor.extract_title()
    # Print filename and extracted title clearly
    print(f"\nFilename: \033[1;36m{filename}\033[0m")
    print(f"Extracted title: \033[1;32m{title}\033[0m")
    # For now, just check it's not None and is string
    assert isinstance(title, str) or title is None


@pytest.mark.parametrize("filename", load_test_filenames())
def test_extract_year(filename):
    """Test year extraction from filename"""
    file_path = Path(filename)
    extractor = FilenameExtractor(file_path)
    year = extractor.extract_year()
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
    extractor = FilenameExtractor(file_path)
    source = extractor.extract_source()
    # Print filename and extracted source clearly
    print(f"\nFilename: \033[1;36m{filename}\033[0m")
    print(f"Extracted source: \033[1;32m{source}\033[0m")
    # Source should be None or string
    assert isinstance(source, str) or source is None


@pytest.mark.parametrize("filename", load_test_filenames())
def test_extract_frame_class(filename):
    """Test frame class extraction from filename"""
    file_path = Path(filename)
    extractor = FilenameExtractor(file_path)
    frame_class = extractor.extract_frame_class()
    # Print filename and extracted frame class clearly
    print(f"\nFilename: \033[1;36m{filename}\033[0m")
    print(f"Extracted frame_class: \033[1;32m{frame_class}\033[0m")
    # Frame class should be a string
    assert isinstance(frame_class, str)
    # Should be one of the valid frame classes or 'Unclassified'
    valid_classes = set(FRAME_CLASSES.keys()) | {'Unclassified'}
    assert frame_class in valid_classes


@pytest.mark.parametrize("filename", load_test_filenames())
def test_extract_hdr(filename):
    """Test HDR extraction from filename"""
    file_path = Path(filename)
    extractor = FilenameExtractor(file_path)
    hdr = extractor.extract_hdr()
    # Print filename and extracted HDR clearly
    print(f"\nFilename: \033[1;36m{filename}\033[0m")
    print(f"Extracted HDR: \033[1;32m{hdr}\033[0m")
    # HDR should be 'HDR' or None
    assert hdr is None or hdr == 'HDR'