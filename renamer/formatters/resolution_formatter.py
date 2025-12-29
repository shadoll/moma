class ResolutionFormatter:
    """Class for formatting video resolutions and frame classes"""

    @staticmethod
    def format_resolution_dimensions(resolution: tuple[int, int]) -> str:
        """Format resolution as WIDTHxHEIGHT"""
        width, height = resolution
        return f"{width}x{height}"