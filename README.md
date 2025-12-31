# Renamer - Media File Renamer and Metadata Viewer

A powerful terminal-based (TUI) application for managing media collections. Scan directories, view detailed metadata, browse TMDB catalog information with posters, and intelligently rename files. Built with Python and Textual.

**Version**: 0.5.10

## Features

### Core Capabilities
- **Dual Display Modes**: Switch between Technical (codec/track details) and Catalog (TMDB metadata with posters)
- **Recursive Directory Scanning**: Finds all video files in nested directories
- **Tree View Navigation**: Keyboard and mouse support with expand/collapse
- **Multi-Source Metadata**: Combines MediaInfo, filename parsing, embedded tags, and TMDB API
- **Intelligent Renaming**: Proposes standardized names based on extracted metadata
- **Persistent Settings**: Configurable mode and cache TTLs saved to `~/.config/renamer/`
- **Advanced Caching**: File-based cache with TTL (6h extractors, 6h TMDB, 30d posters)
- **Terminal Poster Display**: View movie posters in your terminal using rich-pixels
- **Color-Coded Display**: Visual highlighting for different data types
- **Confirmation Dialogs**: Safe file operations with preview and confirmation
- **Extensible Architecture**: Modular extractor and formatter system for easy extension

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

### Keyboard Commands
- **q**: Quit the application
- **o**: Open directory selection dialog
- **s**: Scan/rescan current directory
- **f**: Force refresh metadata for selected file (bypass cache)
- **r**: Rename selected file with proposed name
- **p**: Toggle tree expansion (expand/collapse all)
- **h**: Show help screen
- **^p**: Open command palette (settings, mode toggle)
- **Settings**: Access via action bar (top-right corner)

### Navigation
- Use arrow keys to navigate the file tree
- Right arrow: Expand directory
- Left arrow: Collapse directory or go to parent
- Mouse clicks supported
- Select a video file to view its details in the right panel

### File Renaming
1. Select a media file in the tree
2. Press **r** to initiate rename
3. Review the proposed new name in the confirmation dialog
4. Press **y** to confirm or **n** to cancel
5. The file will be renamed and the tree updated automatically (cache invalidated)

### Display Modes
- **Technical Mode**: Shows codec details, bitrates, track information, resolutions
- **Catalog Mode**: Shows TMDB data including title, year, rating, overview, genres, and poster
- Toggle between modes via Settings menu or command palette (^p)

## Development

For development setup, architecture details, debugging information, and contribution guidelines, see [DEVELOP.md](DEVELOP.md).

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
- **textual** ≥6.11.0: TUI framework
- **pymediainfo** ≥6.0.0: Detailed media track information
- **mutagen** ≥1.47.0: Embedded metadata extraction
- **python-magic** ≥0.4.27: MIME type detection
- **langcodes** ≥3.5.1: Language code handling
- **requests** ≥2.31.0: HTTP client for TMDB API
- **rich-pixels** ≥1.0.0: Terminal image display
- **pytest** ≥7.0.0: Testing framework

### System Requirements
- **Python**: 3.11 or higher
- **MediaInfo Library**: System dependency for pymediainfo
  - Ubuntu/Debian: `sudo apt install libmediainfo-dev`
  - Fedora/CentOS: `sudo dnf install libmediainfo-devel`
  - Arch Linux: `sudo pacman -S libmediainfo`
  - macOS/Windows: Automatically handled by pymediainfo
