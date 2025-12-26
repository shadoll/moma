from .text_formatter import TextFormatter
from .date_formatter import DateFormatter
from .special_info_formatter import SpecialInfoFormatter


class ProposedNameFormatter:
    """Class for formatting proposed filenames"""

    def __init__(self, extractor):
        """Initialize with media extractor data"""

        self.__order = f"[{extractor.get('order')}] " if extractor.get("order") else ""
        self.__title = extractor.get("title") or "Unknown Title"
        self.__year = DateFormatter.format_year(extractor.get("year"))
        self.__source = f" {extractor.get('source')}" if extractor.get("source") else ""
        self.__frame_class = extractor.get("frame_class") or None
        self.__hdr = f",{extractor.get('hdr')}" if extractor.get("hdr") else ""
        self.__audio_langs = extractor.get("audio_langs") or None
        # self.__special_info = f" [{SpecialInfoFormatter.format_special_info(extractor.get('special_info'))}]" if extractor.get("special_info") else ""
        self.__special_info = f" \[{SpecialInfoFormatter.format_special_info(extractor.get('special_info'))}]" if extractor.get("special_info") else ""
        self.__extension = extractor.get("extension") or "ext"

    def __str__(self) -> str:
        """Convert the proposed name to string"""
        return self.rename_line()

    def rename_line(self) -> str:
        return f"{self.__order}{self.__title} {self.__year}{self.__special_info}{self.__source} [{self.__frame_class}{self.__hdr},{self.__audio_langs}].{self.__extension}"

    def rename_line_formatted(self, file_path) -> str:
        """Format the proposed name for display with color"""
        if file_path.name == str(self):
            return f">> {TextFormatter.green(str(self))} <<"
        return f">> {TextFormatter.bold_yellow(str(self))} <<"
