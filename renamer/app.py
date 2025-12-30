from textual.app import App, ComposeResult
from textual.widgets import Tree, Static, Footer, LoadingIndicator
from textual.containers import Horizontal, Container, ScrollableContainer, Vertical
from textual.widget import Widget
from rich.markup import escape
from pathlib import Path
import threading
import time
import logging
import os

from .constants import MEDIA_TYPES
from .screens import OpenScreen, HelpScreen, RenameConfirmScreen, SettingsScreen
from .extractors.extractor import MediaExtractor
from .formatters.media_formatter import MediaFormatter
from .formatters.proposed_name_formatter import ProposedNameFormatter
from .formatters.text_formatter import TextFormatter
from .formatters.catalog_formatter import CatalogFormatter
from .settings import Settings


# Set up logging conditionally
if os.getenv('FORMATTER_LOG', '0') == '1':
    logging.basicConfig(filename='formatter.log', level=logging.INFO, 
                        format='%(asctime)s - %(levelname)s - %(message)s')
else:
    logging.basicConfig(level=logging.INFO)  # Enable logging for debugging


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
        ("f", "refresh", "Refresh"),
        ("r", "rename", "Rename"),
        ("p", "expand", "Toggle Tree"),
        ("m", "toggle_mode", "Toggle Mode"),
        ("h", "help", "Help"),
        ("ctrl+s", "settings", "Settings"),
    ]

    def __init__(self, scan_dir):
        super().__init__()
        self.scan_dir = Path(scan_dir) if scan_dir else None
        self.tree_expanded = False
        self.settings = Settings()

    def compose(self) -> ComposeResult:
        with Horizontal():
            with Container(id="left"):
                yield Tree("Files", id="file_tree")
            with Container(id="right"):
                with Vertical():
                    yield LoadingIndicator(id="loading")
                    with ScrollableContainer(id="details_container"):
                        yield Static(
                            "Select a file to view details", id="details_technical", markup=True
                        )
                        yield Static(
                            "", id="details_catalog", markup=False
                        )
                    yield Static("", id="proposed", markup=True)
        yield Footer()

    def on_mount(self):
        loading = self.query_one("#loading", LoadingIndicator)
        loading.display = False
        self.scan_files()

    def scan_files(self):
        logging.info("scan_files called")
        if not self.scan_dir or not self.scan_dir.exists() or not self.scan_dir.is_dir():
            details = self.query_one("#details_technical", Static)
            details.update("Error: Directory does not exist or is not a directory")
            return
        tree = self.query_one("#file_tree", Tree)
        tree.clear()
        self.build_tree(self.scan_dir, tree.root)
        tree.root.expand()  # Expand root level
        self.tree_expanded = False  # Sub-levels are collapsed
        self.set_focus(tree)

    def build_tree(self, path: Path, node):
        try:
            for item in sorted(path.iterdir()):
                try:
                    if item.is_dir():
                        if item.name.startswith(".") or item.name == "lost+found":
                            continue
                        subnode = node.add(escape(item.name), data=item)
                        self.build_tree(item, subnode)
                    elif item.is_file() and item.suffix.lower() in {
                        f".{ext}" for ext in MEDIA_TYPES
                    }:
                        logging.info(f"Adding file to tree: {item.name!r} (full path: {item})")
                        node.add(escape(item.name), data=item)
                except PermissionError:
                    pass
        except PermissionError:
            pass

    def _start_loading_animation(self):
        loading = self.query_one("#loading", LoadingIndicator)
        loading.display = True
        mode = self.settings.get("mode")
        if mode == "technical":
            details = self.query_one("#details_technical", Static)
        else:
            details = self.query_one("#details_catalog", Static)
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
                details = self.query_one("#details_technical", Static)
                details.display = True
                details_catalog = self.query_one("#details_catalog", Static)
                details_catalog.display = False
                details.update("Directory")
                proposed = self.query_one("#proposed", Static)
                proposed.update("")
            elif node.data.is_file():
                self._start_loading_animation()
                threading.Thread(
                    target=self._extract_and_show_details, args=(node.data,)
                ).start()

    def _extract_and_show_details(self, file_path: Path):
        try:
            # Initialize extractors and formatters
            extractor = MediaExtractor(file_path)
            
            mode = self.settings.get("mode")
            if mode == "technical":
                formatter = MediaFormatter(extractor)
                full_info = formatter.file_info_panel()
            else:  # catalog
                formatter = CatalogFormatter(extractor)
                full_info = formatter.format_catalog_info()
            
            # Update UI
            self.call_later(
                self._update_details,
                full_info,
                ProposedNameFormatter(extractor).rename_line_formatted(file_path),
            )
        except Exception as e:
            self.call_later(
                self._update_details,
                TextFormatter.red(f"Error extracting details: {str(e)}"),
                "",
            )

    def _update_details(self, full_info: str, display_string: str):
        self._stop_loading_animation()
        details_technical = self.query_one("#details_technical", Static)
        details_catalog = self.query_one("#details_catalog", Static)
        mode = self.settings.get("mode")
        if mode == "technical":
            details_technical.display = True
            details_catalog.display = False
            details_technical.update(full_info)
        else:
            details_technical.display = False
            details_catalog.display = True
            details_catalog.update(full_info)
        
        proposed = self.query_one("#proposed", Static)
        proposed.update(display_string)

    async def action_quit(self):
        self.exit()

    async def action_open(self):
        self.push_screen(OpenScreen())

    async def action_scan(self):
        if self.scan_dir:
            self.scan_files()

    async def action_refresh(self):
        tree = self.query_one("#file_tree", Tree)
        node = tree.cursor_node
        if node and node.data and isinstance(node.data, Path) and node.data.is_file():
            self._start_loading_animation()
            threading.Thread(
                target=self._extract_and_show_details, args=(node.data,)
            ).start()

    async def action_help(self):
        self.push_screen(HelpScreen())

    async def action_settings(self):
        self.push_screen(SettingsScreen())

    async def action_toggle_mode(self):
        current_mode = self.settings.get("mode")
        new_mode = "catalog" if current_mode == "technical" else "technical"
        self.settings.set("mode", new_mode)
        self.notify(f"Switched to {new_mode} mode", severity="information", timeout=2)
        # Refresh current file display if any
        tree = self.query_one("#file_tree", Tree)
        node = tree.cursor_node
        if node and node.data and isinstance(node.data, Path) and node.data.is_file():
            self._start_loading_animation()
            threading.Thread(
                target=self._extract_and_show_details, args=(node.data,)
            ).start()

    async def action_rename(self):
        tree = self.query_one("#file_tree", Tree)
        node = tree.cursor_node
        if node and node.data and isinstance(node.data, Path) and node.data.is_file():
            # Get the proposed name from the extractor
            extractor = MediaExtractor(node.data)
            proposed_formatter = ProposedNameFormatter(extractor)
            new_name = str(proposed_formatter)
            logging.info(f"Proposed new name: {new_name!r} for file: {node.data}")
            if new_name and new_name != node.data.name:
                self.push_screen(RenameConfirmScreen(node.data, new_name))
            else:
                self.notify("Proposed name is the same as current name; no rename needed.", severity="information", timeout=3)

    async def action_expand(self):
        tree = self.query_one("#file_tree", Tree)
        if self.tree_expanded:
            # Collapse all sub-levels, keep root expanded
            def collapse_sub(node):
                if node != tree.root:
                    node.collapse()
                for child in node.children:
                    collapse_sub(child)
            collapse_sub(tree.root)
            self.tree_expanded = False
        else:
            # Expand all
            def expand_all(node):
                node.expand()
                for child in node.children:
                    expand_all(child)
            expand_all(tree.root)
            self.tree_expanded = True

    def update_renamed_file(self, old_path: Path, new_path: Path):
        """Update the tree node for a renamed file."""
        logging.info(f"update_renamed_file called with old_path={old_path}, new_path={new_path}")
        
        tree = self.query_one("#file_tree", Tree)
        logging.info(f"Before update: cursor_node.data = {tree.cursor_node.data if tree.cursor_node else None}")
        
        # Update only the specific node
        def find_node(node):
            if node.data == old_path:
                return node
            for child in node.children:
                found = find_node(child)
                if found:
                    return found
            return None
        
        node = find_node(tree.root)
        if node:
            logging.info(f"Found node for {old_path}, updating to {new_path.name}")
            node.label = escape(new_path.name)
            node.data = new_path
            logging.info(f"After update: node.data = {node.data}, node.label = {node.label}")
            # Ensure cursor stays on the renamed file
            tree.select_node(node)
            logging.info(f"Selected node: {tree.cursor_node.data if tree.cursor_node else None}")
        else:
            logging.info(f"No node found for {old_path}")
        
        logging.info(f"After update: cursor_node.data = {tree.cursor_node.data if tree.cursor_node else None}")
        
        # Refresh the details if the node is currently selected
        if tree.cursor_node and tree.cursor_node.data == new_path:
            logging.info("Refreshing details for renamed file")
            self._start_loading_animation()
            threading.Thread(
                target=self._extract_and_show_details, args=(new_path,)
            ).start()
        else:
            logging.info("Not refreshing details, cursor not on renamed file")

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
