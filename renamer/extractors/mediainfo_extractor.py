from pathlib import Path
from pymediainfo import MediaInfo
from collections import Counter
from ..constants import FRAME_CLASSES
import langcodes


class MediaInfoExtractor:
    """Class to extract information from MediaInfo"""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        try:
            self.media_info = MediaInfo.parse(file_path)
            self.video_tracks = [t for t in self.media_info.tracks if t.track_type == 'Video']
            self.audio_tracks = [t for t in self.media_info.tracks if t.track_type == 'Audio']
            self.sub_tracks = [t for t in self.media_info.tracks if t.track_type == 'Text']
        except Exception:
            self.media_info = None
            self.video_tracks = []
            self.audio_tracks = []
            self.sub_tracks = []

    def _get_frame_class_from_height(self, height: int) -> str | None:
        """Get frame class from video height using FRAME_CLASSES constant"""
        for frame_class, info in FRAME_CLASSES.items():
            if height == info['nominal_height']:
                return frame_class
        return None

    def extract_duration(self) -> float | None:
        """Extract duration from media info in seconds"""
        if self.media_info:
            for track in self.media_info.tracks:
                if track.track_type == 'General':
                    return getattr(track, 'duration', 0) / 1000 if getattr(track, 'duration', None) else None
        return None

    def extract_frame_class(self) -> str | None:
        """Extract frame class from media info (480p, 720p, 1080p, etc.)"""
        if not self.video_tracks:
            return None
        height = getattr(self.video_tracks[0], 'height', None)
        if height:
            return self._get_frame_class_from_height(height)
        return None

    def extract_resolution(self) -> tuple[int, int] | None:
        """Extract actual video resolution as (width, height) tuple from media info"""
        if not self.video_tracks:
            return None
        width = getattr(self.video_tracks[0], 'width', None)
        height = getattr(self.video_tracks[0], 'height', None)
        if width and height:
            return width, height
        return None
    
    def extract_aspect_ratio(self) -> str | None:
        """Extract video aspect ratio from media info"""
        if not self.video_tracks:
            return None
        aspect_ratio = getattr(self.video_tracks[0], 'display_aspect_ratio', None)
        if aspect_ratio:
            return str(aspect_ratio)
        return None

    def extract_hdr(self) -> str | None:
        """Extract HDR info from media info"""
        if not self.video_tracks:
            return None
        profile = getattr(self.video_tracks[0], 'format_profile', '')
        if 'HDR' in profile.upper():
            return 'HDR'
        return None

    def extract_audio_langs(self) -> str:
        """Extract audio languages from media info"""
        if not self.audio_tracks:
            return ''
        langs = []
        for a in self.audio_tracks:
            lang_code = getattr(a, 'language', 'und').lower()
            try:
                # Try to get the 3-letter code
                lang_obj = langcodes.Language.get(lang_code)
                alpha3 = lang_obj.to_alpha3()
                langs.append(alpha3)
            except:
                # If conversion fails, use the original code
                langs.append(lang_code[:3])
        
        lang_counts = Counter(langs)
        audio_langs = [f"{count}{lang}" if count > 1 else lang for lang, count in lang_counts.items()]
        return ','.join(audio_langs)

    def extract_video_tracks(self) -> list[dict]:
        """Extract video track data"""
        tracks = []
        for v in self.video_tracks[:2]:  # Up to 2 videos
            track_data = {
                'codec': getattr(v, 'format', None) or getattr(v, 'codec', None) or 'unknown',
                'width': getattr(v, 'width', None),
                'height': getattr(v, 'height', None),
                'bitrate': getattr(v, 'bit_rate', None),
                'fps': getattr(v, 'frame_rate', None),
                'profile': getattr(v, 'format_profile', None),
            }
            tracks.append(track_data)
        return tracks

    def extract_audio_tracks(self) -> list[dict]:
        """Extract audio track data"""
        tracks = []
        for a in self.audio_tracks[:10]:  # Up to 10 audios
            track_data = {
                'codec': getattr(a, 'format', None) or getattr(a, 'codec', None) or 'unknown',
                'channels': getattr(a, 'channel_s', None),
                'language': getattr(a, 'language', None) or 'und',
                'bitrate': getattr(a, 'bit_rate', None),
            }
            tracks.append(track_data)
        return tracks

    def extract_subtitle_tracks(self) -> list[dict]:
        """Extract subtitle track data"""
        tracks = []
        for s in self.sub_tracks[:10]:  # Up to 10 subs
            track_data = {
                'language': getattr(s, 'language', None) or 'und',
                'format': getattr(s, 'format', None) or getattr(s, 'codec', None) or 'unknown',
            }
            tracks.append(track_data)
        return tracks