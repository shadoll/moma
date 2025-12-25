from pathlib import Path
from pymediainfo import MediaInfo
from collections import Counter


class MediaInfoExtractor:
    """Class to extract information from MediaInfo"""

    def __init__(self):
        self.lang_map = {
            'en': 'eng', 'fr': 'fre', 'de': 'ger', 'uk': 'ukr', 'ru': 'rus',
            'es': 'spa', 'it': 'ita', 'pt': 'por', 'ja': 'jpn', 'ko': 'kor',
            'zh': 'chi', 'und': 'und'
        }

    def extract_resolution(self, file_path: Path) -> str | None:
        """Extract resolution from media info"""
        try:
            media_info = MediaInfo.parse(file_path)
            video_tracks = [t for t in media_info.tracks if t.track_type == 'Video']
            if video_tracks:
                height = getattr(video_tracks[0], 'height', None)
                if height:
                    if height >= 2160:
                        return '2160p'
                    elif height >= 1080:
                        return '1080p'
                    elif height >= 720:
                        return '720p'
                    elif height >= 480:
                        return '480p'
                    else:
                        return f'{height}p'
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