import mutagen
from pathlib import Path


class MetadataExtractor:
    """Class to extract information from file metadata"""

    @staticmethod
    def extract_title(file_path: Path) -> str | None:
        """Extract title from metadata"""
        try:
            info = mutagen.File(file_path)
            if info:
                return getattr(info, 'title', None) or getattr(info, 'get', lambda x, default=None: default)('title', [None])[0]
        except:
            pass
        return None

    @staticmethod
    def extract_duration(file_path: Path) -> float | None:
        """Extract duration from metadata"""
        try:
            info = mutagen.File(file_path)
            if info:
                return getattr(info, 'length', None)
        except:
            pass
        return None

    @staticmethod
    def extract_artist(file_path: Path) -> str | None:
        """Extract artist from metadata"""
        try:
            info = mutagen.File(file_path)
            if info:
                return getattr(info, 'artist', None) or getattr(info, 'get', lambda x, default=None: default)('artist', [None])[0]
        except:
            pass
        return None

    @staticmethod
    def extract_all_metadata(file_path: Path) -> dict:
        """Extract all metadata"""
        return {
            'title': MetadataExtractor.extract_title(file_path),
            'duration': MetadataExtractor.extract_duration(file_path),
            'artist': MetadataExtractor.extract_artist(file_path)
        }