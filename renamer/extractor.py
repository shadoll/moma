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
                ('metadata', lambda: self.metadata_extractor.extract_title()),
                ('filename', lambda: self.filename_extractor.extract_title())
            ],
            'year': [
                ('filename', lambda: self.filename_extractor.extract_year())
            ],
            'source': [
                ('filename', lambda: self.filename_extractor.extract_source())
            ],
            'frame_class': [
                ('mediainfo', lambda: self.mediainfo_extractor.extract_frame_class()),
                ('filename', lambda: self.filename_extractor.extract_frame_class())
            ],
            'resolution': [
                ('mediainfo', lambda: self.mediainfo_extractor.extract_resolution())
            ],
            'aspect_ratio': [
                ('mediainfo', lambda: self.mediainfo_extractor.extract_aspect_ratio())
            ],
            'hdr': [
                ('mediainfo', lambda: self.mediainfo_extractor.extract_hdr())
            ],
            'audio_langs': [
                ('mediainfo', lambda: self.mediainfo_extractor.extract_audio_langs())
            ],
            'metadata': [
                ('metadata', lambda: self.metadata_extractor.extract_all_metadata())
            ],
            'meta_type': [
                ('metadata', lambda: self.metadata_extractor.extract_meta_type())
            ],
            'meta_description': [
                ('metadata', lambda: self.metadata_extractor.extract_meta_description())
            ],
            'file_size': [
                ('fileinfo', lambda: self.fileinfo_extractor.extract_size())
            ],
            'modification_time': [
                ('fileinfo', lambda: self.fileinfo_extractor.extract_modification_time())
            ],
            'file_name': [
                ('fileinfo', lambda: self.fileinfo_extractor.extract_file_name())
            ],
            'file_path': [
                ('fileinfo', lambda: self.fileinfo_extractor.extract_file_path())
            ],
            'extension': [
                ('fileinfo', lambda: self.fileinfo_extractor.extract_extension())
            ],
            'tracks': [
                ('mediainfo', lambda: self.mediainfo_extractor.extract_tracks())
            ]
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
            'audio_langs': lambda x: x is not None,
            'metadata': lambda x: x is not None,
            'tracks': lambda x: x != ""
        }

    def get(self, key: str, source: str | None = None):
        """Get extracted data by key, optionally from specific source"""
        if key not in self._sources:
            raise ValueError(f"Unknown key: {key}")
        
        condition = self._conditions.get(key, lambda x: x is not None)
        
        if source:
            for src, func in self._sources[key]:
                if src == source:
                    val = func()
                    return val if condition(val) else None
            raise ValueError(f"No such source '{source}' for key '{key}'")
        else:
            # Use fallback: return first valid value
            for src, func in self._sources[key]:
                val = func()
                if condition(val):
                    return val
            return None