"""Media type constants for supported video formats.

This module defines all supported video container formats and their metadata.
"""

MEDIA_TYPES = {
    "mkv": {
        "description": "Matroska multimedia container",
        "meta_type": "Matroska",
        "mime": "video/x-matroska",
    },
    "mk3d": {
        "description": "Matroska 3D multimedia container",
        "meta_type": "Matroska",
        "mime": "video/x-matroska",
    },
    "avi": {
        "description": "Audio Video Interleave",
        "meta_type": "AVI",
        "mime": "video/x-msvideo",
    },
    "mov": {
        "description": "QuickTime movie",
        "meta_type": "QuickTime",
        "mime": "video/quicktime",
    },
    "mp4": {
        "description": "MPEG-4 video container",
        "meta_type": "MP4",
        "mime": "video/mp4",
    },
    "wmv": {
        "description": "Windows Media Video",
        "meta_type": "ASF",
        "mime": "video/x-ms-wmv",
    },
    "flv": {"description": "Flash Video", "meta_type": "FLV", "mime": "video/x-flv"},
    "webm": {
        "description": "WebM multimedia",
        "meta_type": "WebM",
        "mime": "video/webm",
    },
    "m4v": {"description": "MPEG-4 video", "meta_type": "MP4", "mime": "video/mp4"},
    "3gp": {"description": "3GPP multimedia", "meta_type": "MP4", "mime": "video/3gpp"},
    "ogv": {"description": "Ogg Video", "meta_type": "Ogg", "mime": "video/ogg"},
    "mpg": {
        "description": "MPEG video",
        "meta_type": "MPEG-PS",
        "mime": "video/mpeg",
    },
    "mpeg": {
        "description": "MPEG video",
        "meta_type": "MPEG-PS",
        "mime": "video/mpeg",
    },
}

# Reverse mapping: meta_type -> list of extensions
# Built once at module load instead of rebuilding in every extractor instance
META_TYPE_TO_EXTENSIONS = {}
for ext, info in MEDIA_TYPES.items():
    meta_type = info.get('meta_type')
    if meta_type:
        if meta_type not in META_TYPE_TO_EXTENSIONS:
            META_TYPE_TO_EXTENSIONS[meta_type] = []
        META_TYPE_TO_EXTENSIONS[meta_type].append(ext)
