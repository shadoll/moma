from renamer.constants import FRAME_CLASSES

class ResolutionFormatter:
    """Class for formatting video resolutions and frame classes"""

    @staticmethod
    def get_frame_class_from_resolution(resolution: str) -> str:
        """Convert resolution string (WIDTHxHEIGHT) to frame class (480p, 720p, etc.)"""
        if not resolution:
            return 'Unclassified'

        try:
            # Extract height from WIDTHxHEIGHT format
            if 'x' in resolution:
                height = int(resolution.split('x')[1])
            else:
                # Try to extract number directly
                import re
                match = re.search(r'(\d{3,4})', resolution)
                if match:
                    height = int(match.group(1))
                else:
                    return 'Unclassified'

            # Find the closest frame class based on nominal height
            closest_class = 'Unclassified'
            min_diff = float('inf')
            for frame_class, info in FRAME_CLASSES.items():
                nominal_height = info['nominal_height']
                diff = abs(height - nominal_height)
                if diff < min_diff:
                    min_diff = diff
                    closest_class = frame_class

            return closest_class
        except (ValueError, IndexError):
            return 'Unclassified'

    @staticmethod
    def format_resolution_dimensions(resolution: tuple[int, int]) -> str:
        """Format resolution as WIDTHxHEIGHT"""
        width, height = resolution
        return f"{width}x{height}"