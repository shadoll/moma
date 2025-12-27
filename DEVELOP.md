# Developer Guide

This guide contains information for developers working on the Renamer project.

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

This creates `formatter.log` with:
- Formatter call sequences and ordering
- Input/output values for each formatter
- Caller information (file and line number)
- Any errors during formatting

## Architecture

The application uses a modular architecture:

### Extractors (`renamer/extractors/`)
- **MediaInfoExtractor**: Extracts detailed track information using PyMediaInfo
- **FilenameExtractor**: Parses metadata from filenames
- **MetadataExtractor**: Extracts embedded metadata using Mutagen
- **FileInfoExtractor**: Provides basic file information
- **DefaultExtractor**: Fallback extractor
- **MediaExtractor**: Main extractor coordinating all others

### Formatters (`renamer/formatters/`)
- **MediaFormatter**: Formats extracted data for display
- **ProposedNameFormatter**: Generates intelligent rename suggestions
- **TrackFormatter**: Formats video/audio/subtitle track information
- **SizeFormatter**: Formats file sizes
- **DateFormatter**: Formats timestamps
- **DurationFormatter**: Formats time durations
- **ResolutionFormatter**: Formats video resolutions
- **TextFormatter**: Text styling utilities

### Screens (`renamer/screens.py`)
- **OpenScreen**: Directory selection dialog
- **HelpScreen**: Application help and key bindings
- **RenameConfirmScreen**: File rename confirmation dialog

### Main Components
- **app.py**: Main TUI application
- **main.py**: Entry point
- **constants.py**: Application constants

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

The project uses standard Python formatting. Consider using tools like:
- `ruff` for linting and formatting
- `mypy` for type checking (if added)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `uv run pytest`
5. Run the release process: `uv run release`
6. Submit a pull request

For more information, see the main [README.md](../README.md).