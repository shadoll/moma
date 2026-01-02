"""Embedded metadata extractor using Mutagen.

This module provides the MetadataExtractor class for reading embedded
metadata tags from media files using the Mutagen library.
"""

import mutagen
import logging
from pathlib import Path
from ..constants import MEDIA_TYPES
from ..decorators import cached_method

logger = logging.getLogger(__name__)


class MetadataExtractor:
    """Extractor for embedded metadata tags from media files.

    This class uses the Mutagen library to read embedded metadata tags
    such as title, artist, and duration. Falls back to MIME type detection
    when Mutagen cannot read the file.

    Attributes:
        file_path: Path object pointing to the file
        info: Mutagen file info object, or None if file cannot be read
        _cache: Internal cache for method results

    Example:
        >>> from pathlib import Path
        >>> extractor = MetadataExtractor(Path("movie.mkv"))
        >>> title = extractor.extract_title()
        >>> duration = extractor.extract_duration()
    """

    def __init__(self, file_path: Path):
        """Initialize the MetadataExtractor.

        Args:
            file_path: Path object pointing to the media file
        """
        self.file_path = file_path
        self._cache: dict[str, any] = {}  # Internal cache for method results
        try:
            self.info = mutagen.File(file_path) # type: ignore
        except Exception as e:
            logger.debug(f"Failed to read metadata from {file_path}: {e}")
            self.info = None

    @cached_method()
    def extract_title(self) -> str | None:
        """Extract title from embedded metadata tags.

        Returns:
            Title string if found in metadata, None otherwise
        """
        if self.info:
            return getattr(self.info, 'title', None) or getattr(self.info, 'get', lambda x, default=None: default)('title', [None])[0]  # type: ignore
        return None

    @cached_method()
    def extract_duration(self) -> float | None:
        """Extract duration from metadata.

        Returns:
            Duration in seconds as a float, or None if not available
        """
        if self.info:
            return getattr(self.info, 'length', None)
        return None

    @cached_method()
    def extract_artist(self) -> str | None:
        """Extract artist from embedded metadata tags.

        Returns:
            Artist string if found in metadata, None otherwise
        """
        if self.info:
            return getattr(self.info, 'artist', None) or getattr(self.info, 'get', lambda x, default=None: default)('artist', [None])[0]  # type: ignore
        return None

    @cached_method()
    def extract_meta_type(self) -> str:
        """Extract metadata container type.

        Returns the Mutagen class name (e.g., "FLAC", "MP4") if available,
        otherwise falls back to MIME type detection.

        Returns:
            Container type name, or "Unknown" if cannot be determined
        """
        if self.info:
            return type(self.info).__name__
        return self._detect_by_mime()

    def _detect_by_mime(self) -> str:
        """Detect metadata type by MIME type.

        Uses python-magic library to detect file MIME type and maps it
        to a metadata container type.

        Returns:
            Container type name based on MIME type, or "Unknown" if detection fails
        """
        try:
            import magic
            mime = magic.from_file(str(self.file_path), mime=True)
            for ext, info in MEDIA_TYPES.items():
                if info['mime'] == mime:
                    return info['meta_type']
            return 'Unknown'
        except Exception as e:
            logger.debug(f"Failed to detect MIME type for {self.file_path}: {e}")
            return 'Unknown'