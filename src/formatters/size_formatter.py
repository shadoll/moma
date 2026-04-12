class SizeFormatter:
    """Class for formatting file sizes"""

    @staticmethod
    def format_size(bytes_size: int) -> str:
        """Format bytes to human readable with unit"""
        size: float = bytes_size
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    @staticmethod
    def format_size_full(bytes_size: int) -> str:
        """Format size with both human readable and bytes"""
        size_formatted = SizeFormatter.format_size(bytes_size)
        return f"{size_formatted} ({bytes_size:,} bytes)"

    @staticmethod
    def format_size_short(bytes_size: int) -> str:
        """Format size with only human readable"""
        return SizeFormatter.format_size(bytes_size)
