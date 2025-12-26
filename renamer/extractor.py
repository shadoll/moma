from pathlib import Path
from .extractors.filename_extractor import FilenameExtractor
from .extractors.metadata_extractor import MetadataExtractor
from .extractors.mediainfo_extractor import MediaInfoExtractor
from .extractors.fileinfo_extractor import FileInfoExtractor


class MediaExtractor:
    """Class to extract various metadata from media files using specialized extractors"""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.filename_extractor = FilenameExtractor(file_path)
        self.metadata_extractor = MetadataExtractor(file_path)
        self.mediainfo_extractor = MediaInfoExtractor(file_path)
        self.fileinfo_extractor = FileInfoExtractor(file_path)
        
        # Define sources for each data type
        self._sources = {
            'title': [
                ('Metadata', lambda: self.metadata_extractor.extract_title()),
                ('Filename', lambda: self.filename_extractor.extract_title())
            ],
            'year': [
                ('Filename', lambda: self.filename_extractor.extract_year())
            ],
            'source': [
                ('Filename', lambda: self.filename_extractor.extract_source())
            ],
            'frame_class': [
                ('MediaInfo', lambda: self.mediainfo_extractor.extract_frame_class()),
                ('Filename', lambda: self.filename_extractor.extract_frame_class())
            ],
            'resolution': [
                ('MediaInfo', lambda: self.mediainfo_extractor.extract_resolution())
            ],
            'aspect_ratio': [
                ('MediaInfo', lambda: self.mediainfo_extractor.extract_aspect_ratio())
            ],
            'hdr': [
                ('MediaInfo', lambda: self.mediainfo_extractor.extract_hdr()),
                ('Filename', lambda: self.filename_extractor.extract_hdr())
            ],
            'movie_db': [
                ('Filename', lambda: self.filename_extractor.extract_movie_db())
            ],
            'audio_langs': [
                ('MediaInfo', lambda: self.mediainfo_extractor.extract_audio_langs())
            ],
            'meta_type': [
                ('Metadata', lambda: self.metadata_extractor.extract_meta_type())
            ],
            'file_size': [
                ('FileInfo', lambda: self.fileinfo_extractor.extract_size())
            ],
            'modification_time': [
                ('FileInfo', lambda: self.fileinfo_extractor.extract_modification_time())
            ],
            'file_name': [
                ('FileInfo', lambda: self.fileinfo_extractor.extract_file_name())
            ],
            'file_path': [
                ('FileInfo', lambda: self.fileinfo_extractor.extract_file_path())
            ],
            'extension': [
                ('FileInfo', lambda: self.fileinfo_extractor.extract_extension())
            ],
            'video_tracks': [
                ('MediaInfo', lambda: self.mediainfo_extractor.extract_video_tracks())
            ],
            'audio_tracks': [
                ('MediaInfo', lambda: self.mediainfo_extractor.extract_audio_tracks())
            ],
            'subtitle_tracks': [
                ('MediaInfo', lambda: self.mediainfo_extractor.extract_subtitle_tracks())
            ],
        }
        
        # Conditions for when a value is considered valid
        self._conditions = {
            'title': lambda x: x is not None,
            'year': lambda x: x is not None,
            'source': lambda x: x is not None,
            'frame_class': lambda x: x and x != 'Unclassified',
            'resolution': lambda x: x is not None,
            'aspect_ratio': lambda x: x is not None,
            'hdr': lambda x: x is not None,
            'movie_db': lambda x: x is not None,
            'audio_langs': lambda x: x is not None,
            'tracks': lambda x: x is not None and any(x.get(k, []) for k in ['video_tracks', 'audio_tracks', 'subtitle_tracks']),
            'video_tracks': lambda x: x is not None and len(x) > 0,
            'audio_tracks': lambda x: x is not None and len(x) > 0,
            'subtitle_tracks': lambda x: x is not None and len(x) > 0,
        }

    def get(self, key: str, source: str | None = None):
        """Get extracted data by key, optionally from specific source"""
        if key in self._sources:
            condition = self._conditions.get(key, lambda x: x is not None)
            
            if source:
                for src, func in self._sources[key]:
                    if src.lower() == source.lower():
                        val = func()
                        return val if condition(val) else None
                return None  # Source not found for this key, return None
            else:
                # Use fallback: return first valid value
                for src, func in self._sources[key]:
                    val = func()
                    if condition(val):
                        return val
                return None
        else:
            # Key not in _sources, try to call extract_<key> on extractors
            extract_method = f'extract_{key}'
            extractors = [
                ('MediaInfo', self.mediainfo_extractor),
                ('Metadata', self.metadata_extractor),
                ('Filename', self.filename_extractor),
                ('FileInfo', self.fileinfo_extractor)
            ]
            
            if source:
                for src_name, extractor in extractors:
                    if src_name.lower() == source.lower():
                        if hasattr(extractor, extract_method):
                            val = getattr(extractor, extract_method)()
                            return val
                return None
            else:
                # Try all extractors in order
                for src_name, extractor in extractors:
                    if hasattr(extractor, extract_method):
                        val = getattr(extractor, extract_method)()
                        if val is not None:
                            return val
                return None