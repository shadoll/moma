"""Formatter coordinator and application system.

This module provides the FormatterApplier class which coordinates the application
of multiple formatters in the correct order (data → text → markup). It ensures
formatters are applied sequentially based on their type.
"""

from .text_formatter import TextFormatter
from .duration_formatter import DurationFormatter
from .size_formatter import SizeFormatter
from .date_formatter import DateFormatter
from .extension_formatter import ExtensionFormatter
from .resolution_formatter import ResolutionFormatter
from .track_formatter import TrackFormatter
from .special_info_formatter import SpecialInfoFormatter
import logging
import inspect
import os


# Set up logging conditionally
if os.getenv('FORMATTER_LOG', '0') == '1':
    logging.basicConfig(filename='formatter.log', level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
else:
    logging.basicConfig(level=logging.CRITICAL)  # Disable logging


class FormatterApplier:
    """Coordinator for applying multiple formatters in the correct order.

    This class manages the application of formatters to data values, ensuring they
    are applied in the proper sequence:
    1. Data formatters (transform raw data: size, duration, etc.)
    2. Text formatters (transform text: uppercase, lowercase, etc.)
    3. Markup formatters (add visual styling: bold, colors, etc.)

    The ordering prevents conflicts and ensures consistent output formatting.

    Example:
        >>> from renamer.formatters.formatter import FormatterApplier
        >>> from renamer.formatters.size_formatter import SizeFormatter
        >>> from renamer.formatters.text_formatter import TextFormatter
        >>> value = 1073741824
        >>> formatters = [SizeFormatter.format_size, TextFormatter.bold]
        >>> result = FormatterApplier.apply_formatters(value, formatters)
        >>> # Result: bold("1.00 GB")
    """

    # Define the global order of all formatters
    FORMATTER_ORDER = [
        # Data formatters first (transform raw data)
        DurationFormatter.format_seconds,
        DurationFormatter.format_hhmmss,
        DurationFormatter.format_hhmm,
        DurationFormatter.format_full,
        SizeFormatter.format_size,
        SizeFormatter.format_size_full,
        DateFormatter.format_modification_date,
        DateFormatter.format_year,
        ExtensionFormatter.format_extension_info,
        ResolutionFormatter.format_resolution_dimensions,
        TrackFormatter.format_video_track,
        TrackFormatter.format_audio_track,
        TrackFormatter.format_subtitle_track,
        SpecialInfoFormatter.format_special_info,
        SpecialInfoFormatter.format_database_info,
        
        # Text formatters second (transform text content)
        TextFormatter.uppercase,
        TextFormatter.lowercase,
        TextFormatter.camelcase,
        
        # Markup formatters last (add visual styling)
        TextFormatter.bold,
        TextFormatter.italic,
        TextFormatter.underline,
        TextFormatter.bold_green,
        TextFormatter.bold_cyan,
        TextFormatter.bold_magenta,
        TextFormatter.bold_yellow,
        TextFormatter.green,
        TextFormatter.yellow,
        TextFormatter.magenta,
        TextFormatter.cyan,
        TextFormatter.red,
        TextFormatter.blue,
        TextFormatter.grey,
        TextFormatter.dim,
        TextFormatter.format_url,
    ]

    @staticmethod
    def apply_formatters(value, formatters):
        """Apply multiple formatters to a value in the correct global order.

        Formatters are automatically sorted based on FORMATTER_ORDER to ensure
        proper sequencing (data → text → markup). If a formatter fails, the
        value is set to "Unknown" and processing continues.

        Args:
            value: The value to format (can be any type)
            formatters: Single formatter or list of formatter functions

        Returns:
            The formatted value after all formatters have been applied

        Example:
            >>> formatters = [SizeFormatter.format_size, TextFormatter.bold]
            >>> result = FormatterApplier.apply_formatters(1024, formatters)
        """
        if not isinstance(formatters, list):
            formatters = [formatters] if formatters else []

        # Sort formatters according to the global order
        ordered_formatters = sorted(formatters, key=lambda f: FormatterApplier.FORMATTER_ORDER.index(f) if f in FormatterApplier.FORMATTER_ORDER else len(FormatterApplier.FORMATTER_ORDER))

        # Apply in the ordered sequence
        for formatter in ordered_formatters:
            try:
                old_value = value
                value = formatter(value)
                logging.debug(f"Applied {formatter.__name__ if hasattr(formatter, '__name__') else str(formatter)}: {repr(old_value)} -> {repr(value)}")
            except Exception as e:
                logging.error(f"Error applying {formatter.__name__ if hasattr(formatter, '__name__') else str(formatter)}: {e}")
                value = "Unknown"

        return value

    @staticmethod
    def format_data_item(item: dict) -> str | None:
        """Apply all formatting to a data item and return the formatted string.

        Processes a data item dictionary containing value, label, and formatters,
        applying them in the correct order to produce a formatted display string.

        Args:
            item: Dictionary containing:
                - value: The raw value to format
                - label: Label text for the item
                - value_formatters: List of formatters to apply to the value
                - label_formatters: List of formatters to apply to the label
                - display_formatters: List of formatters for the final display

        Returns:
            Formatted string combining label and value, or None if value is None

        Example:
            >>> item = {
            ...     "value": 1024,
            ...     "label": "Size",
            ...     "value_formatters": [SizeFormatter.format_size],
            ...     "label_formatters": [TextFormatter.bold]
            ... }
            >>> result = FormatterApplier.format_data_item(item)
        """
        # Handle value formatting first (e.g., size formatting)
        value = item.get("value")
        if value is not None and value != "Not extracted":
            value_formatters = item.get("value_formatters", [])
            value = FormatterApplier.apply_formatters(value, value_formatters)

        # Handle label formatting
        label = item.get("label", "")
        if label:
            label_formatters = item.get("label_formatters", [])
            label = FormatterApplier.apply_formatters(label, label_formatters)

        # Create the display string
        if value is not None:
            display_string = f"{label}: {value}"
        else:
            display_string = label

        # Handle display formatting (e.g., color)
        display_formatters = item.get("display_formatters", [])
        display_string = FormatterApplier.apply_formatters(display_string, display_formatters)

        return display_string

    @staticmethod
    def format_data_items(data: list[dict]) -> list:
        """Apply formatting to a list of data items"""
        return [FormatterApplier.format_data_item(item) for item in data]