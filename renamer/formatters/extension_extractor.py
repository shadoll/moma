from pathlib import Path
from ..constants import MEDIA_TYPES


class ExtensionExtractor:
    """Class for extracting extension information"""
    
    @staticmethod
    def get_extension_name(file_path: Path) -> str:
        """Get extension name without dot"""
        return file_path.suffix.lower().lstrip('.')
    
    @staticmethod
    def get_extension_description(ext_name: str) -> str:
        """Get description for extension"""
        return MEDIA_TYPES.get(ext_name, {}).get('description', f'Unknown extension .{ext_name}')