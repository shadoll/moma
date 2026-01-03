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
        self._file_path = file_path
        self._stat = file_path.stat()
        self._cache: dict[str, any] = {}  # Internal cache for method results

    @cached_method()
    def extract_size(self) -> int:
        """Extract file size in bytes.

        Returns:
            File size in bytes as an integer
        """
        return self._stat.st_size

    @cached_method()
    def extract_modification_time(self) -> float:
        """Extract file modification time.

        Returns:
            Unix timestamp (seconds since epoch) as a float
        """
        return self._stat.st_mtime

    @cached_method()
    def extract_file_name(self) -> str:
        """Extract file name (basename).

        Returns:
            File name including extension (e.g., "movie.mkv")
        """
        return self._file_path.name

    @cached_method()
    def extract_file_path(self) -> str:
        """Extract full file path as string.

        Returns:
            Absolute file path as a string
        """
        return str(self._file_path)

    @cached_method()
    def extract_extension(self) -> str:
        """Extract file extension without the dot.

        Returns:
            File extension in lowercase without leading dot (e.g., "mkv", "mp4")
        """
        return self._file_path.suffix.lower().lstrip('.')