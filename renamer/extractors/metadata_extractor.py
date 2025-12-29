import mutagen
from pathlib import Path
from ..constants import MEDIA_TYPES
from ..decorators import cached_method


class MetadataExtractor:
    """Class to extract information from file metadata"""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self._cache = {}  # Internal cache for method results
        try:
            self.info = mutagen.File(file_path) # type: ignore
        except Exception:
            self.info = None

    @cached_method()
    def extract_title(self) -> str | None:
        """Extract title from metadata"""
        if self.info:
            return getattr(self.info, 'title', None) or getattr(self.info, 'get', lambda x, default=None: default)('title', [None])[0]  # type: ignore
        return None

    @cached_method()
    def extract_duration(self) -> float | None:
        """Extract duration from metadata"""
        if self.info:
            return getattr(self.info, 'length', None)
        return None

    @cached_method()
    def extract_artist(self) -> str | None:
        """Extract artist from metadata"""
        if self.info:
            return getattr(self.info, 'artist', None) or getattr(self.info, 'get', lambda x, default=None: default)('artist', [None])[0]  # type: ignore
        return None

    @cached_method()
    def extract_meta_type(self) -> str:
        """Extract meta type from metadata"""
        if self.info:
            return type(self.info).__name__
        return self._detect_by_mime()

    def _detect_by_mime(self) -> str:
        """Detect meta type by MIME"""
        try:
            import magic
            mime = magic.from_file(str(self.file_path), mime=True)
            for ext, info in MEDIA_TYPES.items():
                if info['mime'] == mime:
                    return info['meta_type']
            return 'Unknown'
        except Exception:
            return 'Unknown'