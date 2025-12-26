import re
from pathlib import Path
from ..constants import SOURCE_DICT, FRAME_CLASSES


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
        temp_name = re.sub(r'\s*\(\d{4}\)\s*|\s*\d{4}\s*|\.\d{4}\.', '', self.file_name)

        # Find and remove source
        source = self.extract_source()
        if source:
            for alias in SOURCE_DICT[source]:
                temp_name = re.sub(r'\b' + re.escape(alias) + r'\b', '', temp_name, flags=re.IGNORECASE)

        return temp_name.rsplit('.', 1)[0].strip()

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