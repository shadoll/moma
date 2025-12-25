class ResolutionFormatter:
    """Class for formatting video resolutions"""
    
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
    def format_resolution_dimensions(width: int, height: int) -> str:
        """Format resolution as WIDTHxHEIGHT"""
        return f"{width}x{height}"