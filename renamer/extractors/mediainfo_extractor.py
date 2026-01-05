from pathlib import Path
from pymediainfo import MediaInfo
from collections import Counter
from ..constants import FRAME_CLASSES, get_extension_from_format
from ..cache import cached_method, Cache
import langcodes
import logging

logger = logging.getLogger(__name__)


class MediaInfoExtractor:
    """Class to extract information from MediaInfo"""

    def __init__(self, file_path: Path, use_cache: bool = True):
        self.file_path = file_path
        self.cache = Cache() if use_cache else None  # Singleton cache for @cached_method decorator
        self.settings = None  # Will be set by Settings singleton if needed
        self._cache = {}  # Internal cache for method results

        # Parse media info - set to None on failure
        self.media_info = MediaInfo.parse(file_path) if file_path.exists() else None

        # Extract tracks
        if self.media_info:
            self.video_tracks = [t for t in self.media_info.tracks if t.track_type == 'Video']
            self.audio_tracks = [t for t in self.media_info.tracks if t.track_type == 'Audio']
            self.sub_tracks = [t for t in self.media_info.tracks if t.track_type == 'Text']
        else:
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

        # Check if interlaced - try multiple attributes
        # PyMediaInfo may use different attribute names depending on version
        scan_type_attr = getattr(self.video_tracks[0], 'scan_type', None)
        interlaced = getattr(self.video_tracks[0], 'interlaced', None)

        logger.debug(f"[{self.file_path.name}] Frame class detection - Resolution: {width}x{height}")
        logger.debug(f"[{self.file_path.name}]   scan_type attribute: {scan_type_attr!r} (type: {type(scan_type_attr).__name__})")
        logger.debug(f"[{self.file_path.name}]   interlaced attribute: {interlaced!r} (type: {type(interlaced).__name__})")

        # Determine scan type from available attributes
        # Check scan_type first (e.g., "Interlaced", "Progressive", "MBAFF")
        if scan_type_attr and isinstance(scan_type_attr, str):
            scan_type = 'i' if 'interlaced' in scan_type_attr.lower() else 'p'
            logger.debug(f"[{self.file_path.name}]   Using scan_type: {scan_type_attr!r} -> scan_type={scan_type!r}")
        # Then check interlaced flag (e.g., "Yes", "No")
        elif interlaced and isinstance(interlaced, str):
            scan_type = 'i' if interlaced.lower() in ['yes', 'true', '1'] else 'p'
            logger.debug(f"[{self.file_path.name}]   Using interlaced: {interlaced!r} -> scan_type={scan_type!r}")
        else:
            # Default to progressive if no information available
            scan_type = 'p'
            logger.debug(f"[{self.file_path.name}]   No scan type info, defaulting to progressive")

        # Calculate effective height for frame class determination
        aspect_ratio = 16 / 9
        if height > width:
            effective_height = height / aspect_ratio
        else:
            effective_height = height

        # First, try to match width to typical widths
        # Use a larger tolerance (10 pixels) to handle cinema/ultrawide aspect ratios
        width_matches = []
        for frame_class, info in FRAME_CLASSES.items():
            for tw in info['typical_widths']:
                if abs(width - tw) <= 10 and frame_class.endswith(scan_type):
                    diff = abs(height - info['nominal_height'])
                    width_matches.append((frame_class, diff))

        if width_matches:
            # Choose the frame class with the smallest height difference
            width_matches.sort(key=lambda x: x[1])
            result = width_matches[0][0]
            logger.debug(f"[{self.file_path.name}]   Result (width match): {result!r}")
            return result

        # If no width match, fall back to height-based matching
        # First try exact match with standard frame classes
        frame_class = f"{int(round(effective_height))}{scan_type}"
        if frame_class in FRAME_CLASSES:
            logger.debug(f"[{self.file_path.name}]   Result (exact height match): {frame_class!r}")
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
            logger.debug(f"[{self.file_path.name}]   Result (closest match, diff={min_diff}): {closest_class!r}")
            return closest_class

        # For non-standard resolutions, create a custom frame class
        logger.debug(f"[{self.file_path.name}]   Result (custom/non-standard): {frame_class!r}")
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
        """Extract file extension based on container format.

        Uses MediaInfo's format field to determine the appropriate file extension.
        Handles special cases like Matroska 3D (mk3d vs mkv).

        Returns:
            File extension (e.g., "mp4", "mkv") or None if format is unknown
        """
        if not self.media_info:
            return None
        general_track = next((t for t in self.media_info.tracks if t.track_type == 'General'), None)
        if not general_track:
            return None
        format_ = getattr(general_track, 'format', None)
        if not format_:
            return None

        # Use the constants function to get extension from format
        ext = get_extension_from_format(format_)

        # Special case: Matroska 3D uses mk3d extension
        if ext == 'mkv' and self.is_3d():
            return 'mk3d'

        return ext

    @cached_method()
    def extract_3d_layout(self) -> str | None:
        """Extract 3D stereoscopic layout from MediaInfo"""
        if not self.is_3d():
            return None
        stereoscopic = getattr(self.video_tracks[0], 'stereoscopic', None)
        return stereoscopic if stereoscopic else None

    @cached_method()
    def extract_interlaced(self) -> bool | None:
        """Determine if the video is interlaced.

        Returns:
            True: Video is interlaced
            False: Video is progressive (explicitly set)
            None: Information not available in MediaInfo
        """
        if not self.video_tracks:
            logger.debug(f"[{self.file_path.name}] Interlaced detection: No video tracks")
            return None

        scan_type_attr = getattr(self.video_tracks[0], 'scan_type', None)
        interlaced = getattr(self.video_tracks[0], 'interlaced', None)

        logger.debug(f"[{self.file_path.name}] Interlaced detection:")
        logger.debug(f"[{self.file_path.name}]   scan_type: {scan_type_attr!r} (type: {type(scan_type_attr).__name__})")
        logger.debug(f"[{self.file_path.name}]   interlaced: {interlaced!r} (type: {type(interlaced).__name__})")

        # Check scan_type attribute first (e.g., "Interlaced", "Progressive", "MBAFF")
        if scan_type_attr and isinstance(scan_type_attr, str):
            scan_lower = scan_type_attr.lower()
            if 'interlaced' in scan_lower or 'mbaff' in scan_lower:
                logger.debug(f"[{self.file_path.name}]   Result: True (from scan_type={scan_type_attr!r})")
                return True
            elif 'progressive' in scan_lower:
                logger.debug(f"[{self.file_path.name}]   Result: False (from scan_type={scan_type_attr!r})")
                return False
            # If scan_type has some other value, fall through to check interlaced
            logger.debug(f"[{self.file_path.name}]   scan_type unrecognized, checking interlaced attribute")

        # Check interlaced attribute (e.g., "Yes", "No")
        if interlaced and isinstance(interlaced, str):
            interlaced_lower = interlaced.lower()
            if interlaced_lower in ['yes', 'true', '1']:
                logger.debug(f"[{self.file_path.name}]   Result: True (from interlaced={interlaced!r})")
                return True
            elif interlaced_lower in ['no', 'false', '0']:
                logger.debug(f"[{self.file_path.name}]   Result: False (from interlaced={interlaced!r})")
                return False

        # No information available
        logger.debug(f"[{self.file_path.name}]   Result: None (no information available)")
        return None
