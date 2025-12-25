from datetime import datetime


class DateFormatter:
    """Class for formatting dates"""
    
    @staticmethod
    def format_modification_date(mtime: float) -> str:
        """Format file modification time"""
        return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")