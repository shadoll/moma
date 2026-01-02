import re
import logging
from pathlib import Path
from collections import Counter
from ..constants import (
    SOURCE_DICT, FRAME_CLASSES, MOVIE_DB_DICT, SPECIAL_EDITIONS, SKIP_WORDS,
    NON_STANDARD_QUALITY_INDICATORS,
    is_valid_year,
    CYRILLIC_TO_ENGLISH
)
from ..cache import cached_method
from ..utils.pattern_utils import PatternExtractor
import langcodes

logger = logging.getLogger(__name__)


class FilenameExtractor:
    """Class to extract information from filename"""

    def __init__(self, file_path: Path | str):
        if isinstance(file_path, str):
            self.file_path = Path(file_path)
            self.file_name = file_path
        else:
            self.file_path = file_path
            self.file_name = file_path.name

        # Initialize utility helper
        self._pattern_extractor = PatternExtractor()

    def _normalize_cyrillic(self, text: str) -> str:
        """Normalize Cyrillic characters to English equivalents for parsing"""
        for cyr, eng in CYRILLIC_TO_ENGLISH.items():
            text = text.replace(cyr, eng)
        return text

    def _get_frame_class_from_height(self, height: int) -> str | None:
        """Get frame class from video height using FRAME_CLASSES constant"""
        for frame_class, info in FRAME_CLASSES.items():
            if height == info['nominal_height']:
                return frame_class
        return None

    @cached_method()
    def extract_title(self) -> str | None:
        """Extract movie title from filename"""
        # Find positions of year, source, and quality brackets
        year_pos = -1
        source_pos = -1
        quality_pos = -1
        paren_match = None
        dot_match = None
        
        # Find year position (either (YYYY) or .YYYY.)
        paren_match = re.search(r'\((\d{4})\)', self.file_name)
        if paren_match:
            year_pos = paren_match.start()
        else:
            dot_match = re.search(r'\.(\d{4})\.', self.file_name)
            if dot_match:
                year_pos = dot_match.start()
            else:
                # Last resort: any 4-digit number
                any_match = re.search(r'\b(\d{4})\b', self.file_name)
                if any_match:
                    year = int(any_match.group(1))
                    # Basic sanity check using constants
                    if is_valid_year(year):
                        year_pos = any_match.start()  # Cut before the year for plain years
        
        # Find source position
        source = self.extract_source()
        if source:
            for alias in SOURCE_DICT[source]:
                match = re.search(r'\b' + re.escape(alias) + r'\b', self.file_name, re.IGNORECASE)
                if match:
                    source_pos = match.start()
                    break
        
        # Find quality bracket position (like [720p,ukr,eng])
        quality_match = re.search(r'\[[^\]]*(?:720p|1080p|2160p|480p|SD|HD|HDR)[^\]]*\]', self.file_name)
        if quality_match:
            quality_pos = quality_match.start()
        
        # Find the earliest position that's not at the beginning
        positions = [pos for pos in [year_pos, source_pos, quality_pos] if pos > 0]
        cut_pos = min(positions) if positions else -1
        
        # Extract title (everything before the cut position)
        if cut_pos > 0:
            title = self.file_name[:cut_pos].strip()
        else:
            # No delimiters found after position 0, take everything before the last dot
            title = self.file_name.rsplit('.', 1)[0].strip()
        
        # If year is at the beginning, remove it
        if year_pos == 0:
            if paren_match and paren_match.start() == 0:
                title = re.sub(r'^\(\d{4}\)\s*', '', title)
            elif dot_match and dot_match.start() == 0:
                title = re.sub(r'^\.\d{4}\.\s*', '', title)
        
        # Remove common prefixes that are not part of the title
        # Remove bracketed prefixes like [01.1], [1], etc.
        title = re.sub(r'^\s*\[[^\]]+\]\s*', '', title)
        
        # Remove order number prefixes like 01., 1., 1.1 followed by space/underscore
        # Only remove if the number is multi-digit or has decimal (to avoid removing single digit titles)
        match = re.match(r'^\s*(\d+(?:\.\d+)?)\.(?=\s|_)', title)
        if match:
            order = match.group(1)
            if len(order) > 1 or '.' in order:
                title = re.sub(r'^\s*(\d+(?:\.\d+)?)\.(?=\s|_)', '', title)
        
        # Remove order like 1.9 where 1 is order, 9 is title
        order = self.extract_order()
        if order:
            match = re.match(r'^' + re.escape(order) + r'\.(.+)', title)
            if match:
                title = match.group(1)
        
        # Clean up any remaining leading separators
        title = title.lstrip('_ \t')
        
        # Clean up title: remove leading/trailing brackets and dots
        title = title.strip('[](). ')
        
        return title if title else None

    @cached_method()
    def extract_year(self) -> str | None:
        """Extract year from filename"""
        # First try to find year in parentheses (most common and reliable)
        paren_match = re.search(r'\((\d{4})\)', self.file_name)
        if paren_match:
            return paren_match.group(1)
        
        # Fallback: look for year in dots (like .1971.)
        dot_match = re.search(r'\.(\d{4})\.', self.file_name)
        if dot_match:
            return dot_match.group(1)
        
        # Last resort: any 4-digit number (but this is less reliable)
        any_match = re.search(r'\b(\d{4})\b', self.file_name)
        if any_match:
            year = int(any_match.group(1))
            # Basic sanity check using constants
            if is_valid_year(year):
                year_pos = any_match.start()
                return str(year)
        
        return None

    @cached_method()
    def extract_source(self) -> str | None:
        """Extract video source from filename"""
        temp_name = re.sub(r'\s*\(\d{4}\)\s*|\s*\d{4}\s*|\.\d{4}\.', ' ', self.file_name)

        for src, aliases in SOURCE_DICT.items():
            for alias in aliases:
                if alias.upper() in temp_name.upper():
                    return src
        return None

    @cached_method()
    def extract_order(self) -> str | None:
        """Extract collection order number from filename (at the beginning)"""
        # Look for order patterns at the start of filename
        # Patterns: [01], [01.1], 01., 1., 1.1 followed by space or underscore
        
        # Check for bracketed patterns: [01], [01.1], etc.
        bracket_match = re.match(r'^\[(\d+(?:\.\d+)?)\]', self.file_name)
        if bracket_match:
            return bracket_match.group(1)
        
        # Check for dot patterns: 01., 1., 1.1 followed by title before (
        dot_match = re.match(r'^(\d+(?:\.\d)*)\.?\s*', self.file_name)
        if dot_match and '.' in dot_match.group(0):
            order = dot_match.group(1)
            if '.' in order:
                parts = order.split('.')
                if len(parts) > 1 and parts[-1] != '1':
                    order = parts[0]
            return order
        
        return None

    @cached_method()
    def extract_frame_class(self) -> str | None:
        """Extract frame class from filename (480p, 720p, 1080p, 2160p, etc.)"""
        # Normalize Cyrillic characters for resolution parsing
        normalized_name = self._normalize_cyrillic(self.file_name)
        
        # First check for specific numeric resolutions with p/i
        match = re.search(r'(\d{3,4})([pi])', normalized_name, re.IGNORECASE)
        if match:
            height = int(match.group(1))
            scan_type = match.group(2).lower()
            frame_class = f"{height}{scan_type}"
            if frame_class in FRAME_CLASSES:
                return frame_class
            # Fallback to height-based if not in constants
            return self._get_frame_class_from_height(height)
        
        # If no specific resolution found, check for non-standard quality indicators
        for indicator in NON_STANDARD_QUALITY_INDICATORS:
            if re.search(r'\b' + re.escape(indicator) + r'\b', self.file_name, re.IGNORECASE):
                return None
        
        return None

    @cached_method()
    def extract_hdr(self) -> str | None:
        """Extract HDR information from filename"""
        # Check for SDR first - indicates no HDR
        if re.search(r'\bSDR\b', self.file_name, re.IGNORECASE):
            return None
        
        # Check for HDR, but not NoHDR
        if re.search(r'\bHDR\b', self.file_name, re.IGNORECASE) and not re.search(r'\bNoHDR\b', self.file_name, re.IGNORECASE):
            return 'HDR'
        
        return None

    @cached_method()
    def extract_movie_db(self) -> list[str] | None:
        """Extract movie database identifier from filename"""
        # Use PatternExtractor utility to avoid code duplication
        db_info = self._pattern_extractor.extract_movie_db_ids(self.file_name)
        if db_info:
            return [db_info['type'], db_info['id']]
        return None

    @cached_method()
    def extract_special_info(self) -> list[str] | None:
        """Extract special edition information from filename"""
        # Look for special edition indicators in brackets or as standalone text
        special_info = []
        
        for canonical_edition, variants in SPECIAL_EDITIONS.items():
            for edition in variants:
                # Check in brackets: [Theatrical Cut], [Director's Cut], etc.
                bracket_pattern = r'\[([^\]]+)\]'
                brackets = re.findall(bracket_pattern, self.file_name)
                for bracket in brackets:
                    # Check if bracket contains comma-separated items
                    items = [item.strip() for item in bracket.split(',')]
                    for item in items:
                        if edition.lower() == item.lower().strip():
                            if canonical_edition not in special_info:
                                special_info.append(canonical_edition)
                
                # Check as standalone text (case-insensitive)
                if re.search(r'\b' + re.escape(edition) + r'\b', self.file_name, re.IGNORECASE):
                    if canonical_edition not in special_info:
                        special_info.append(canonical_edition)
        
        return special_info if special_info else None

    @cached_method()
    def extract_audio_langs(self) -> str:
        """Extract audio languages from filename"""
        # Look for language patterns in brackets and outside brackets
        # Skip subtitle indicators and focus on audio languages
        
        langs = []
        
        # First, look for languages inside brackets
        bracket_pattern = r'\[([^\]]+)\]'
        brackets = re.findall(bracket_pattern, self.file_name)
        
        for bracket in brackets:
            bracket_lower = bracket.lower()
            
            # Skip brackets that contain movie database patterns
            if any(db in bracket_lower for db in ['imdb', 'tmdb', 'tvdb']):
                continue
            
            # Parse items separated by commas or underscores
            items = re.split(r'[,_]', bracket)
            items = [item.strip() for item in items]
            
            for item in items:
                # Skip empty items or items that are clearly not languages
                if not item or len(item) < 2:
                    continue
                
                item_lower = item.lower()
                
                # Skip subtitle indicators
                if item_lower in ['sub', 'subs', 'subtitle']:
                    continue
                
                # Check if item contains language codes (2-3 letter codes)
                # Pattern: optional number + optional 'x' + language code
                # Allow the language code to be at the end of the item
                lang_match = re.search(r'(?:(\d+)x?)?([a-z]{2,3})$', item_lower)
                if lang_match:
                    count = int(lang_match.group(1)) if lang_match.group(1) else 1
                    lang_code = lang_match.group(2)
                    
                    # Skip if it's a quality/resolution indicator or other skip word
                    if lang_code in SKIP_WORDS:
                        continue
                    
                    # Skip if the language code is not at the end or if there are extra letters after
                    # But allow prefixes like numbers and 'x'
                    prefix = item_lower[:-len(lang_code)]
                    if not re.match(r'^(?:\d+x?)?$', prefix):
                        continue
                    
                    # Convert to 3-letter ISO code
                    try:
                        lang_obj = langcodes.Language.get(lang_code)
                        iso3_code = lang_obj.to_alpha3()
                        langs.extend([iso3_code] * count)
                    except (LookupError, ValueError, AttributeError) as e:
                        # Skip invalid language codes
                        logger.debug(f"Invalid language code '{lang_code}': {e}")
                        pass
        
        # Second, look for standalone language codes outside brackets
        # Remove bracketed content first
        text_without_brackets = re.sub(r'\[([^\]]+)\]', '', self.file_name)

        # Split on dots, spaces, and underscores
        parts = re.split(r'[.\s_]+', text_without_brackets)

        for part in parts:
            part = part.strip()
            if not part or len(part) < 2:
                continue

            part_lower = part.lower()

            # Check if this part is a 2-3 letter code
            if not re.match(r'^[a-zA-Z]{2,3}$', part):
                continue

            # Skip title case 2-letter words to avoid false positives like "In" -> "ind"
            if part.istitle() and len(part) == 2:
                continue

            # Skip known non-language words
            if part_lower in SKIP_WORDS:
                continue

            # Try to validate with langcodes library
            try:
                lang_obj = langcodes.Language.get(part_lower)
                iso3_code = lang_obj.to_alpha3()
                langs.append(iso3_code)
            except (LookupError, ValueError, AttributeError) as e:
                # Not a valid language code, skip
                logger.debug(f"Invalid language code '{part_lower}': {e}")
                pass
        
        if not langs:
            return ''
            
        # Count occurrences while preserving order of first appearance
        lang_counts = {}
        for lang in langs:
            if lang not in lang_counts:
                lang_counts[lang] = 0
            lang_counts[lang] += 1
        
        # Format like mediainfo: "2ukr,eng" preserving order
        audio_langs = [f"{count}{lang}" if count > 1 else lang for lang, count in lang_counts.items()]
        return ','.join(audio_langs)

    @cached_method()
    def extract_extension(self) -> str | None:
        """Extract file extension from filename"""
        # Use pathlib to extract extension properly
        ext = self.file_path.suffix
        # Remove leading dot and return
        return ext[1:] if ext else None

    @cached_method()
    def extract_audio_tracks(self) -> list[dict]:
        """Extract audio track data from filename (simplified version with only language)"""
        # Similar to extract_audio_langs but returns list of dicts

        tracks = []

        # First, look for languages inside brackets
        bracket_pattern = r'\[([^\]]+)\]'
        brackets = re.findall(bracket_pattern, self.file_name)

        for bracket in brackets:
            bracket_lower = bracket.lower()

            # Skip brackets that contain movie database patterns
            if any(db in bracket_lower for db in ['imdb', 'tmdb', 'tvdb']):
                continue

            # Parse items separated by commas or underscores
            items = re.split(r'[,_]', bracket)
            items = [item.strip() for item in items]

            for item in items:
                # Skip empty items or items that are clearly not languages
                if not item or len(item) < 2:
                    continue

                item_lower = item.lower()

                # Skip subtitle indicators
                if item_lower in ['sub', 'subs', 'subtitle']:
                    continue

                # Check if item contains language codes (2-3 letter codes)
                # Pattern: optional number + optional 'x' + language code
                # Allow the language code to be at the end of the item
                lang_match = re.search(r'(?:(\d+)x?)?([a-z]{2,3})$', item_lower)
                if lang_match:
                    count = int(lang_match.group(1)) if lang_match.group(1) else 1
                    lang_code = lang_match.group(2)

                    # Skip if it's a quality/resolution indicator or other skip word
                    if lang_code in SKIP_WORDS:
                        continue

                    # Skip if the language code is not at the end or if there are extra letters after
                    # But allow prefixes like numbers and 'x'
                    prefix = item_lower[:-len(lang_code)]
                    if not re.match(r'^(?:\d+x?)?$', prefix):
                        continue

                    # Convert to 3-letter ISO code
                    try:
                        lang_obj = langcodes.Language.get(lang_code)
                        iso3_code = lang_obj.to_alpha3()
                        tracks.append({'language': iso3_code})
                    except (LookupError, ValueError, AttributeError) as e:
                        # Skip invalid language codes
                        logger.debug(f"Invalid language code '{lang_code}': {e}")
                        pass

        # Second, look for standalone language codes outside brackets
        # Remove bracketed content first
        text_without_brackets = re.sub(r'\[([^\]]+)\]', '', self.file_name)

        # Split on dots, spaces, and underscores
        parts = re.split(r'[.\s_]+', text_without_brackets)

        for part in parts:
            part = part.strip()
            if not part or len(part) < 2:
                continue

            part_lower = part.lower()

            # Check if this part is a 2-3 letter code
            if not re.match(r'^[a-zA-Z]{2,3}$', part):
                continue

            # Skip title case 2-letter words to avoid false positives like "In" -> "ind"
            if part.istitle() and len(part) == 2:
                continue

            # Skip known non-language words
            if part_lower in SKIP_WORDS:
                continue

            # Try to validate with langcodes library
            try:
                lang_obj = langcodes.Language.get(part_lower)
                iso3_code = lang_obj.to_alpha3()
                tracks.append({'language': iso3_code})
            except (LookupError, ValueError, AttributeError) as e:
                # Not a valid language code, skip
                logger.debug(f"Invalid language code '{part_lower}': {e}")
                pass

        return tracks