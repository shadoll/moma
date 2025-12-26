# AI Agent Instructions for Media File Renamer Project

## Project Description

This is a Python Terminal User Interface (TUI) application for managing media files. It uses the Textual library to provide a curses-like interface in the terminal. The app allows users to scan directories for video files, display them in a hierarchical tree view, view detailed metadata information including video, audio, and subtitle tracks, and rename files based on intelligent metadata extraction.

Key features:
- Recursive directory scanning
- Tree-based file navigation with expand/collapse functionality
- Detailed metadata extraction from multiple sources
- Intelligent file renaming with proposed names
- Color-coded information display
- Keyboard and mouse navigation
- Multiple UI screens (main app, directory selection, help, rename confirmation)
- Extensible extractor and formatter architecture
- Loading indicators and error handling

## Technology Stack

- Python 3.11+
- Textual (TUI framework)
- PyMediaInfo (detailed track information)
- Mutagen (embedded metadata)
- Python-Magic (MIME type detection)
- Langcodes (language code handling)
- UV (package manager)

## Code Structure

- `main.py`: Main application entry point
- `pyproject.toml`: Project configuration and dependencies
- `README.md`: User documentation
- `AI_AGENT.md`: This file
- `renamer/`: Main package
  - `app.py`: Main Textual application class
  - `extractor.py`: MediaExtractor class coordinating multiple extractors
  - `extractors/`: Individual extractor classes
    - `mediainfo_extractor.py`: PyMediaInfo-based extraction
    - `filename_extractor.py`: Filename parsing
    - `metadata_extractor.py`: Mutagen-based metadata
    - `fileinfo_extractor.py`: Basic file information
  - `formatters/`: Data formatting classes
    - `media_formatter.py`: Main formatter coordinating display
    - `track_formatter.py`: Track information formatting
    - `size_formatter.py`: File size formatting
    - `date_formatter.py`: Timestamp formatting
    - `duration_formatter.py`: Duration formatting
    - `resolution_formatter.py`: Resolution formatting
    - `text_formatter.py`: Text styling utilities
  - `constants.py`: Application constants
  - `screens.py`: Additional UI screens
  - `test/`: Unit tests

## Instructions for AI Agents

### Coding Standards

- Use type hints where possible
- Follow PEP 8 style guidelines
- Use descriptive variable and function names
- Add docstrings for functions and classes
- Handle exceptions appropriately
- Use pathlib for file operations

### Development Workflow

1. Read the current code and understand the architecture
2. Check the TODO list for pending tasks
3. Implement features incrementally
4. Test changes by running the app with `uv run python main.py [directory]`
5. Update tests as needed
6. Ensure backward compatibility

### Key Components

- `RenamerApp`: Main application class inheriting from Textual's App
- `MediaTree`: Custom Tree widget with file-specific styling
- `MediaExtractor`: Coordinates multiple specialized extractors
- `MediaFormatter`: Formats extracted data for TUI display
- Various extractor classes for different data sources
- Various formatter classes for different data types

### Extractor Architecture

Extractors are responsible for gathering raw data from different sources:
- Each extractor inherits from no base class but follows the pattern of `__init__(file_path)` and `extract_*()` methods
- The `MediaExtractor` class coordinates multiple extractors and provides a unified `get()` interface
- Extractors return raw data (strings, numbers, dicts) without formatting

### Formatter Architecture

Formatters are responsible for converting raw data into display strings:
- Each formatter provides static methods like `format_*()`
- The `MediaFormatter` coordinates formatters and applies them based on data types
- Formatters handle text styling, color coding, and human-readable representations

### Future Enhancements

- File renaming functionality
- Batch operations
- Advanced metadata editing
- Plugin system for different media types

### Testing

- Run the app with `uv run python main.py [directory]`
- Test navigation, selection, and display
- Verify metadata extraction accuracy
- Check for any errors or edge cases
- Run unit tests with `uv run pytest`

### Contribution Guidelines

- Make small, focused changes
- Update documentation as needed
- Ensure the app runs without errors
- Follow the existing code patterns
- Update tests for new functionality

This document should be updated as the project evolves.