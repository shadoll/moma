"""Frame class and aspect ratio matching utilities.

This module provides centralized logic for determining frame class
(resolution classification) based on video dimensions.
"""

import logging
from typing import Optional

from renamer.constants import FRAME_CLASSES


logger = logging.getLogger(__name__)


class FrameClassMatcher:
    """Shared frame class matching logic.

    This class centralizes the logic for determining frame class
    (e.g., "1080p", "720p") from video dimensions.

    Example:
        >>> matcher = FrameClassMatcher()
        >>> matcher.match_by_dimensions(1920, 1080, scan_type='p')
        '1080p'
    """

    # Tolerance for matching dimensions (pixels)
    HEIGHT_TOLERANCE_LARGE = 50  # For initial height matching
    HEIGHT_TOLERANCE_SMALL = 20  # For closest match
    WIDTH_TOLERANCE = 5  # For width matching

    def __init__(self):
        """Initialize the frame class matcher."""
        pass

    def match_by_dimensions(
        self,
        width: int,
        height: int,
        scan_type: str = 'p'
    ) -> Optional[str]:
        """Match frame class by width and height dimensions.

        Uses a multi-step matching algorithm:
        1. Try width-based matching with typical widths
        2. Fall back to effective height calculation
        3. Try exact height match
        4. Find closest standard height
        5. Return custom frame class if no match

        Args:
            width: Video width in pixels
            height: Video height in pixels
            scan_type: 'p' for progressive, 'i' for interlaced

        Returns:
            Frame class string (e.g., "1080p") or None if invalid input

        Example:
            >>> matcher = FrameClassMatcher()
            >>> matcher.match_by_dimensions(1920, 1080, 'p')
            '1080p'
            >>> matcher.match_by_dimensions(1280, 720, 'p')
            '720p'
        """
        if not width or not height:
            return None

        # Calculate effective height for aspect ratio consideration
        aspect_ratio = 16 / 9
        if height > width:
            # Portrait mode - unlikely for video but handle it
            effective_height = height / aspect_ratio
        else:
            effective_height = height

        # Step 1: Try to match width to typical widths
        width_match = self._match_by_width_and_aspect(
            width, height, scan_type
        )
        if width_match:
            return width_match

        # Step 2: Try exact match with standard frame classes
        frame_class = f"{int(round(effective_height))}{scan_type}"
        if frame_class in FRAME_CLASSES:
            return frame_class

        # Step 3: Find closest standard height match
        closest_match = self._match_by_closest_height(
            effective_height, scan_type
        )
        if closest_match:
            return closest_match

        # Step 4: Return custom frame class for non-standard resolutions
        return frame_class

    def match_by_height(self, height: int) -> Optional[str]:
        """Get frame class from video height only.

        Tries exact match first, then finds closest match within tolerance.

        Args:
            height: Video height in pixels

        Returns:
            Frame class string or None if no match within tolerance

        Example:
            >>> matcher = FrameClassMatcher()
            >>> matcher.match_by_height(1080)
            '1080p'
            >>> matcher.match_by_height(1078)  # Close to 1080
            '1080p'
        """
        if not height:
            return None

        # Try exact match first
        for frame_class, info in FRAME_CLASSES.items():
            if height == info['nominal_height']:
                return frame_class

        # Find closest match
        closest = None
        min_diff = float('inf')

        for frame_class, info in FRAME_CLASSES.items():
            diff = abs(height - info['nominal_height'])
            if diff < min_diff:
                min_diff = diff
                closest = frame_class

        # Only return if difference is within tolerance
        if min_diff <= self.HEIGHT_TOLERANCE_LARGE:
            return closest

        return None

    def _match_by_width_and_aspect(
        self,
        width: int,
        height: int,
        scan_type: str
    ) -> Optional[str]:
        """Match frame class by width and aspect ratio.

        Args:
            width: Video width in pixels
            height: Video height in pixels
            scan_type: 'p' or 'i'

        Returns:
            Frame class string or None if no match
        """
        width_matches = []

        for frame_class, info in FRAME_CLASSES.items():
            # Only consider frame classes with matching scan type
            if not frame_class.endswith(scan_type):
                continue

            # Check if width matches any typical width for this frame class
            for typical_width in info['typical_widths']:
                if abs(width - typical_width) <= self.WIDTH_TOLERANCE:
                    # Calculate height difference for this match
                    height_diff = abs(height - info['nominal_height'])
                    width_matches.append((frame_class, height_diff))

        if width_matches:
            # Choose the frame class with smallest height difference
            width_matches.sort(key=lambda x: x[1])
            return width_matches[0][0]

        return None

    def _match_by_closest_height(
        self,
        height: float,
        scan_type: str
    ) -> Optional[str]:
        """Find closest standard frame class by height.

        Args:
            height: Effective video height in pixels (can be float)
            scan_type: 'p' or 'i'

        Returns:
            Frame class string or None if no match within tolerance
        """
        closest_class = None
        min_diff = float('inf')

        for frame_class, info in FRAME_CLASSES.items():
            # Only consider frame classes with matching scan type
            if not frame_class.endswith(scan_type):
                continue

            diff = abs(height - info['nominal_height'])
            if diff < min_diff:
                min_diff = diff
                closest_class = frame_class

        # Only return if within tolerance
        if closest_class and min_diff <= self.HEIGHT_TOLERANCE_SMALL:
            return closest_class

        return None

    def get_nominal_height(self, frame_class: str) -> Optional[int]:
        """Get the nominal height for a frame class.

        Args:
            frame_class: Frame class string (e.g., "1080p")

        Returns:
            Nominal height in pixels or None if not found

        Example:
            >>> matcher = FrameClassMatcher()
            >>> matcher.get_nominal_height("1080p")
            1080
        """
        if frame_class in FRAME_CLASSES:
            return FRAME_CLASSES[frame_class]['nominal_height']
        return None

    def get_typical_widths(self, frame_class: str) -> list[int]:
        """Get typical widths for a frame class.

        Args:
            frame_class: Frame class string (e.g., "1080p")

        Returns:
            List of typical widths in pixels

        Example:
            >>> matcher = FrameClassMatcher()
            >>> matcher.get_typical_widths("1080p")
            [1920, 1440, 1280]
        """
        if frame_class in FRAME_CLASSES:
            return FRAME_CLASSES[frame_class]['typical_widths']
        return []

    def is_standard_resolution(self, width: int, height: int) -> bool:
        """Check if dimensions match a standard resolution.

        Args:
            width: Video width in pixels
            height: Video height in pixels

        Returns:
            True if dimensions are close to a standard resolution

        Example:
            >>> matcher = FrameClassMatcher()
            >>> matcher.is_standard_resolution(1920, 1080)
            True
            >>> matcher.is_standard_resolution(1234, 567)
            False
        """
        # Try to match with either scan type
        match_p = self.match_by_dimensions(width, height, 'p')
        match_i = self.match_by_dimensions(width, height, 'i')

        # If we got a match that exists in FRAME_CLASSES, it's standard
        if match_p and match_p in FRAME_CLASSES:
            return True
        if match_i and match_i in FRAME_CLASSES:
            return True

        return False

    def detect_scan_type(self, interlaced: Optional[str]) -> str:
        """Detect scan type from interlaced flag.

        Args:
            interlaced: Interlaced flag (e.g., "Yes", "No", None)

        Returns:
            'i' for interlaced, 'p' for progressive

        Example:
            >>> matcher = FrameClassMatcher()
            >>> matcher.detect_scan_type("Yes")
            'i'
            >>> matcher.detect_scan_type("No")
            'p'
        """
        if interlaced and str(interlaced).lower() in ['yes', 'true', '1']:
            return 'i'
        return 'p'

    def calculate_aspect_ratio(self, width: int, height: int) -> Optional[float]:
        """Calculate aspect ratio from dimensions.

        Args:
            width: Video width in pixels
            height: Video height in pixels

        Returns:
            Aspect ratio as float (e.g., 1.777 for 16:9) or None if invalid

        Example:
            >>> matcher = FrameClassMatcher()
            >>> ratio = matcher.calculate_aspect_ratio(1920, 1080)
            >>> round(ratio, 2)
            1.78
        """
        if not width or not height or height == 0:
            return None
        return width / height

    def format_aspect_ratio(self, ratio: float) -> str:
        """Format aspect ratio as a string.

        Args:
            ratio: Aspect ratio as float

        Returns:
            Formatted string (e.g., "16:9", "21:9")

        Example:
            >>> matcher = FrameClassMatcher()
            >>> matcher.format_aspect_ratio(1.777)
            '16:9'
            >>> matcher.format_aspect_ratio(2.35)
            '21:9'
        """
        # Common aspect ratios
        common_ratios = {
            1.33: "4:3",
            1.78: "16:9",
            1.85: "1.85:1",
            2.35: "21:9",
            2.39: "2.39:1",
        }

        # Find closest match
        closest = min(common_ratios.keys(), key=lambda x: abs(x - ratio))
        if abs(closest - ratio) < 0.05:  # Within 5% tolerance
            return common_ratios[closest]

        # Return as decimal if no match
        return f"{ratio:.2f}:1"
