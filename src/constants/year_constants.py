"""Year validation constants for filename parsing.

This module contains constants used for validating years extracted from filenames.
"""

import datetime

# Current year for validation
CURRENT_YEAR = datetime.datetime.now().year

# Minimum valid year for movies/media (start of cinema era)
MIN_VALID_YEAR = 1900

# Allow years slightly into the future (for upcoming releases)
YEAR_FUTURE_BUFFER = 10

# Valid year range: MIN_VALID_YEAR to (CURRENT_YEAR + YEAR_FUTURE_BUFFER)
def is_valid_year(year: int) -> bool:
    """Check if a year is within the valid range for media files."""
    return MIN_VALID_YEAR <= year <= CURRENT_YEAR + YEAR_FUTURE_BUFFER
