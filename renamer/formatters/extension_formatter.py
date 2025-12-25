from pathlib import Path
from ..constants import MEDIA_TYPES
from .color_formatter import ColorFormatter


class ExtensionFormatter:
    """Class for formatting extension information"""
    
    @staticmethod
    def check_extension_match(ext_name: str, meta_type: str) -> bool:
        """Check if file extension matches detected type"""
        if ext_name in MEDIA_TYPES and MEDIA_TYPES[ext_name]['meta_type'] == meta_type:
            return True
        return False
    
    @staticmethod
    def format_extension_info(ext_name: str, ext_desc: str, meta_type: str, meta_desc: str, match: bool) -> str:
        """Format extension information with match status"""
        if match:
            return f"{ColorFormatter.bold_green('Extension:')} {ext_name} - {ColorFormatter.grey(ext_desc)}"
        else:
            return (f"{ColorFormatter.bold_yellow('Extension:')} {ext_name} - {ColorFormatter.grey(ext_desc)}\n"
                    f"{ColorFormatter.bold_red('Meta extension:')} {meta_type} - {ColorFormatter.grey(meta_desc)}\n"
                    f"{ColorFormatter.bold_red('Warning: Extensions do not match!')}")