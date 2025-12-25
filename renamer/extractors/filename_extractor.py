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
        year_match = re.search(r'\((\d{4})\)|(\d{4})', self.file_name)
        return (year_match.group(1) or year_match.group(2)) if year_match else None

    def extract_source(self) -> str | None:
        """Extract video source from filename"""
        temp_name = re.sub(r'\s*\(\d{4}\)\s*|\s*\d{4}\s*|\.\d{4}\.', '', self.file_name)

        for src, aliases in SOURCE_DICT.items():
            for alias in aliases:
                if re.search(r'\b' + re.escape(alias) + r'\b', temp_name, re.IGNORECASE):
                    return src
        return None

    def extract_frame_class(self) -> str | None:
        """Extract frame class from filename (480p, 720p, 1080p, 2160p, etc.)"""
        match = re.search(r'(\d{3,4})[pi]', self.file_name, re.IGNORECASE)
        if match:
            height = int(match.group(1))
            return self._get_frame_class_from_height(height)
        return 'Unclassified'