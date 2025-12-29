from pathlib import Path
from .filename_extractor import FilenameExtractor
from .metadata_extractor import MetadataExtractor
from .mediainfo_extractor import MediaInfoExtractor
from .fileinfo_extractor import FileInfoExtractor
from .tmdb_extractor import TMDBExtractor
from .default_extractor import DefaultExtractor


class MediaExtractor:
    """Class to extract various metadata from media files using specialized extractors"""

    @classmethod
    def create(cls, file_path: Path, cache=None, ttl_seconds: int = 21600):
        """Factory method that returns cached object if available, else creates new."""
        if cache:
            cache_key = f"extractor_{file_path}"
            cached_obj = cache.get_object(cache_key)
            if cached_obj:
                print(f"Loaded MediaExtractor object from cache for {file_path.name}")
                return cached_obj
        
        # Create new instance
        instance = cls(file_path, cache, ttl_seconds)
        
        # Cache the object
        if cache:
            cache_key = f"extractor_{file_path}"
            cache.set_object(cache_key, instance, ttl_seconds)
            print(f"Cached MediaExtractor object for {file_path.name}")
        
        return instance

    def __init__(self, file_path: Path, cache=None, ttl_seconds: int = 21600):
        self.file_path = file_path
        self.cache = cache
        self.ttl_seconds = ttl_seconds
        self.cache_key = f"file_data_{file_path}"
        
        self.filename_extractor = FilenameExtractor(file_path)
        self.metadata_extractor = MetadataExtractor(file_path)
        self.mediainfo_extractor = MediaInfoExtractor(file_path)
        self.fileinfo_extractor = FileInfoExtractor(file_path)
        self.tmdb_extractor = TMDBExtractor(file_path, cache, ttl_seconds)
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
        }
        
        # No caching logic here - handled in create() method
    
    def get(self, key: str, source: str | None = None):
        """Get extracted data by key, optionally from specific source"""
        print(f"Extracting real data for key '{key}' in {self.file_path.name}")
        return self._get_uncached(key, source)

    def _get_uncached(self, key: str, source: str | None = None):
        """Original get logic without caching"""
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
