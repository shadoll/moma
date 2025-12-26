# Renamer - Media File Renamer and Metadata Editor

A terminal-based (TUI) application for scanning directories, viewing media file details, and managing file metadata. Built with Python and Textual.

## Features

- Recursive directory scanning for video files
- Tree view navigation with keyboard and mouse support
- Detailed metadata extraction from multiple sources (MediaInfo, filename parsing, embedded metadata)
- Color-coded information display
- Command-based interface with hotkeys
- Extensible extractor and formatter system
- Support for video, audio, and subtitle track information

## Installation

### Prerequisites
- Python 3.11+
- UV package manager

### Install UV (if not already installed)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Install the Application
```bash
# Clone or download the project
cd /path/to/renamer

# Install dependencies and build
uv sync

# Install as a global tool
uv tool install .
```

## Usage

### Running the App
```bash
# Scan current directory
renamer

# Scan specific directory
renamer /path/to/media/directory
```

### Commands
- **q**: Quit the application
- **o**: Open directory selection dialog
- **s**: Rescan current directory

### Navigation
- Use arrow keys to navigate the file tree
- Mouse clicks supported
- Select a video file to view its details in the right panel

## Architecture

The application uses a modular architecture with separate extractors and formatters:

### Extractors
- **MediaInfoExtractor**: Extracts detailed track information using PyMediaInfo
- **FilenameExtractor**: Parses metadata from filenames
- **MetadataExtractor**: Extracts embedded metadata using Mutagen
- **FileInfoExtractor**: Provides basic file information

### Formatters
- **MediaFormatter**: Formats extracted data for display
- **TrackFormatter**: Formats video/audio/subtitle track information
- **SizeFormatter**: Formats file sizes
- **DateFormatter**: Formats timestamps
- **DurationFormatter**: Formats time durations
- **ResolutionFormatter**: Formats video resolutions

### Setup Development Environment
```bash
# Install in development mode
uv sync

# Run directly (development)
uv run python main.py

# Or run installed version
renamer
```

### Running Without Rebuilding (Development)
```bash
# Run directly from source (no installation needed)
uv run python main.py

# Or run with specific directory
uv run python main.py /path/to/directory
```

### Uninstall
```bash
uv tool uninstall renamer
```

## Supported Video Formats
- .mkv
- .avi
- .mov
- .mp4
- .wmv
- .flv
- .webm
- .m4v
- .3gp
- .ogv

## Dependencies
- textual: TUI framework
- pymediainfo: Detailed media track information
- mutagen: Embedded metadata extraction
- python-magic: MIME type detection
