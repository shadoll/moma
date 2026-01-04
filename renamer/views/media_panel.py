from .media_panel_properties import MediaPanelProperties
from ..formatters.conditional_decorators import conditional_decorators


class MediaPanelView:
    """View for assembling media data panels for display.

    This view aggregates multiple formatters to create comprehensive
    display panels for technical and catalog modes.
    """

    def __init__(self, extractor):
        self.extractor = extractor
        self._props = MediaPanelProperties(extractor)

    def file_info_panel(self) -> str:
        """Return formatted file info panel string"""
        return "\n".join(
            [
                self.selected_section(),
                self.fileinfo_section(),
                self.tmdb_section(),
                self.tracksinfo_section(),
                self.filename_section(),
                self.metadata_section(),
                self.mediainfo_section(),
            ]
        )

    @conditional_decorators.wrap("", "\n")
    def selected_section(self) -> str:
        """Return formatted selected data"""
        return "\n".join(
            [
                self._props.media_title,
                self._props.media_year,
                self._props.tmdb_genres,
                self._props.media_duration,
                self._props.media_file_size,
                self._props.media_file_extension,
                self._props.selected_frame_class,
                self._props.selected_source,
                self._props.selected_audio_langs,
                self._props.tmdb_database_info,
                self._props.selected_order,
            ]
        )

    @conditional_decorators.wrap("", "\n")
    def fileinfo_section(self) -> str:
        """Return formatted file info"""
        return "\n".join(
            [
                self._props.file_info_title,
                self._props.file_path,
                self._props.file_size,
                self._props.file_name,
                self._props.modification_time,
                self._props.extension_fileinfo,
            ]
        )

    @conditional_decorators.wrap("", "\n")
    def tmdb_section(self) -> str:
        """Return formatted TMDB data"""
        return "\n".join(
            [
                self._props.tmdb_id,
                self._props.tmdb_title,
                self._props.tmdb_original_title,
                self._props.tmdb_year,
                self._props.tmdb_countries,
                self._props.tmdb_genres,
                self._props.tmdb_database_info,
                self._props.tmdb_url,
            ]
        )

    @conditional_decorators.wrap("", "\n")
    def tracksinfo_section(self) -> str:
        """Return formatted tracks information panel"""
        return "\n".join(
            [
                self._props.title("Tracks Info"),
                *self._props.video_tracks,
                *self._props.audio_tracks,
                *self._props.subtitle_tracks,
            ]
        )

    @conditional_decorators.wrap("", "\n")
    def filename_section(self) -> str:
        """Return formatted filename extracted data"""
        return "\n".join(
            [
                self._props.title("Filename Extracted Data"),
                self._props.filename_order,
                self._props.filename_title,
                self._props.filename_year,
                self._props.filename_source,
                self._props.filename_frame_class,
                self._props.filename_hdr,
                self._props.filename_audio_langs,
                self._props.filename_special_info,
                self._props.filename_movie_db,
            ]
        )

    @conditional_decorators.wrap("", "\n")
    def metadata_section(self) -> str:
        """Return formatted metadata extraction data"""
        return "\n".join(
            [
                self._props.title("Metadata Extraction"),
                self._props.metadata_title,
                self._props.metadata_duration,
                self._props.metadata_artist,
            ]
        )

    @conditional_decorators.wrap("", "\n")
    def mediainfo_section(self) -> str:
        """Return formatted media info extraction data"""
        return "\n".join(
            [
                self._props.title("Media Info Extraction"),
                self._props.mediainfo_duration,
                self._props.mediainfo_frame_class,
                self._props.mediainfo_resolution,
                self._props.mediainfo_aspect_ratio,
                self._props.mediainfo_hdr,
                self._props.mediainfo_audio_langs,
                self._props.mediainfo_anamorphic,
                self._props.mediainfo_extension,
                self._props.mediainfo_3d_layout,
            ]
        )
