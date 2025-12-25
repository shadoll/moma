from pathlib import Path
from pymediainfo import MediaInfo
from collections import Counter
from ..constants import FRAME_CLASSES


class MediaInfoExtractor:
    """Class to extract information from MediaInfo"""

    def __init__(self):
        self.lang_map = {
            'en': 'eng', 'fr': 'fre', 'de': 'ger', 'uk': 'ukr', 'ru': 'rus',
            'es': 'spa', 'it': 'ita', 'pt': 'por', 'ja': 'jpn', 'ko': 'kor',
            'zh': 'chi', 'und': 'und'
        }

    def _get_frame_class_from_height(self, height: int) -> str:
        """Get frame class from video height using FRAME_CLASSES constant"""
        for frame_class, info in FRAME_CLASSES.items():
            if height == info['nominal_height']:
                return frame_class
        return 'Unclassified'

    def extract_frame_class(self, file_path: Path) -> str | None:
        """Extract frame class from media info (480p, 720p, 1080p, etc.)"""
        try:
            media_info = MediaInfo.parse(file_path)
            video_tracks = [t for t in media_info.tracks if t.track_type == 'Video']
            if video_tracks:
                height = getattr(video_tracks[0], 'height', None)
                if height:
                    return self._get_frame_class_from_height(height)
        except:
            pass
        return 'Unclassified'

    def extract_resolution(self, file_path: Path) -> str | None:
        """Extract actual video resolution (WIDTHxHEIGHT) from media info"""
        try:
            media_info = MediaInfo.parse(file_path)
            video_tracks = [t for t in media_info.tracks if t.track_type == 'Video']
            if video_tracks:
                width = getattr(video_tracks[0], 'width', None)
                height = getattr(video_tracks[0], 'height', None)
                if width and height:
                    return f"{width}x{height}"
        except:
            pass
        return None

    def extract_aspect_ratio(self, file_path: Path) -> str | None:
        """Extract video aspect ratio from media info"""
        try:
            media_info = MediaInfo.parse(file_path)
            video_tracks = [t for t in media_info.tracks if t.track_type == 'Video']
            if video_tracks:
                aspect_ratio = getattr(video_tracks[0], 'display_aspect_ratio', None)
                if aspect_ratio:
                    return str(aspect_ratio)
        except:
            pass
        return None

    def extract_hdr(self, file_path: Path) -> str | None:
        """Extract HDR info from media info"""
        try:
            media_info = MediaInfo.parse(file_path)
            video_tracks = [t for t in media_info.tracks if t.track_type == 'Video']
            if video_tracks:
                profile = getattr(video_tracks[0], 'format_profile', '')
                if 'HDR' in profile.upper():
                    return 'HDR'
        except:
            pass
        return None

    def extract_audio_langs(self, file_path: Path) -> str:
        """Extract audio languages from media info"""
        try:
            media_info = MediaInfo.parse(file_path)
            audio_tracks = [t for t in media_info.tracks if t.track_type == 'Audio']
            langs = [getattr(a, 'language', 'und').lower()[:3] for a in audio_tracks]
            langs = [self.lang_map.get(lang, lang) for lang in langs]
            lang_counts = Counter(langs)
            audio_langs = [f"{count}{lang}" if count > 1 else lang for lang, count in lang_counts.items()]
            return ','.join(audio_langs)
        except:
            return ''

    def extract_video_dimensions(self, file_path: Path) -> tuple[int, int] | None:
        """Extract video width and height"""
        try:
            media_info = MediaInfo.parse(file_path)
            video_tracks = [t for t in media_info.tracks if t.track_type == 'Video']
            if video_tracks:
                width = getattr(video_tracks[0], 'width', None)
                height = getattr(video_tracks[0], 'height', None)
                if width and height:
                    return width, height
        except:
            pass
        return None