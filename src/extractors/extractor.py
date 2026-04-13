"""Media metadata extraction coordinator.

This module provides the MediaExtractor class which coordinates multiple
specialized extractors to gather comprehensive metadata about media files.
It implements a priority-based extraction system where data is retrieved
from the most appropriate source.
"""

from pathlib import Path
from .filename_extractor import FilenameExtractor
from .metadata_extractor import MetadataExtractor
from .mediainfo_extractor import MediaInfoExtractor
from .fileinfo_extractor import FileInfoExtractor
from .tmdb_extractor import TMDBExtractor
from .default_extractor import DefaultExtractor


class MediaExtractor:
    """Coordinator for extracting metadata from media files using multiple specialized extractors.

    This class manages a collection of specialized extractors and provides a unified
    interface for retrieving metadata. It implements a priority-based system where
    each type of data is retrieved from the most appropriate source.

    The extraction priority order varies by data type:
    - Title: TMDB → Metadata → Filename → Default
    - Year: Filename → Default
    - Technical info: MediaInfo → Default
    - File info: FileInfo → Default

    Attributes:
        file_path: Path to the media file
        filename_extractor: Extracts metadata from filename patterns
        metadata_extractor: Extracts embedded metadata tags
        mediainfo_extractor: Extracts technical media information
        fileinfo_extractor: Extracts basic file system information
        tmdb_extractor: Fetches metadata from The Movie Database API
        default_extractor: Provides fallback default values

    Example:
        >>> from pathlib import Path
        >>> extractor = MediaExtractor(Path("Movie (2020) [1080p].mkv"))
        >>> title = extractor.get("title")
        >>> year = extractor.get("year")
        >>> tracks = extractor.get("video_tracks")
    """

    def __init__(self, file_path: Path, use_cache: bool = True):
        self.file_path = file_path

        # Initialize all extractors - they use singleton Cache internally
        self.filename_extractor = FilenameExtractor(file_path, use_cache)
        self.metadata_extractor = MetadataExtractor(file_path, use_cache)
        self.mediainfo_extractor = MediaInfoExtractor(file_path, use_cache)
        self.fileinfo_extractor = FileInfoExtractor(file_path, use_cache)
        self.tmdb_extractor = TMDBExtractor(file_path, use_cache)
        self.default_extractor = DefaultExtractor()
        
        # Extractor mapping
        self._extractors = {
            "Metadata": self.metadata_extractor,
            "Filename": self.filename_extractor,
            "MediaInfo": self.mediainfo_extractor,
            "FileInfo": self.fileinfo_extractor,
            "TMDB": self.tmdb_extractor,
            "Default": self.default_extractor,
        }

        # Define sources and conditions for each data type
        self._data = {
            "title": {
                "sources": [
                    ("TMDB", "extract_title"),
                    ("Metadata", "extract_title"),
                    ("Filename", "extract_title"),
                    ("Default", "extract_title"),
                ],
            },
            "year": {
                "sources": [
                    ("Filename", "extract_year"),
                    ("Default", "extract_year"),
                ],
            },
            "source": {
                "sources": [
                    ("Filename", "extract_source"),
                    ("Default", "extract_source"),
                ],
            },
            "order": {
                "sources": [
                    ("Filename", "extract_order"),
                    ("Default", "extract_order"),
                ],
            },
            "frame_class": {
                "sources": [
                    ("MediaInfo", "extract_frame_class"),
                    ("Filename", "extract_frame_class"),
                    ("Default", "extract_frame_class"),
                ],
            },
            "resolution": {
                "sources": [
                    ("MediaInfo", "extract_resolution"),
                    ("Default", "extract_resolution"),
                ],
            },
            "hdr": {
                "sources": [
                    ("MediaInfo", "extract_hdr"),
                    ("Filename", "extract_hdr"),
                    ("Default", "extract_hdr"),
                ],
            },
            "anamorphic": {
                "sources": [
                    ("MediaInfo", "extract_anamorphic"),
                    ("Default", "extract_anamorphic"),
                ],
            },
            "3d_layout": {
                "sources": [
                    ("MediaInfo", "extract_3d_layout"),
                    ("Filename", "extract_3d_layout"),
                    ("Default", "extract_3d_layout"),
                ],
            },
            "movie_db": {
                "sources": [
                    ("TMDB", "extract_movie_db"),
                    ("Filename", "extract_movie_db"),
                    ("Default", "extract_movie_db"),
                ],
            },
            "special_info": {
                "sources": [
                    ("Filename", "extract_special_info"),
                    ("Default", "extract_special_info"),
                ],
            },
            "audio_langs": {
                "sources": [
                    ("MediaInfo", "extract_audio_langs"),
                    ("Filename", "extract_audio_langs"),
                    ("Default", "extract_audio_langs"),
                ],
            },
            "meta_type": {
                "sources": [
                    ("Metadata", "extract_meta_type"),
                    ("Default", "extract_meta_type"),
                ],
            },
            "file_size": {
                "sources": [
                    ("FileInfo", "extract_size"),
                    ("Default", "extract_size"),
                ],
            },
            "modification_time": {
                "sources": [
                    ("FileInfo", "extract_modification_time"),
                    ("Default", "extract_modification_time"),
                ],
            },
            "file_name": {
                "sources": [
                    ("FileInfo", "extract_file_name"),
                    ("Default", "extract_file_name"),
                ],
            },
            "file_path": {
                "sources": [
                    ("FileInfo", "extract_file_path"),
                    ("Default", "extract_file_path"),
                ],
            },
            "extension": {
                "sources": [
                    ("MediaInfo", "extract_extension"),
                    ("FileInfo", "extract_extension"),
                    ("Default", "extract_extension"),
                ],
            },
            "video_tracks": {
                "sources": [
                    ("MediaInfo", "extract_video_tracks"),
                    ("Default", "extract_video_tracks"),
                ],
            },
            "audio_tracks": {
                "sources": [
                    ("MediaInfo", "extract_audio_tracks"),
                    ("Default", "extract_audio_tracks"),
                ],
            },
            "subtitle_tracks": {
                "sources": [
                    ("MediaInfo", "extract_subtitle_tracks"),
                    ("Default", "extract_subtitle_tracks"),
                ],
            },
            "genres": {
                "sources": [
                    ("TMDB", "extract_genres"),
                    ("Default", "extract_genres"),
                ],
            },
            "production_countries": {
                "sources": [
                    ("TMDB", "extract_production_countries"),
                ],
            },
        }

    def get(self, key: str, source: str | None = None):
        """Get metadata value by key, optionally from a specific source.

        Retrieves metadata using a priority-based system. If a source is specified,
        only that extractor is used. Otherwise, extractors are tried in priority
        order until a non-None value is found.

        Args:
            key: The metadata key to retrieve (e.g., "title", "year", "resolution")
            source: Optional specific extractor to use ("TMDB", "MediaInfo", "Filename", etc.)

        Returns:
            The extracted metadata value, or None if not found

        Example:
            >>> extractor = MediaExtractor(Path("movie.mkv"))
            >>> title = extractor.get("title")  # Try all sources in priority order
            >>> year = extractor.get("year", source="Filename")  # Use only filename
        """
        if source:
            # Specific source requested - find the extractor and call the method directly
            for extractor_name, extractor in self._extractors.items():
                if extractor_name.lower() == source.lower():
                    method = f"extract_{key}"
                    if hasattr(extractor, method):
                        val = getattr(extractor, method)()
                        return val if val is not None else None
            return None
        
        # Fallback mode - try sources in order
        if key in self._data:
            sources = self._data[key]["sources"]
        else:
            # Try extractors in order for unconfigured keys
            sources = [(name, f"extract_{key}") for name in ["MediaInfo", "Metadata", "Filename", "FileInfo"]]
        
        # Try each source in order until a valid value is found
        for src, method in sources:
            if src in self._extractors and hasattr(self._extractors[src], method):
                val = getattr(self._extractors[src], method)()
                if val is not None:
                    return val
        return None
