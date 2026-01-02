"""File system information extractor.

This module provides the FileInfoExtractor class for extracting basic
file system metadata such as size, timestamps, paths, and extensions.
"""

from pathlib import Path
import logging
import os
from ..cache import cached_method

# Set up logging conditionally
if os.getenv('FORMATTER_LOG', '0') == '1':
    logging.basicConfig(filename='formatter.log', level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
else:
    logging.basicConfig(level=logging.CRITICAL)  # Disable logging


class FileInfoExtractor:
    """Extractor for basic file system information.

    This class extracts file system metadata including size, modification time,
    file name, path, and extension. All extraction methods are cached for
    performance.

    Attributes:
        file_path: Path object pointing to the file
        _size: Cached file size in bytes
        _modification_time: Cached modification timestamp
        _file_name: Cached file name
        _file_path: Cached full file path as string
        _cache: Internal cache for method results

    Example:
        >>> from pathlib import Path
        >>> extractor = FileInfoExtractor(Path("movie.mkv"))
        >>> size = extractor.extract_size()  # Returns size in bytes
        >>> name = extractor.extract_file_name()  # Returns "movie.mkv"
    """

    def __init__(self, file_path: Path):
        """Initialize the FileInfoExtractor.

        Args:
            file_path: Path object pointing to the file to extract info from
        """
        self.file_path = file_path
        self._size = file_path.stat().st_size
        self._modification_time = file_path.stat().st_mtime
        self._file_name = file_path.name
        self._file_path = str(file_path)
        self._cache: dict[str, any] = {}  # Internal cache for method results
        logging.info(f"FileInfoExtractor: file_name={self._file_name!r}, file_path={self._file_path!r}")

    @cached_method()
    def extract_size(self) -> int:
        """Extract file size in bytes.

        Returns:
            File size in bytes as an integer
        """
        return self._size

    @cached_method()
    def extract_modification_time(self) -> float:
        """Extract file modification time.

        Returns:
            Unix timestamp (seconds since epoch) as a float
        """
        return self._modification_time

    @cached_method()
    def extract_file_name(self) -> str:
        """Extract file name (basename).

        Returns:
            File name including extension (e.g., "movie.mkv")
        """
        return self._file_name

    @cached_method()
    def extract_file_path(self) -> str:
        """Extract full file path as string.

        Returns:
            Absolute file path as a string
        """
        return self._file_path

    @cached_method()
    def extract_extension(self) -> str:
        """Extract file extension without the dot.

        Returns:
            File extension in lowercase without leading dot (e.g., "mkv", "mp4")
        """
        return self.file_path.suffix.lower().lstrip('.')