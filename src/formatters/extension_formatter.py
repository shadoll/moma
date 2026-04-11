from pathlib import Path
from ..constants import MEDIA_TYPES
from .text_formatter import TextFormatter


class ExtensionFormatter:
    """Class for formatting extension information"""
    
    @staticmethod
    def format_extension_info(ext_name: str) -> str:
        """Format extension information"""
        if ext_name in MEDIA_TYPES:
            ext_desc = MEDIA_TYPES[ext_name]['description']
            return f"{ext_name} - {TextFormatter.grey(ext_desc)}"
        else:
            return f"{ext_name} - {TextFormatter.grey('Unknown extension')}"