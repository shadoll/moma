from pathlib import Path


class FileInfoExtractor:
    """Class to extract file information"""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self._size = file_path.stat().st_size
        self._modification_time = file_path.stat().st_mtime
        self._file_name = file_path.name
        self._file_path = str(file_path)

    def extract_size(self) -> int:
        """Extract file size in bytes"""
        return self._size

    def extract_modification_time(self) -> float:
        """Extract file modification time"""
        return self._modification_time

    def extract_file_name(self) -> str:
        """Extract file name"""
        return self._file_name

    def extract_file_path(self) -> str:
        """Extract full file path as string"""
        return self._file_path

    def extract_extension(self) -> str:
        """Extract file extension without the dot"""
        return self.file_path.suffix.lower().lstrip('.')