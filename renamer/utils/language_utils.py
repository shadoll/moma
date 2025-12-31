"""Language code extraction and conversion utilities.

This module provides centralized logic for extracting and converting language codes
from filenames and metadata. This eliminates the ~150+ lines of duplicated code
between FilenameExtractor and MediaInfoExtractor.
"""

import logging
import re
from typing import Optional
import langcodes


logger = logging.getLogger(__name__)


class LanguageCodeExtractor:
    """Shared language code extraction logic.

    This class centralizes all language code detection and conversion logic,
    eliminating duplication across multiple extractors.

    Example:
        >>> extractor = LanguageCodeExtractor()
        >>> langs = extractor.extract_from_brackets("[2xUKR_ENG]")
        >>> print(langs)  # ['ukr', 'ukr', 'eng']
    """

    # Comprehensive set of known ISO 639-1/639-2/639-3 language codes
    KNOWN_CODES = {
        # Most common codes
        'eng', 'ukr', 'rus', 'fra', 'deu', 'spa', 'ita', 'por', 'nor', 'swe',
        'dan', 'fin', 'pol', 'cze', 'hun', 'tur', 'ara', 'heb', 'hin', 'jpn',
        'kor', 'chi', 'tha', 'vie', 'und',

        # European languages
        'dut', 'nld', 'bel', 'bul', 'hrv', 'ces', 'est', 'ell', 'ind',
        'lav', 'lit', 'mkd', 'ron', 'slk', 'slv', 'srp', 'zho',

        # South Asian languages
        'arb', 'ben', 'mar', 'tam', 'tel', 'urd', 'guj', 'kan', 'mal', 'ori',
        'pan', 'asm', 'mai', 'bho', 'nep', 'sin', 'san', 'tib', 'mon',

        # Central Asian languages
        'kaz', 'uzb', 'kir', 'tuk', 'aze', 'kat', 'hye', 'geo',

        # Balkan languages
        'sqi', 'bos', 'alb', 'mol',

        # Nordic languages
        'isl', 'fao',

        # Other Asian languages
        'per', 'kur', 'pus', 'div', 'lao', 'khm', 'mya', 'msa',
        'yue', 'wuu', 'nan', 'hak', 'gan', 'hsn',

        # Various other codes
        'awa', 'mag',
    }

    # Language codes that are allowed in title case (to avoid false positives)
    ALLOWED_TITLE_CASE = {
        'ukr', 'nor', 'eng', 'rus', 'fra', 'deu', 'spa', 'ita', 'por', 'swe',
        'dan', 'fin', 'pol', 'cze', 'hun', 'tur', 'ara', 'heb', 'hin', 'jpn',
        'kor', 'chi', 'tha', 'vie', 'und'
    }

    # Words to skip (common English words, file extensions, quality indicators)
    SKIP_WORDS = {
        # Common English words
        'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had',
        'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his',
        'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'way', 'who',
        'boy', 'did', 'let', 'put', 'say', 'she', 'too', 'use',

        # File extensions
        'avi', 'mkv', 'mp4', 'mpg', 'mov', 'wmv', 'flv', 'webm', 'm4v',
        'm2ts', 'ts', 'vob', 'iso', 'img',

        # Quality/resolution indicators
        'sd', 'hd', 'lq', 'qhd', 'uhd', 'p', 'i', 'hdr', 'sdr', '4k', '8k',
        '2160p', '1080p', '720p', '480p', '360p', '240p', '144p',

        # Source/encoding indicators
        'web', 'dl', 'rip', 'bluray', 'dvd', 'hdtv', 'bdrip', 'dvdrip',
        'xvid', 'divx', 'h264', 'h265', 'x264', 'x265', 'hevc', 'avc',

        # Audio codecs
        'ma', 'atmos', 'dts', 'aac', 'ac3', 'mp3', 'flac', 'wav', 'wma',
        'ogg', 'opus',

        # Subtitle indicator
        'sub', 'subs', 'subtitle',
    }

    def __init__(self):
        """Initialize the language code extractor."""
        pass

    def extract_from_brackets(self, text: str) -> list[str]:
        """Extract language codes from bracketed content.

        Handles patterns like:
        - [UKR_ENG] → ['ukr', 'eng']
        - [2xUKR_ENG] → ['ukr', 'ukr', 'eng']
        - [4xUKR,ENG] → ['ukr', 'ukr', 'ukr', 'ukr', 'eng']

        Args:
            text: Text containing bracketed language codes

        Returns:
            List of ISO 639-3 language codes (3-letter)

        Example:
            >>> extractor = LanguageCodeExtractor()
            >>> extractor.extract_from_brackets("[2xUKR_ENG]")
            ['ukr', 'ukr', 'eng']
        """
        langs = []

        # Find all bracketed content
        bracket_pattern = r'\[([^\]]+)\]'
        brackets = re.findall(bracket_pattern, text)

        for bracket in brackets:
            bracket_lower = bracket.lower()

            # Skip brackets containing movie database patterns
            if any(db in bracket_lower for db in ['imdb', 'tmdb', 'tvdb']):
                continue

            # Parse items separated by commas or underscores
            items = re.split(r'[,_]', bracket)
            items = [item.strip() for item in items]

            for item in items:
                # Skip empty items or too short
                if not item or len(item) < 2:
                    continue

                item_lower = item.lower()

                # Skip subtitle indicators
                if item_lower in self.SKIP_WORDS:
                    continue

                # Pattern: optional number + optional 'x' + language code
                lang_match = re.search(r'(?:(\d+)x?)?([a-z]{2,3})$', item_lower)
                if lang_match:
                    count = int(lang_match.group(1)) if lang_match.group(1) else 1
                    lang_code = lang_match.group(2)

                    # Skip quality/resolution indicators
                    if lang_code in self.SKIP_WORDS:
                        continue

                    # Validate prefix (only digits and 'x' allowed)
                    prefix = item_lower[:-len(lang_code)]
                    if not re.match(r'^(?:\d+x?)?$', prefix):
                        continue

                    # Convert to ISO 639-3 code
                    iso3_code = self._convert_to_iso3(lang_code)
                    if iso3_code:
                        langs.extend([iso3_code] * count)

        return langs

    def extract_standalone(self, text: str) -> list[str]:
        """Extract standalone language codes from text.

        Looks for language codes outside of brackets in various formats:
        - Uppercase: ENG, UKR, NOR
        - Title case: Ukr, Nor, Eng
        - Lowercase: ukr, nor, eng
        - Dot-separated: .ukr. .eng.

        Args:
            text: Text to extract language codes from

        Returns:
            List of ISO 639-3 language codes (3-letter)

        Example:
            >>> extractor = LanguageCodeExtractor()
            >>> extractor.extract_standalone("Movie.2024.UKR.ENG.1080p.mkv")
            ['ukr', 'eng']
        """
        langs = []

        # Remove bracketed content first
        text_without_brackets = re.sub(r'\[([^\]]+)\]', '', text)

        # Split on dots, spaces, and underscores
        parts = re.split(r'[.\s_]+', text_without_brackets)

        for part in parts:
            part = part.strip()
            if not part or len(part) < 2:
                continue

            part_lower = part.lower()

            # Check if this is a 2-3 letter code
            if re.match(r'^[a-zA-Z]{2,3}$', part):
                # Skip title case 2-letter words to avoid false positives
                if part.istitle() and len(part) == 2:
                    continue

                # For title case, only allow known language codes
                if part.istitle() and part_lower not in self.ALLOWED_TITLE_CASE:
                    continue

                # Skip common words and non-language codes
                if part_lower in self.SKIP_WORDS:
                    continue

                # Check if it's a known language code
                if part_lower in self.KNOWN_CODES:
                    iso3_code = self._convert_to_iso3(part_lower)
                    if iso3_code:
                        langs.append(iso3_code)

        return langs

    def extract_all(self, text: str) -> list[str]:
        """Extract all language codes from text (both bracketed and standalone).

        Args:
            text: Text to extract language codes from

        Returns:
            List of ISO 639-3 language codes (3-letter), duplicates removed
            while preserving order

        Example:
            >>> extractor = LanguageCodeExtractor()
            >>> extractor.extract_all("Movie [UKR_ENG] 2024.rus.mkv")
            ['ukr', 'eng', 'rus']
        """
        # Extract from both sources
        bracketed = self.extract_from_brackets(text)
        standalone = self.extract_standalone(text)

        # Combine while removing duplicates but preserving order
        seen = set()
        result = []

        for lang in bracketed + standalone:
            if lang not in seen:
                seen.add(lang)
                result.append(lang)

        return result

    def format_lang_counts(self, langs: list[str]) -> str:
        """Format language list with counts like MediaInfo.

        Formats like: "2ukr,eng" for 2 Ukrainian tracks and 1 English track.

        Args:
            langs: List of language codes (can have duplicates)

        Returns:
            Formatted string with counts

        Example:
            >>> extractor = LanguageCodeExtractor()
            >>> extractor.format_lang_counts(['ukr', 'ukr', 'eng'])
            '2ukr,eng'
        """
        if not langs:
            return ''

        # Count occurrences while preserving order of first appearance
        lang_counts = {}
        lang_order = []

        for lang in langs:
            if lang not in lang_counts:
                lang_counts[lang] = 0
                lang_order.append(lang)
            lang_counts[lang] += 1

        # Format with counts
        formatted = []
        for lang in lang_order:
            count = lang_counts[lang]
            formatted.append(f"{count}{lang}" if count > 1 else lang)

        return ','.join(formatted)

    def _convert_to_iso3(self, lang_code: str) -> Optional[str]:
        """Convert a language code to ISO 639-3 (3-letter code).

        Args:
            lang_code: 2 or 3 letter language code

        Returns:
            ISO 639-3 code or None if invalid

        Example:
            >>> extractor = LanguageCodeExtractor()
            >>> extractor._convert_to_iso3('en')
            'eng'
            >>> extractor._convert_to_iso3('ukr')
            'ukr'
        """
        try:
            lang_obj = langcodes.Language.get(lang_code)
            return lang_obj.to_alpha3()
        except (LookupError, ValueError, AttributeError) as e:
            logger.debug(f"Invalid language code '{lang_code}': {e}")
            return None

    def is_valid_code(self, code: str) -> bool:
        """Check if a code is a valid language code.

        Args:
            code: The code to check

        Returns:
            True if valid language code

        Example:
            >>> extractor = LanguageCodeExtractor()
            >>> extractor.is_valid_code('eng')
            True
            >>> extractor.is_valid_code('xyz')
            False
        """
        return self._convert_to_iso3(code) is not None
