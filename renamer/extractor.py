from pathlib import Path
from .extractors.filename_extractor import FilenameExtractor
from .extractors.metadata_extractor import MetadataExtractor
from .extractors.mediainfo_extractor import MediaInfoExtractor


class MediaExtractor:
    """Class to extract various metadata from media files using specialized extractors"""

    def __init__(self):
        self.mediainfo_extractor = MediaInfoExtractor()

    def extract_title(self, file_path: Path) -> str | None:
        """Extract movie title from metadata or filename"""
        # Try metadata first
        title = MetadataExtractor.extract_title(file_path)
        if title:
            return title
        # Fallback to filename
        return FilenameExtractor.extract_title(file_path)

    def extract_year(self, file_path: Path) -> str | None:
        """Extract year from filename"""
        return FilenameExtractor.extract_year(file_path)

    def extract_source(self, file_path: Path) -> str | None:
        """Extract video source from filename"""
        return FilenameExtractor.extract_source(file_path)

    def extract_frame_class(self, file_path: Path) -> str | None:
        """Extract frame class from media info or filename"""
        # Try media info first
        frame_class = self.mediainfo_extractor.extract_frame_class(file_path)
        if frame_class:
            return frame_class
        # Fallback to filename
        return FilenameExtractor.extract_frame_class(file_path)

    def extract_resolution(self, file_path: Path) -> str | None:
        """Extract actual video resolution (WIDTHxHEIGHT) from media info"""
        return self.mediainfo_extractor.extract_resolution(file_path)

    def extract_aspect_ratio(self, file_path: Path) -> str | None:
        """Extract video aspect ratio from media info"""
        return self.mediainfo_extractor.extract_aspect_ratio(file_path)

    def extract_hdr(self, file_path: Path) -> str | None:
        """Extract HDR info from media info"""
        return self.mediainfo_extractor.extract_hdr(file_path)

    def extract_audio_langs(self, file_path: Path) -> str:
        """Extract audio languages from media info"""
        return self.mediainfo_extractor.extract_audio_langs(file_path)

    def extract_metadata(self, file_path: Path) -> dict:
        """Extract general metadata"""
        return MetadataExtractor.extract_all_metadata(file_path)

    def extract_all(self, file_path: Path) -> dict:
        """Extract all rename-related data"""
        return {
            'title': self.extract_title(file_path),
            'year': self.extract_year(file_path),
            'source': self.extract_source(file_path),
            'frame_class': self.extract_frame_class(file_path),
            'resolution': self.extract_resolution(file_path),
            'aspect_ratio': self.extract_aspect_ratio(file_path),
            'hdr': self.extract_hdr(file_path),
            'audio_langs': self.extract_audio_langs(file_path),
            'metadata': self.extract_metadata(file_path)
        }