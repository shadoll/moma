"""Default extractor providing fallback values.

This module provides a minimal implementation of the DataExtractor protocol
that returns default/empty values for all extraction methods. Used as a
fallback when no specific extractor is available.
"""

from typing import Optional


class DefaultExtractor:
    """Extractor that provides default fallback values for all extraction methods.

    This class implements the DataExtractor protocol by returning sensible
    defaults (None, empty strings, empty lists) for all extraction operations.
    It's used as a final fallback in the extractor chain when no other
    extractor can provide data.

    All methods return None or empty values, making it safe to use when
    no actual data extraction is possible.
    """

    def extract_title(self) -> Optional[str]:
        """Return default title.

        Returns:
            Default title string "Unknown Title"
        """
        return "Unknown Title"

    def extract_year(self) -> Optional[str]:
        """Return year. Returns None as no year information is available."""
        return None

    def extract_source(self) -> Optional[str]:
        """Return video source. Returns None as no source information is available."""
        return None

    def extract_order(self) -> Optional[str]:
        """Return sequence order. Returns None as no order information is available."""
        return None

    def extract_resolution(self) -> Optional[str]:
        """Return resolution. Returns None as no resolution information is available."""
        return None

    def extract_hdr(self) -> Optional[str]:
        """Return HDR information. Returns None as no HDR information is available."""
        return None

    def extract_movie_db(self) -> list[str] | None:
        """Return movie database ID. Returns None as no database information is available."""
        return None

    def extract_special_info(self) -> Optional[str]:
        """Return special edition info. Returns None as no special info is available."""
        return None

    def extract_audio_langs(self) -> Optional[str]:
        """Return audio languages. Returns None as no language information is available."""
        return None

    def extract_meta_type(self) -> Optional[str]:
        """Return metadata type. Returns None as no type information is available."""
        return None

    def extract_size(self) -> Optional[int]:
        """Return file size. Returns None as no size information is available."""
        return None

    def extract_modification_time(self) -> Optional[float]:
        """Return modification time. Returns None as no timestamp is available."""
        return None

    def extract_file_name(self) -> Optional[str]:
        """Return file name. Returns None as no filename is available."""
        return None

    def extract_file_path(self) -> Optional[str]:
        """Return file path. Returns None as no file path is available."""
        return None

    def extract_frame_class(self) -> Optional[str]:
        """Return frame class. Returns None as no frame class information is available."""
        return None

    def extract_video_tracks(self) -> list[dict]:
        """Return video tracks. Returns empty list as no video tracks are available."""
        return []

    def extract_audio_tracks(self) -> list[dict]:
        """Return audio tracks. Returns empty list as no audio tracks are available."""
        return []

    def extract_subtitle_tracks(self) -> list[dict]:
        """Return subtitle tracks. Returns empty list as no subtitle tracks are available."""
        return []

    def extract_anamorphic(self) -> Optional[str]:
        """Return anamorphic info. Returns None as no anamorphic information is available."""
        return None

    def extract_extension(self) -> Optional[str]:
        """Return file extension. Returns 'ext' as default placeholder."""
        return "ext"

    def extract_tmdb_url(self) -> Optional[str]:
        """Return TMDB URL. Returns None as no TMDB URL is available."""
        return None

    def extract_tmdb_id(self) -> Optional[str]:
        """Return TMDB ID. Returns None as no TMDB ID is available."""
        return None

    def extract_original_title(self) -> Optional[str]:
        """Return original title. Returns None as no original title is available."""
        return None