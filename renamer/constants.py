MEDIA_TYPES = {
    "mkv": {
        "description": "Matroska multimedia container",
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
}

SOURCE_DICT = {
    "WEB-DL": ["WEB-DL", "WEBRip", "WEB-Rip", "WEB", "WEB-DLRip"],
    "BDRip": ["BDRip", "BD-Rip", "BDRIP"],
    "BDRemux": ["BDRemux", "BD-Remux", "BDREMUX"],
    "DVDRip": ["DVDRip", "DVD-Rip", "DVDRIP"],
    "HDTV": ["HDTV"],
    "BluRay": ["BluRay", "BLURAY", "Blu-ray"],
}

FRAME_CLASSES = {
    "480p": {
        "nominal_height": 480,
        "typical_widths": [640, 704, 720],
        "description": "Standard Definition (SD) - DVD quality",
    },
    "576p": {
        "nominal_height": 576,
        "typical_widths": [720, 768],
        "description": "PAL Standard Definition (SD) - European DVD quality",
    },
    "720p": {
        "nominal_height": 720,
        "typical_widths": [1280],
        "description": "High Definition (HD) - 720p HD",
    },
    "1080p": {
        "nominal_height": 1080,
        "typical_widths": [1920],
        "description": "Full High Definition (FHD) - 1080p HD",
    },
    "1440p": {
        "nominal_height": 1440,
        "typical_widths": [2560],
        "description": "Quad High Definition (QHD) - 1440p 2K",
    },
    "2160p": {
        "nominal_height": 2160,
        "typical_widths": [3840],
        "description": "Ultra High Definition (UHD) - 2160p 4K",
    },
    "4320p": {
        "nominal_height": 4320,
        "typical_widths": [7680],
        "description": "Ultra High Definition (UHD) - 4320p 8K",
    },
}
