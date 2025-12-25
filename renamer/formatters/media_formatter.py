from pathlib import Path
from .size_formatter import SizeFormatter
from .date_formatter import DateFormatter
from .extension_extractor import ExtensionExtractor
from .extension_formatter import ExtensionFormatter
from .color_formatter import ColorFormatter


class MediaFormatter:
    """Class to format media data for display"""

    def format_file_info_panel(self, extractor) -> str:
        """Format file information for the file info panel"""
        data = [
            {
                "label": "Path",
                "value": extractor.get("file_path"),
                "format_func": ColorFormatter.bold_blue,
            },
            {
                "label": "Size",
                "value": SizeFormatter.format_size_full(extractor.get("file_size")),
                "format_func": ColorFormatter.bold_green,
            },
            {
                "label": "File",
                "value": extractor.get("file_name"),
                "format_func": ColorFormatter.bold_cyan,
            },
            {
                "label": "Modified",
                "value": DateFormatter.format_modification_date(
                    extractor.get("modification_time")
                ),
                "format_func": ColorFormatter.bold_magenta,
            },
        ]

        # Get extension info
        ext_name = ExtensionExtractor.get_extension_name(
            Path(extractor.get("file_path"))
        )
        ext_desc = ExtensionExtractor.get_extension_description(ext_name)
        meta_type = extractor.get("meta_type")
        meta_desc = extractor.get("meta_description")
        match = ExtensionFormatter.check_extension_match(ext_name, meta_type)
        ext_info = ExtensionFormatter.format_extension_info(
            ext_name, ext_desc, meta_type, meta_desc, match
        )

        output = [ColorFormatter.bold_blue("FILE INFO"), ""]
        output.extend(
            item["format_func"](f"{item['label']}: {item['value']}") for item in data
        )
        output.append(ext_info)

        # Add tracks info
        tracks_text = extractor.get('tracks')
        if not tracks_text:
            tracks_text = ColorFormatter.grey("No track info available")
        output.append("")
        output.append(tracks_text)

        # Add rename lines
        rename_lines = self.format_rename_lines(extractor)
        output.append("")
        output.extend(rename_lines)

        return "\n".join(output)

    def format_filename_extraction_panel(self, extractor) -> str:
        """Format filename extraction data for the filename panel"""
        data = [
            {
                "label": "Title",
                "value": extractor.get("title") or "Not found",
                "format_func": ColorFormatter.yellow,
            },
            {
                "label": "Year",
                "value": extractor.get("year") or "Not found",
                "format_func": ColorFormatter.yellow,
            },
            {
                "label": "Source",
                "value": extractor.get("source") or "Not found",
                "format_func": ColorFormatter.yellow,
            },
            {
                "label": "Frame Class",
                "value": extractor.get("frame_class") or "Not found",
                "format_func": ColorFormatter.yellow,
            },
        ]

        output = [ColorFormatter.bold_yellow("FILENAME EXTRACTION"), ""]
        output.extend(
            item["format_func"](f"{item['label']}: {item['value']}") for item in data
        )

        return "\n".join(output)

    def format_metadata_extraction_panel(self, extractor) -> str:
        """Format metadata extraction data for the metadata panel"""
        metadata = extractor.get("metadata") or {}
        data = []
        if metadata.get("duration"):
            data.append(
                {
                    "label": "Duration",
                    "value": f"{metadata['duration']:.1f} seconds",
                    "format_func": ColorFormatter.cyan,
                }
            )
        if metadata.get("title"):
            data.append(
                {
                    "label": "Title",
                    "value": metadata["title"],
                    "format_func": ColorFormatter.cyan,
                }
            )
        if metadata.get("artist"):
            data.append(
                {
                    "label": "Artist",
                    "value": metadata["artist"],
                    "format_func": ColorFormatter.cyan,
                }
            )

        output = [ColorFormatter.bold_cyan("METADATA EXTRACTION"), ""]
        if data:
            output.extend(
                item["format_func"](f"{item['label']}: {item['value']}")
                for item in data
            )
        else:
            output.append(ColorFormatter.dim("No metadata found"))

        return "\n".join(output)

    def format_mediainfo_extraction_panel(self, extractor) -> str:
        """Format media info extraction data for the mediainfo panel"""
        data = [
            {
                "label": "Resolution",
                "value": extractor.get("resolution") or "Not found",
                "format_func": ColorFormatter.green,
            },
            {
                "label": "Aspect Ratio",
                "value": extractor.get("aspect_ratio") or "Not found",
                "format_func": ColorFormatter.green,
            },
            {
                "label": "HDR",
                "value": extractor.get("hdr") or "Not found",
                "format_func": ColorFormatter.green,
            },
            {
                "label": "Audio Languages",
                "value": extractor.get("audio_langs") or "Not found",
                "format_func": ColorFormatter.green,
            },
        ]

        output = [ColorFormatter.bold_green("MEDIA INFO EXTRACTION"), ""]
        output.extend(
            item["format_func"](f"{item['label']}: {item['value']}") for item in data
        )

        return "\n".join(output)

    def format_rename_lines(self, extractor) -> list[str]:
        """Format the rename information lines"""
        data = {
            "Movie title": extractor.get("title") or "Unknown",
            "Year": extractor.get("year") or "Unknown",
            "Video source": extractor.get("source") or "Unknown",
            "Frame class": extractor.get("frame_class") or "Unknown",
            "Resolution": extractor.get("resolution") or "Unknown",
            "Aspect ratio": extractor.get("aspect_ratio") or "Unknown",
            "HDR": extractor.get("hdr") or "No",
            "Audio langs": extractor.get("audio_langs") or "None",
        }

        return [f"{key}: {value}" for key, value in data.items()]

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
            ColorFormatter.cyan(f"{key}: {value}") for key, value in data.items()
        )
