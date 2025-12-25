import mutagen
from pathlib import Path
from ..constants import MEDIA_TYPES


class MetadataExtractor:
    """Class to extract information from file metadata"""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        try:
            self.info = mutagen.File(file_path) # type: ignore
        except Exception:
            self.info = None

    def extract_title(self) -> str | None:
        """Extract title from metadata"""
        if self.info:
            return getattr(self.info, 'title', None) or getattr(self.info, 'get', lambda x, default=None: default)('title', [None])[0]  # type: ignore
        return None

    def extract_duration(self) -> float | None:
        """Extract duration from metadata"""
        if self.info:
            return getattr(self.info, 'length', None)
        return None

    def extract_artist(self) -> str | None:
        """Extract artist from metadata"""
        if self.info:
            return getattr(self.info, 'artist', None) or getattr(self.info, 'get', lambda x, default=None: default)('artist', [None])[0]  # type: ignore
        return None

    def extract_all_metadata(self) -> dict:
        """Extract all metadata"""
        return {
            'title': self.extract_title(),
            'duration': self.extract_duration(),
            'artist': self.extract_artist()
        }

    def extract_meta_type(self) -> str:
        """Extract meta type from metadata"""
        if self.info:
            return type(self.info).__name__
        return self._detect_by_mime()

    def extract_meta_description(self) -> str:
        """Extract meta description"""
        meta_type = self.extract_meta_type()
        return {info['meta_type']: info['description'] for info in MEDIA_TYPES.values()}.get(meta_type, f'Unknown type {meta_type}')

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