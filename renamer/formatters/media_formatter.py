from pathlib import Path
from .size_formatter import SizeFormatter
from .date_formatter import DateFormatter
from .extension_extractor import ExtensionExtractor
from .extension_formatter import ExtensionFormatter
from .text_formatter import TextFormatter
from .track_formatter import TrackFormatter
from .resolution_formatter import ResolutionFormatter


class MediaFormatter:
    """Class to format media data for display"""

    def __init__(self, extractor):
        self.extractor = extractor

    def _format_data_item(self, item: dict) -> str:
        """Apply all formatting to a data item and return the formatted string"""
        # Define text formatters that should be applied before markup
        text_formatters_set = {
            TextFormatter.uppercase,
            TextFormatter.lowercase,
            TextFormatter.camelcase,
        }

        # Handle value formatting first (e.g., size formatting)
        value = item.get("value")
        if value is not None:
            value_formatters = item.get("value_formatters", [])
            if not isinstance(value_formatters, list):
                value_formatters = [value_formatters] if value_formatters else []
            for formatter in value_formatters:
                value = formatter(value)

        # Handle label formatting
        label = item.get("label", "")
        if label:
            label_formatters = item.get("label_formatters", [])
            if not isinstance(label_formatters, list):
                label_formatters = [label_formatters] if label_formatters else []
            # Separate text and markup formatters, apply text first
            text_fs = [f for f in label_formatters if f in text_formatters_set]
            markup_fs = [f for f in label_formatters if f not in text_formatters_set]
            ordered_formatters = text_fs + markup_fs
            for formatter in ordered_formatters:
                label = formatter(label)

        # Create the display string
        if value is not None:
            display_string = f"{label}: {value}"
        else:
            display_string = label

        # Handle display formatting (e.g., color)
        display_formatters = item.get("display_formatters", [])
        if not isinstance(display_formatters, list):
            display_formatters = [display_formatters] if display_formatters else []
        # Separate text and markup formatters, apply text first
        text_fs = [f for f in display_formatters if f in text_formatters_set]
        markup_fs = [f for f in display_formatters if f not in text_formatters_set]
        ordered_formatters = text_fs + markup_fs
        for formatter in ordered_formatters:
            display_string = formatter(display_string)

        return display_string

    def file_info_panel(self) -> str:
        """Return formatted file info panel string"""

        output = self.file_info()

        # Add tracks info
        output.append("")
        output.extend(self.tracks_info())

        # Add filename extracted data
        output.append("")
        output.extend(self.filename_extracted_data())

        # Add mediainfo extracted data
        output.append("")
        output.extend(self.mediainfo_extracted_data())

        return "\n".join(output)

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
                "value": self.extractor.get("file_path"),
                "display_formatters": [TextFormatter.blue],
            },
            {
                "group": "File Info",
                "label": "Size",
                "value": self.extractor.get("file_size"),
                "value_formatters": [SizeFormatter.format_size_full],
                "display_formatters": [TextFormatter.bold, TextFormatter.green],
            },
            {
                "group": "File Info",
                "label": "Name",
                "label_formatters": [TextFormatter.bold],
                "value": self.extractor.get("file_name"),
                "display_formatters": [TextFormatter.cyan],
            },
            {
                "group": "File Info",
                "label": "Modified",
                "label_formatters": [TextFormatter.bold],
                "value": self.extractor.get("modification_time"),
                "value_formatters": [DateFormatter.format_modification_date],
                "display_formatters": [TextFormatter.bold, TextFormatter.magenta],
            },
            {
                "group": "File Info",
                "label": "Extension",
                "label_formatters": [TextFormatter.bold],
                "value": self.extractor.get("extension"),
                "value_formatters": [ExtensionFormatter.format_extension_info],
                "display_formatters": [TextFormatter.green],
            },
        ]
        return [self._format_data_item(item) for item in data]

    def tracks_info(self) -> list[str]:
        """Return formatted tracks information"""
        data = [
            {
                "group": "Tracks Info",
                "label": "Tracks Info",
                "label_formatters": [TextFormatter.bold, TextFormatter.uppercase],
            }
        ]
        for item in self.extractor.get("tracks").get("video_tracks"):
            data.append(
                {
                    "group": "Tracks Info",
                    "label": "Video Track",
                    "value": item,
                    "value_formatters": TrackFormatter.format_video_track,
                    "display_formatters": [TextFormatter.green],
                }
            )
        for i, item in enumerate(
            self.extractor.get("tracks").get("audio_tracks"), start=1
        ):
            data.append(
                {
                    "group": "Tracks Info",
                    "label": f"Audio Track {i}",
                    "value": item,
                    "value_formatters": TrackFormatter.format_audio_track,
                    "display_formatters": [TextFormatter.yellow],
                }
            )
        for i, item in enumerate(
            self.extractor.get("tracks").get("subtitle_tracks"), start=1
        ):
            data.append(
                {
                    "group": "Tracks Info",
                    "label": f"Subtitle Track {i}",
                    "value": item,
                    "value_formatters": TrackFormatter.format_subtitle_track,
                    "display_formatters": [TextFormatter.magenta],
                }
            )

        return [self._format_data_item(item) for item in data]

    def format_filename_extraction_panel(self) -> str:
        """Format filename extraction data for the filename panel"""
        data = [
            {
                "label": "Title",
                "value": self.extractor.get("title") or "Not found",
                "display_formatters": [TextFormatter.yellow],
            },
            {
                "label": "Year",
                "value": self.extractor.get("year") or "Not found",
                "display_formatters": [TextFormatter.yellow],
            },
            {
                "label": "Source",
                "value": self.extractor.get("source") or "Not found",
                "display_formatters": [TextFormatter.yellow],
            },
            {
                "label": "Frame Class",
                "value": self.extractor.get("frame_class") or "Not found",
                "display_formatters": [TextFormatter.yellow],
            },
        ]

        output = [TextFormatter.bold_yellow("FILENAME EXTRACTION"), ""]
        for item in data:
            output.append(self._format_data_item(item))

        return "\n".join(output)

    def format_metadata_extraction_panel(self) -> str:
        """Format metadata extraction data for the metadata panel"""
        metadata = self.extractor.get("metadata") or {}
        data = []
        if metadata.get("duration"):
            data.append(
                {
                    "label": "Duration",
                    "value": f"{metadata['duration']:.1f} seconds",
                    "display_formatters": [TextFormatter.cyan],
                }
            )
        if metadata.get("title"):
            data.append(
                {
                    "label": "Title",
                    "value": metadata["title"],
                    "display_formatters": [TextFormatter.cyan],
                }
            )
        if metadata.get("artist"):
            data.append(
                {
                    "label": "Artist",
                    "value": metadata["artist"],
                    "display_formatters": [TextFormatter.cyan],
                }
            )

        output = [TextFormatter.bold_cyan("METADATA EXTRACTION"), ""]
        if data:
            for item in data:
                output.append(self._format_data_item(item))
        else:
            output.append(TextFormatter.dim("No metadata found"))

        return "\n".join(output)

    def mediainfo_extracted_data(self) -> list[str]:
        """Format media info extraction data for the mediainfo panel"""
        data = [
            {
                "label": "Media Info Extraction",
                "label_formatters": [TextFormatter.bold, TextFormatter.uppercase],
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
        return [self._format_data_item(item) for item in data]

    def filename_extracted_data(self) -> list[str]:
        """Return formatted filename extracted data"""
        data = [
            {
                "label": "Filename Extracted Data",
                "label_formatters": [TextFormatter.bold, TextFormatter.uppercase],
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
                "label": "Aspect ratio",
                "label_formatters": [TextFormatter.bold],
                "value": self.extractor.get("aspect_ratio", "Filename")
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
        ]

        return [self._format_data_item(item) for item in data]

    def _format_extra_metadata(self, metadata: dict) -> str:
        """Format extra metadata like duration, title, artist"""
        data = {}
        if metadata.get("duration"):
            data["Duration"] = f"{metadata['duration']:.1f} seconds"
        if metadata.get("title"):
            data["Title"] = metadata["title"]
        if metadata.get("artist"):
            data["Artist"] = metadata["artist"]

        return "\n".join(
            TextFormatter.cyan(f"{key}: {value}") for key, value in data.items()
        )
