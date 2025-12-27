# Renamer - Media File Renamer and Metadata Editor

A terminal-based (TUI) application for scanning directories, viewing media file details, and renaming files based on extracted metadata. Built with Python and Textual.

## Features

- Recursive directory scanning for video files
- Tree view navigation with keyboard and mouse support
- Detailed metadata extraction from multiple sources (MediaInfo, filename parsing, embedded metadata)
- Intelligent file renaming with proposed names based on metadata
- Color-coded information display
- Command-based interface with hotkeys
- Extensible extractor and formatter system
- Support for video, audio, and subtitle track information
- Confirmation dialogs for file operations

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
- **f**: Refresh metadata for selected file
- **r**: Rename selected file with proposed name
- **p**: Toggle tree expansion (expand/collapse all)
- **h**: Show help screen

### Navigation
- Use arrow keys to navigate the file tree
- Right arrow: Expand directory
- Left arrow: Collapse directory or go to parent
- Mouse clicks supported
- Select a video file to view its details in the right panel

### File Renaming
1. Select a media file in the tree
2. Press **r** to initiate rename
3. Review the proposed new name
4. Press **y** to confirm or **n** to cancel
5. The file will be renamed and the tree updated automatically

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
- textual: TUI framework
- pymediainfo: Detailed media track information
- mutagen: Embedded metadata extraction
- python-magic: MIME type detection
- langcodes: Language code handling
