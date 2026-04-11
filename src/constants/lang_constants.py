"""Language-related constants for filename parsing.

This module contains sets of words and patterns used to identify and skip
non-language codes when extracting language information from filenames.
"""

# Words to skip when looking for language codes in filenames
# These are common words, file extensions, or technical terms that might
# look like language codes but aren't
SKIP_WORDS = {
    # Common English words that might look like language codes (2-3 letters)
    'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had',
    'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his',
    'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'way', 'who',
    'boy', 'did', 'let', 'put', 'say', 'she', 'too', 'use',

    # File extensions (video)
    'avi', 'mkv', 'mp4', 'mpg', 'mov', 'wmv', 'flv', 'webm', 'm4v', 'm2ts',
    'ts', 'vob', 'iso', 'img',

    # Quality/resolution indicators
    'sd', 'hd', 'lq', 'qhd', 'uhd', 'p', 'i', 'hdr', 'sdr', '4k', '8k',
    '2160p', '1080p', '720p', '480p', '360p', '240p', '144p',

    # Source/codec indicators
    'web', 'dl', 'rip', 'bluray', 'dvd', 'hdtv', 'bdrip', 'dvdrip', 'xvid',
    'divx', 'h264', 'h265', 'x264', 'x265', 'hevc', 'avc',

    # Audio codecs
    'ma', 'atmos', 'dts', 'aac', 'ac3', 'mp3', 'flac', 'wav', 'wma', 'ogg', 'opus'
}
