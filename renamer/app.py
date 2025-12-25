from textual.app import App, ComposeResult
from textual.widgets import Tree, Static, Footer, LoadingIndicator
from textual.containers import Horizontal, Container, ScrollableContainer, Vertical
from pathlib import Path
import threading
import time
import concurrent.futures

from .constants import MEDIA_TYPES
from .screens import OpenScreen
from .extractor import MediaExtractor
from .formatters.media_formatter import MediaFormatter
from .formatters.proposed_name_formatter import ProposedNameFormatter
from .formatters.color_formatter import ColorFormatter


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
                        yield Static(
                            "Select a file to view details", id="details", markup=True
                        )
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
        self.build_tree(self.scan_dir, tree.root)
        tree.root.expand()
        self.set_focus(tree)

    def build_tree(self, path: Path, node):
        try:
            for item in sorted(path.iterdir()):
                try:
                    if item.is_dir():
                        if item.name.startswith(".") or item.name == "lost+found":
                            continue
                        subnode = node.add(item.name, data=item)
                        self.build_tree(item, subnode)
                    elif item.is_file() and item.suffix.lower() in {
                        f".{ext}" for ext in MEDIA_TYPES
                    }:
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
                threading.Thread(
                    target=self._extract_and_show_details, args=(node.data,)
                ).start()

    def _extract_and_show_details(self, file_path: Path):
        time.sleep(1)  # Minimum delay to show loading
        try:
            # Initialize extractors and formatters
            extractor = MediaExtractor(file_path)
            formatter = MediaFormatter()
            name_formatter = ProposedNameFormatter(extractor)

            # Update UI
            self.call_later(
                self._update_details,
                formatter.format_file_info_panel(extractor),
                name_formatter.format_display_string(),
            )
        except Exception as e:
            self.call_later(
                self._update_details,
                ColorFormatter.red(f"Error extracting details: {str(e)}"),
                "",
            )

    def _update_details(self, full_info: str, display_string: str):
        self._stop_loading_animation()
        details = self.query_one("#details", Static)
        details.update(full_info)

        proposed = self.query_one("#proposed", Static)
        proposed.update(display_string)

    async def action_quit(self):
        self.exit()

    async def action_open(self):
        self.push_screen(OpenScreen())

    async def action_scan(self):
        if self.scan_dir:
            self.scan_files()

    def on_key(self, event):
        if event.key == "right":
            tree = self.query_one("#file_tree", Tree)
            node = tree.cursor_node
            if (
                node
                and node.data
                and isinstance(node.data, Path)
                and node.data.is_dir()
            ):
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
