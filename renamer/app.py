from textual.app import App, ComposeResult
from textual.widgets import Tree, Static, Footer, LoadingIndicator
from textual.containers import Horizontal, Container, ScrollableContainer, Vertical
from textual.widget import Widget
from textual.command import Provider, Hit
from rich.markup import escape
from pathlib import Path
from functools import partial
import threading
import time
import logging
import os

from .constants import MEDIA_TYPES
from .screens import OpenScreen, HelpScreen, RenameConfirmScreen, SettingsScreen, ConvertConfirmScreen
from .extractors.extractor import MediaExtractor
from .views import MediaPanelView, ProposedFilenameView
from .formatters.text_formatter import TextFormatter
from .formatters.catalog_formatter import CatalogFormatter
from .settings import Settings
from .cache import Cache, CacheManager
from .services.conversion_service import ConversionService


# Set up logging conditionally
if os.getenv('FORMATTER_LOG', '0') == '1':
    logging.basicConfig(filename='formatter.log', level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
else:
    logging.basicConfig(level=logging.INFO)  # Enable logging for debugging


class CacheCommandProvider(Provider):
    """Command provider for cache management operations."""

    async def search(self, query: str):
        """Search for cache commands matching the query."""
        matcher = self.matcher(query)

        commands = [
            ("cache_stats", "Cache: View Statistics", "View cache statistics (size, entries, etc.)"),
            ("cache_clear_all", "Cache: Clear All", "Clear all cache entries"),
            ("cache_clear_extractors", "Cache: Clear Extractors", "Clear extractor cache only"),
            ("cache_clear_tmdb", "Cache: Clear TMDB", "Clear TMDB API cache only"),
            ("cache_clear_posters", "Cache: Clear Posters", "Clear poster image cache only"),
            ("cache_clear_expired", "Cache: Clear Expired", "Remove expired cache entries"),
            ("cache_compact", "Cache: Compact", "Remove empty cache directories"),
        ]

        for command_name, display_name, help_text in commands:
            if (score := matcher.match(display_name)) > 0:
                yield Hit(
                    score,
                    matcher.highlight(display_name),
                    partial(self.app.action_cache_command, command_name),
                    help=help_text
                )


class AppCommandProvider(Provider):
    """Command provider for main application operations."""

    async def search(self, query: str):
        """Search for app commands matching the query."""
        matcher = self.matcher(query)

        commands = [
            ("open", "Open Directory", "Open a directory to browse media files (o)"),
            ("scan", "Scan Directory", "Scan current directory for media files (s)"),
            ("refresh", "Refresh File", "Refresh metadata for selected file (f)"),
            ("rename", "Rename File", "Rename the selected file (r)"),
            ("convert", "Convert to MKV", "Convert AVI/MPG/MPEG file to MKV container with metadata (c)"),
            ("delete", "Delete File", "Delete the selected file (d)"),
            ("toggle_mode", "Toggle Display Mode", "Switch between technical and catalog view (m)"),
            ("expand", "Toggle Tree Expansion", "Expand or collapse all tree nodes (p)"),
            ("settings", "Settings", "Open settings screen (Ctrl+S)"),
            ("help", "Help", "Show keyboard shortcuts and help (h)"),
        ]

        for command_name, display_name, help_text in commands:
            if (score := matcher.match(display_name)) > 0:
                yield Hit(
                    score,
                    matcher.highlight(display_name),
                    partial(self.app.run_action, command_name),
                    help=help_text
                )


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
        ("c", "convert", "Convert to MKV"),
        ("d", "delete", "Delete"),
        ("p", "expand", "Toggle Tree"),
        ("m", "toggle_mode", "Toggle Mode"),
        ("h", "help", "Help"),
        ("ctrl+s", "settings", "Settings"),
    ]

    # Command palette - extend built-in commands with cache and app commands
    COMMANDS = App.COMMANDS | {CacheCommandProvider, AppCommandProvider}

    def __init__(self, scan_dir):
        super().__init__()
        self.scan_dir = Path(scan_dir) if scan_dir else None
        self.tree_expanded = False
        self.settings = Settings()
        # Initialize cache system
        self.cache = Cache()
        self.cache_manager = CacheManager(self.cache)

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

    def _get_file_icon(self, file_path: Path) -> str:
        """Get icon for file based on extension.

        Args:
            file_path: Path to the file

        Returns:
            Icon character for the file type
        """
        ext = file_path.suffix.lower().lstrip('.')

        # File type icons
        icons = {
            'mkv': '📹',   # Video camera for MKV
            'mk3d': '🎬',  # Clapper board for 3D
            'avi': '💿',   # Film frames for AVI
            'mp4': '📹',   # Video camera
            'mov': '📹',   # Video camera
            'wmv': '📀',   # Video camera
            'webm': '📹',  # Video camera
            'm4v': '📹',   # Video camera
            'mpg': '📼',   # Video camera
            'mpeg': '📼',  # Video camera
        }

        return icons.get(ext, '📄')  # Default to document icon

    def build_tree(self, path: Path, node):
        try:
            for item in sorted(path.iterdir()):
                try:
                    if item.is_dir():
                        if item.name.startswith(".") or item.name == "lost+found":
                            continue
                        # Add folder icon before directory name
                        label = f"📁 {escape(item.name)}"
                        subnode = node.add(label, data=item)
                        self.build_tree(item, subnode)
                    elif item.is_file() and item.suffix.lower() in {
                        f".{ext}" for ext in MEDIA_TYPES
                    }:
                        logging.info(f"Adding file to tree: {item.name!r} (full path: {item})")
                        # Add file type icon before filename
                        icon = self._get_file_icon(item)
                        label = f"{icon} {escape(item.name)}"
                        node.add(label, data=item)
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
                formatter = MediaPanelView(extractor)
                full_info = formatter.file_info_panel()
            else:  # catalog
                formatter = CatalogFormatter(extractor, self.settings)
                full_info = formatter.format_catalog_info()
            
            # Update UI
            self.call_later(
                self._update_details,
                full_info,
                ProposedFilenameView(extractor).rename_line_formatted(file_path),
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

    async def action_cache_command(self, command: str):
        """Execute a cache management command.

        Args:
            command: The cache command to execute (e.g., 'cache_stats', 'cache_clear_all')
        """
        try:
            if command == "cache_stats":
                stats = self.cache_manager.get_stats()
                stats_text = f"""Cache Statistics:

Total Files: {stats['total_files']}
Total Size: {stats['total_size_mb']:.2f} MB
Memory Entries: {stats['memory_cache_entries']}

By Category:"""
                for subdir, info in stats['subdirs'].items():
                    stats_text += f"\n  {subdir}: {info['file_count']} files, {info['size_mb']:.2f} MB"

                self.notify(stats_text, severity="information", timeout=10)

            elif command == "cache_clear_all":
                count = self.cache_manager.clear_all()
                self.notify(f"Cleared all cache: {count} entries removed", severity="information", timeout=3)

            elif command == "cache_clear_extractors":
                count = self.cache_manager.clear_by_prefix("extractor_")
                self.notify(f"Cleared extractor cache: {count} entries removed", severity="information", timeout=3)

            elif command == "cache_clear_tmdb":
                count = self.cache_manager.clear_by_prefix("tmdb_")
                self.notify(f"Cleared TMDB cache: {count} entries removed", severity="information", timeout=3)

            elif command == "cache_clear_posters":
                count = self.cache_manager.clear_by_prefix("poster_")
                self.notify(f"Cleared poster cache: {count} entries removed", severity="information", timeout=3)

            elif command == "cache_clear_expired":
                count = self.cache_manager.clear_expired()
                self.notify(f"Cleared {count} expired entries", severity="information", timeout=3)

            elif command == "cache_compact":
                self.cache_manager.compact_cache()
                self.notify("Cache compacted successfully", severity="information", timeout=3)

        except Exception as e:
            self.notify(f"Error executing cache command: {str(e)}", severity="error", timeout=5)

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
            proposed_formatter = ProposedFilenameView(extractor)
            new_name = str(proposed_formatter)
            logging.info(f"Proposed new name: {new_name!r} for file: {node.data}")
            if new_name and new_name != node.data.name:
                self.push_screen(RenameConfirmScreen(node.data, new_name))
            else:
                self.notify("Proposed name is the same as current name; no rename needed.", severity="information", timeout=3)

    async def action_convert(self):
        """Convert AVI/MPG/MPEG file to MKV with metadata preservation."""
        tree = self.query_one("#file_tree", Tree)
        node = tree.cursor_node

        if not (node and node.data and isinstance(node.data, Path) and node.data.is_file()):
            self.notify("Please select a file first", severity="warning", timeout=3)
            return

        file_path = node.data
        conversion_service = ConversionService()

        # Check if file can be converted
        if not conversion_service.can_convert(file_path):
            self.notify("Only AVI, MPG, and MPEG files can be converted to MKV", severity="error", timeout=3)
            return

        # Create extractor for metadata
        try:
            extractor = MediaExtractor(file_path)
        except Exception as e:
            self.notify(f"Failed to read file metadata: {e}", severity="error", timeout=5)
            return

        # Get audio track count and map languages
        audio_tracks = extractor.get('audio_tracks', 'MediaInfo') or []
        if not audio_tracks:
            self.notify("No audio tracks found in file", severity="error", timeout=3)
            return

        audio_languages = conversion_service.map_audio_languages(extractor, len(audio_tracks))
        subtitle_files = conversion_service.find_subtitle_files(file_path)
        mkv_path = file_path.with_suffix('.mkv')

        # Show confirmation screen (conversion happens in screen's on_button_pressed)
        self.push_screen(
            ConvertConfirmScreen(file_path, mkv_path, audio_languages, subtitle_files, extractor)
        )

    async def action_delete(self):
        """Delete a file with confirmation."""
        from .screens import DeleteConfirmScreen

        tree = self.query_one("#file_tree", Tree)
        node = tree.cursor_node

        if not (node and node.data and isinstance(node.data, Path) and node.data.is_file()):
            self.notify("Please select a file first", severity="warning", timeout=3)
            return

        file_path = node.data

        # Show confirmation screen
        self.push_screen(DeleteConfirmScreen(file_path))

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
            # Update label with icon
            icon = self._get_file_icon(new_path)
            node.label = f"{icon} {escape(new_path.name)}"
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

    def add_file_to_tree(self, file_path: Path):
        """Add a new file to the tree in the correct position.

        Args:
            file_path: Path to the new file to add
        """
        logging.info(f"add_file_to_tree called with file_path={file_path}")

        tree = self.query_one("#file_tree", Tree)
        parent_dir = file_path.parent
        logging.info(f"Looking for parent directory node: {parent_dir}")
        logging.info(f"Scan directory: {self.scan_dir}")

        # Check if parent directory is the scan directory (root level)
        # If so, the parent node is the tree root itself
        parent_node = None

        if self.scan_dir and parent_dir.resolve() == self.scan_dir.resolve():
            logging.info("File is in root scan directory, using tree.root as parent")
            parent_node = tree.root
        else:
            # Find the parent directory node in the tree
            def find_node(node, depth=0):
                if node.data and isinstance(node.data, Path):
                    logging.info(f"{'  ' * depth}Checking node: data={node.data}")
                    # Resolve both paths to absolute for comparison
                    if node.data.resolve() == parent_dir.resolve():
                        logging.info(f"{'  ' * depth}Found match! node.data={node.data}")
                        return node
                for child in node.children:
                    found = find_node(child, depth + 1)
                    if found:
                        return found
                return None

            parent_node = find_node(tree.root)

        if parent_node:
            logging.info(f"Found parent node for {parent_dir}, adding file {file_path.name}")

            # Get icon for the file
            icon = self._get_file_icon(file_path)
            label = f"{icon} {escape(file_path.name)}"

            # Add the new file node in alphabetically sorted position
            new_node = None
            inserted = False

            for i, child in enumerate(parent_node.children):
                if child.data and isinstance(child.data, Path):
                    # Compare filenames for sorting
                    if child.data.name > file_path.name:
                        # Insert before this child
                        new_node = parent_node.add(label, data=file_path, before=i)
                        inserted = True
                        logging.info(f"Inserted file before {child.data.name}")
                        break

            # If not inserted, add at the end
            if not inserted:
                new_node = parent_node.add(label, data=file_path)
                logging.info(f"Added file at end of directory")

            # Select the new node and show its details
            if new_node:
                tree.select_node(new_node)
                logging.info(f"Selected new node: {new_node.data}")

                # Refresh the details panel for the new file
                self._start_loading_animation()
                threading.Thread(
                    target=self._extract_and_show_details, args=(file_path,)
                ).start()
        else:
            logging.warning(f"No parent node found for {parent_dir}")
            logging.warning(f"Rescanning entire tree instead")
            # If we can't find the parent node, rescan the tree and try to select the new file
            tree = self.query_one("#file_tree", Tree)
            current_selection = tree.cursor_node.data if tree.cursor_node else None

            self.scan_files()

            # Try to restore selection to the new file, or the old selection, or parent dir
            def find_and_select(node, target_path):
                if node.data and isinstance(node.data, Path):
                    if node.data.resolve() == target_path.resolve():
                        tree.select_node(node)
                        return True
                for child in node.children:
                    if find_and_select(child, target_path):
                        return True
                return False

            # Try to select the new file first
            if not find_and_select(tree.root, file_path):
                # If that fails, try to restore previous selection
                if current_selection:
                    find_and_select(tree.root, current_selection)

            # Refresh details panel for selected node
            if tree.cursor_node and tree.cursor_node.data:
                self._start_loading_animation()
                threading.Thread(
                    target=self._extract_and_show_details, args=(tree.cursor_node.data,)
                ).start()

    def remove_file_from_tree(self, file_path: Path):
        """Remove a file from the tree.

        Args:
            file_path: Path to the file to remove
        """
        logging.info(f"remove_file_from_tree called with file_path={file_path}")

        tree = self.query_one("#file_tree", Tree)

        # Find the node to remove
        def find_node(node):
            if node.data and isinstance(node.data, Path):
                if node.data.resolve() == file_path.resolve():
                    return node
            for child in node.children:
                found = find_node(child)
                if found:
                    return found
            return None

        node_to_remove = find_node(tree.root)

        if node_to_remove:
            logging.info(f"Found node to remove: {node_to_remove.data}")

            # Find the parent node to select after deletion
            parent_node = node_to_remove.parent
            next_node = None

            # Try to select next sibling, or previous sibling, or parent
            if parent_node:
                siblings = list(parent_node.children)
                try:
                    current_index = siblings.index(node_to_remove)
                    # Try next sibling first
                    if current_index + 1 < len(siblings):
                        next_node = siblings[current_index + 1]
                    # Try previous sibling
                    elif current_index > 0:
                        next_node = siblings[current_index - 1]
                    # Fall back to parent
                    else:
                        next_node = parent_node if parent_node != tree.root else None
                except ValueError:
                    pass

            # Remove the node
            node_to_remove.remove()
            logging.info(f"Removed node from tree")

            # Select the next appropriate node
            if next_node:
                tree.select_node(next_node)
                logging.info(f"Selected next node: {next_node.data}")

                # Refresh details if it's a file
                if next_node.data and isinstance(next_node.data, Path) and next_node.data.is_file():
                    self._start_loading_animation()
                    threading.Thread(
                        target=self._extract_and_show_details, args=(next_node.data,)
                    ).start()
                else:
                    # Clear details panel
                    details = self.query_one("#details_technical", Static)
                    details.update("Select a file to view details")
                    proposed = self.query_one("#proposed", Static)
                    proposed.update("")
            else:
                # No node to select, clear details
                details = self.query_one("#details_technical", Static)
                details.update("No files in directory")
                proposed = self.query_one("#proposed", Static)
                proposed.update("")
        else:
            logging.warning(f"Node not found for {file_path}")

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
