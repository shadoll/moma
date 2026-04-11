"""Duration formatting utilities"""

import math


class DurationFormatter:
    """Class to format duration values"""

    @staticmethod
    def format_seconds(duration: float | None) -> str:
        """Format duration as seconds: '1234 seconds'"""
        if duration is None:
            return "Unknown"
        return f"{int(duration)} seconds"

    @staticmethod
    def format_hhmmss(duration: float | None) -> str:
        """Format duration as HH:MM:SS"""
        if duration is None:
            return "Unknown"
        total_seconds = int(duration)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    @staticmethod
    def format_hhmm(duration: float | None) -> str:
        """Format duration as HH:MM (rounded)"""
        if duration is None:
            return "Unknown"
        total_seconds = int(duration)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours:02d}:{minutes:02d}"

    @staticmethod
    def format_full(duration: float | None) -> str:
        """Format duration as HH:MM:SS (1234 sec)"""
        if duration is None:
            return "Unknown"
        total_seconds = int(duration)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d} ({total_seconds} sec)"