"""Constants package for moma.

This package contains constants split into logical modules:
- media_constants.py: Media type definitions (MEDIA_TYPES)
- source_constants.py: Video source types (SOURCE_DICT)
- frame_constants.py: Resolution/frame classes (FRAME_CLASSES)
- moviedb_constants.py: Movie database identifiers (MOVIE_DB_DICT)
- edition_constants.py: Special edition types (SPECIAL_EDITIONS)
- lang_constants.py: Language-related constants (SKIP_WORDS)
- year_constants.py: Year validation (CURRENT_YEAR, MIN_VALID_YEAR, etc.)
- cyrillic_constants.py: Cyrillic character normalization (CYRILLIC_TO_ENGLISH)
"""

# Import from all constant modules
from .media_constants import (
    MEDIA_TYPES,
    META_TYPE_TO_EXTENSIONS,
    get_extension_from_format
)
from .source_constants import SOURCE_DICT
from .frame_constants import FRAME_CLASSES, NON_STANDARD_QUALITY_INDICATORS
from .moviedb_constants import MOVIE_DB_DICT
from .edition_constants import SPECIAL_EDITIONS
from .lang_constants import SKIP_WORDS
from .year_constants import CURRENT_YEAR, MIN_VALID_YEAR, YEAR_FUTURE_BUFFER, is_valid_year
from .cyrillic_constants import CYRILLIC_TO_ENGLISH

__all__ = [
    # Media types
    'MEDIA_TYPES',
    'META_TYPE_TO_EXTENSIONS',
    'get_extension_from_format',
    # Source types
    'SOURCE_DICT',
    # Frame classes
    'FRAME_CLASSES',
    'NON_STANDARD_QUALITY_INDICATORS',
    # Movie databases
    'MOVIE_DB_DICT',
    # Special editions
    'SPECIAL_EDITIONS',
    # Language constants
    'SKIP_WORDS',
    # Year validation
    'CURRENT_YEAR',
    'MIN_VALID_YEAR',
    'YEAR_FUTURE_BUFFER',
    'is_valid_year',
    # Cyrillic normalization
    'CYRILLIC_TO_ENGLISH',
]
