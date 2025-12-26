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

            if height == 4320:
                return '4320p'
            elif height >= 2160:
                return '2160p'
            elif height >= 1440:
                return '1440p'
            elif height >= 1080:
                return '1080p'
            elif height >= 720:
                return '720p'
            elif height >= 576:
                return '576p'
            elif height >= 480:
                return '480p'
            else:
                return 'Unclassified'
        except (ValueError, IndexError):
            return 'Unclassified'

    @staticmethod
    def format_resolution_p(height: int) -> str:
        """Format resolution as 2160p, 1080p, etc."""
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

    @staticmethod
    def format_resolution_dimensions(resolution: tuple[int, int]) -> str:
        """Format resolution as WIDTHxHEIGHT"""
        width, height = resolution
        return f"{width}x{height}"