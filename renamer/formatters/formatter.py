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
    """Class to apply multiple formatters in correct order"""

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
        ResolutionFormatter.get_frame_class_from_resolution,
        ResolutionFormatter.format_resolution_p,
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
        """Apply multiple formatters to value in the global order"""
        if not isinstance(formatters, list):
            formatters = [formatters] if formatters else []
        
        # Sort formatters according to the global order
        ordered_formatters = sorted(formatters, key=lambda f: FormatterApplier.FORMATTER_ORDER.index(f) if f in FormatterApplier.FORMATTER_ORDER else len(FormatterApplier.FORMATTER_ORDER))
        
        # Get caller info
        frame = inspect.currentframe()
        if frame and frame.f_back:
            caller = f"{frame.f_back.f_code.co_filename}:{frame.f_back.f_lineno} in {frame.f_back.f_code.co_name}"
        else:
            caller = "Unknown"
        
        logging.info(f"Caller: {caller}")
        logging.info(f"Original formatters: {[f.__name__ if hasattr(f, '__name__') else str(f) for f in formatters]}")
        logging.info(f"Ordered formatters: {[f.__name__ if hasattr(f, '__name__') else str(f) for f in ordered_formatters]}")
        logging.info(f"Input value: {repr(value)}")
        
        # Apply in the ordered sequence
        for formatter in ordered_formatters:
            try:
                old_value = value
                value = formatter(value)
                logging.debug(f"Applied {formatter.__name__ if hasattr(formatter, '__name__') else str(formatter)}: {repr(old_value)} -> {repr(value)}")
            except Exception as e:
                logging.error(f"Error applying {formatter.__name__ if hasattr(formatter, '__name__') else str(formatter)}: {e}")
                value = "Unknown"
        
        logging.info(f"Final value: {repr(value)}")
        return value
        
    @staticmethod
    def format_data_item(item: dict) -> str | None:
        """Apply all formatting to a data item and return the formatted string"""
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