VIDEO_EXTENSIONS = {'.mkv', '.avi', '.mov', '.mp4', '.wmv', '.flv', '.webm', '.m4v', '.3gp', '.ogv'}

VIDEO_EXT_DESCRIPTIONS = {
    'mkv': 'Matroska multimedia container',
    'avi': 'Audio Video Interleave',
    'mov': 'QuickTime movie',
    'mp4': 'MPEG-4 video container',
    'wmv': 'Windows Media Video',
    'flv': 'Flash Video',
    'webm': 'WebM multimedia',
    'm4v': 'MPEG-4 video',
    '3gp': '3GPP multimedia',
    'ogv': 'Ogg Video',
}

META_DESCRIPTIONS = {
    'MP4': 'MPEG-4 video container',
    'Matroska': 'Matroska multimedia container',
    'AVI': 'Audio Video Interleave',
    'QuickTime': 'QuickTime movie',
    'ASF': 'Windows Media',
    'FLV': 'Flash Video',
    'WebM': 'WebM multimedia',
    'Ogg': 'Ogg multimedia',
}

SOURCE_DICT = {
    'WEB-DL': ['WEB-DL', 'WEBRip', 'WEB-Rip', 'WEB'],
    'BDRip': ['BDRip', 'BD-Rip', 'BDRIP'],
    'BDRemux': ['BDRemux', 'BD-Remux', 'BDREMUX'],
    'DVDRip': ['DVDRip', 'DVD-Rip', 'DVDRIP'],
    'HDTV': ['HDTV'],
    'BluRay': ['BluRay', 'BLURAY', 'Blu-ray'],
}

FRAME_CLASSES = {
    '480p': {
        'nominal_height': 480,
        'typical_widths': [640, 704, 720],
        'description': 'Standard Definition (SD) - DVD quality'
    },
    '576p': {
        'nominal_height': 576,
        'typical_widths': [720, 768],
        'description': 'PAL Standard Definition (SD) - European DVD quality'
    },
    '720p': {
        'nominal_height': 720,
        'typical_widths': [1280],
        'description': 'High Definition (HD) - 720p HD'
    },
    '1080p': {
        'nominal_height': 1080,
        'typical_widths': [1920],
        'description': 'Full High Definition (FHD) - 1080p HD'
    },
    '1440p': {
        'nominal_height': 1440,
        'typical_widths': [2560],
        'description': 'Quad High Definition (QHD) - 1440p 2K'
    },
    '2160p': {
        'nominal_height': 2160,
        'typical_widths': [3840],
        'description': 'Ultra High Definition (UHD) - 2160p 4K'
    },
    '4320p': {
        'nominal_height': 4320,
        'typical_widths': [7680],
        'description': 'Ultra High Definition (UHD) - 4320p 8K'
    }
}