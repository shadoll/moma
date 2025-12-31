# Developer Guide

This guide contains information for developers working on the Renamer project.

**Current Version**: 0.5.10

## Development Setup

### Prerequisites
- Python 3.11+
- UV package manager

### Install UV (if not already installed)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Development Installation
```bash
# Clone the repository
git clone <repository-url>
cd renamer

# Install in development mode with all dependencies
uv sync

# Install the package in editable mode
uv pip install -e .
```

### Running in Development
```bash
# Run directly from source
uv run python renamer/main.py

# Or run with specific directory
uv run python renamer/main.py /path/to/directory

# Or use the installed command
uv run renamer
```

## Development Commands

The project includes several development commands defined in `pyproject.toml`:

### bump-version
Increments the patch version in `pyproject.toml` (e.g., 0.2.6 → 0.2.7).
```bash
uv run bump-version
```

### release
Runs a batch process: bump version, sync dependencies, and build the package.
```bash
uv run release
```

### Other Commands
- `uv sync`: Install/update dependencies
- `uv build`: Build the package
- `uv run pytest`: Run tests

## Debugging

### Formatter Logging
Enable detailed logging for formatter operations:
```bash
FORMATTER_LOG=1 uv run renamer /path/to/directory
```

This creates `formatter.log` in the current directory with:
- Formatter call sequences and ordering
- Input/output values for each formatter
- Caller information (file and line number)
- Any errors during formatting
- Timestamp for each operation

### Cache Inspection
Cache is stored in `~/.cache/renamer/` with subdirectories:
- `extractors/`: Extractor results cache
- `tmdb/`: TMDB API response cache
- `posters/`: Downloaded poster images
- `general/`: General purpose cache

To clear cache:
```bash
rm -rf ~/.cache/renamer/
```

### Settings Location
Settings are stored in `~/.config/renamer/config.json`:
```json
{
  "mode": "technical",
  "cache_ttl_extractors": 21600,
  "cache_ttl_tmdb": 21600,
  "cache_ttl_posters": 2592000
}
```

## Architecture

The application uses a modular architecture with clear separation of concerns:

### Core Application (`renamer/`)
- **app.py**: Main RenamerApp class (Textual App), tree management, file operations
- **main.py**: Entry point with argument parsing
- **constants.py**: Comprehensive constants (media types, sources, resolutions, editions)
- **settings.py**: Settings management with JSON persistence (`~/.config/renamer/`)
- **cache.py**: File-based caching system with TTL support (`~/.cache/renamer/`)
- **secrets.py**: API keys and secrets (TMDB)

### Extractors (`renamer/extractors/`)
Data extraction from multiple sources:
- **extractor.py**: MediaExtractor coordinator class
- **mediainfo_extractor.py**: PyMediaInfo for detailed track information
- **filename_extractor.py**: Regex-based filename parsing
- **metadata_extractor.py**: Mutagen for embedded metadata
- **fileinfo_extractor.py**: Basic file information (size, dates, MIME)
- **tmdb_extractor.py**: The Movie Database API integration
- **default_extractor.py**: Fallback extractor

### Formatters (`renamer/formatters/`)
Display formatting and rendering:
- **formatter.py**: Base formatter interface
- **media_formatter.py**: Main formatter coordinating all format operations
- **catalog_formatter.py**: Catalog mode display (TMDB data, posters)
- **proposed_name_formatter.py**: Intelligent rename suggestions
- **track_formatter.py**: Video/audio/subtitle track formatting
- **size_formatter.py**: Human-readable file sizes
- **date_formatter.py**: Timestamp formatting
- **duration_formatter.py**: Duration in HH:MM:SS format
- **resolution_formatter.py**: Resolution display
- **extension_formatter.py**: File extension handling
- **special_info_formatter.py**: Edition/source formatting
- **text_formatter.py**: Text styling utilities
- **helper_formatter.py**: General formatting helpers

### Screens (`renamer/screens.py`)
UI screens for user interaction:
- **OpenScreen**: Directory selection with validation
- **HelpScreen**: Comprehensive help with key bindings
- **RenameConfirmScreen**: File rename confirmation with preview
- **SettingsScreen**: Settings configuration UI

### Utilities
- **decorators/caching.py**: Caching decorator for automatic method caching
- **bump.py**: Version bump utility script
- **release.py**: Release automation (bump + sync + build)

## Testing

Run tests with:
```bash
uv run pytest
```

Test files are located in `renamer/test/` with sample filenames in `filenames.txt`.

## Building and Distribution

### Build the Package
```bash
uv build
```

### Install as Tool
```bash
uv tool install .
```

### Uninstall
```bash
uv tool uninstall renamer
```

## Code Style

The project follows Python best practices:
- **PEP 8**: Standard Python style guide
- **Type Hints**: Encouraged where appropriate
- **Docstrings**: For all classes and public methods
- **Descriptive Naming**: Clear variable and function names
- **Pathlib**: For all file operations
- **Error Handling**: Appropriate exception handling at boundaries

Consider using tools like:
- `ruff` for linting and formatting
- `mypy` for type checking
- `black` for consistent formatting

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `uv run pytest`
5. Run the release process: `uv run release`
6. Submit a pull request

## Additional Documentation

For comprehensive project information:
- **[README.md](README.md)**: User guide and features
- **[CLAUDE.md](CLAUDE.md)**: Complete AI assistant reference
- **[AI_AGENT.md](AI_AGENT.md)**: AI agent instructions
- **[INSTALL.md](INSTALL.md)**: Installation methods
- **[ToDo.md](ToDo.md)**: Task list and priorities

## Project Resources

- **Cache Directory**: `~/.cache/renamer/`
- **Config Directory**: `~/.config/renamer/`
- **Test Files**: `renamer/test/`
- **Build Output**: `dist/` and `build/`

---

**Last Updated**: 2025-12-31