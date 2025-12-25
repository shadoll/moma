from pathlib import Path
from ..constants import VIDEO_EXT_DESCRIPTIONS
from ..utils import detect_file_type


class ExtensionFormatter:
    """Class for formatting extension information"""
    
    @staticmethod
    def check_extension_match(ext_name: str, meta_type: str) -> bool:
        """Check if file extension matches detected type"""
        if ext_name.upper() == meta_type:
            return True
        elif ext_name == 'mkv' and meta_type == 'Matroska':
            return True
        elif ext_name == 'avi' and meta_type == 'AVI':
            return True
        elif ext_name == 'mov' and meta_type == 'QuickTime':
            return True
        elif ext_name == 'wmv' and meta_type == 'ASF':
            return True
        elif ext_name == 'flv' and meta_type == 'FLV':
            return True
        elif ext_name == 'webm' and meta_type == 'WebM':
            return True
        elif ext_name == 'ogv' and meta_type == 'Ogg':
            return True
        return False
    
    @staticmethod
    def format_extension_info(ext_name: str, ext_desc: str, meta_type: str, meta_desc: str, match: bool) -> str:
        """Format extension information with match status"""
        if match:
            return f"[bold green]Extension:[/bold green] {ext_name} - [grey]{ext_desc}[/grey]"
        else:
            return (f"[bold yellow]Extension:[/bold yellow] {ext_name} - [grey]{ext_desc}[/grey]\n"
                    f"[bold red]Meta extension:[/bold red] {meta_type} - [grey]{meta_desc}[/grey]\n"
                    "[bold red]Warning: Extensions do not match![/bold red]")