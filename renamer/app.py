from textual.app import App, ComposeResult
from textual.widgets import Tree, Static, Footer, LoadingIndicator
from textual.containers import Horizontal, Container, ScrollableContainer, Vertical
from pathlib import Path
import threading
import time

from .constants import VIDEO_EXTENSIONS
from .utils import get_media_tracks
from .screens import OpenScreen
from .extractor import MediaExtractor
from .formatters.media_formatter import MediaFormatter


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
                with Vertical():
                    yield LoadingIndicator(id="loading")
                    with ScrollableContainer(id="details_container"):
                        yield Static("Select a file to view details", id="details", markup=True)
                    yield Static("", id="proposed", markup=True)
        yield Footer()

    def on_mount(self):
        loading = self.query_one("#loading", LoadingIndicator)
        loading.display = False
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

    def _start_loading_animation(self):
        loading = self.query_one("#loading", LoadingIndicator)
        loading.display = True
        details = self.query_one("#details", Static)
        details.update("Retrieving media data")
        proposed = self.query_one("#proposed", Static)
        proposed.update("")

    def _stop_loading_animation(self):
        loading = self.query_one("#loading", LoadingIndicator)
        loading.display = False

    def on_tree_node_highlighted(self, event):
        node = event.node
        if node.data and isinstance(node.data, Path):
            if node.data.is_dir():
                self._stop_loading_animation()
                details = self.query_one("#details", Static)
                details.update("Directory")
                proposed = self.query_one("#proposed", Static)
                proposed.update("")
            elif node.data.is_file():
                self._start_loading_animation()
                threading.Thread(target=self._extract_and_show_details, args=(node.data,)).start()

    def _extract_and_show_details(self, file_path: Path):
        time.sleep(1)  # Minimum delay to show loading
        # Initialize extractors and formatters
        extractor = MediaExtractor()
        formatter = MediaFormatter()
        
        # Extract all data
        rename_data = extractor.extract_all(file_path)
        
        # Get media tracks info
        tracks_text = get_media_tracks(file_path)
        if not tracks_text:
            tracks_text = "[grey]No track info available[/grey]"
        
        # Format file info
        full_info = formatter.format_file_info(file_path, rename_data)
        full_info += f"\n\n{tracks_text}"
        
        # Format proposed name
        ext_name = file_path.suffix.lower().lstrip('.')
        proposed_name = formatter.format_proposed_name(rename_data, ext_name)
        
        # Format rename lines
        rename_lines = formatter.format_rename_lines(rename_data, proposed_name)
        full_info += f"\n\n" + "\n".join(rename_lines[:-1])
        
        # Update UI
        self.call_later(self._update_details, full_info, proposed_name)

    def _update_details(self, full_info: str, proposed_name: str):
        self._stop_loading_animation()
        details = self.query_one("#details", Static)
        details.update(full_info)
        
        proposed = self.query_one("#proposed", Static)
        proposed.update(f"[bold yellow]Proposed filename: {proposed_name}[/bold yellow]")

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