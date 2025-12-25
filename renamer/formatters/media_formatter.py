from pathlib import Path
from .size_formatter import SizeFormatter
from .date_formatter import DateFormatter
from .extension_extractor import ExtensionExtractor
from .extension_formatter import ExtensionFormatter
from ..utils import detect_file_type


class MediaFormatter:
    """Class to format media data for display"""

    def format_file_info_panel(self, file_path: Path, rename_data: dict) -> str:
        """Format file information for the file info panel"""
        output = []

        # Panel title
        output.append("[bold blue]FILE INFO[/bold blue]")
        output.append("")  # Empty line for spacing

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

        output.append(f"[bold blue]Path:[/bold blue] {str(file_path)}")
        output.append(f"[bold green]Size:[/bold green] {size_full}")
        output.append(f"[bold cyan]File:[/bold cyan] {file_name}")
        output.append(f"[bold magenta]Modified:[/bold magenta] {date_formatted}")
        output.append(f"{ext_info}")

        return "\n".join(output)

    def format_filename_extraction_panel(self, rename_data: dict) -> str:
        """Format filename extraction data for the filename panel"""
        output = []
        output.append("[bold yellow]FILENAME EXTRACTION[/bold yellow]")
        output.append("")  # Empty line for spacing
        output.append(f"[yellow]Title:[/yellow] {rename_data.get('title', 'Not found')}")
        output.append(f"[yellow]Year:[/yellow] {rename_data.get('year', 'Not found')}")
        output.append(f"[yellow]Source:[/yellow] {rename_data.get('source', 'Not found')}")
        output.append(f"[yellow]Frame Class:[/yellow] {rename_data.get('frame_class', 'Not found')}")
        return "\n".join(output)

    def format_metadata_extraction_panel(self, rename_data: dict) -> str:
        """Format metadata extraction data for the metadata panel"""
        output = []
        output.append("[bold cyan]METADATA EXTRACTION[/bold cyan]")
        output.append("")  # Empty line for spacing
        metadata = rename_data.get('metadata', {})
        if metadata.get('duration'):
            output.append(f"[cyan]Duration:[/cyan] {metadata['duration']:.1f} seconds")
        if metadata.get('title'):
            output.append(f"[cyan]Title:[/cyan] {metadata['title']}")
        if metadata.get('artist'):
            output.append(f"[cyan]Artist:[/cyan] {metadata['artist']}")
        if not any(key in metadata for key in ['duration', 'title', 'artist']):
            output.append("[dim]No metadata found[/dim]")
        return "\n".join(output) if output else "[dim]No metadata found[/dim]"

    def format_mediainfo_extraction_panel(self, rename_data: dict) -> str:
        """Format media info extraction data for the mediainfo panel"""
        output = []
        output.append("[bold green]MEDIA INFO EXTRACTION[/bold green]")
        output.append("")  # Empty line for spacing
        output.append(f"[green]Resolution:[/green] {rename_data.get('resolution', 'Not found')}")
        output.append(f"[green]Aspect Ratio:[/green] {rename_data.get('aspect_ratio', 'Not found')}")
        output.append(f"[green]HDR:[/green] {rename_data.get('hdr', 'Not found')}")
        output.append(f"[green]Audio Languages:[/green] {rename_data.get('audio_langs', 'Not found')}")
        return "\n".join(output)

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
        if rename_data['frame_class'] and rename_data['frame_class'] != 'Unclassified':
            tags.append(rename_data['frame_class'])
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
        lines.append(f"Frame class: {rename_data['frame_class'] or 'Unknown'}")
        lines.append(f"Resolution: {rename_data['resolution'] or 'Unknown'}")
        lines.append(f"Aspect ratio: {rename_data['aspect_ratio'] or 'Unknown'}")
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