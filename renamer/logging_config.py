"""Singleton logging configuration for the renamer application.

This module provides centralized logging configuration that is initialized
once and used throughout the application.
"""

import logging
import os
import threading


class LoggerConfig:
    """Singleton logger configuration."""

    _instance = None
    _lock = threading.Lock()
    _initialized = False

    def __new__(cls):
        """Create or return singleton instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize logging configuration (only once)."""
        if LoggerConfig._initialized:
            return

        # Check environment variable for formatter logging
        if os.getenv('FORMATTER_LOG', '0') == '1':
            logging.basicConfig(
                filename='formatter.log',
                level=logging.DEBUG,
                format='%(asctime)s - %(levelname)s - %(message)s'
            )
        # When FORMATTER_LOG is not '1', do not configure logging at all

        LoggerConfig._initialized = True


# Initialize logging on import
LoggerConfig()
