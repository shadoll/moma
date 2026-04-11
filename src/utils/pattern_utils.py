"""Pattern extraction utilities.

This module provides centralized regex pattern matching and extraction logic
for common patterns found in media filenames.
"""

import logging
import re
from typing import Optional, Dict
from datetime import datetime

from src.constants import MOVIE_DB_DICT


logger = logging.getLogger(__name__)


class PatternExtractor:
    """Shared regex pattern extraction logic.

    This class centralizes pattern matching for:
    - Movie database IDs (TMDB, IMDB, etc.)
    - Year detection and validation
    - Quality indicators
    - Source indicators

    Example:
        >>> extractor = PatternExtractor()
        >>> db_info = extractor.extract_movie_db_ids("[tmdbid-12345]")
        >>> print(db_info)  # {'type': 'tmdb', 'id': '12345'}
    """

    # Year validation constants
    CURRENT_YEAR = datetime.now().year
    YEAR_FUTURE_BUFFER = 10  # Allow up to 10 years in the future
    MIN_VALID_YEAR = 1900

    # Common quality indicators
    QUALITY_PATTERNS = {
        '2160p', '1080p', '720p', '480p', '360p', '240p', '144p',
        '4K', '8K', 'SD', 'HD', 'UHD', 'QHD', 'LQ'
    }

    # Source indicators
    SOURCE_PATTERNS = {
        'BluRay', 'BDRip', 'BRRip', 'DVDRip', 'WEB-DL', 'WEBRip',
        'HDTV', 'PDTV', 'HDRip', 'CAM', 'TS', 'TC', 'R5', 'DVD'
    }

    def __init__(self):
        """Initialize the pattern extractor."""
        self.max_valid_year = self.CURRENT_YEAR + self.YEAR_FUTURE_BUFFER

    def extract_movie_db_ids(self, text: str) -> Optional[dict[str, str]]:
        """Extract movie database IDs from text.

        Supports patterns like:
        - [tmdbid-123456]
        - {imdb-tt1234567}
        - [imdbid-tt123]

        Args:
            text: Text to search for database IDs

        Returns:
            Dictionary with 'type' and 'id' keys, or None if not found

        Example:
            >>> extractor = PatternExtractor()
            >>> extractor.extract_movie_db_ids("[tmdbid-12345]")
            {'type': 'tmdb', 'id': '12345'}
        """
        # Match patterns like [tmdbid-123456] or {imdb-tt1234567}
        pattern = r'[\[\{]([a-zA-Z]+(?:id)?)[-\s]*([a-zA-Z0-9]+)[\]\}]'
        matches = re.findall(pattern, text)

        if matches:
            # Take the last match (closest to end of filename)
            db_type, db_id = matches[-1]

            # Normalize database type
            db_type_lower = db_type.lower()

            for db_key, db_info in MOVIE_DB_DICT.items():
                if any(db_type_lower.startswith(pattern.rstrip('-'))
                       for pattern in db_info['patterns']):
                    return {'type': db_key, 'id': db_id}

        return None

    def extract_year(self, text: str, validate: bool = True) -> Optional[str]:
        """Extract year from text with optional validation.

        Looks for 4-digit years in parentheses or standalone.
        Validates that the year is within a reasonable range.

        Args:
            text: Text to extract year from
            validate: If True, validate year is within MIN_VALID_YEAR and max_valid_year

        Returns:
            Year as string (e.g., "2024") or None if not found/invalid

        Example:
            >>> extractor = PatternExtractor()
            >>> extractor.extract_year("Movie Title (2024)")
            '2024'
            >>> extractor.extract_year("Movie (1899)")  # Too old
            None
        """
        # Look for year in parentheses first (most common)
        year_pattern = r'\((\d{4})\)'
        match = re.search(year_pattern, text)

        if match:
            year = match.group(1)
            if validate:
                year_int = int(year)
                if self.MIN_VALID_YEAR <= year_int <= self.max_valid_year:
                    return year
                else:
                    logger.debug(f"Year {year} outside valid range "
                               f"{self.MIN_VALID_YEAR}-{self.max_valid_year}")
                    return None
            return year

        # Fall back to standalone 4-digit number
        standalone_pattern = r'\b(\d{4})\b'
        matches = re.findall(standalone_pattern, text)

        for potential_year in matches:
            if validate:
                year_int = int(potential_year)
                if self.MIN_VALID_YEAR <= year_int <= self.max_valid_year:
                    return potential_year
            else:
                return potential_year

        return None

    def find_year_position(self, text: str) -> Optional[int]:
        """Find the position of the year in text.

        Args:
            text: Text to search

        Returns:
            Character index of the year, or None if not found

        Example:
            >>> extractor = PatternExtractor()
            >>> extractor.find_year_position("Movie (2024) 1080p")
            6  # Position of '(' before year
        """
        year_pattern = r'\((\d{4})\)'
        match = re.search(year_pattern, text)

        if match:
            year = match.group(1)
            year_int = int(year)
            if self.MIN_VALID_YEAR <= year_int <= self.max_valid_year:
                return match.start()

        return None

    def extract_quality(self, text: str) -> Optional[str]:
        """Extract quality indicator from text.

        Args:
            text: Text to search

        Returns:
            Quality string (e.g., "1080p") or None

        Example:
            >>> extractor = PatternExtractor()
            >>> extractor.extract_quality("Movie.1080p.BluRay")
            '1080p'
        """
        text_upper = text.upper()

        for quality in self.QUALITY_PATTERNS:
            # Case-insensitive search
            pattern = r'\b' + re.escape(quality) + r'\b'
            if re.search(pattern, text_upper, re.IGNORECASE):
                return quality

        return None

    def find_quality_position(self, text: str) -> Optional[int]:
        """Find the position of quality indicator in text.

        Args:
            text: Text to search

        Returns:
            Character index of quality indicator, or None if not found

        Example:
            >>> extractor = PatternExtractor()
            >>> extractor.find_quality_position("Movie 1080p BluRay")
            6
        """
        for quality in self.QUALITY_PATTERNS:
            pattern = r'\b' + re.escape(quality) + r'\b'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.start()

        return None

    def extract_source(self, text: str) -> Optional[str]:
        """Extract source indicator from text.

        Args:
            text: Text to search

        Returns:
            Source string (e.g., "BluRay") or None

        Example:
            >>> extractor = PatternExtractor()
            >>> extractor.extract_source("Movie.BluRay.1080p")
            'BluRay'
        """
        for source in self.SOURCE_PATTERNS:
            pattern = r'\b' + re.escape(source) + r'\b'
            if re.search(pattern, text, re.IGNORECASE):
                return source

        return None

    def find_source_position(self, text: str) -> Optional[int]:
        """Find the position of source indicator in text.

        Args:
            text: Text to search

        Returns:
            Character index of source indicator, or None if not found

        Example:
            >>> extractor = PatternExtractor()
            >>> extractor.find_source_position("Movie BluRay 1080p")
            6
        """
        for source in self.SOURCE_PATTERNS:
            pattern = r'\b' + re.escape(source) + r'\b'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.start()

        return None

    def extract_bracketed_content(self, text: str) -> list[str]:
        """Extract all content from square brackets.

        Args:
            text: Text to search

        Returns:
            List of strings found in brackets

        Example:
            >>> extractor = PatternExtractor()
            >>> extractor.extract_bracketed_content("[UKR] Movie [ENG]")
            ['UKR', 'ENG']
        """
        bracket_pattern = r'\[([^\]]+)\]'
        return re.findall(bracket_pattern, text)

    def remove_bracketed_content(self, text: str) -> str:
        """Remove all bracketed content from text.

        Args:
            text: Text to clean

        Returns:
            Text with brackets and their content removed

        Example:
            >>> extractor = PatternExtractor()
            >>> extractor.remove_bracketed_content("[UKR] Movie [ENG]")
            ' Movie '
        """
        return re.sub(r'\[([^\]]+)\]', '', text)

    def split_on_delimiters(self, text: str) -> list[str]:
        """Split text on common delimiters (dots, spaces, underscores).

        Args:
            text: Text to split

        Returns:
            List of parts

        Example:
            >>> extractor = PatternExtractor()
            >>> extractor.split_on_delimiters("Movie.Title.2024")
            ['Movie', 'Title', '2024']
        """
        return re.split(r'[.\s_]+', text)

    def sanitize_for_regex(self, text: str) -> str:
        """Escape special regex characters in text.

        Args:
            text: Text to sanitize

        Returns:
            Escaped text safe for use in regex patterns

        Example:
            >>> extractor = PatternExtractor()
            >>> extractor.sanitize_for_regex("Movie (2024)")
            'Movie \\(2024\\)'
        """
        return re.escape(text)

    def is_quality_indicator(self, text: str) -> bool:
        """Check if text is a quality indicator.

        Args:
            text: Text to check

        Returns:
            True if text is a known quality indicator

        Example:
            >>> extractor = PatternExtractor()
            >>> extractor.is_quality_indicator("1080p")
            True
        """
        return text.upper() in self.QUALITY_PATTERNS

    def is_source_indicator(self, text: str) -> bool:
        """Check if text is a source indicator.

        Args:
            text: Text to check

        Returns:
            True if text is a known source indicator

        Example:
            >>> extractor = PatternExtractor()
            >>> extractor.is_source_indicator("BluRay")
            True
        """
        return any(source.lower() == text.lower() for source in self.SOURCE_PATTERNS)
