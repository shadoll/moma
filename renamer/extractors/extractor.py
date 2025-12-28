from pathlib import Path
from .filename_extractor import FilenameExtractor
from .metadata_extractor import MetadataExtractor
from .mediainfo_extractor import MediaInfoExtractor
from .fileinfo_extractor import FileInfoExtractor
from .tmdb_extractor import TMDBExtractor
from .default_extractor import DefaultExtractor


class MediaExtractor:
    """Class to extract various metadata from media files using specialized extractors"""

    def __init__(self, file_path: Path):
        self.filename_extractor = FilenameExtractor(file_path)
        self.metadata_extractor = MetadataExtractor(file_path)
        self.mediainfo_extractor = MediaInfoExtractor(file_path)
        self.fileinfo_extractor = FileInfoExtractor(file_path)
        self.tmdb_extractor = TMDBExtractor(file_path)
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
        }

    def get(self, key: str, source: str | None = None):
        """Get extracted data by key, optionally from specific source"""
        if source:
            # Specific source requested - find the extractor and call the method directly
            for extractor_name, extractor in self._extractors.items():
                if extractor_name.lower() == source.lower():
                    method = f"extract_{key}"
                    if hasattr(extractor, method):
                        val = getattr(extractor, method)()
                        # Apply condition if specified
                        if key in self._data and "condition" in self._data[key]:
                            condition = self._data[key]["condition"]
                            return val if condition(val) else None
                        return val
            return None
        
        # Fallback mode - try sources in order
        if key in self._data:
            data = self._data[key]
            sources = data["sources"]
            condition = data.get("condition", lambda x: x is not None)
        else:
            # Try extractors in order for unconfigured keys
            sources = [(name, f"extract_{key}") for name in ["MediaInfo", "Metadata", "Filename", "FileInfo"]]
            condition = lambda x: x is not None
        
        # Try each source in order until a valid value is found
        for src, method in sources:
            if src in self._extractors and hasattr(self._extractors[src], method):
                val = getattr(self._extractors[src], method)()
                if condition(val):
                    return val
        return None
