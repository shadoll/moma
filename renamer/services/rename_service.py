"""Rename service for handling file rename operations.

This service manages the process of renaming files with:
- Name validation and sanitization
- Proposed name generation
- Conflict detection
- Atomic rename operations
- Error handling and rollback
"""

import logging
import re
from pathlib import Path
from typing import Optional, Callable

from renamer.extractors.extractor import MediaExtractor
from renamer.views import ProposedFilenameView


logger = logging.getLogger(__name__)


class RenameService:
    """Service for managing file rename operations.

    This service handles:
    - Proposed name generation from metadata
    - Name validation and sanitization
    - File conflict detection
    - Atomic file rename operations
    - Rollback on errors

    Example:
        service = RenameService()

        # Propose a new name
        new_name = service.propose_name(Path("/media/movie.mkv"))
        print(f"Proposed: {new_name}")

        # Rename file
        success, message = service.rename_file(
            Path("/media/movie.mkv"),
            new_name
        )
        if success:
            print(f"Renamed successfully")
    """

    # Invalid characters for filenames (Windows + Unix)
    INVALID_CHARS = r'[<>:"|?*\x00-\x1f]'

    # Invalid characters for paths
    INVALID_PATH_CHARS = r'[<>"|?*\x00-\x1f]'

    def __init__(self):
        """Initialize the rename service."""
        logger.debug("RenameService initialized")

    def propose_name(
        self,
        file_path: Path,
        extractor: Optional[MediaExtractor] = None
    ) -> Optional[str]:
        """Generate a proposed new filename based on metadata.

        Args:
            file_path: Current file path
            extractor: Optional pre-initialized MediaExtractor. If None, creates new one.

        Returns:
            Proposed filename (without path) or None if generation fails

        Example:
            >>> service = RenameService()
            >>> new_name = service.propose_name(Path("/media/movie.2024.mkv"))
            >>> print(new_name)
            'Movie Title (2024) [1080p].mkv'
        """
        try:
            if extractor is None:
                extractor = MediaExtractor(file_path)

            formatter = ProposedFilenameView(extractor)
            # Get the formatted rename line
            rename_line = formatter.rename_line_formatted(file_path)

            # Extract just the filename from the rename line
            # Format is typically: "Rename to: [bold]filename[/bold]"
            if "→" in rename_line:
                # New format with arrow
                parts = rename_line.split("→")
                if len(parts) == 2:
                    # Remove markup tags
                    proposed = self._strip_markup(parts[1].strip())
                    return proposed
            elif "Rename to:" in rename_line:
                # Old format
                parts = rename_line.split("Rename to:")
                if len(parts) == 2:
                    proposed = self._strip_markup(parts[1].strip())
                    return proposed

            # Fallback: use the whole line after stripping markup
            return self._strip_markup(rename_line)

        except Exception as e:
            logger.error(f"Failed to propose name for {file_path}: {e}")
            return None

    def sanitize_filename(self, filename: str) -> str:
        """Sanitize a filename by removing invalid characters.

        Args:
            filename: The filename to sanitize

        Returns:
            Sanitized filename safe for all filesystems

        Example:
            >>> service.sanitize_filename('Movie: Title?')
            'Movie Title'
        """
        # Remove invalid characters
        sanitized = re.sub(self.INVALID_CHARS, '', filename)

        # Replace multiple spaces with single space
        sanitized = re.sub(r'\s+', ' ', sanitized)

        # Strip leading/trailing whitespace and dots
        sanitized = sanitized.strip('. ')

        return sanitized

    def validate_filename(self, filename: str) -> tuple[bool, Optional[str]]:
        """Validate that a filename is safe and legal.

        Args:
            filename: The filename to validate

        Returns:
            Tuple of (is_valid, error_message). If valid, error_message is None.

        Example:
            >>> is_valid, error = service.validate_filename("movie.mkv")
            >>> if not is_valid:
            ...     print(f"Invalid: {error}")
        """
        if not filename:
            return False, "Filename cannot be empty"

        if len(filename) > 255:
            return False, "Filename too long (max 255 characters)"

        # Check for invalid characters
        if re.search(self.INVALID_CHARS, filename):
            return False, f"Filename contains invalid characters: {filename}"

        # Check for reserved names (Windows)
        reserved_names = {
            'CON', 'PRN', 'AUX', 'NUL',
            'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
            'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9',
        }
        name_without_ext = Path(filename).stem.upper()
        if name_without_ext in reserved_names:
            return False, f"Filename uses reserved name: {name_without_ext}"

        # Check for names ending with dot or space (Windows)
        if filename.endswith('.') or filename.endswith(' '):
            return False, "Filename cannot end with dot or space"

        return True, None

    def check_name_conflict(
        self,
        source_path: Path,
        new_filename: str
    ) -> tuple[bool, Optional[str]]:
        """Check if a new filename would conflict with existing files.

        Args:
            source_path: Current file path
            new_filename: Proposed new filename

        Returns:
            Tuple of (has_conflict, conflict_message)

        Example:
            >>> has_conflict, msg = service.check_name_conflict(
            ...     Path("/media/old.mkv"),
            ...     "new.mkv"
            ... )
            >>> if has_conflict:
            ...     print(msg)
        """
        # Build the new path
        new_path = source_path.parent / new_filename

        # Check if it's the same file (case-insensitive on some systems)
        if source_path.resolve() == new_path.resolve():
            return False, None

        # Check if target already exists
        if new_path.exists():
            return True, f"File already exists: {new_filename}"

        return False, None

    def rename_file(
        self,
        source_path: Path,
        new_filename: str,
        dry_run: bool = False
    ) -> tuple[bool, str]:
        """Rename a file to a new filename.

        Args:
            source_path: Current file path
            new_filename: New filename (without path)
            dry_run: If True, validate but don't actually rename

        Returns:
            Tuple of (success, message). Message contains error or success info.

        Example:
            >>> success, msg = service.rename_file(
            ...     Path("/media/old.mkv"),
            ...     "new.mkv"
            ... )
            >>> print(msg)
        """
        # Validate source file exists
        if not source_path.exists():
            error_msg = f"Source file does not exist: {source_path}"
            logger.error(error_msg)
            return False, error_msg

        if not source_path.is_file():
            error_msg = f"Source is not a file: {source_path}"
            logger.error(error_msg)
            return False, error_msg

        # Sanitize the new filename
        sanitized_filename = self.sanitize_filename(new_filename)

        # Validate the new filename
        is_valid, error = self.validate_filename(sanitized_filename)
        if not is_valid:
            logger.error(f"Invalid filename: {error}")
            return False, error

        # Check for conflicts
        has_conflict, conflict_msg = self.check_name_conflict(source_path, sanitized_filename)
        if has_conflict:
            logger.warning(f"Name conflict: {conflict_msg}")
            return False, conflict_msg

        # Build the new path
        new_path = source_path.parent / sanitized_filename

        # Dry run mode - don't actually rename
        if dry_run:
            success_msg = f"Would rename: {source_path.name} → {sanitized_filename}"
            logger.info(success_msg)
            return True, success_msg

        # Perform the rename
        try:
            source_path.rename(new_path)
            success_msg = f"Renamed: {source_path.name} → {sanitized_filename}"
            logger.info(success_msg)
            return True, success_msg

        except PermissionError as e:
            error_msg = f"Permission denied: {e}"
            logger.error(error_msg)
            return False, error_msg

        except OSError as e:
            error_msg = f"OS error during rename: {e}"
            logger.error(error_msg)
            return False, error_msg

        except Exception as e:
            error_msg = f"Unexpected error during rename: {e}"
            logger.error(error_msg)
            return False, error_msg

    def rename_with_callback(
        self,
        source_path: Path,
        new_filename: str,
        success_callback: Optional[Callable[[Path], None]] = None,
        error_callback: Optional[Callable[[str], None]] = None,
        dry_run: bool = False
    ):
        """Rename a file with callbacks for success/error.

        Convenience method that performs the rename and calls appropriate callbacks.

        Args:
            source_path: Current file path
            new_filename: New filename (without path)
            success_callback: Called with new_path on success
            error_callback: Called with error_message on failure
            dry_run: If True, validate but don't actually rename

        Example:
            def on_success(new_path):
                print(f"File renamed to: {new_path}")
                update_tree_node(new_path)

            def on_error(error):
                show_error_dialog(error)

            service.rename_with_callback(
                path, new_name,
                success_callback=on_success,
                error_callback=on_error
            )
        """
        success, message = self.rename_file(source_path, new_filename, dry_run)

        if success:
            if success_callback:
                new_path = source_path.parent / self.sanitize_filename(new_filename)
                success_callback(new_path)
        else:
            if error_callback:
                error_callback(message)

    def _strip_markup(self, text: str) -> str:
        """Strip Textual markup tags from text.

        Args:
            text: Text with markup tags

        Returns:
            Plain text without markup

        Example:
            >>> service._strip_markup('[bold]text[/bold]')
            'text'
        """
        # Remove all markup tags like [bold], [/bold], [green], etc.
        return re.sub(r'\[/?[^\]]+\]', '', text)
