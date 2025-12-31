# AI Agent Instructions for Media File Renamer Project

## Project Description

This is a Python Terminal User Interface (TUI) application for managing media files. It uses the Textual library to provide a curses-like interface in the terminal. The app allows users to scan directories for video files, display them in a hierarchical tree view, view detailed metadata information including video, audio, and subtitle tracks, and rename files based on intelligent metadata extraction.

**Current Version**: 0.7.0-dev (Phase 1 complete)

Key features:
- Recursive directory scanning with tree navigation
- Dual-mode display: Technical (codec/track details) and Catalog (TMDB metadata with posters)
- Tree-based file navigation with expand/collapse functionality
- Multi-source metadata extraction (MediaInfo, filename parsing, embedded tags, TMDB API)
- Intelligent file renaming with proposed names and confirmation
- Settings management with persistent configuration
- **NEW**: Unified cache subsystem with flexible strategies and decorators
- **NEW**: Command palette (Ctrl+P) with cache management commands
- **NEW**: Thread-safe cache with RLock protection
- **NEW**: Comprehensive logging (warning/debug levels)
- **NEW**: Proper exception handling (no bare except clauses)
- Terminal poster display using rich-pixels
- Color-coded information display
- Keyboard and mouse navigation
- Multiple UI screens (main app, directory selection, help, rename confirmation, settings)
- Extensible extractor and formatter architecture
- Loading indicators and comprehensive error handling

## Technology Stack

- Python 3.11+
- Textual ≥6.11.0 (TUI framework)
- PyMediaInfo ≥6.0.0 (detailed track information)
- Mutagen ≥1.47.0 (embedded metadata)
- Python-Magic ≥0.4.27 (MIME type detection)
- Langcodes ≥3.5.1 (language code handling)
- Requests ≥2.31.0 (HTTP client for TMDB API)
- Rich-Pixels ≥1.0.0 (terminal image display)
- Pytest ≥7.0.0 (testing framework)
- UV (package manager and build tool)

## Code Structure

- `renamer/main.py`: Main application entry point with argument parsing
- `pyproject.toml`: Project configuration and dependencies (version 0.5.10)
- `README.md`: User documentation
- `DEVELOP.md`: Developer guide with debugging info
- `INSTALL.md`: Installation instructions
- `CLAUDE.md`: Comprehensive AI assistant reference guide
- `ToDo.md`: Development task tracking
- `AI_AGENT.md`: This file (AI agent instructions)
- `renamer/`: Main package
  - `app.py`: Main Textual application class with tree management, file operations, and command palette
  - `settings.py`: Settings management with JSON storage
  - `cache/`: **NEW** Unified cache subsystem (v0.7.0)
    - `core.py`: Thread-safe Cache class
    - `strategies.py`: Cache key generation strategies
    - `managers.py`: CacheManager for operations
    - `decorators.py`: Enhanced cache decorators
    - `types.py`: Type definitions
  - `secrets.py`: API keys and secrets (TMDB)
  - `constants.py`: Application constants (media types, sources, resolutions, special editions)
  - `screens.py`: Additional UI screens (OpenScreen, HelpScreen, RenameConfirmScreen, SettingsScreen)
  - `bump.py`: Version bump utility
  - `release.py`: Release automation script
  - `extractors/`: Individual extractor classes
    - `extractor.py`: MediaExtractor class coordinating all extractors
    - `mediainfo_extractor.py`: PyMediaInfo-based extraction
    - `filename_extractor.py`: Filename parsing with regex patterns
    - `metadata_extractor.py`: Mutagen-based embedded metadata
    - `fileinfo_extractor.py`: Basic file information
    - `tmdb_extractor.py`: The Movie Database API integration
    - `default_extractor.py`: Fallback extractor
  - `formatters/`: Data formatting classes
    - `formatter.py`: Base formatter interface
    - `media_formatter.py`: Main formatter coordinating display
    - `catalog_formatter.py`: Catalog mode formatting with TMDB data
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
  - `decorators/`: Utility decorators
    - `caching.py`: Caching decorator for automatic method caching
  - `test/`: Unit tests for extractors
    - `test_filename_extractor.py`: Filename parsing tests
    - `test_mediainfo_extractor.py`: MediaInfo extraction tests
    - `test_mediainfo_frame_class.py`: Frame class detection tests
    - `test_fileinfo_extractor.py`: File info tests
    - `test_metadata_extractor.py`: Metadata extraction tests
    - `test_filename_detection.py`: Filename pattern detection tests
    - `filenames.txt`, `test_filenames.txt`: Sample test data
    - `test_cases.json`, `test_mediainfo_frame_class.json`: Test fixtures

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

### Completed Major Features

- ✅ Settings management with JSON configuration
- ✅ Mode toggle (technical/catalog)
- ✅ Caching system with TTL support
- ✅ TMDB integration for catalog data
- ✅ Poster display in terminal
- ✅ Settings UI screen

### Future Enhancements

- Metadata editing capabilities
- Batch rename operations
- Plugin system for custom extractors/formatters
- Advanced search and filtering
- Undo/redo functionality
- Blue highlighting for changed parts in proposed filename
- Exclude dev commands from distributed package
- Full genre name expansion (currently shows codes)
- Optimized poster quality and display

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

## Important Files for AI Assistants

For comprehensive project information, AI assistants should refer to:
1. **CLAUDE.md**: Complete AI assistant reference guide (most comprehensive)
2. **AI_AGENT.md**: This file (concise instructions)
3. **DEVELOP.md**: Developer setup and debugging
4. **ToDo.md**: Current task list and completed items
5. **README.md**: User-facing documentation

This document should be updated as the project evolves.

---
**Last Updated**: 2025-12-31