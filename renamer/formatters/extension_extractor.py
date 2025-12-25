from pathlib import Path
from ..constants import VIDEO_EXT_DESCRIPTIONS


class ExtensionExtractor:
    """Class for extracting extension information"""
    
    @staticmethod
    def get_extension_name(file_path: Path) -> str:
        """Get extension name without dot"""
        return file_path.suffix.lower().lstrip('.')
    
    @staticmethod
    def get_extension_description(ext_name: str) -> str:
        """Get description for extension"""
        return VIDEO_EXT_DESCRIPTIONS.get(ext_name, f'Unknown extension .{ext_name}')