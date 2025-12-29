from pathlib import Path
import logging
import os
from ..decorators import cached_method

# Set up logging conditionally
if os.getenv('FORMATTER_LOG', '0') == '1':
    logging.basicConfig(filename='formatter.log', level=logging.INFO, 
                        format='%(asctime)s - %(levelname)s - %(message)s')
else:
    logging.basicConfig(level=logging.CRITICAL)  # Disable logging


class FileInfoExtractor:
    """Class to extract file information"""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self._size = file_path.stat().st_size
        self._modification_time = file_path.stat().st_mtime
        self._file_name = file_path.name
        self._file_path = str(file_path)
        self._cache = {}  # Internal cache for method results
        logging.info(f"FileInfoExtractor: file_name={self._file_name!r}, file_path={self._file_path!r}")

    @cached_method()
    def extract_size(self) -> int:
        """Extract file size in bytes"""
        return self._size

    @cached_method()
    def extract_modification_time(self) -> float:
        """Extract file modification time"""
        return self._modification_time

    @cached_method()
    def extract_file_name(self) -> str:
        """Extract file name"""
        return self._file_name

    @cached_method()
    def extract_file_path(self) -> str:
        """Extract full file path as string"""
        return self._file_path

    @cached_method()
    def extract_extension(self) -> str:
        """Extract file extension without the dot"""
        return self.file_path.suffix.lower().lstrip('.')