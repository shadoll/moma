# moma - Media Manager, File Renamer and Metadata Viewer

**Version**: 0.7.0-dev

A powerful Terminal User Interface (TUI) for managing media collections. View detailed metadata, browse TMDB catalog with posters, and intelligently rename files.

> **📘 For complete documentation, see [ENGINEERING_GUIDE.md](ENGINEERING_GUIDE.md)**

---

## Features

- **Dual Display Modes**: Technical (codecs/tracks) or Catalog (TMDB with posters)
- **Multi-Source Metadata**: MediaInfo, filename parsing, embedded tags, TMDB API
- **Intelligent Renaming**: Standardized names from metadata
- **Advanced Caching**: 6h extractors, 6h TMDB, 30d posters
- **Terminal Posters**: View movie posters in your terminal
- **Tree View Navigation**: Keyboard and mouse support

---

## Quick Start

### Installation

```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Renamer
cd /path/to/renamer
uv sync
uv tool install .
```

See [INSTALL.md](INSTALL.md) for detailed installation instructions.

### Usage

```bash
# Scan current directory
renamer

# Scan specific directory
renamer /path/to/media
```

---

## Keyboard Commands

| Key | Action |
|-----|--------|
| `q` | Quit |
| `o` | Open directory |
| `s` | Scan/rescan |
| `f` | Refresh metadata |
| `r` | Rename file |
| `m` | Toggle mode (technical/catalog) |
| `p` | Toggle tree expansion |
| `h` | Show help |
| `Ctrl+S` | Settings |
| `Ctrl+P` | Command palette |

---

## Display Modes

### Technical Mode
- Video tracks (codec, bitrate, resolution, frame rate)
- Audio tracks (codec, channels, sample rate, language)
- Subtitle tracks (format, language)
- File information (size, modification time, path)

### Catalog Mode
- TMDB title, year, rating
- Overview/description
- Genres
- Poster image (if terminal supports)
- Technical metadata

Toggle with `m` key.

---

## File Renaming

**Proposed Format**: `Title (Year) [Resolution Source Edition].ext`

**Example**: `The Matrix (1999) [1080p BluRay].mkv`

1. Press `r` on selected file
2. Review proposed name
3. Confirm with `y` or cancel with `n`

---

## Configuration

**Location**: `~/.config/renamer/config.json`

```json
{
  "mode": "technical",
  "cache_ttl_extractors": 21600,
  "cache_ttl_tmdb": 21600,
  "cache_ttl_posters": 2592000
}
```

Access via `Ctrl+S` or edit file directly.

---

## Requirements

- **Python**: 3.11+
- **UV**: Package manager
- **MediaInfo**: System library (for technical metadata)
- **Internet**: For TMDB catalog mode

---

## Project Structure

```
renamer/
├── app.py                  # Main TUI application
├── services/               # Business logic
├── extractors/             # Metadata extraction
├── formatters/             # Display formatting
├── utils/                  # Shared utilities
├── cache/                  # Caching subsystem
└── constants/              # Configuration constants
```

See [ENGINEERING_GUIDE.md](ENGINEERING_GUIDE.md) for complete architecture documentation.

---

## Development

```bash
# Setup
uv sync --extra dev

# Run tests
uv run pytest

# Run from source
uv run renamer [directory]
```

See [DEVELOP.md](DEVELOP.md) for development documentation.

---

## Documentation

- **[ENGINEERING_GUIDE.md](ENGINEERING_GUIDE.md)** - Complete technical reference
- **[INSTALL.md](INSTALL.md)** - Installation instructions
- **[DEVELOP.md](DEVELOP.md)** - Development guide
- **[CHANGELOG.md](CHANGELOG.md)** - Version history
- **[CLAUDE.md](CLAUDE.md)** - AI assistant reference

---

## License

Not specified

---

## Credits

- Built with [Textual](https://textual.textualize.io/)
- Metadata from [MediaInfo](https://mediaarea.net/en/MediaInfo)
- Catalog data from [TMDB](https://www.themoviedb.org/)

---

**For complete documentation, see [ENGINEERING_GUIDE.md](ENGINEERING_GUIDE.md)**
