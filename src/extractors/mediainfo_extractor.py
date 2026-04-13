from pathlib import Path
from pymediainfo import MediaInfo
from collections import Counter
from typing import Any
from ..constants import FRAME_CLASSES, get_extension_from_format
from ..cache import cached_method, Cache
import langcodes
import logging
import functools

logger = logging.getLogger(__name__)


def requires_tracks(func):
    """Decorator that returns None if media_info has no tracks."""

    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        media_info = self._get_media_info()
        if not media_info or not media_info.tracks:
            return None
        return func(self, *args, **kwargs)

    return wrapper


def requires_tracks_type(track_type: str):
    """Decorator that returns None if no tracks of the specified type are available."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            tracks = self._get_tracks(track_type=track_type)
            if tracks is None:
                return None
            if type(tracks) is not list:
                return None
            if len(tracks) == 0:
                return None
            return func(self, *args, **kwargs)

        return wrapper

    return decorator


class MediaInfoExtractor:
    """Class to extract information from MediaInfo"""

    def __init__(self, file_path: Path, use_cache: bool = True):
        self.file_path = file_path
        self.cache = (
            Cache() if use_cache else None
        )  # Singleton cache for @cached_method decorator
        self.settings = None  # Will be set by Settings singleton if needed
        self._cache: dict[str, Any] = {}  # Internal cache for method results

    @cached_method()
    def _get_media_info(self) -> MediaInfo | None:
        """Get parsed MediaInfo object, cached. Returns None if no media."""
        if not self.file_path.exists():
            return None
        parsed = MediaInfo.parse(self.file_path)
        return parsed if parsed else None

    @requires_tracks
    def _get_tracks(self, track_type="General") -> list | None:
        """Return tracks of given type or specific track by ID."""
        media_info = self._get_media_info()
        tracks = [t for t in media_info.tracks if t.track_type == track_type]
        return tracks

    def _get_track(self, track_type="General", track_id: int = 0) -> object | None:
        """Return tracks of given type or specific track by ID."""
        tracks = self._get_tracks(track_type=track_type)
        if tracks is None:
            return None
        return tracks[track_id] if track_id < len(tracks) else None

    @requires_tracks_type("General")
    def extract_general_track(self) -> dict | None:
        """Extract general track data"""
        general = self._get_track(track_type="General", track_id=0)
        result = {
            "format": getattr(general, "format", None) or "unknown",
            "file_size": getattr(general, "file_size", None),
            "duration": getattr(general, "duration", 0) / 1000
            if getattr(general, "duration", None)
            else None,
            "overall_bit_rate": getattr(general, "overall_bit_rate", None),
            "movie_name": getattr(general, "movie_name", None),
            "encoded_date": getattr(general, "encoded_date", None),
        }
        return result

    @requires_tracks_type("Video")
    def extract_video_tracks(self) -> list[dict] | None:
        """Extract video track data"""
        tracks = self._get_tracks(track_type="Video")
        # Type assertion: decorator guarantees tracks is a list
        assert isinstance(tracks, list)
        result = []
        for v in tracks[:2]:  # Up to 2 videos
            track_data = {
                "codec": getattr(v, "format", None)
                or getattr(v, "codec", None)
                or "unknown",
                "width": getattr(v, "width", None),
                "height": getattr(v, "height", None),
                "bitrate": getattr(v, "bit_rate", None),
                "fps": getattr(v, "frame_rate", None),
                "profile": getattr(v, "format_profile", None) or "",
                "interlaced": getattr(v, "interlaced", None) == "Yes",
                "anamorphic": getattr(v, "anamorphic", None) == "Yes",
            }
            result.append(track_data)
        return result if result else None

    @requires_tracks_type("Audio")
    def extract_audio_tracks(self) -> list[dict] | None:
        """Extract audio track data"""
        tracks = self._get_tracks(track_type="Audio")
        # Type assertion: decorator guarantees tracks is a list
        assert isinstance(tracks, list)
        result = []
        for a in tracks[:10]:  # Up to 10 audios
            track_data = {
                "codec": getattr(a, "format", None)
                or getattr(a, "codec", None)
                or "unknown",
                "channels": getattr(a, "channel_s", None),
                "language": getattr(a, "language", "und"),
                "bitrate": getattr(a, "bit_rate", None),
            }
            result.append(track_data)
        return result if result else None

    @requires_tracks_type("Text")
    def extract_subtitle_tracks(self) -> list[dict] | None:
        """Extract subtitle track data"""
        tracks = self._get_tracks(track_type="Text")
        # Type assertion: decorator guarantees tracks is a list
        assert isinstance(tracks, list)
        result = []
        for s in tracks[:10]:  # Up to 10 subs
            track_data = {
                "language": getattr(s, "language", "und"),
                "format": getattr(s, "format", None)
                or getattr(s, "codec", None)
                or "unknown",
                "forced": getattr(s, "forced", None) == "Yes",
                "default": getattr(s, "default", None) == "Yes",
            }
            result.append(track_data)
        return result if result else None

    @requires_tracks
    @requires_tracks_type("General")
    def extract_duration(self) -> float | None:
        """Extract duration from media info in seconds"""
        tracks = self._get_tracks(track_type="General")
        # Type assertion: decorators guarantee tracks is a list
        assert isinstance(tracks, list)
        for track in tracks:
            return (
                getattr(track, "duration", 0) / 1000
                if getattr(track, "duration", None)
                else None
            )
        return None

    @requires_tracks_type("Video")
    def extract_resolution(self) -> tuple[int, int] | None:
        """Extract actual video resolution as (width, height) tuple from media info"""
        track = self._get_track(track_type="Video", track_id=0)
        width = getattr(track, "width", None)
        height = getattr(track, "height", None)
        if width is not None and height is not None:
            try:
                return int(width), int(height)
            except (ValueError, TypeError):
                return None
        return None

    @requires_tracks_type("Video")
    def extract_frame_class(self) -> str | None:
        """Extract frame class from media info (480p, 720p, 1080p, etc.)"""
        track = self._get_track(track_type="Video", track_id=0)

        scan_type_attr = getattr(track, "scan_type", None)

        interlaced = self.extract_interlaced()
        scan_order = getattr(track, "scan_order", None)

        resolution = self.extract_resolution()
        if not resolution:
            return None
        width, height = resolution

        logger.debug(
            f"[{self.file_path.name}] Frame class detection - Resolution: {width}x{height}"
        )
        logger.debug(
            f"[{self.file_path.name}]   scan_type attribute: {scan_type_attr!r} (type: {type(scan_type_attr).__name__})"
        )
        logger.debug(
            f"[{self.file_path.name}]   interlaced attribute: {interlaced!r} (type: {type(interlaced).__name__})"
        )
        logger.debug(
            f"[{self.file_path.name}]   scan_order attribute: {scan_order!r} (type: {type(scan_order).__name__})"
        )

        # Determine scan type from available attributes
        # Check scan_type first (e.g., "Interlaced", "Progressive", "MBAFF")
        if scan_type_attr and isinstance(scan_type_attr, str):
            scan_type = "i" if "interlaced" in scan_type_attr.lower() else "p"
            logger.debug(
                f"[{self.file_path.name}]   Using scan_type: {scan_type_attr!r} -> scan_type={scan_type!r}"
            )
        # Check scan_order (e.g., "TFF", "BFF" for interlaced, "Progressive" for progressive)
        elif scan_order and isinstance(scan_order, str):
            scan_type = "i" if scan_order.upper() in ["TFF", "BFF"] else "p"
            logger.debug(
                f"[{self.file_path.name}]   Using scan_order: {scan_order!r} -> scan_type={scan_type!r}"
            )
        # Then check interlaced flag from extract_interlaced() method
        elif interlaced is True:
            scan_type = "i"
            logger.debug(
                f"[{self.file_path.name}]   Using interlaced: True -> scan_type=i"
            )
        elif interlaced is False:
            scan_type = "p"
            logger.debug(
                f"[{self.file_path.name}]   Using interlaced: False -> scan_type=p"
            )
        else:
            # Default to progressive if no information available
            scan_type = "p"
            logger.debug(
                f"[{self.file_path.name}]   No scan type info, defaulting to progressive"
            )

        # Calculate effective height for frame class determination
        aspect_ratio = 16 / 9
        if height > width:
            effective_height = height / aspect_ratio
        else:
            effective_height = height

        # First, try to match width to typical widths
        # Use proportional tolerance (2% of typical width, min 10px) to handle
        # cinema/ultrawide aspect ratios where encoded width may differ slightly
        # (e.g. 3820×1592 scope 4K → 2160p, not a non-standard 1592p)
        width_matches = []
        for frame_class, info in FRAME_CLASSES.items():
            for tw in info["typical_widths"]:
                width_tolerance = max(10, int(tw * 0.02))
                if abs(width - tw) <= width_tolerance and frame_class.endswith(scan_type):
                    diff = abs(height - info["nominal_height"])
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
            logger.debug(
                f"[{self.file_path.name}]   Result (exact height match): {frame_class!r}"
            )
            return frame_class

        # Find closest standard height match
        closest_class = None
        min_diff = float("inf")
        for fc, info in FRAME_CLASSES.items():
            if fc.endswith(scan_type):
                diff = abs(effective_height - info["nominal_height"])
                if diff < min_diff:
                    min_diff = diff
                    closest_class = fc

        # Return closest standard match if within reasonable distance (20 pixels)
        if closest_class and min_diff <= 20:
            logger.debug(
                f"[{self.file_path.name}]   Result (closest match, diff={min_diff}): {closest_class!r}"
            )
            return closest_class

        # For non-standard resolutions, create a custom frame class
        logger.debug(
            f"[{self.file_path.name}]   Result (custom/non-standard): {frame_class!r}"
        )
        return frame_class

    @requires_tracks_type("Video")
    def extract_aspect_ratio(self) -> str | None:
        """Extract video aspect ratio from media info"""
        tracks = self._get_tracks(track_type="Video")
        # Type assertion: decorator guarantees tracks is a list
        assert isinstance(tracks, list)
        track = tracks[0]
        aspect_ratio = getattr(track, "display_aspect_ratio", None)
        if aspect_ratio:
            return str(aspect_ratio)
        return None

    @requires_tracks_type("Video")
    def extract_hdr(self) -> str | None:
        """Extract HDR info from media info"""
        tracks = self._get_tracks(track_type="Video")
        # Type assertion: decorator guarantees tracks is a list
        assert isinstance(tracks, list)
        track = tracks[0]
        profile = getattr(track, "format_profile", "") or ""
        if "HDR" in profile.upper():
            return "HDR"
        return None

    @requires_tracks
    @requires_tracks_type("Audio")
    def extract_audio_langs(self) -> str | None:
        """Extract audio languages from media info"""
        tracks = self._get_tracks(track_type="Audio")
        if not isinstance(tracks, list):
            return None
        langs = []
        for a in tracks:
            lang_code = getattr(a, "language", None)
            # Skip tracks with no language tag or 'und' (undetermined)
            if not lang_code or lang_code.lower() in ("und", "undefined"):
                continue
            try:
                # Try to get the 3-letter code
                lang_obj = langcodes.Language.get(lang_code.lower())
                alpha3 = lang_obj.to_alpha3()
                langs.append(alpha3)
            except (LookupError, ValueError, AttributeError) as e:
                # If conversion fails, use the original code
                logger.debug(f"Invalid language code '{lang_code}': {e}")
                langs.append(lang_code.lower()[:3])

        if not langs:
            return None  # No meaningful language info — let Filename extractor try

        lang_counts = Counter(langs)
        audio_langs = [
            f"{count}{lang}" if count > 1 else lang
            for lang, count in lang_counts.items()
        ]
        return ",".join(audio_langs)

    def is_3d(self) -> bool:
        """Check if the video is 3D"""
        track = self._get_track("Video", 0)
        if not track:
            return False
        multi_view = getattr(track, "multi_view_count", None)
        if multi_view and int(multi_view) > 1:
            return True
        stereoscopic = getattr(track, "stereoscopic", None)
        if stereoscopic == "Yes":
            return True
        return False

    @requires_tracks_type("General")
    def extract_extension(self) -> str | None:
        """Extract file extension based on container format.

        Uses MediaInfo's format field to determine the appropriate file extension.
        Handles special cases like Matroska 3D (mk3d vs mkv).

        Returns:
            File extension (e.g., "mp4", "mkv") or None if format is unknown
        """

        general_track = self._get_track(track_type="General", track_id=0)
        format_ = getattr(general_track, "format", None)
        if not format_:
            return None

        # Use the constants function to get extension from format
        ext = get_extension_from_format(format_)

        # Special case: Matroska 3D uses mk3d extension
        if ext == "mkv" and self.is_3d():
            return "mk3d"

        return ext

    @requires_tracks_type("Video")
    def extract_3d_layout(self) -> str | None:
        """Extract 3D stereoscopic layout from MediaInfo"""
        if not self.is_3d():
            return None
        tracks = self._get_tracks(track_type="Video")
        # Type assertion: decorator guarantees tracks is a list
        assert isinstance(tracks, list)
        track = tracks[0]
        stereoscopic = getattr(track, "stereoscopic", None)
        return stereoscopic if stereoscopic else None

    @requires_tracks_type("Video")
    def extract_interlaced(self) -> bool | None:
        """Determine if the video is interlaced.

        Returns:
            True: Video is interlaced
            False: Video is progressive (explicitly set)
            None: Information not available in MediaInfo
        """
        tracks = self._get_tracks(track_type="Video")
        # Type assertion: decorator guarantees tracks is a list
        assert isinstance(tracks, list)
        track = tracks[0]
        scan_type_attr = getattr(track, "scan_type", None)
        interlaced = getattr(track, "interlaced", None)
        scan_order = getattr(track, "scan_order", None)

        logger.debug(f"[{self.file_path.name}] Interlaced detection:")
        logger.debug(
            f"[{self.file_path.name}]   scan_type: {scan_type_attr!r} (type: {type(scan_type_attr).__name__})"
        )
        logger.debug(
            f"[{self.file_path.name}]   interlaced: {interlaced!r} (type: {type(interlaced).__name__})"
        )
        logger.debug(
            f"[{self.file_path.name}]   scan_order: {scan_order!r} (type: {type(scan_order).__name__})"
        )

        # Check scan_type attribute first (e.g., "Interlaced", "Progressive", "MBAFF")
        if scan_type_attr and isinstance(scan_type_attr, str):
            scan_lower = scan_type_attr.lower()
            if "interlaced" in scan_lower or "mbaff" in scan_lower:
                logger.debug(
                    f"[{self.file_path.name}]   Result: True (from scan_type={scan_type_attr!r})"
                )
                return True
            elif "progressive" in scan_lower:
                logger.debug(
                    f"[{self.file_path.name}]   Result: False (from scan_type={scan_type_attr!r})"
                )
                return False
            # If scan_type has some other value, fall through to check other attributes
            logger.debug(
                f"[{self.file_path.name}]   scan_type unrecognized, checking other attributes"
            )

        # Check scan_order attribute (e.g., "TFF", "BFF" for interlaced, "Progressive" for progressive)
        if scan_order and isinstance(scan_order, str):
            scan_order_upper = scan_order.upper()
            if scan_order_upper in ["TFF", "BFF"]:
                logger.debug(
                    f"[{self.file_path.name}]   Result: True (from scan_order={scan_order!r})"
                )
                return True
            elif scan_order_upper == "PROGRESSIVE":
                logger.debug(
                    f"[{self.file_path.name}]   Result: False (from scan_order={scan_order!r})"
                )
                return False
            # If scan_order has some other value, fall through
            logger.debug(
                f"[{self.file_path.name}]   scan_order unrecognized, checking interlaced attribute"
            )

        # Check interlaced attribute (e.g., "Yes", "No")
        if interlaced and isinstance(interlaced, str):
            interlaced_lower = interlaced.lower()
            if interlaced_lower in ["yes", "true", "1"]:
                logger.debug(
                    f"[{self.file_path.name}]   Result: True (from interlaced={interlaced!r})"
                )
                return True
            elif interlaced_lower in ["no", "false", "0"]:
                logger.debug(
                    f"[{self.file_path.name}]   Result: False (from interlaced={interlaced!r})"
                )
                return False

        # No information available
        logger.debug(
            f"[{self.file_path.name}]   Result: None (no information available)"
        )
        return None

    @requires_tracks_type("Video")
    def extract_anamorphic(self) -> bool | None:
        """Determine if the video uses anamorphic (pixel aspect ratio != 1) encoding.

        Returns:
            True: Video is anamorphic
            False: Video is not anamorphic
            None: Information not available in MediaInfo
        """
        tracks = self._get_tracks(track_type="Video")
        assert isinstance(tracks, list)
        track = tracks[0]
        anamorphic = getattr(track, "anamorphic", None)
        if anamorphic is None:
            return None
        return anamorphic == "Yes"
