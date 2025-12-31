"""Base classes for formatters.

This module defines the Formatter Abstract Base Class (ABC) that all formatters
should inherit from. This ensures a consistent interface and enables type checking.
"""

from abc import ABC, abstractmethod
from typing import Any


class Formatter(ABC):
    """Abstract base class for all formatters.

    All formatter classes should inherit from this base class and implement
    the format() method. Formatters are responsible for transforming raw values
    into display-ready strings.

    The Formatter ABC supports three categories of formatters:
    1. Data formatters: Transform raw data (e.g., bytes to "1.2 GB")
    2. Text formatters: Transform text content (e.g., uppercase, lowercase)
    3. Markup formatters: Add visual styling (e.g., bold, colored text)

    Example:
        class MyFormatter(Formatter):
            @staticmethod
            def format(value: Any) -> str:
                return str(value).upper()

    Note:
        All formatter methods should be static methods to allow
        usage without instantiation and composition in FormatterApplier.
    """

    @staticmethod
    @abstractmethod
    def format(value: Any) -> str:
        """Format a value for display.

        This is the core method that all formatters must implement.
        It takes a raw value and returns a formatted string.

        Args:
            value: The value to format (type depends on formatter)

        Returns:
            The formatted string representation

        Raises:
            ValueError: If the value cannot be formatted
            TypeError: If the value type is incompatible

        Example:
            >>> class SizeFormatter(Formatter):
            ...     @staticmethod
            ...     def format(value: int) -> str:
            ...         return f"{value / 1024:.1f} KB"
            >>> SizeFormatter.format(2048)
            '2.0 KB'
        """
        pass


class DataFormatter(Formatter):
    """Base class for data formatters.

    Data formatters transform raw data values into human-readable formats.
    Examples include:
    - File sizes (bytes to "1.2 GB")
    - Durations (seconds to "1h 23m")
    - Dates (timestamp to "2024-01-15")
    - Resolutions (width/height to "1920x1080")

    Data formatters should be applied first in the formatting pipeline,
    before text transformations and markup.
    """
    pass


class TextFormatter(Formatter):
    """Base class for text formatters.

    Text formatters transform text content without adding markup.
    Examples include:
    - Case transformations (uppercase, lowercase, camelcase)
    - Text replacements
    - String truncation

    Text formatters should be applied after data formatters but before
    markup formatters in the formatting pipeline.
    """
    pass


class MarkupFormatter(Formatter):
    """Base class for markup formatters.

    Markup formatters add visual styling using markup tags.
    Examples include:
    - Color formatting ([red]text[/red])
    - Style formatting ([bold]text[/bold])
    - Link formatting ([link=url]text[/link])

    Markup formatters should be applied last in the formatting pipeline,
    after all data and text transformations are complete.
    """
    pass


class CompositeFormatter(Formatter):
    """Formatter that applies multiple formatters in sequence.

    This class allows chaining multiple formatters together in a specific order.
    Useful for creating complex formatting pipelines.

    Example:
        >>> formatters = [SizeFormatter, BoldFormatter, GreenFormatter]
        >>> composite = CompositeFormatter(formatters)
        >>> composite.format(1024)
        '[bold green]1.0 KB[/bold green]'

    Attributes:
        formatters: List of formatter functions to apply in order
    """

    def __init__(self, formatters: list[callable]):
        """Initialize the composite formatter.

        Args:
            formatters: List of formatter functions to apply in order
        """
        self.formatters = formatters

    def format(self, value: Any) -> str:
        """Apply all formatters in sequence.

        Args:
            value: The value to format

        Returns:
            The result after applying all formatters

        Raises:
            Exception: If any formatter in the chain raises an exception
        """
        result = value
        for formatter in self.formatters:
            result = formatter(result)
        return result
