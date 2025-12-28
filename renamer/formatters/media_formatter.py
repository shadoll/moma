from pathlib import Path
from rich.markup import escape
from .size_formatter import SizeFormatter
from .date_formatter import DateFormatter
from .extension_formatter import ExtensionFormatter
from .text_formatter import TextFormatter
from .track_formatter import TrackFormatter
from .resolution_formatter import ResolutionFormatter
from .duration_formatter import DurationFormatter
from .special_info_formatter import SpecialInfoFormatter
from .formatter import FormatterApplier


class MediaFormatter:
    """Class to format media data for display"""

    def __init__(self, extractor):
        self.extractor = extractor

    def file_info_panel(self) -> str:
        """Return formatted file info panel string"""
        sections = [
            self.file_info(),
            self.selected_data(),
            self.tmdb_data(),
            self.tracks_info(),
            self.filename_extracted_data(),
            self.metadata_extracted_data(),
            self.mediainfo_extracted_data(),
        ]
        return "\n\n".join("\n".join(section) for section in sections)

    def file_info(self) -> list[str]:
        data = [
            {
                "group": "File Info",
                "label": "File Info",
                "label_formatters": [TextFormatter.bold, TextFormatter.uppercase],
            },
            {
                "group": "File Info",
                "label": "Path",
                "label_formatters": [TextFormatter.bold],
                "value": escape(str(self.extractor.get("file_path", "FileInfo"))),
                "display_formatters": [TextFormatter.blue],
            },
            {
                "group": "File Info",
                "label": "Size",
                "value": self.extractor.get("file_size", "FileInfo"),
                "value_formatters": [SizeFormatter.format_size_full],
                "display_formatters": [TextFormatter.bold, TextFormatter.green],
            },
            {
                "group": "File Info",
                "label": "Name",
                "label_formatters": [TextFormatter.bold],
                "value": escape(str(self.extractor.get("file_name", "FileInfo"))),
                "display_formatters": [TextFormatter.cyan],
            },
            {
                "group": "File Info",
                "label": "Modified",
                "label_formatters": [TextFormatter.bold],
                "value": self.extractor.get("modification_time", "FileInfo"),
                "value_formatters": [DateFormatter.format_modification_date],
                "display_formatters": [TextFormatter.bold, TextFormatter.magenta],
            },
            {
                "group": "File Info",
                "label": "Extension",
                "label_formatters": [TextFormatter.bold],
                "value": self.extractor.get("extension", "FileInfo"),
                "value_formatters": [ExtensionFormatter.format_extension_info],
                "display_formatters": [TextFormatter.green],
            },
        ]
        return FormatterApplier.format_data_items(data)

    def tmdb_data(self) -> list[str]:
        """Return formatted TMDB data"""
        data = [
            {
                "label": "TMDB Data",
                "label_formatters": [TextFormatter.bold, TextFormatter.uppercase],
            },
            {
                "label": "ID",
                "label_formatters": [TextFormatter.bold, TextFormatter.blue],
                "value": self.extractor.get("tmdb_id", "TMDB") or "<None>",
                "value_formatters": [TextFormatter.yellow],
            },
            {
                "label": "Title",
                "label_formatters": [TextFormatter.bold, TextFormatter.blue],
                "value": self.extractor.get("title", "TMDB") or "<None>",
                "value_formatters": [TextFormatter.yellow],
            },
            {
                "label": "Original Title",
                "label_formatters": [TextFormatter.bold, TextFormatter.blue],
                "value": self.extractor.get("original_title", "TMDB") or "<None>",
                "value_formatters": [TextFormatter.yellow],
            },
            {
                "label": "Year",
                "label_formatters": [TextFormatter.bold, TextFormatter.blue],
                "value": self.extractor.get("year", "TMDB") or "<None>",
                "value_formatters": [TextFormatter.yellow,],
            },
            {
                "label": "Database Info",
                "label_formatters": [TextFormatter.bold, TextFormatter.blue],
                "value": self.extractor.get("movie_db", "TMDB") or "<None>",
                "value_formatters": [SpecialInfoFormatter.format_database_info, TextFormatter.yellow],
            },
            {
                "label": "URL",
                "label_formatters": [TextFormatter.bold, TextFormatter.blue],
                "value": self.extractor.get("tmdb_url", "TMDB") or "<None>",
                "value_formatters": [TextFormatter.format_url],
            }
        ]
        return FormatterApplier.format_data_items(data)

    def tracks_info(self) -> list[str]:
        """Return formatted tracks information"""
        data = [
            {
                "group": "Tracks Info",
                "label": "Tracks Info",
                "label_formatters": [TextFormatter.bold, TextFormatter.uppercase],
            }
        ]

        # Get video tracks
        video_tracks = self.extractor.get("video_tracks", "MediaInfo") or []
        for item in video_tracks:
            data.append(
                {
                    "group": "Tracks Info",
                    "label": "Video Track",
                    "value": item,
                    "value_formatters": TrackFormatter.format_video_track,
                    "display_formatters": [TextFormatter.green],
                }
            )

        # Get audio tracks
        audio_tracks = self.extractor.get("audio_tracks", "MediaInfo") or []
        for i, item in enumerate(audio_tracks, start=1):
            data.append(
                {
                    "group": "Tracks Info",
                    "label": f"Audio Track {i}",
                    "value": item,
                    "value_formatters": TrackFormatter.format_audio_track,
                    "display_formatters": [TextFormatter.yellow],
                }
            )

        # Get subtitle tracks
        subtitle_tracks = self.extractor.get("subtitle_tracks", "MediaInfo") or []
        for i, item in enumerate(subtitle_tracks, start=1):
            data.append(
                {
                    "group": "Tracks Info",
                    "label": f"Subtitle Track {i}",
                    "value": item,
                    "value_formatters": TrackFormatter.format_subtitle_track,
                    "display_formatters": [TextFormatter.magenta],
                }
            )

        return FormatterApplier.format_data_items(data)

    def metadata_extracted_data(self) -> list[str]:
        """Format metadata extraction data for the metadata panel"""
        data = [
            {
                "label": "Metadata Extraction",
                "label_formatters": [TextFormatter.bold, TextFormatter.uppercase],
            },
            {
                "label": "Title",
                "label_formatters": [TextFormatter.bold],
                "value": self.extractor.get("title", "Metadata") or "Not extracted",
                "display_formatters": [TextFormatter.grey],
            },
            {
                "label": "Duration",
                "label_formatters": [TextFormatter.bold],
                "value": self.extractor.get("duration", "Metadata") or "Not extracted",
                "value_formatters": [DurationFormatter.format_full],
                "display_formatters": [TextFormatter.grey],
            },
            {
                "label": "Artist",
                "label_formatters": [TextFormatter.bold],
                "value": self.extractor.get("artist", "Metadata") or "Not extracted",
                "display_formatters": [TextFormatter.grey],
            },
        ]

        return FormatterApplier.format_data_items(data)

    def mediainfo_extracted_data(self) -> list[str]:
        """Format media info extraction data for the mediainfo panel"""
        data = [
            {
                "label": "Media Info Extraction",
                "label_formatters": [TextFormatter.bold, TextFormatter.uppercase],
            },
            {
                "label": "Duration",
                "label_formatters": [TextFormatter.bold],
                "value": self.extractor.get("duration", "MediaInfo") or "Not extracted",
                "value_formatters": [DurationFormatter.format_full],
                "display_formatters": [TextFormatter.grey],
            },
            {
                "label": "Frame Class",
                "label_formatters": [TextFormatter.bold],
                "value": self.extractor.get("frame_class", "MediaInfo")
                or "Not extracted",
                "display_formatters": [TextFormatter.grey],
            },
            {
                "label": "Resolution",
                "label_formatters": [TextFormatter.bold],
                "value": self.extractor.get("resolution", "MediaInfo")
                or "Not extracted",
                "value_formatters": [ResolutionFormatter.format_resolution_dimensions],
                "display_formatters": [TextFormatter.grey],
            },
            {
                "label": "Aspect Ratio",
                "label_formatters": [TextFormatter.bold],
                "value": self.extractor.get("aspect_ratio", "MediaInfo")
                or "Not extracted",
                "display_formatters": [TextFormatter.grey],
            },
            {
                "label": "HDR",
                "label_formatters": [TextFormatter.bold],
                "value": self.extractor.get("hdr", "MediaInfo") or "Not extracted",
                "display_formatters": [TextFormatter.grey],
            },
            {
                "label": "Audio Languages",
                "label_formatters": [TextFormatter.bold],
                "value": self.extractor.get("audio_langs", "MediaInfo")
                or "Not extracted",
                "display_formatters": [TextFormatter.grey],
            },
        ]
        return FormatterApplier.format_data_items(data)

    def filename_extracted_data(self) -> list[str]:
        """Return formatted filename extracted data"""
        data = [
            {
                "label": "Filename Extracted Data",
                "label_formatters": [TextFormatter.bold, TextFormatter.uppercase],
            },
            {
                "label": "Order",
                "label_formatters": [TextFormatter.bold],
                "value": self.extractor.get("order", "Filename") or "Not extracted",
                "display_formatters": [TextFormatter.yellow],
            },
            {
                "label": "Movie title",
                "label_formatters": [TextFormatter.bold],
                "value": self.extractor.get("title", "Filename"),
                "display_formatters": [TextFormatter.grey],
            },
            {
                "label": "Year",
                "label_formatters": [TextFormatter.bold],
                "value": self.extractor.get("year", "Filename"),
                "display_formatters": [TextFormatter.grey],
            },
            {
                "label": "Video source",
                "label_formatters": [TextFormatter.bold],
                "value": self.extractor.get("source", "Filename") or "Not extracted",
                "display_formatters": [TextFormatter.grey],
            },
            {
                "label": "Frame class",
                "label_formatters": [TextFormatter.bold],
                "value": self.extractor.get("frame_class", "Filename")
                or "Not extracted",
                "display_formatters": [TextFormatter.grey],
            },
            {
                "label": "HDR",
                "label_formatters": [TextFormatter.bold],
                "value": self.extractor.get("hdr", "Filename") or "Not extracted",
                "display_formatters": [TextFormatter.grey],
            },
            {
                "label": "Audio langs",
                "label_formatters": [TextFormatter.bold],
                "value": self.extractor.get("audio_langs", "Filename")
                or "Not extracted",
                "display_formatters": [TextFormatter.grey],
            },
            {
                "label": "Special info",
                "label_formatters": [TextFormatter.bold],
                "value": self.extractor.get("special_info", "Filename")
                or "Not extracted",
                "value_formatters": [
                    SpecialInfoFormatter.format_special_info,
                    TextFormatter.blue,
                ],
                "display_formatters": [TextFormatter.grey],
            },
            {
                "label": "Movie DB",
                "label_formatters": [TextFormatter.bold],
                "value": self.extractor.get("movie_db", "Filename") or "Not extracted",
                "display_formatters": [TextFormatter.grey],
            },
        ]

        return FormatterApplier.format_data_items(data)

    def selected_data(self) -> list[str]:
        """Return formatted selected data string"""
        import logging
        import os
        if os.getenv("FORMATTER_LOG"):
            frame_class = self.extractor.get("frame_class")
            audio_langs = self.extractor.get("audio_langs")
            logging.info(f"Selected data - frame_class: {frame_class!r}, audio_langs: {audio_langs!r}")
            # Also check from Filename source
            frame_class_filename = self.extractor.get("frame_class", "Filename")
            audio_langs_filename = self.extractor.get("audio_langs", "Filename")
            logging.info(f"From Filename - frame_class: {frame_class_filename!r}, audio_langs: {audio_langs_filename!r}")
        data = [
            {
                "label": "Selected Data",
                "label_formatters": [TextFormatter.bold, TextFormatter.uppercase],
            },
            {
                "label": "Order",
                "label_formatters": [TextFormatter.bold, TextFormatter.blue],
                "value": self.extractor.get("order") or "<None>",
                "value_formatters": [TextFormatter.yellow],
            },
            {
                "label": "Title",
                "label_formatters": [TextFormatter.bold, TextFormatter.blue],
                "value": self.extractor.get("title") or "<None>",
                "value_formatters": [TextFormatter.yellow],
            },
            {
                "label": "Year",
                "label_formatters": [TextFormatter.bold, TextFormatter.blue],
                "value": self.extractor.get("year") or "<None>",
                "value_formatters": [TextFormatter.yellow],
            },
            {
                "label": "Special info",
                "label_formatters": [TextFormatter.bold, TextFormatter.blue],
                "value": self.extractor.get("special_info") or "<None>",
                "value_formatters": [
                    SpecialInfoFormatter.format_special_info,
                    TextFormatter.yellow,
                ],
            },
            {
                "label": "Source",
                "label_formatters": [TextFormatter.bold, TextFormatter.blue],
                "value": self.extractor.get("source") or "<None>",
                "value_formatters": [TextFormatter.yellow],
            },
            {
                "label": "Frame class",
                "label_formatters": [TextFormatter.bold, TextFormatter.blue],
                "value": self.extractor.get("frame_class") or "<None>",
                "value_formatters": [TextFormatter.yellow],
            },
            {
                "label": "HDR",
                "label_formatters": [TextFormatter.bold, TextFormatter.blue],
                "value": self.extractor.get("hdr") or "<None>",
                "value_formatters": [TextFormatter.yellow],
            },
            {
                "label": "Audio langs",
                "label_formatters": [TextFormatter.bold, TextFormatter.blue],
                "value": self.extractor.get("audio_langs") or "<None>",
                "value_formatters": [TextFormatter.yellow],
            },
            {
                "label": "Database Info",
                "label_formatters": [TextFormatter.bold, TextFormatter.blue],
                "value": self.extractor.get("movie_db") or "<None>",
                "value_formatters": [SpecialInfoFormatter.format_database_info, TextFormatter.yellow],
            }
        ]
        return FormatterApplier.format_data_items(data)
