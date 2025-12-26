import re
from pathlib import Path
from ..constants import SOURCE_DICT, FRAME_CLASSES, MOVIE_DB_DICT


class FilenameExtractor:
    """Class to extract information from filename"""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.file_name = file_path.name

    def _get_frame_class_from_height(self, height: int) -> str:
        """Get frame class from video height using FRAME_CLASSES constant"""
        for frame_class, info in FRAME_CLASSES.items():
            if height == info['nominal_height']:
                return frame_class
        return 'Unclassified'

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
        
        # Clean up title: remove leading/trailing brackets and dots
        title = title.strip('[](). ')
        
        # Replace colons with periods in the title
        title = title.replace(':', '.')
        
        return title if title else None

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
            year = any_match.group(1)
            # Basic sanity check: years should be between 1900 and current year + a few years
            current_year = 2025  # Update this as needed
            if 1900 <= int(year) <= current_year + 10:
                return year
        
        return None

    def extract_source(self) -> str | None:
        """Extract video source from filename"""
        temp_name = re.sub(r'\s*\(\d{4}\)\s*|\s*\d{4}\s*|\.\d{4}\.', ' ', self.file_name)

        for src, aliases in SOURCE_DICT.items():
            for alias in aliases:
                if alias.upper() in temp_name.upper():
                    return src
        return None

    def extract_frame_class(self) -> str | None:
        """Extract frame class from filename (480p, 720p, 1080p, 2160p, etc.)"""
        # First check for specific numeric resolutions
        match = re.search(r'(\d{3,4})[pi]', self.file_name, re.IGNORECASE)
        if match:
            height = int(match.group(1))
            return self._get_frame_class_from_height(height)
        
        # If no specific resolution found, check for quality indicators
        unclassified_indicators = ['SD', 'LQ', 'HD', 'QHD']
        for indicator in unclassified_indicators:
            if re.search(r'\b' + re.escape(indicator) + r'\b', self.file_name, re.IGNORECASE):
                return 'Unclassified'
        
        return 'Unclassified'

    def extract_hdr(self) -> str | None:
        """Extract HDR information from filename"""
        # Check for SDR first - indicates no HDR
        if re.search(r'\bSDR\b', self.file_name, re.IGNORECASE):
            return None
        
        # Check for HDR, but not NoHDR
        if re.search(r'\bHDR\b', self.file_name, re.IGNORECASE) and not re.search(r'\bNoHDR\b', self.file_name, re.IGNORECASE):
            return 'HDR'
        
        return None

    def extract_movie_db(self) -> tuple[str, str] | None:
        """Extract movie database identifier from filename"""
        # Look for patterns at the end of filename in brackets or braces
        # Patterns: [tmdbid-123] {imdb-tt123} [imdbid-tt123] etc.
        
        # Match patterns like [tmdbid-123456] or {imdb-tt1234567}
        pattern = r'[\[\{]([a-zA-Z]+(?:id)?)[-\s]*([a-zA-Z0-9]+)[\]\}]'
        matches = re.findall(pattern, self.file_name)
        
        if matches:
            # Take the last match (closest to end of filename)
            db_type, db_id = matches[-1]
            
            # Normalize database type
            db_type_lower = db_type.lower()
            for db_key, db_info in MOVIE_DB_DICT.items():
                if any(db_type_lower.startswith(pattern.rstrip('-')) for pattern in db_info['patterns']):
                    return (db_key, db_id)
        
        return None