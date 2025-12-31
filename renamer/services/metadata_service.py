"""Metadata service for coordinating metadata extraction and caching.

This service manages the extraction of metadata from media files with:
- Thread pool for concurrent extraction
- Cache integration for performance
- Formatter coordination for display
- Error handling and recovery
"""

import logging
from pathlib import Path
from typing import Optional, Callable
from concurrent.futures import ThreadPoolExecutor, Future
from threading import Lock

from renamer.cache import Cache
from renamer.settings import Settings
from renamer.extractors.extractor import MediaExtractor
from renamer.formatters.media_formatter import MediaFormatter
from renamer.formatters.catalog_formatter import CatalogFormatter
from renamer.formatters.proposed_name_formatter import ProposedNameFormatter
from renamer.formatters.text_formatter import TextFormatter


logger = logging.getLogger(__name__)


class MetadataService:
    """Service for managing metadata extraction and formatting.

    This service coordinates:
    - Metadata extraction from media files
    - Caching of extracted metadata
    - Thread pool management for concurrent operations
    - Formatting for different display modes (technical/catalog)
    - Proposed name generation

    The service uses a thread pool to extract metadata concurrently while
    maintaining thread safety with proper locking mechanisms.

    Example:
        cache = Cache()
        settings = Settings()
        service = MetadataService(cache, settings, max_workers=3)

        # Extract metadata
        result = service.extract_metadata(Path("/media/movie.mkv"))
        if result:
            print(result['formatted_info'])

        # Cleanup when done
        service.shutdown()
    """

    def __init__(
        self,
        cache: Cache,
        settings: Settings,
        max_workers: int = 3
    ):
        """Initialize the metadata service.

        Args:
            cache: Cache instance for storing extracted metadata
            settings: Settings instance for user preferences
            max_workers: Maximum number of concurrent extraction threads
        """
        self.cache = cache
        self.settings = settings
        self.max_workers = max_workers

        # Thread pool for concurrent extraction
        self.executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="metadata_"
        )

        # Lock for thread-safe operations
        self._lock = Lock()

        # Track active futures for cancellation
        self._active_futures: dict[Path, Future] = {}

        logger.info(f"MetadataService initialized with {max_workers} workers")

    def extract_metadata(
        self,
        file_path: Path,
        callback: Optional[Callable] = None,
        error_callback: Optional[Callable] = None
    ) -> Optional[dict]:
        """Extract metadata from a media file.

        This method can be called synchronously (returns result immediately) or
        asynchronously (uses callbacks when complete).

        Args:
            file_path: Path to the media file
            callback: Optional callback(result_dict) called when extraction completes
            error_callback: Optional callback(error_message) called on error

        Returns:
            Dictionary with 'formatted_info' and 'proposed_name' if synchronous,
            None if using callbacks (async mode)

        Example:
            # Synchronous
            result = service.extract_metadata(path)
            print(result['formatted_info'])

            # Asynchronous
            service.extract_metadata(
                path,
                callback=lambda r: print(r['formatted_info']),
                error_callback=lambda e: print(f"Error: {e}")
            )
        """
        if callback or error_callback:
            # Asynchronous mode - submit to thread pool
            future = self.executor.submit(
                self._extract_metadata_internal,
                file_path
            )

            # Track the future
            with self._lock:
                # Cancel any existing extraction for this file
                if file_path in self._active_futures:
                    self._active_futures[file_path].cancel()
                self._active_futures[file_path] = future

            # Add callback handlers
            def done_callback(f: Future):
                with self._lock:
                    # Remove from active futures
                    self._active_futures.pop(file_path, None)

                try:
                    result = f.result()
                    if callback:
                        callback(result)
                except Exception as e:
                    logger.error(f"Error extracting metadata for {file_path}: {e}")
                    if error_callback:
                        error_callback(str(e))

            future.add_done_callback(done_callback)
            return None
        else:
            # Synchronous mode - extract directly
            return self._extract_metadata_internal(file_path)

    def _extract_metadata_internal(self, file_path: Path) -> dict:
        """Internal method to extract and format metadata.

        Args:
            file_path: Path to the media file

        Returns:
            Dictionary with 'formatted_info' and 'proposed_name'

        Raises:
            Exception: If extraction fails
        """
        try:
            # Initialize extractor (uses cache internally via decorators)
            extractor = MediaExtractor(file_path)

            # Get current mode from settings
            mode = self.settings.get("mode")

            # Format based on mode
            if mode == "technical":
                formatter = MediaFormatter(extractor)
                formatted_info = formatter.file_info_panel()
            else:  # catalog
                formatter = CatalogFormatter(extractor)
                formatted_info = formatter.format_catalog_info()

            # Generate proposed name
            proposed_formatter = ProposedNameFormatter(extractor)
            proposed_name = proposed_formatter.rename_line_formatted(file_path)

            return {
                'formatted_info': formatted_info,
                'proposed_name': proposed_name,
                'mode': mode,
            }

        except Exception as e:
            logger.error(f"Failed to extract metadata for {file_path}: {e}")
            return {
                'formatted_info': TextFormatter.red(f"Error extracting details: {str(e)}"),
                'proposed_name': "",
                'mode': self.settings.get("mode"),
            }

    def extract_for_display(
        self,
        file_path: Path,
        display_callback: Callable[[str, str], None],
        error_callback: Optional[Callable[[str], None]] = None
    ):
        """Extract metadata and update display via callback.

        Convenience method that extracts metadata and calls the display callback
        with the formatted info and proposed name.

        Args:
            file_path: Path to the media file
            display_callback: Callback(formatted_info, proposed_name) to update UI
            error_callback: Optional callback(error_message) for errors

        Example:
            def update_ui(info, proposed):
                details_widget.update(info)
                proposed_widget.update(proposed)

            service.extract_for_display(path, update_ui)
        """
        def on_success(result: dict):
            display_callback(result['formatted_info'], result['proposed_name'])

        def on_error(error_message: str):
            if error_callback:
                error_callback(error_message)
            else:
                display_callback(
                    TextFormatter.red(f"Error: {error_message}"),
                    ""
                )

        self.extract_metadata(file_path, callback=on_success, error_callback=on_error)

    def cancel_extraction(self, file_path: Path) -> bool:
        """Cancel an ongoing extraction for a file.

        Args:
            file_path: Path to the file whose extraction should be canceled

        Returns:
            True if an extraction was canceled, False if none was active

        Example:
            # User selected a different file
            service.cancel_extraction(old_path)
            service.extract_metadata(new_path, callback=update_ui)
        """
        with self._lock:
            future = self._active_futures.get(file_path)
            if future and not future.done():
                future.cancel()
                self._active_futures.pop(file_path, None)
                logger.debug(f"Canceled extraction for {file_path}")
                return True
        return False

    def cancel_all_extractions(self):
        """Cancel all ongoing extractions.

        Useful when closing the application or switching directories.

        Example:
            # User closing app
            service.cancel_all_extractions()
            service.shutdown()
        """
        with self._lock:
            canceled_count = 0
            for file_path, future in list(self._active_futures.items()):
                if not future.done():
                    future.cancel()
                    canceled_count += 1
            self._active_futures.clear()

        if canceled_count > 0:
            logger.info(f"Canceled {canceled_count} active extractions")

    def get_active_extraction_count(self) -> int:
        """Get the number of currently active extractions.

        Returns:
            Number of extractions in progress

        Example:
            >>> count = service.get_active_extraction_count()
            >>> print(f"{count} extractions in progress")
        """
        with self._lock:
            return sum(1 for f in self._active_futures.values() if not f.done())

    def shutdown(self, wait: bool = True):
        """Shutdown the metadata service.

        Cancels all pending extractions and shuts down the thread pool.
        Should be called when the application is closing.

        Args:
            wait: If True, wait for all threads to complete. If False, cancel immediately.

        Example:
            # Clean shutdown
            service.shutdown(wait=True)

            # Force shutdown
            service.shutdown(wait=False)
        """
        logger.info("Shutting down MetadataService")

        # Cancel all active extractions
        self.cancel_all_extractions()

        # Shutdown thread pool
        self.executor.shutdown(wait=wait)

        logger.info("MetadataService shutdown complete")

    def __enter__(self):
        """Context manager support."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup."""
        self.shutdown(wait=True)
        return False
