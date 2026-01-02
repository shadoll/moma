"""Formatters package - provides value formatting for display.

This package contains various formatter classes that transform raw values
into display-ready strings with optional styling.

All formatters should inherit from the Formatter ABC defined in base.py.
"""

from .base import (
    Formatter,
    DataFormatter,
    TextFormatter as TextFormatterBase,
    MarkupFormatter,
    CompositeFormatter
)
from .text_formatter import TextFormatter
from .duration_formatter import DurationFormatter
from .size_formatter import SizeFormatter
from .date_formatter import DateFormatter
from .extension_formatter import ExtensionFormatter
from .resolution_formatter import ResolutionFormatter
from .track_formatter import TrackFormatter
from .special_info_formatter import SpecialInfoFormatter
from .formatter import FormatterApplier

# Decorator instances
from .date_decorators import date_decorators, DateDecorators
from .special_info_decorators import special_info_decorators, SpecialInfoDecorators
from .text_decorators import text_decorators, TextDecorators
from .conditional_decorators import conditional_decorators, ConditionalDecorators

__all__ = [
    # Base classes
    'Formatter',
    'DataFormatter',
    'TextFormatterBase',
    'MarkupFormatter',
    'CompositeFormatter',

    # Concrete formatters
    'TextFormatter',
    'DurationFormatter',
    'SizeFormatter',
    'DateFormatter',
    'ExtensionFormatter',
    'ResolutionFormatter',
    'TrackFormatter',
    'SpecialInfoFormatter',
    'FormatterApplier',

    # Decorator instances and classes
    'date_decorators',
    'DateDecorators',
    'special_info_decorators',
    'SpecialInfoDecorators',
    'text_decorators',
    'TextDecorators',
    'conditional_decorators',
    'ConditionalDecorators',
]