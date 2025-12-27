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
        """Get frame class from video height, finding closest match if exact not found"""
        if not height:
            return None
        
        # First try exact match
        for frame_class, info in FRAME_CLASSES.items():
            if height == info['nominal_height']:
                return frame_class
        
        # If no exact match, find closest
        closest = None
        min_diff = float('inf')
        for frame_class, info in FRAME_CLASSES.items():
            diff = abs(height - info['nominal_height'])
            if diff < min_diff:
                min_diff = diff
                closest = frame_class
        
        # Only return if difference is reasonable (within 50 pixels)
        if min_diff <= 50:
            return closest
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
        width = getattr(self.video_tracks[0], 'width', None)
        if not height or not width:
            return None
        
        # Check if interlaced
        interlaced = getattr(self.video_tracks[0], 'interlaced', None)
        scan_type = 'i' if interlaced == 'Yes' else 'p'
        
        # First, try to match width to typical widths
        matching_classes = []
        for frame_class, info in FRAME_CLASSES.items():
            if width in info['typical_widths'] and frame_class.endswith(scan_type):
                matching_classes.append((frame_class, info))
        
        if matching_classes:
            # If multiple matches, choose the one with closest height
            closest = min(matching_classes, key=lambda x: abs(height - x[1]['nominal_height']))
            return closest[0]
        
        # If no width match, fall back to height-based matching
        # First try exact match
        frame_class = f"{height}{scan_type}"
        if frame_class in FRAME_CLASSES:
            return frame_class
        
        # Find closest height with same scan type
        closest_height = None
        min_diff = float('inf')
        for fc, info in FRAME_CLASSES.items():
            if fc.endswith(scan_type):
                diff = abs(height - info['nominal_height'])
                if diff < min_diff:
                    min_diff = diff
                    closest_height = info['nominal_height']
        
        if closest_height and min_diff <= 100:
            return f"{closest_height}{scan_type}"
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
        profile = getattr(self.video_tracks[0], 'format_profile', '') or ''
        if 'HDR' in profile.upper():
            return 'HDR'
        return None

    def extract_audio_langs(self) -> str | None:
        """Extract audio languages from media info"""
        if not self.audio_tracks:
            return None
        langs = []
        for a in self.audio_tracks:
            lang_code = getattr(a, 'language', 'und') or 'und'
            try:
                # Try to get the 3-letter code
                lang_obj = langcodes.Language.get(lang_code.lower())
                alpha3 = lang_obj.to_alpha3()
                langs.append(alpha3)
            except:
                # If conversion fails, use the original code
                langs.append(lang_code.lower()[:3])
        
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
                'profile': getattr(v, 'format_profile', None) or '',
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