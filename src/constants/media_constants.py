"""Media type constants for supported video formats.

This module defines all supported video container formats and their metadata.
Each entry includes the MediaInfo format name for proper detection.
"""

MEDIA_TYPES = {
    "mkv": {
        "description": "Matroska multimedia container",
        "meta_type": "Matroska",
        "mime": "video/x-matroska",
        "mediainfo_format": "Matroska",
    },
    "mk3d": {
        "description": "Matroska 3D multimedia container",
        "meta_type": "Matroska",
        "mime": "video/x-matroska",
        "mediainfo_format": "Matroska",
    },
    "avi": {
        "description": "Audio Video Interleave",
        "meta_type": "AVI",
        "mime": "video/x-msvideo",
        "mediainfo_format": "AVI",
    },
    "mov": {
        "description": "QuickTime movie",
        "meta_type": "QuickTime",
        "mime": "video/quicktime",
        "mediainfo_format": "QuickTime",
    },
    "mp4": {
        "description": "MPEG-4 video container",
        "meta_type": "MP4",
        "mime": "video/mp4",
        "mediainfo_format": "MPEG-4",
    },
    "wmv": {
        "description": "Windows Media Video",
        "meta_type": "ASF",
        "mime": "video/x-ms-wmv",
        "mediainfo_format": "Windows Media",
    },
    "flv": {
        "description": "Flash Video",
        "meta_type": "FLV",
        "mime": "video/x-flv",
        "mediainfo_format": "Flash Video",
    },
    "webm": {
        "description": "WebM multimedia",
        "meta_type": "WebM",
        "mime": "video/webm",
        "mediainfo_format": "WebM",
    },
    "m4v": {
        "description": "MPEG-4 video",
        "meta_type": "MP4",
        "mime": "video/mp4",
        "mediainfo_format": "MPEG-4",
    },
    "3gp": {
        "description": "3GPP multimedia",
        "meta_type": "MP4",
        "mime": "video/3gpp",
        "mediainfo_format": "MPEG-4",
    },
    "ogv": {
        "description": "Ogg Video",
        "meta_type": "Ogg",
        "mime": "video/ogg",
        "mediainfo_format": "Ogg",
    },
    "mpg": {
        "description": "MPEG video",
        "meta_type": "MPEG-PS",
        "mime": "video/mpeg",
        "mediainfo_format": "MPEG-PS",
    },
    "mpeg": {
        "description": "MPEG video",
        "meta_type": "MPEG-PS",
        "mime": "video/mpeg",
        "mediainfo_format": "MPEG-PS",
    },
}

# Reverse mapping: meta_type -> list of extensions
# Built once at module load instead of rebuilding in every extractor instance
META_TYPE_TO_EXTENSIONS: dict[str, list[str]] = {}
for ext, info in MEDIA_TYPES.items():
    meta_type = info.get('meta_type')
    if meta_type:
        if meta_type not in META_TYPE_TO_EXTENSIONS:
            META_TYPE_TO_EXTENSIONS[meta_type] = []
        META_TYPE_TO_EXTENSIONS[meta_type].append(ext)

# Reverse mapping: MediaInfo format name -> extension
# Built from MEDIA_TYPES at module load
MEDIAINFO_FORMAT_TO_EXTENSION = {}
for ext, info in MEDIA_TYPES.items():
    mediainfo_format = info.get('mediainfo_format')
    if mediainfo_format:
        # Store only the first (primary) extension for each format
        if mediainfo_format not in MEDIAINFO_FORMAT_TO_EXTENSION:
            MEDIAINFO_FORMAT_TO_EXTENSION[mediainfo_format] = ext


def get_extension_from_format(format_name: str) -> str | None:
    """Get file extension from MediaInfo format name.

    Args:
        format_name: Format name as reported by MediaInfo (e.g., "MPEG-4", "Matroska")

    Returns:
        File extension (e.g., "mp4", "mkv") or None if format is unknown

    Example:
        >>> get_extension_from_format("MPEG-4")
        'mp4'
        >>> get_extension_from_format("Matroska")
        'mkv'
    """
    return MEDIAINFO_FORMAT_TO_EXTENSION.get(format_name)
