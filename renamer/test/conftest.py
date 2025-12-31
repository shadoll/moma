# conftest.py - pytest configuration
import os
import sys
import json
import pytest
from pathlib import Path

# Force UTF-8 encoding for all I/O operations
os.environ['PYTHONIOENCODING'] = 'utf-8'
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Configure pytest to handle Unicode properly
def pytest_configure(config):
    # Ensure UTF-8 encoding for test output
    config.option.capture = 'no'  # Don't capture output to avoid encoding issues


# Dataset loading helpers
@pytest.fixture
def datasets_dir():
    """Get the datasets directory path."""
    return Path(__file__).parent / "datasets"


@pytest.fixture
def load_filename_patterns(datasets_dir):
    """Load filename pattern test cases from JSON dataset.

    Returns:
        list: List of test case dictionaries with 'filename' and 'expected' keys
    """
    dataset_file = datasets_dir / "filenames" / "filename_patterns.json"
    with open(dataset_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['test_cases']


@pytest.fixture
def load_frame_class_tests(datasets_dir):
    """Load frame class test cases from JSON dataset.

    Returns:
        list: List of frame class test dictionaries
    """
    dataset_file = datasets_dir / "mediainfo" / "frame_class_tests.json"
    with open(dataset_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_dataset(dataset_name: str) -> dict:
    """Load a dataset by name.

    Args:
        dataset_name: Name of the dataset file (without .json extension)

    Returns:
        dict: Loaded dataset

    Example:
        >>> data = load_dataset('filename_patterns')
        >>> test_cases = data['test_cases']
    """
    datasets_dir = Path(__file__).parent / "datasets"

    # Search for the dataset in subdirectories
    for subdir in ['filenames', 'mediainfo', 'expected_results']:
        dataset_file = datasets_dir / subdir / f"{dataset_name}.json"
        if dataset_file.exists():
            with open(dataset_file, 'r', encoding='utf-8') as f:
                return json.load(f)

    raise FileNotFoundError(f"Dataset '{dataset_name}' not found in datasets directory")


def get_test_file_path(filename: str) -> Path:
    """Get path to a test file in the datasets directory.

    Args:
        filename: Name of the test file

    Returns:
        Path: Full path to the test file

    Example:
        >>> path = get_test_file_path('test.mkv')
        >>> # Returns: /path/to/test/datasets/sample_mediafiles/test.mkv
    """
    return Path(__file__).parent / "datasets" / "sample_mediafiles" / filename