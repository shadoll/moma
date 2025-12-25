from pathlib import Path
from .size_formatter import SizeFormatter
from .date_formatter import DateFormatter
from .extension_extractor import ExtensionExtractor
from .extension_formatter import ExtensionFormatter
from ..utils import detect_file_type


class MediaFormatter:
    """Class to format media data for display"""

    def format_file_info(self, file_path: Path, rename_data: dict) -> str:
        """Format complete file information for display"""
        # Get file stats
        size_full = SizeFormatter.format_size_full(file_path.stat().st_size)
        date_formatted = DateFormatter.format_modification_date(file_path.stat().st_mtime)
        
        # Get extension info
        ext_name = ExtensionExtractor.get_extension_name(file_path)
        ext_desc = ExtensionExtractor.get_extension_description(ext_name)
        meta_type, meta_desc = detect_file_type(file_path)
        match = ExtensionFormatter.check_extension_match(ext_name, meta_type)
        ext_info = ExtensionFormatter.format_extension_info(ext_name, ext_desc, meta_type, meta_desc, match)
        
        file_name = file_path.name
        
        # Build basic info
        full_info = f"[bold blue]Path:[/bold blue] {str(file_path)}\n\n"
        full_info += f"[bold green]Size:[/bold green] {size_full}\n"
        full_info += f"[bold cyan]File:[/bold cyan] {file_name}\n"
        full_info += f"{ext_info}\n"
        full_info += f"[bold magenta]Modified:[/bold magenta] {date_formatted}"
        
        # Extra metadata
        extra_text = self._format_extra_metadata(rename_data['metadata'])
        if extra_text:
            full_info += f"\n\n{extra_text}"
        
        return full_info

    def format_proposed_name(self, rename_data: dict, ext_name: str) -> str:
        """Format the proposed filename"""
        proposed_parts = []
        if rename_data['title']:
            proposed_parts.append(rename_data['title'])
        if rename_data['year']:
            proposed_parts.append(f"({rename_data['year']})")
        if rename_data['source']:
            proposed_parts.append(rename_data['source'])

        tags = []
        if rename_data['resolution']:
            tags.append(rename_data['resolution'])
        if rename_data['hdr']:
            tags.append(rename_data['hdr'])
        if rename_data['audio_langs']:
            tags.append(rename_data['audio_langs'])
        if tags:
            proposed_parts.append(f"[{','.join(tags)}]")

        return ' '.join(proposed_parts) + f".{ext_name}"

    def format_rename_lines(self, rename_data: dict, proposed_name: str) -> list[str]:
        """Format the rename information lines"""
        lines = []
        lines.append(f"Movie title: {rename_data['title'] or 'Unknown'}")
        lines.append(f"Year: {rename_data['year'] or 'Unknown'}")
        lines.append(f"Video source: {rename_data['source'] or 'Unknown'}")
        lines.append(f"Resolution: {rename_data['resolution'] or 'Unknown'}")
        lines.append(f"HDR: {rename_data['hdr'] or 'No'}")
        lines.append(f"Audio langs: {rename_data['audio_langs'] or 'None'}")
        lines.append(f"Proposed filename: {proposed_name}")
        return lines

    def _format_extra_metadata(self, metadata: dict) -> str:
        """Format extra metadata like duration, title, artist"""
        extra_info = []
        if metadata.get('duration'):
            extra_info.append(f"[cyan]Duration:[/cyan] {metadata['duration']:.1f} seconds")
        if metadata.get('title'):
            extra_info.append(f"[cyan]Title:[/cyan] {metadata['title']}")
        if metadata.get('artist'):
            extra_info.append(f"[cyan]Artist:[/cyan] {metadata['artist']}")
        return "\n".join(extra_info) if extra_info else ""