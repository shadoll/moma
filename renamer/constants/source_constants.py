"""Video source type constants.

This module defines video source types (WEB-DL, BDRip, etc.) and their aliases.
"""

SOURCE_DICT = {
    "WEB-DL": ["WEB-DL", "WEBRip", "WEB-Rip", "WEB", "WEB-DLRip"],
    "BDRip": ["BDRip", "BD-Rip", "BDRIP"],
    "BDRemux": ["BDRemux", "BD-Remux", "BDREMUX"],
    "DVDRip": ["DVDRip", "DVD-Rip", "DVDRIP"],
    "HDTVRip": ["HDTVRip", "HDTV"],
    "BluRay": ["BluRay", "BLURAY", "Blu-ray"],
    "SATRip": ["SATRip", "SAT-Rip", "SATRIP"],
    "VHSRecord": [
        "VHSRecord",
        "VHS Record",
        "VHS-Rip",
        "VHSRip",
        "VHS",
        "VHS Tape",
        "VHS-Tape",
    ],
}
