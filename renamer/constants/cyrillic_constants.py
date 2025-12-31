"""Cyrillic character normalization constants.

This module contains mappings for normalizing Cyrillic characters to their
English equivalents for parsing filenames.
"""

# Cyrillic to English character mappings
# Used for normalizing Cyrillic characters that look like English letters
CYRILLIC_TO_ENGLISH = {
    'р': 'p',  # Cyrillic 'er' looks like Latin 'p'
    'і': 'i',  # Cyrillic 'i' looks like Latin 'i'
    'о': 'o',  # Cyrillic 'o' looks like Latin 'o'
    'с': 'c',  # Cyrillic 'es' looks like Latin 'c'
    'е': 'e',  # Cyrillic 'ie' looks like Latin 'e'
    'а': 'a',  # Cyrillic 'a' looks like Latin 'a'
    'т': 't',  # Cyrillic 'te' looks like Latin 't'
    'у': 'y',  # Cyrillic 'u' looks like Latin 'y'
    'к': 'k',  # Cyrillic 'ka' looks like Latin 'k'
    'х': 'x',  # Cyrillic 'ha' looks like Latin 'x
    # Add more mappings as needed
}
