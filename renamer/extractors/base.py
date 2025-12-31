"""Base classes and protocols for extractors.

This module defines the DataExtractor Protocol that all extractors should implement.
The protocol ensures a consistent interface across all extractor types.
"""

from pathlib import Path
from typing import Protocol, Optional


class DataExtractor(Protocol):
    """Protocol defining the standard interface for all extractors.

    All extractor classes should implement this protocol to ensure consistent
    behavior across the application. The protocol defines methods for extracting
    various metadata from media files.

    Attributes:
        file_path: Path to the file being analyzed

    Example:
        class MyExtractor:
            def __init__(self, file_path: Path):
                self.file_path = file_path

            def extract_title(self) -> Optional[str]:
                # Implementation here
                return "Movie Title"
    """

    file_path: Path

    def extract_title(self) -> Optional[str]:
        """Extract the title of the media file.

        Returns:
            The extracted title or None if not available
        """
        ...

    def extract_year(self) -> Optional[str]:
        """Extract the release year.

        Returns:
            The year as a string (e.g., "2024") or None if not available
        """
        ...

    def extract_source(self) -> Optional[str]:
        """Extract the source/release type (e.g., BluRay, WEB-DL, HDTV).

        Returns:
            The source type or None if not available
        """
        ...

    def extract_order(self) -> Optional[str]:
        """Extract ordering information (e.g., episode number, disc number).

        Returns:
            The order information or None if not available
        """
        ...

    def extract_resolution(self) -> Optional[str]:
        """Extract the video resolution (e.g., 1080p, 2160p, 720p).

        Returns:
            The resolution or None if not available
        """
        ...

    def extract_hdr(self) -> Optional[str]:
        """Extract HDR information (e.g., HDR10, Dolby Vision).

        Returns:
            The HDR format or None if not available
        """
        ...

    def extract_movie_db(self) -> Optional[str]:
        """Extract movie database IDs (e.g., TMDB, IMDB).

        Returns:
            Database identifiers or None if not available
        """
        ...

    def extract_special_info(self) -> Optional[str]:
        """Extract special information (e.g., REPACK, PROPER, Director's Cut).

        Returns:
            Special release information or None if not available
        """
        ...

    def extract_audio_langs(self) -> Optional[str]:
        """Extract audio language codes.

        Returns:
            Comma-separated language codes or None if not available
        """
        ...

    def extract_meta_type(self) -> Optional[str]:
        """Extract metadata type/format information.

        Returns:
            The metadata type or None if not available
        """
        ...

    def extract_size(self) -> Optional[int]:
        """Extract the file size in bytes.

        Returns:
            File size in bytes or None if not available
        """
        ...

    def extract_modification_time(self) -> Optional[float]:
        """Extract the file modification timestamp.

        Returns:
            Unix timestamp of last modification or None if not available
        """
        ...

    def extract_file_name(self) -> Optional[str]:
        """Extract the file name without path.

        Returns:
            The file name or None if not available
        """
        ...

    def extract_file_path(self) -> Optional[str]:
        """Extract the full file path as string.

        Returns:
            The full file path or None if not available
        """
        ...

    def extract_frame_class(self) -> Optional[str]:
        """Extract the frame class/aspect ratio classification.

        Returns:
            Frame class (e.g., "Widescreen", "Ultra-Widescreen") or None
        """
        ...

    def extract_video_tracks(self) -> list[dict]:
        """Extract video track information.

        Returns:
            List of dictionaries containing video track metadata.
            Returns empty list if no tracks available.
        """
        ...

    def extract_audio_tracks(self) -> list[dict]:
        """Extract audio track information.

        Returns:
            List of dictionaries containing audio track metadata.
            Returns empty list if no tracks available.
        """
        ...

    def extract_subtitle_tracks(self) -> list[dict]:
        """Extract subtitle track information.

        Returns:
            List of dictionaries containing subtitle track metadata.
            Returns empty list if no tracks available.
        """
        ...

    def extract_anamorphic(self) -> Optional[str]:
        """Extract anamorphic encoding information.

        Returns:
            Anamorphic status or None if not available
        """
        ...

    def extract_extension(self) -> Optional[str]:
        """Extract the file extension.

        Returns:
            File extension (without dot) or None if not available
        """
        ...

    def extract_tmdb_url(self) -> Optional[str]:
        """Extract TMDB URL if available.

        Returns:
            Full TMDB URL or None if not available
        """
        ...

    def extract_tmdb_id(self) -> Optional[str]:
        """Extract TMDB ID if available.

        Returns:
            TMDB ID as string or None if not available
        """
        ...

    def extract_original_title(self) -> Optional[str]:
        """Extract the original title (non-localized).

        Returns:
            The original title or None if not available
        """
        ...
