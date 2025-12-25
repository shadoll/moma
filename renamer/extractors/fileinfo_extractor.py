from pathlib import Path


class FileInfoExtractor:
    """Class to extract file information"""

    @staticmethod
    def extract_size(file_path: Path) -> int:
        """Extract file size in bytes"""
        return file_path.stat().st_size

    @staticmethod
    def extract_modification_time(file_path: Path) -> float:
        """Extract file modification time"""
        return file_path.stat().st_mtime

    @staticmethod
    def extract_file_name(file_path: Path) -> str:
        """Extract file name"""
        return file_path.name

    @staticmethod
    def extract_file_path(file_path: Path) -> str:
        """Extract full file path as string"""
        return str(file_path)