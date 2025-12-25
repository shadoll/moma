# conftest.py - pytest configuration
import os
import sys

# Force UTF-8 encoding for all I/O operations
os.environ['PYTHONIOENCODING'] = 'utf-8'
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Configure pytest to handle Unicode properly
def pytest_configure(config):
    # Ensure UTF-8 encoding for test output
    config.option.capture = 'no'  # Don't capture output to avoid encoding issues