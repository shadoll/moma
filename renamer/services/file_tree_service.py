"""File tree service for managing directory scanning and tree building.

This service encapsulates all file system operations related to building
and managing the file tree display.
"""

import logging
from pathlib import Path
from typing import Optional, Callable
from rich.markup import escape

from renamer.constants import MEDIA_TYPES


logger = logging.getLogger(__name__)


class FileTreeService:
    """Service for managing file tree operations.

    This service handles:
    - Directory scanning and validation
    - File tree construction with filtering
    - File type filtering based on media types
    - Permission error handling

    Example:
        service = FileTreeService()
        files = service.scan_directory(Path("/media/movies"))
        service.build_tree(Path("/media/movies"), tree_node)
    """

    def __init__(self, media_types: Optional[set[str]] = None):
        """Initialize the file tree service.

        Args:
            media_types: Set of file extensions to include (without dot).
                        If None, uses MEDIA_TYPES from constants.
        """
        self.media_types = media_types or MEDIA_TYPES
        logger.debug(f"FileTreeService initialized with {len(self.media_types)} media types")

    def validate_directory(self, path: Path) -> tuple[bool, Optional[str]]:
        """Validate that a path is a valid directory.

        Args:
            path: The path to validate

        Returns:
            Tuple of (is_valid, error_message). If valid, error_message is None.

        Example:
            >>> service = FileTreeService()
            >>> is_valid, error = service.validate_directory(Path("/tmp"))
            >>> if is_valid:
            ...     print("Directory is valid")
        """
        if not path:
            return False, "No directory specified"

        if not path.exists():
            return False, f"Directory does not exist: {path}"

        if not path.is_dir():
            return False, f"Path is not a directory: {path}"

        try:
            # Test if we can read the directory
            list(path.iterdir())
            return True, None
        except PermissionError:
            return False, f"Permission denied: {path}"
        except Exception as e:
            return False, f"Error accessing directory: {e}"

    def scan_directory(self, path: Path, recursive: bool = True) -> list[Path]:
        """Scan a directory and return all media files.

        Args:
            path: The directory to scan
            recursive: If True, scan subdirectories recursively

        Returns:
            List of Path objects for all media files found

        Example:
            >>> service = FileTreeService()
            >>> files = service.scan_directory(Path("/media/movies"))
            >>> print(f"Found {len(files)} media files")
        """
        is_valid, error = self.validate_directory(path)
        if not is_valid:
            logger.warning(f"Cannot scan directory: {error}")
            return []

        media_files = []
        try:
            for item in sorted(path.iterdir()):
                try:
                    if item.is_dir():
                        # Skip hidden directories and system directories
                        if item.name.startswith(".") or item.name == "lost+found":
                            continue

                        if recursive:
                            # Recursively scan subdirectories
                            media_files.extend(self.scan_directory(item, recursive=True))
                    elif item.is_file():
                        # Check if file has a media extension
                        if self._is_media_file(item):
                            media_files.append(item)
                            logger.debug(f"Found media file: {item}")
                except PermissionError:
                    logger.debug(f"Permission denied: {item}")
                    continue
        except PermissionError:
            logger.warning(f"Permission denied scanning directory: {path}")

        return media_files

    def build_tree(
        self,
        path: Path,
        node,
        add_node_callback: Optional[Callable] = None
    ):
        """Build a tree structure from a directory.

        This method recursively builds a tree by adding directories and media files
        to the provided node. Uses a callback to add nodes to maintain compatibility
        with different tree implementations.

        Args:
            path: The directory path to build tree from
            node: The tree node to add children to
            add_node_callback: Optional callback(node, label, data) to add a child node.
                             If None, uses node.add(label, data=data)

        Example:
            >>> from textual.widgets import Tree
            >>> tree = Tree("Files")
            >>> service = FileTreeService()
            >>> service.build_tree(Path("/media"), tree.root)
        """
        if add_node_callback is None:
            # Default implementation for Textual Tree
            add_node_callback = lambda parent, label, data: parent.add(label, data=data)

        try:
            for item in sorted(path.iterdir()):
                try:
                    if item.is_dir():
                        # Skip hidden and system directories
                        if item.name.startswith(".") or item.name == "lost+found":
                            continue

                        # Add directory node
                        subnode = add_node_callback(node, escape(item.name), item)
                        # Recursively build tree for subdirectory
                        self.build_tree(item, subnode, add_node_callback)

                    elif item.is_file() and self._is_media_file(item):
                        # Add media file node
                        logger.debug(f"Adding file to tree: {item.name!r} (full path: {item})")
                        add_node_callback(node, escape(item.name), item)

                except PermissionError:
                    logger.debug(f"Permission denied: {item}")
                    continue
        except PermissionError:
            logger.warning(f"Permission denied building tree: {path}")

    def find_node_by_path(self, root_node, target_path: Path):
        """Find a tree node by file path.

        Recursively searches the tree for a node with matching data path.

        Args:
            root_node: The root node to start searching from
            target_path: The Path to search for

        Returns:
            The matching node or None if not found

        Example:
            >>> node = service.find_node_by_path(tree.root, Path("/media/movie.mkv"))
            >>> if node:
            ...     node.label = "New Name.mkv"
        """
        # Check if this node matches
        if hasattr(root_node, 'data') and root_node.data == target_path:
            return root_node

        # Recursively search children
        if hasattr(root_node, 'children'):
            for child in root_node.children:
                result = self.find_node_by_path(child, target_path)
                if result:
                    return result

        return None

    def count_media_files(self, path: Path) -> int:
        """Count the number of media files in a directory.

        Args:
            path: The directory to count files in

        Returns:
            Number of media files found (including subdirectories)

        Example:
            >>> count = service.count_media_files(Path("/media/movies"))
            >>> print(f"Found {count} media files")
        """
        return len(self.scan_directory(path, recursive=True))

    def _is_media_file(self, path: Path) -> bool:
        """Check if a file is a media file based on extension.

        Args:
            path: The file path to check

        Returns:
            True if the file has a media extension

        Example:
            >>> service._is_media_file(Path("movie.mkv"))
            True
            >>> service._is_media_file(Path("readme.txt"))
            False
        """
        extension = path.suffix.lower()
        # Remove the leading dot and check against media types
        return extension.lstrip('.') in {ext.lower() for ext in self.media_types}

    def get_directory_stats(self, path: Path) -> dict[str, int]:
        """Get statistics about a directory.

        Args:
            path: The directory to analyze

        Returns:
            Dictionary with stats: total_files, total_dirs, media_files

        Example:
            >>> stats = service.get_directory_stats(Path("/media"))
            >>> print(f"Media files: {stats['media_files']}")
        """
        stats = {
            'total_files': 0,
            'total_dirs': 0,
            'media_files': 0,
        }

        is_valid, _ = self.validate_directory(path)
        if not is_valid:
            return stats

        try:
            for item in path.iterdir():
                try:
                    if item.is_dir():
                        if not item.name.startswith(".") and item.name != "lost+found":
                            stats['total_dirs'] += 1
                            # Recursively count subdirectories
                            sub_stats = self.get_directory_stats(item)
                            stats['total_files'] += sub_stats['total_files']
                            stats['total_dirs'] += sub_stats['total_dirs']
                            stats['media_files'] += sub_stats['media_files']
                    elif item.is_file():
                        stats['total_files'] += 1
                        if self._is_media_file(item):
                            stats['media_files'] += 1
                except PermissionError:
                    continue
        except PermissionError:
            pass

        return stats
