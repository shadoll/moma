from rich.markup import escape
from ..formatters.special_info_decorators import special_info_decorators
from ..formatters.conditional_decorators import conditional_decorators
from ..formatters.text_decorators import text_decorators


class ProposedFilenameView:
    """View for generating proposed filenames using decorator pattern with properties.

    This view composes formatter decorators to generate clean, standardized filenames
    from extracted metadata. It uses property decorators for declarative formatting.
    """

    def __init__(self, extractor):
        """Initialize with media extractor data"""
        self._extractor = extractor

    def __str__(self) -> str:
        """Convert the proposed name to string"""
        return self.rename_line

    @property
    @conditional_decorators.wrap("[", "] ")
    def _order(self) -> str:
        """Get the order number formatted as [XX] """
        return self._extractor.get("order")

    @property
    @conditional_decorators.replace_slashes()
    def _title(self) -> str:
        """Get the title with slashes replaced"""
        return self._extractor.get("title")

    @property
    @conditional_decorators.wrap(" (", ")")
    def _year(self) -> str:
        """Get the year formatted as (YYYY)"""
        return self._extractor.get("year")

    @property
    @conditional_decorators.wrap(" ")
    def _source(self) -> str:
        """Get the source"""
        return self._extractor.get("source")

    @property
    def _frame_class(self) -> str:
        """Get the frame class"""
        return self._extractor.get("frame_class") or ""

    @property
    @conditional_decorators.wrap(",")
    def _hdr(self) -> str:
        """Get the HDR info formatted with a trailing comma if present"""
        return self._extractor.get("hdr")

    @property
    def _audio_langs(self) -> str:
        """Get the audio languages formatted with a trailing comma if present"""
        return self._extractor.get("audio_langs") or ""

    @property
    @conditional_decorators.wrap(" [", "]")
    @special_info_decorators.special_info()
    def _special_info(self) -> str:
        """Get the special info formatted within brackets"""
        return self._extractor.get("special_info")

    @property
    @conditional_decorators.wrap(" [", "]")
    @special_info_decorators.database_info()
    def _db_info(self) -> str:
        """Get the database info formatted within brackets"""
        return self._extractor.get("movie_db")

    @property
    def _extension(self) -> str:
        """Get the file extension"""
        return self._extractor.get("extension")

    @property
    def rename_line(self) -> str:
        """Generate the proposed filename."""
        result = f"{self._order}{self._title}{self._year}{self._special_info}{self._source} [{self._frame_class}{self._hdr},{self._audio_langs}]{self._db_info}.{self._extension}"
        return result.replace("/", "-").replace("\\", "-")

    def rename_line_formatted(self, file_path) -> str:
        """Format the proposed name for display with color"""
        if file_path.name == str(self):
            return self.rename_line_similar
        return self.rename_line_different

    @property
    @conditional_decorators.wrap(">> ", " <<")
    @text_decorators.colour(name="green")
    def rename_line_similar(self) -> str:
        """Generate a simplified proposed filename for similarity checks."""
        return escape(str(self))

    @property
    @conditional_decorators.wrap(left=">> ", right=" <<")
    @text_decorators.colour(name="orange")
    def rename_line_different(self) -> str:
        """Generate a detailed proposed filename for difference checks."""
        return escape(str(self))
