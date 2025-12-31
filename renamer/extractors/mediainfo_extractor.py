from pathlib import Path
from pymediainfo import MediaInfo
from collections import Counter
from ..constants import FRAME_CLASSES, MEDIA_TYPES
from ..decorators import cached_method
import langcodes
import logging

logger = logging.getLogger(__name__)


class MediaInfoExtractor:
    """Class to extract information from MediaInfo"""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self._cache = {}  # Internal cache for method results
        try:
            self.media_info = MediaInfo.parse(file_path)
            self.video_tracks = [t for t in self.media_info.tracks if t.track_type == 'Video']
            self.audio_tracks = [t for t in self.media_info.tracks if t.track_type == 'Audio']
            self.sub_tracks = [t for t in self.media_info.tracks if t.track_type == 'Text']
        except Exception as e:
            logger.warning(f"Failed to parse media info for {file_path}: {e}")
            self.media_info = None
            self.video_tracks = []
            self.audio_tracks = []
            self.sub_tracks = []

        # Build mapping from meta_type to extensions
        self._format_to_extensions = {}
        for ext, info in MEDIA_TYPES.items():
            meta_type = info.get('meta_type')
            if meta_type:
                if meta_type not in self._format_to_extensions:
                    self._format_to_extensions[meta_type] = []
                self._format_to_extensions[meta_type].append(ext)

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

    @cached_method()
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
        
        # Calculate effective height for frame class determination
        aspect_ratio = 16 / 9
        if height > width:
            effective_height = height / aspect_ratio
        else:
            effective_height = height
        
        # First, try to match width to typical widths
        width_matches = []
        for frame_class, info in FRAME_CLASSES.items():
            for tw in info['typical_widths']:
                if abs(width - tw) <= 5 and frame_class.endswith(scan_type):
                    diff = abs(height - info['nominal_height'])
                    width_matches.append((frame_class, diff))
        
        if width_matches:
            # Choose the frame class with the smallest height difference
            width_matches.sort(key=lambda x: x[1])
            return width_matches[0][0]
        
        # If no width match, fall back to height-based matching
        # First try exact match with standard frame classes
        frame_class = f"{int(round(effective_height))}{scan_type}"
        if frame_class in FRAME_CLASSES:
            return frame_class
        
        # Find closest standard height match
        closest_class = None
        min_diff = float('inf')
        for fc, info in FRAME_CLASSES.items():
            if fc.endswith(scan_type):
                diff = abs(effective_height - info['nominal_height'])
                if diff < min_diff:
                    min_diff = diff
                    closest_class = fc
        
        # Return closest standard match if within reasonable distance (20 pixels)
        if closest_class and min_diff <= 20:
            return closest_class
        
        # For non-standard resolutions, create a custom frame class
        return frame_class

    @cached_method()
    def extract_resolution(self) -> tuple[int, int] | None:
        """Extract actual video resolution as (width, height) tuple from media info"""
        if not self.video_tracks:
            return None
        width = getattr(self.video_tracks[0], 'width', None)
        height = getattr(self.video_tracks[0], 'height', None)
        if width and height:
            return width, height
        return None
    
    @cached_method()
    def extract_aspect_ratio(self) -> str | None:
        """Extract video aspect ratio from media info"""
        if not self.video_tracks:
            return None
        aspect_ratio = getattr(self.video_tracks[0], 'display_aspect_ratio', None)
        if aspect_ratio:
            return str(aspect_ratio)
        return None

    @cached_method()
    def extract_hdr(self) -> str | None:
        """Extract HDR info from media info"""
        if not self.video_tracks:
            return None
        profile = getattr(self.video_tracks[0], 'format_profile', '') or ''
        if 'HDR' in profile.upper():
            return 'HDR'
        return None

    @cached_method()
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
            except (LookupError, ValueError, AttributeError) as e:
                # If conversion fails, use the original code
                logger.debug(f"Invalid language code '{lang_code}': {e}")
                langs.append(lang_code.lower()[:3])
        
        lang_counts = Counter(langs)
        audio_langs = [f"{count}{lang}" if count > 1 else lang for lang, count in lang_counts.items()]
        return ','.join(audio_langs)

    @cached_method()
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

    @cached_method()
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

    @cached_method()
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

    @cached_method()
    def is_3d(self) -> bool:
        """Check if the video is 3D"""
        if not self.video_tracks:
            return False
        multi_view = getattr(self.video_tracks[0], 'multi_view_count', None)
        if multi_view and int(multi_view) > 1:
            return True
        stereoscopic = getattr(self.video_tracks[0], 'stereoscopic', None)
        if stereoscopic == 'Yes':
            return True
        return False

    @cached_method()
    def extract_anamorphic(self) -> str | None:
        """Extract anamorphic info for 3D videos"""
        if not self.video_tracks:
            return None
        anamorphic = getattr(self.video_tracks[0], 'anamorphic', None)
        if anamorphic == 'Yes' and self.is_3d():
            return 'Anamorphic:Yes'
        return None

    @cached_method()
    def extract_extension(self) -> str | None:
        """Extract file extension based on container format"""
        if not self.media_info:
            return None
        general_track = next((t for t in self.media_info.tracks if t.track_type == 'General'), None)
        if not general_track:
            return None
        format_ = getattr(general_track, 'format', None)
        if format_ in self._format_to_extensions:
            exts = self._format_to_extensions[format_]
            if format_ == 'Matroska':
                if self.is_3d() and 'mk3d' in exts:
                    return 'mk3d'
                else:
                    return 'mkv'
            else:
                return exts[0] if exts else None
        return None

    @cached_method()
    def extract_3d_layout(self) -> str | None:
        """Extract 3D stereoscopic layout from MediaInfo"""
        if not self.is_3d():
            return None
        stereoscopic = getattr(self.video_tracks[0], 'stereoscopic', None)
        return stereoscopic if stereoscopic else None