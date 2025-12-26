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

- `main.py`: Main application entry point with argument parsing
- `pyproject.toml`: Project configuration and dependencies (version 0.2.0)
- `README.md`: User documentation
- `ToDo.md`: Development task tracking
- `AI_AGENT.md`: This file
- `renamer/`: Main package
  - `app.py`: Main Textual application class with tree management and file operations
  - `extractor.py`: MediaExtractor class coordinating multiple extractors
  - `extractors/`: Individual extractor classes
    - `mediainfo_extractor.py`: PyMediaInfo-based extraction
    - `filename_extractor.py`: Filename parsing
    - `metadata_extractor.py`: Mutagen-based metadata
    - `fileinfo_extractor.py`: Basic file information
  - `formatters/`: Data formatting classes
    - `media_formatter.py`: Main formatter coordinating display
    - `proposed_name_formatter.py`: Generates rename suggestions
    - `track_formatter.py`: Track information formatting
    - `size_formatter.py`: File size formatting
    - `date_formatter.py`: Timestamp formatting
    - `duration_formatter.py`: Duration formatting
    - `resolution_formatter.py`: Resolution formatting
    - `text_formatter.py`: Text styling utilities
    - `extension_formatter.py`: File extension formatting
    - `helper_formatter.py`: Helper formatting utilities
    - `special_info_formatter.py`: Special edition information
  - `constants.py`: Application constants (supported media types)
  - `screens.py`: Additional UI screens (OpenScreen, HelpScreen, RenameConfirmScreen)
  - `test/`: Unit tests for extractors

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
2. Check the ToDo.md for pending tasks
3. Implement features incrementally
4. Test changes by running the app with `uv run python main.py [directory]`
5. Update tests as needed
6. Ensure backward compatibility
7. Update documentation (README.md, ToDo.md) when adding features

### Key Components

- `RenamerApp`: Main application class inheriting from Textual's App
  - Manages the tree view and file operations
  - Handles keyboard navigation and commands
  - Coordinates metadata extraction and display
  - Implements efficient tree updates for renamed files
- `MediaTree`: Custom Tree widget with file-specific styling (inherited from Textual Tree)
- `MediaExtractor`: Coordinates multiple specialized extractors
- `MediaFormatter`: Formats extracted data for TUI display
- Various extractor classes for different data sources
- Various formatter classes for different data types
- Screen classes for different UI states

### Extractor Architecture

Extractors are responsible for gathering raw data from different sources:
- Each extractor inherits from no base class but follows the pattern of `__init__(file_path)` and `extract_*()` methods
- The `MediaExtractor` class coordinates multiple extractors and provides a unified `get()` interface
- Extractors return raw data (strings, numbers, dicts) without formatting

### Formatter Architecture

Formatters are responsible for converting raw data into display strings:
- Each formatter provides static methods like `format_*()`
- The `MediaFormatter` coordinates formatters and applies them based on data types
- `ProposedNameFormatter` generates intelligent rename suggestions
- Formatters handle text styling, color coding, and human-readable representations

### Screen Architecture

The app uses multiple screens for different operations:
- `OpenScreen`: Directory selection with input validation
- `HelpScreen`: Comprehensive help with key bindings
- `RenameConfirmScreen`: File rename confirmation with error handling

### Future Enhancements

- Metadata editing capabilities
- Batch rename operations
- Configuration file support
- Plugin system for custom extractors/formatters
- Advanced search and filtering
- Undo/redo functionality

### Testing

- Run the app with `uv run python main.py [directory]`
- Test navigation, selection, and display
- Verify metadata extraction accuracy
- Test file renaming functionality
- Check for any errors or edge cases
- Run unit tests with `uv run pytest`

### Contribution Guidelines

- Make small, focused changes
- Update documentation as needed
- Ensure the app runs without errors
- Follow the existing code patterns
- Update tests for new functionality
- Update ToDo.md when completing tasks
- Update version numbers appropriately

This document should be updated as the project evolves.