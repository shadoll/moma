from textual.app import App, ComposeResult
from textual.widgets import Tree, Static, Footer
from textual.containers import Horizontal, Container, ScrollableContainer
from textual.screen import Screen
from textual.widgets import Input, Button
from pathlib import Path
import mutagen
import magic
from pymediainfo import MediaInfo
import os
import argparse
from datetime import datetime

VIDEO_EXTENSIONS = {'.mkv', '.avi', '.mov', '.mp4', '.wmv', '.flv', '.webm', '.m4v', '.3gp', '.ogv'}

VIDEO_EXT_DESCRIPTIONS = {
    'mkv': 'Matroska multimedia container',
    'avi': 'Audio Video Interleave',
    'mov': 'QuickTime movie',
    'mp4': 'MPEG-4 video container',
    'wmv': 'Windows Media Video',
    'flv': 'Flash Video',
    'webm': 'WebM multimedia',
    'm4v': 'MPEG-4 video',
    '3gp': '3GPP multimedia',
    'ogv': 'Ogg Video',
}

META_DESCRIPTIONS = {
    'MP4': 'MPEG-4 video container',
    'Matroska': 'Matroska multimedia container',
    'AVI': 'Audio Video Interleave',
    'QuickTime': 'QuickTime movie',
    'ASF': 'Windows Media',
    'FLV': 'Flash Video',
    'WebM': 'WebM multimedia',
    'Ogg': 'Ogg multimedia',
}

def format_size(bytes_size):
    """Format bytes to human readable with unit"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.1f} TB"

def get_media_tracks(file_path):
    """Extract compact media track information"""
    tracks_info = []
    try:
        media_info = MediaInfo.parse(file_path)
        video_tracks = [t for t in media_info.tracks if t.track_type == 'Video']
        audio_tracks = [t for t in media_info.tracks if t.track_type == 'Audio']
        sub_tracks = [t for t in media_info.tracks if t.track_type == 'Text']
        
        # Video tracks
        for i, v in enumerate(video_tracks[:2]):  # Up to 2 videos
            codec = getattr(v, 'format', None) or getattr(v, 'codec', None) or 'unknown'
            width = getattr(v, 'width', None) or '?'
            height = getattr(v, 'height', None) or '?'
            bitrate = getattr(v, 'bit_rate', None)
            fps = getattr(v, 'frame_rate', None)
            profile = getattr(v, 'format_profile', None)
            
            video_str = f"{codec} {width}x{height}"
            if bitrate:
                video_str += f" {bitrate}bps"
            if fps:
                video_str += f" {fps}fps"
            if profile:
                video_str += f" ({profile})"
            
            tracks_info.append(f"[green]Video {i+1}:[/green] {video_str}")
        
        # Audio tracks
        for i, a in enumerate(audio_tracks[:3]):  # Up to 3 audios
            codec = getattr(a, 'format', None) or getattr(a, 'codec', None) or 'unknown'
            channels = getattr(a, 'channel_s', None) or '?'
            lang = getattr(a, 'language', None) or 'und'
            bitrate = getattr(a, 'bit_rate', None)
            
            audio_str = f"{codec} {channels}ch {lang}"
            if bitrate:
                audio_str += f" {bitrate}bps"
            
            tracks_info.append(f"[yellow]Audio {i+1}:[/yellow] {audio_str}")
        
        # Subtitle tracks
        for i, s in enumerate(sub_tracks[:3]):  # Up to 3 subs
            lang = getattr(s, 'language', None) or 'und'
            format = getattr(s, 'format', None) or getattr(s, 'codec', None) or 'unknown'
            
            sub_str = f"{lang} ({format})"
            tracks_info.append(f"[magenta]Sub {i+1}:[/magenta] {sub_str}")
            
    except Exception as e:
        tracks_info.append(f"[red]Track info error: {str(e)}[/red]")
    
    return "\n".join(tracks_info) if tracks_info else ""

class OpenScreen(Screen):
    def compose(self):
        yield Input(placeholder="Enter directory path", value=".", id="dir_input")
        yield Button("OK", id="ok")

    def on_button_pressed(self, event):
        if event.button.id == "ok":
            self.submit_path()

    def on_input_submitted(self, event):
        self.submit_path()

    def submit_path(self):
        path_str = self.query_one("#dir_input", Input).value
        path = Path(path_str)
        if not path.exists():
            # Show error
            self.query_one("#dir_input", Input).value = f"Path does not exist: {path_str}"
            return
        if not path.is_dir():
            self.query_one("#dir_input", Input).value = f"Not a directory: {path_str}"
            return
        self.app.scan_dir = path
        self.app.scan_files()
        self.app.pop_screen()

class RenamerApp(App):
    CSS = """
    #left {
        width: 50%;
        padding: 1;
    }
    #right {
        width: 50%;
        padding: 1;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("o", "open", "Open directory"),
        ("s", "scan", "Scan"),
    ]

    def __init__(self, scan_dir):
        super().__init__()
        self.scan_dir = Path(scan_dir) if scan_dir else None

    def compose(self) -> ComposeResult:
        with Horizontal():
            with Container(id="left"):
                yield Tree("Files", id="file_tree")
            with Container(id="right"):
                with ScrollableContainer():
                    yield Static("Select a file to view details", id="details")
        yield Footer()

    def on_mount(self):
        self.scan_files()

    def scan_files(self):
        if not self.scan_dir.exists() or not self.scan_dir.is_dir():
            details = self.query_one("#details", Static)
            details.update("Error: Directory does not exist or is not a directory")
            return
        tree = self.query_one("#file_tree", Tree)
        tree.clear()
        tree.root.add(".", data=self.scan_dir)
        self.build_tree(self.scan_dir, tree.root)
        tree.root.expand()
        self.set_focus(tree)

    def build_tree(self, path: Path, node):
        try:
            for item in sorted(path.iterdir()):
                try:
                    if item.is_dir():
                        subnode = node.add(item.name, data=item)
                        self.build_tree(item, subnode)
                    elif item.is_file() and item.suffix.lower() in VIDEO_EXTENSIONS:
                        node.add(item.name, data=item)
                except PermissionError:
                    pass
        except PermissionError:
            pass

    def on_tree_node_highlighted(self, event):
        node = event.node
        if node.data and isinstance(node.data, Path):
            if node.data.is_dir():
                details = self.query_one("#details", Static)
                details.update("Directory")
            elif node.data.is_file():
                self.show_details(node.data)

    def show_details(self, file_path: Path):
        details = self.query_one("#details", Static)
        size = file_path.stat().st_size
        size_formatted = format_size(size)
        size_full = f"{size_formatted} ({size:,} bytes)"
        ext_name = file_path.suffix.lower().lstrip('.')
        ext_desc = VIDEO_EXT_DESCRIPTIONS.get(ext_name, f'Unknown extension .{ext_name}')
        mtime = file_path.stat().st_mtime
        date_formatted = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
        file_name = file_path.name
        # Detect real type and extract metadata
        try:
            info = mutagen.File(file_path)
            mime = None
            if info is None:
                # Fallback to magic
                mime = magic.from_file(str(file_path), mime=True)
                if mime == 'video/x-matroska':
                    meta_type = 'Matroska'
                    meta_desc = 'Matroska multimedia container'
                elif mime == 'video/mp4':
                    meta_type = 'MP4'
                    meta_desc = 'MPEG-4 video container'
                elif mime == 'video/x-msvideo':
                    meta_type = 'AVI'
                    meta_desc = 'Audio Video Interleave'
                elif mime == 'video/quicktime':
                    meta_type = 'QuickTime'
                    meta_desc = 'QuickTime movie'
                elif mime == 'video/x-ms-wmv':
                    meta_type = 'ASF'
                    meta_desc = 'Windows Media'
                elif mime == 'video/x-flv':
                    meta_type = 'FLV'
                    meta_desc = 'Flash Video'
                elif mime == 'video/webm':
                    meta_type = 'WebM'
                    meta_desc = 'WebM multimedia'
                elif mime == 'video/ogg':
                    meta_type = 'Ogg'
                    meta_desc = 'Ogg multimedia'
                else:
                    meta_type = 'Unknown'
                    meta_desc = f'Unknown MIME: {mime}'
            else:
                meta_type = type(info).__name__
                meta_desc = META_DESCRIPTIONS.get(meta_type, f'Unknown type {meta_type}')
            
            # Extract additional metadata
            extra_info = []
            if info:
                duration = getattr(info, 'length', None)
                title = getattr(info, 'title', None) or getattr(info, 'get', lambda x, default=None: default)('title', [None])[0]
                artist = getattr(info, 'artist', None) or getattr(info, 'get', lambda x, default=None: default)('artist', [None])[0]
                if duration:
                    extra_info.append(f"[cyan]Duration:[/cyan] {duration:.1f} seconds")
                if title:
                    extra_info.append(f"[cyan]Title:[/cyan] {title}")
                if artist:
                    extra_info.append(f"[cyan]Artist:[/cyan] {artist}")
            
            extra_text = "\n".join(extra_info) if extra_info else ""
        except Exception as e:
            meta_type = f'Error: {str(e)}'
            meta_desc = f'Error detecting type'
            extra_text = ""
        
        # Get media tracks info
        tracks_text = get_media_tracks(file_path)
        
        # Check if extensions match
        match = False
        if ext_name.upper() == meta_type:
            match = True
        elif ext_name == 'mkv' and meta_type == 'Matroska':
            match = True
        elif ext_name == 'avi' and meta_type == 'AVI':
            match = True
        elif ext_name == 'mov' and meta_type == 'QuickTime':
            match = True
        elif ext_name == 'wmv' and meta_type == 'ASF':
            match = True
        elif ext_name == 'flv' and meta_type == 'FLV':
            match = True
        elif ext_name == 'webm' and meta_type == 'WebM':
            match = True
        elif ext_name == 'ogv' and meta_type == 'Ogg':
            match = True
        
        if match:
            ext_info = f"[bold green]Extension:[/bold green] {ext_name} - [grey]{ext_desc}[/grey]"
        else:
            ext_info = f"[bold yellow]Extension:[/bold yellow] {ext_name} - [grey]{ext_desc}[/grey]\n[bold red]Meta extension:[/bold red] {meta_type} - [grey]{meta_desc}[/grey]\n[bold red]Warning: Extensions do not match![/bold red]"
        
        full_info = f"[bold blue]Path:[/bold blue] {str(file_path).replace('[', '[[')}\n\n[bold green]Size:[/bold green] {size_full}\n[bold cyan]File:[/bold cyan] {file_name.replace('[', '[[')}\n{ext_info}\n[bold magenta]Modified:[/bold magenta] {date_formatted}"
        if extra_text:
            full_info += f"\n\n{extra_text}"
        if tracks_text:
            full_info += f"\n\n{tracks_text}"
        
        details.update(full_info)

    def action_quit(self):
        self.exit()

    def action_open(self):
        self.push_screen(OpenScreen())

    def action_scan(self):
        if self.scan_dir:
            self.scan_files()

    def on_key(self, event):
        if event.key == "right":
            tree = self.query_one("#file_tree", Tree)
            node = tree.cursor_node
            if node and node.data and isinstance(node.data, Path) and node.data.is_dir():
                if not node.is_expanded:
                    node.expand()
                    tree.cursor_line = node.line + 1
                event.prevent_default()
        elif event.key == "left":
            tree = self.query_one("#file_tree", Tree)
            node = tree.cursor_node
            if node and node.parent:
                if node.is_expanded:
                    node.collapse()
                else:
                    tree.cursor_line = node.parent.line
                event.prevent_default()

def main():
    parser = argparse.ArgumentParser(description="Media file renamer")
    parser.add_argument("directory", nargs="?", default=".", help="Directory to scan")
    args = parser.parse_args()
    app = RenamerApp(args.directory)
    app.run()

if __name__ == "__main__":
    main()
