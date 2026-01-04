"""Media panel property methods using decorator pattern.

This module contains all the formatted property methods that return
display-ready values for the media panel view. Each property uses
decorators to apply formatting, similar to ProposedFilenameView.
"""

from ..formatters import (
    date_decorators,
    text_decorators,
    conditional_decorators,
    size_decorators,
    extension_decorators,
    duration_decorators,
    resolution_decorators,
    special_info_decorators,
    track_decorators,
)


class MediaPanelProperties:
    """Formatted properties for media panel display.

    This class provides @property methods that return formatted values
    ready for display in the media panel. Each property applies the
    appropriate decorators for styling and formatting.
    """

    def __init__(self, extractor):
        self._extractor = extractor

    # ============================================================
    # Section Title Formatter
    # ============================================================

    @text_decorators.bold()
    @text_decorators.uppercase()
    def title(self, title: str) -> str:
        """Format section title with bold and uppercase styling."""
        return title

    # ============================================================
    # File Info Properties
    # ============================================================

    @property
    @conditional_decorators.wrap(left="󰷊 ", right="")
    @text_decorators.uppercase()
    @text_decorators.bold()
    def file_info_title(self) -> str:
        """Get file info title formatted with label."""
        return "File Info"

    @property
    @conditional_decorators.wrap("├ 󰙅 : ")
    @text_decorators.colour(name="blue")
    @text_decorators.escape()
    def file_path(self) -> str:
        """Get file path formatted with label."""
        return self._extractor.get("file_path")

    @property
    @conditional_decorators.wrap(left="├  : ")
    @text_decorators.colour(name="bisque")
    @size_decorators.size_full()
    def file_size(self) -> str:
        """Get file size formatted with label."""
        return self._extractor.get("file_size")

    @property
    @conditional_decorators.wrap(left="├ 󰈙 : ")
    @text_decorators.colour(name="bisque")
    @text_decorators.escape()
    def file_name(self) -> str:
        """Get file name formatted with label."""
        return self._extractor.get("file_name")

    @property
    @conditional_decorators.wrap(left="├ 󱋡 : ")
    @text_decorators.colour("bisque")
    @date_decorators.modification_date()
    def modification_time(self) -> str:
        """Get modification time formatted with label."""
        return self._extractor.get("modification_time")

    @property
    @conditional_decorators.wrap(left="└  : ")
    @text_decorators.colour(name="bisque")
    @extension_decorators.extension_info()
    def extension_fileinfo(self) -> str:
        """Get extension from FileInfo formatted with label."""
        return self._extractor.get("extension")

    # ============================================================
    # TMDB Properties
    # ============================================================

    @property
    @conditional_decorators.wrap("󰈚 TMDB : ")
    @text_decorators.colour(name="yellow")
    @conditional_decorators.default("<None>")
    def tmdb_id(self) -> str:
        """Get TMDB ID formatted with label."""
        return self._extractor.get("tmdb_id", "TMDB")

    @property
    @text_decorators.colour(name="blue")
    @conditional_decorators.wrap(left="├ 󰗴 : ")
    @text_decorators.colour(name="yellow")
    @conditional_decorators.default("<None>")
    def tmdb_title(self) -> str:
        """Get TMDB title formatted with label."""
        return self._extractor.get("title", "TMDB")

    @property
    @text_decorators.colour(name="blue")
    @conditional_decorators.wrap(left="├ 󰗴 : ")
    @text_decorators.colour(name="bisque")
    @conditional_decorators.default("<None>")
    def tmdb_original_title(self) -> str:
        """Get TMDB original title formatted with label."""
        return self._extractor.get("original_title", "TMDB")

    @property
    @text_decorators.colour(name="blue")
    @conditional_decorators.wrap(left="├  : ")
    @text_decorators.colour(name="bisque")
    @conditional_decorators.default("<None>")
    def tmdb_year(self) -> str:
        """Get TMDB year formatted with label."""
        return self._extractor.get("year", "TMDB")

    @property
    @text_decorators.colour(name="blue")
    @conditional_decorators.wrap(left="├  : ")
    @text_decorators.colour(name="bisque")
    @conditional_decorators.default("<None>")
    def tmdb_countries(self) -> str:
        """Get TMDB production countries formatted with label."""
        return self._extractor.get("production_countries", "TMDB")

    @property
    @text_decorators.colour(name="blue")
    @conditional_decorators.wrap(left="├ 󰴂 : ")
    @text_decorators.colour(name="cyan")
    @conditional_decorators.default("<None>")
    def tmdb_genres(self) -> str:
        """Get TMDB genres formatted with label."""
        return self._extractor.get("genres", "TMDB")

    @property
    @text_decorators.colour(name="blue")
    @conditional_decorators.wrap(left="├ 󰻾 : ")
    @text_decorators.colour(name="bisque")
    @conditional_decorators.default("<None>")
    @special_info_decorators.database_info()
    def tmdb_database_info(self) -> str:
        """Get TMDB database info formatted with label."""
        return self._extractor.get("movie_db", "TMDB")

    @property
    # @text_decorators.colour(name="blue")
    @conditional_decorators.wrap(left="└ ")
    @conditional_decorators.default(default_value="")
    @text_decorators.url()
    def tmdb_url(self) -> str:
        """Get TMDB URL formatted with label."""
        return self._extractor.get("tmdb_url", "TMDB")

    # ============================================================
    # Metadata Extraction Properties
    # ============================================================

    @property
    @conditional_decorators.wrap("Title: ")
    @text_decorators.colour(name="grey")
    @conditional_decorators.default("Not extracted")
    def metadata_title(self) -> str:
        """Get metadata title formatted with label."""
        return self._extractor.get("title", "Metadata")

    @property
    @conditional_decorators.wrap("Duration: ")
    @text_decorators.colour(name="grey")
    @conditional_decorators.default("Not extracted")
    @duration_decorators.duration_full()
    def metadata_duration(self) -> str:
        """Get metadata duration formatted with label."""
        return self._extractor.get("duration", "Metadata")

    @property
    @conditional_decorators.wrap("Artist: ")
    @text_decorators.colour(name="grey")
    @conditional_decorators.default("Not extracted")
    def metadata_artist(self) -> str:
        """Get metadata artist formatted with label."""
        return self._extractor.get("artist", "Metadata")

    # ============================================================
    # MediaInfo Extraction Properties
    # ============================================================

    @property
    @conditional_decorators.wrap("Duration: ")
    @text_decorators.colour(name="grey")
    @conditional_decorators.default("Not extracted")
    @duration_decorators.duration_full()
    def mediainfo_duration(self) -> str:
        """Get MediaInfo duration formatted with label."""
        return self._extractor.get("duration", "MediaInfo")

    @property
    @conditional_decorators.wrap("Frame Class: ")
    @text_decorators.colour(name="grey")
    @conditional_decorators.default("Not extracted")
    def mediainfo_frame_class(self) -> str:
        """Get MediaInfo frame class formatted with label."""
        return self._extractor.get("frame_class", "MediaInfo")

    @property
    @conditional_decorators.wrap("Resolution: ")
    @text_decorators.colour(name="grey")
    @conditional_decorators.default("Not extracted")
    @resolution_decorators.resolution_dimensions()
    def mediainfo_resolution(self) -> str:
        """Get MediaInfo resolution formatted with label."""
        return self._extractor.get("resolution", "MediaInfo")

    @property
    @conditional_decorators.wrap("Aspect Ratio: ")
    @text_decorators.colour(name="grey")
    @conditional_decorators.default("Not extracted")
    def mediainfo_aspect_ratio(self) -> str:
        """Get MediaInfo aspect ratio formatted with label."""
        return self._extractor.get("aspect_ratio", "MediaInfo")

    @property
    @conditional_decorators.wrap("HDR: ")
    @text_decorators.colour(name="grey")
    @conditional_decorators.default("Not extracted")
    def mediainfo_hdr(self) -> str:
        """Get MediaInfo HDR formatted with label."""
        return self._extractor.get("hdr", "MediaInfo")

    @property
    @conditional_decorators.wrap("Audio Languages: ")
    @text_decorators.colour(name="grey")
    @conditional_decorators.default("Not extracted")
    def mediainfo_audio_langs(self) -> str:
        """Get MediaInfo audio languages formatted with label."""
        return self._extractor.get("audio_langs", "MediaInfo")

    @property
    @conditional_decorators.wrap("Anamorphic: ")
    @text_decorators.colour(name="grey")
    @conditional_decorators.default("Not extracted")
    def mediainfo_anamorphic(self) -> str:
        """Get MediaInfo anamorphic formatted with label."""
        return self._extractor.get("anamorphic", "MediaInfo")

    @property
    @conditional_decorators.wrap("Extension: ")
    @text_decorators.colour(name="grey")
    @conditional_decorators.default("Not extracted")
    @extension_decorators.extension_info()
    def mediainfo_extension(self) -> str:
        """Get MediaInfo extension formatted with label."""
        return self._extractor.get("extension", "MediaInfo")

    @property
    @conditional_decorators.wrap("3D Layout: ")
    @text_decorators.colour(name="grey")
    @conditional_decorators.default("Not extracted")
    def mediainfo_3d_layout(self) -> str:
        """Get MediaInfo 3D layout formatted with label."""
        return self._extractor.get("3d_layout", "MediaInfo")

    # ============================================================
    # Filename Extraction Properties
    # ============================================================

    @property
    @conditional_decorators.wrap("Order: ")
    @text_decorators.colour(name="yellow")
    @conditional_decorators.default("Not extracted")
    def filename_order(self) -> str:
        """Get filename order formatted with label."""
        return self._extractor.get("order", "Filename")

    @property
    @conditional_decorators.wrap("Movie title: ")
    @text_decorators.colour(name="grey")
    @conditional_decorators.default("")
    def filename_title(self) -> str:
        """Get filename title formatted with label."""
        return self._extractor.get("title", "Filename")

    @property
    @conditional_decorators.wrap(left="├  : ")
    @text_decorators.colour(name="bisque")
    @conditional_decorators.default("")
    def filename_year(self) -> str:
        """Get filename year formatted with label."""
        return self._extractor.get("year", "Filename")

    @property
    @conditional_decorators.wrap("Video source: ")
    @text_decorators.colour(name="grey")
    @conditional_decorators.default("Not extracted")
    def filename_source(self) -> str:
        """Get filename source formatted with label."""
        return self._extractor.get("source", "Filename")

    @property
    @conditional_decorators.wrap("Frame class: ")
    @text_decorators.colour(name="grey")
    @conditional_decorators.default("Not extracted")
    def filename_frame_class(self) -> str:
        """Get filename frame class formatted with label."""
        return self._extractor.get("frame_class", "Filename")

    @property
    @conditional_decorators.wrap("HDR: ")
    @text_decorators.colour(name="grey")
    @conditional_decorators.default("Not extracted")
    def filename_hdr(self) -> str:
        """Get filename HDR formatted with label."""
        return self._extractor.get("hdr", "Filename")

    @property
    @conditional_decorators.wrap("Audio langs: ")
    @text_decorators.colour(name="grey")
    @conditional_decorators.default("Not extracted")
    def filename_audio_langs(self) -> str:
        """Get filename audio languages formatted with label."""
        return self._extractor.get("audio_langs", "Filename")

    @property
    @conditional_decorators.wrap("Special info: ")
    @text_decorators.colour(name="grey")
    @conditional_decorators.default("Not extracted")
    @text_decorators.colour(name="blue")
    @special_info_decorators.special_info()
    def filename_special_info(self) -> str:
        """Get filename special info formatted with label."""
        return self._extractor.get("special_info", "Filename")

    @property
    @conditional_decorators.wrap("Movie DB: ")
    @text_decorators.colour(name="grey")
    @conditional_decorators.default("Not extracted")
    def filename_movie_db(self) -> str:
        """Get filename movie DB formatted with label."""
        return self._extractor.get("movie_db", "Filename")

    # ============================================================
    # Media Data Properties
    # ============================================================

    @property
    @text_decorators.colour(name="blue")
    @conditional_decorators.wrap(left="├ 󰔚 : ")
    @text_decorators.colour(name="bisque")
    @duration_decorators.duration_full()
    def media_duration(self) -> str:
        """Get media duration from best available source."""
        return self._extractor.get("duration")

    @property
    @text_decorators.colour(name="blue")
    @conditional_decorators.wrap(left="└ 󰒾 : ")
    @text_decorators.colour(name="bisque")
    @conditional_decorators.default("<None>")
    def selected_order(self) -> str:
        """Get selected order formatted with label."""
        return self._extractor.get("order")

    @property
    @text_decorators.colour(name="blue")
    @conditional_decorators.wrap(left="󰿎 MOVIE : ")
    @text_decorators.colour(name="yellow")
    @conditional_decorators.default("<None>")
    def media_title(self) -> str:
        """Get selected title formatted with label."""
        return self._extractor.get("title")

    @property
    @text_decorators.colour(name="blue")
    @conditional_decorators.wrap(left="├  : ")
    @text_decorators.colour(name="bisque")
    @conditional_decorators.default("<None>")
    def media_year(self) -> str:
        """Get selected year formatted with label."""
        return self._extractor.get("year")

    @property
    @text_decorators.colour(name="blue")
    @conditional_decorators.wrap(left="├  : ")
    @text_decorators.colour(name="green")
    @size_decorators.size_short()
    def media_file_size(self) -> str:
        """Get media file size formatted with label."""
        return self._extractor.get("file_size")

    @property
    @text_decorators.colour(name="blue")
    @conditional_decorators.wrap(left="├  : ")
    @text_decorators.colour(name="bisque")
    @extension_decorators.extension_info()
    def media_file_extension(self) -> str:
        """Get media file extension formatted with label."""
        return self._extractor.get("extension")

    @property
    @text_decorators.colour(name="blue")
    @conditional_decorators.wrap("Special info: ")
    @text_decorators.colour(name="yellow")
    @conditional_decorators.default("<None>")
    @special_info_decorators.special_info()
    def selected_special_info(self) -> str:
        """Get selected special info formatted with label."""
        return self._extractor.get("special_info")

    @property
    @text_decorators.colour(name="blue")
    @conditional_decorators.wrap(left="├  : ")
    @text_decorators.colour(name="bisque")
    @conditional_decorators.default("<None>")
    def selected_source(self) -> str:
        """Get selected source formatted with label."""
        return self._extractor.get("source")

    @property
    @text_decorators.colour(name="blue")
    @conditional_decorators.wrap(left="├ 󱣴 : ")
    @text_decorators.colour(name="bisque")
    @conditional_decorators.default("<None>")
    def selected_frame_class(self) -> str:
        """Get selected frame class formatted with label."""
        return self._extractor.get("frame_class")

    @property
    @text_decorators.colour(name="blue")
    @conditional_decorators.wrap(left="├ 󰵽 : ")
    @text_decorators.colour(name="bisque")
    @conditional_decorators.default("<None>")
    def selected_hdr(self) -> str:
        """Get selected HDR formatted with label."""
        return self._extractor.get("hdr")

    @property
    @text_decorators.colour(name="blue")
    @conditional_decorators.wrap(left="├ 󰗊 : ")
    @text_decorators.colour(name="bisque")
    @conditional_decorators.default("<None>")
    def selected_audio_langs(self) -> str:
        """Get selected audio languages formatted with label."""
        return self._extractor.get("audio_langs")

    @property
    def video_tracks(self) -> list[str]:
        """Return formatted video track data"""
        tracks = self._extractor.get("video_tracks", "MediaInfo") or []
        return [self.video_track(track, i) for i, track in enumerate(tracks, start=1)]

    @text_decorators.colour(name="green")
    @conditional_decorators.wrap("Video Track {index}: ")
    @track_decorators.video_track()
    def video_track(self, track, index) -> str:
        """Get video track info formatted with label."""
        return track

    @property
    def audio_tracks(self) -> list[str]:
        """Return formatted audio track data"""
        tracks = self._extractor.get("audio_tracks", "MediaInfo") or []
        return [self.audio_track(track, i) for i, track in enumerate(tracks, start=1)]

    @text_decorators.colour(name="yellow")
    @conditional_decorators.wrap("Audio Track {index}: ")
    @track_decorators.audio_track()
    def audio_track(self, track, index) -> str:
        """Get audio track info formatted with label."""
        return track

    @property
    def subtitle_tracks(self) -> list[str]:
        """Return formatted subtitle track data"""
        tracks = self._extractor.get("subtitle_tracks", "MediaInfo") or []
        return [
            self.subtitle_track(track, i) for i, track in enumerate(tracks, start=1)
        ]

    @text_decorators.colour(name="magenta")
    @conditional_decorators.wrap("Subtitle Track {index}: ")
    @track_decorators.subtitle_track()
    def subtitle_track(self, track, index) -> str:
        """Get subtitle track info formatted with label."""
        return track
