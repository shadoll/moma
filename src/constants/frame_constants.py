"""Frame class and resolution constants.

This module defines video resolution frame classes (480p, 720p, 1080p, 4K, 8K, etc.)
and their nominal heights and typical widths.

Also includes non-standard quality indicators that appear in filenames but don't
represent specific resolutions.
"""

from typing import TypedDict


class FrameClassInfo(TypedDict):
    """Information about a video frame class."""
    nominal_height: int
    typical_widths: list[int]
    description: str

# Non-standard quality indicators that don't have specific resolution values
# These are used in filenames to indicate quality but aren't proper frame classes
# When found, we return None instead of trying to classify them
# Note: We have specific frame classes like "2160p" (4K) and "4320p" (8K),
# but when files use just "4K" or "8K" without the "p" suffix, we can't determine
# the exact resolution, so we treat them as non-standard indicators
NON_STANDARD_QUALITY_INDICATORS = ['SD', 'LQ', 'HD', 'QHD', 'FHD', 'FullHD', '4K', '8K']

FRAME_CLASSES: dict[str, FrameClassInfo] = {
    "480p": {
        "nominal_height": 480,
        "typical_widths": [640, 704, 720],
        "description": "Standard Definition (SD) - DVD quality",
    },
    "480i": {
        "nominal_height": 480,
        "typical_widths": [640, 704, 720],
        "description": "Standard Definition (SD) interlaced - NTSC quality",
    },
    "360p": {
        "nominal_height": 360,
        "typical_widths": [480, 640],
        "description": "Low Definition (LD) - 360p",
    },
    "576p": {
        "nominal_height": 576,
        "typical_widths": [720, 768],
        "description": "PAL Standard Definition (SD) - European DVD quality",
    },
    "576i": {
        "nominal_height": 576,
        "typical_widths": [720, 768],
        "description": "PAL Standard Definition (SD) interlaced - European quality",
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
    "1080i": {
        "nominal_height": 1080,
        "typical_widths": [1920],
        "description": "Full High Definition (FHD) interlaced - 1080i HD",
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
