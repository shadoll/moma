"""Extractors package - provides metadata extraction from media files.

This package contains various extractor classes that extract metadata from
different sources (filename, MediaInfo, file system, TMDB API, etc.).

All extractors should implement the DataExtractor protocol defined in base.py.
"""

from .base import DataExtractor
from .default_extractor import DefaultExtractor
from .filename_extractor import FilenameExtractor
from .fileinfo_extractor import FileInfoExtractor
from .mediainfo_extractor import MediaInfoExtractor
from .metadata_extractor import MetadataExtractor
from .tmdb_extractor import TMDBExtractor

__all__ = [
    'DataExtractor',
    'DefaultExtractor',
    'FilenameExtractor',
    'FileInfoExtractor',
    'MediaInfoExtractor',
    'MetadataExtractor',
    'TMDBExtractor',
]
