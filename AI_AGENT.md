# AI Agent Instructions for Media File Renamer Project

## Project Description

This is a Python Terminal User Interface (TUI) application for managing media files. It uses the Textual library to provide a curses-like interface in the terminal. The app allows users to scan directories for video files, display them in a hierarchical tree view, and view detailed metadata information including video, audio, and subtitle tracks.

Key features:
- Recursive directory scanning
- Tree-based file navigation
- Detailed metadata extraction and display
- Color-coded information
- Keyboard and mouse navigation
- Extensible for future renaming and editing features

## Technology Stack

- Python 3.11+
- Textual (TUI framework)
- Mutagen (audio/video metadata)
- PyMediaInfo (detailed track information)
- Python-Magic (MIME type detection)
- UV (package manager)

## Code Structure

- `main.py`: Main application code
- `pyproject.toml`: Project configuration and dependencies
- `README.md`: User documentation
- `todo.txt`: Development task list
- `AI_AGENT.md`: This file

## Instructions for AI Agents

### Coding Standards

- Use type hints where possible
- Follow PEP 8 style guidelines
- Use descriptive variable and function names
- Add docstrings for functions and classes
- Handle exceptions appropriately
- Use pathlib for file operations

### Development Workflow

1. Read the current code and understand the structure
2. Check the TODO list for pending tasks
3. Implement features incrementally
4. Test changes by running the app with `uv run python main.py [directory]`
5. Update TODO list as tasks are completed
6. Ensure backward compatibility

### Key Components

- `RenamerApp`: Main application class inheriting from Textual's App
- `MediaTree`: Custom Tree widget with file-specific styling
- `get_media_tracks`: Function to extract media track information
- Various helper functions for formatting and detection

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

### Contribution Guidelines

- Make small, focused changes
- Update documentation as needed
- Ensure the app runs without errors
- Follow the existing code patterns

This document should be updated as the project evolves.