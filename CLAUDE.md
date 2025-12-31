# CLAUDE.md - AI Assistant Reference Guide

This document provides comprehensive project information for AI assistants (like Claude) working on the Renamer project.

## Project Overview

**Renamer** is a sophisticated Terminal User Interface (TUI) application for managing, viewing metadata, and renaming media files. Built with Python and the Textual framework, it provides an interactive, curses-like interface for media collection management.

### Current Version
- **Version**: 0.7.0-dev (in development)
- **Python**: 3.11+
- **Status**: Major refactoring in progress - Phase 1 complete (critical bugs fixed, unified cache subsystem)

## Project Purpose

Renamer serves two primary use cases:
1. **Technical Mode**: Detailed technical metadata viewing (video tracks, audio streams, codecs, bitrates)
2. **Catalog Mode**: Media library catalog view with TMDB integration (posters, ratings, descriptions, genres)

## Architecture Overview

### Core Components

#### Main Application (`renamer/app.py`)
- Main `RenamerApp` class inheriting from Textual's `App`
- Manages TUI layout with split view: file tree (left) and details panel (right)
- Handles keyboard/mouse navigation and user commands
- Coordinates file operations and metadata extraction
- Implements efficient tree updates for file renaming

#### Entry Point (`renamer/main.py`)
- Argument parsing for directory selection
- Application initialization and launch

#### Constants (`renamer/constants.py`)
Defines comprehensive dictionaries:
- `MEDIA_TYPES`: Supported video formats (mkv, avi, mov, mp4, etc.)
- `SOURCE_DICT`: Video source types (WEB-DL, BDRip, BluRay, etc.)
- `FRAME_CLASSES`: Resolution classifications (480p-8K)
- `MOVIE_DB_DICT`: Database identifiers (TMDB, IMDB, Trakt, TVDB)
- `SPECIAL_EDITIONS`: Edition types (Director's Cut, Extended, etc.)

### Extractor System (`renamer/extractors/`)

Modular architecture for gathering metadata from multiple sources:

#### Core Extractors
1. **MediaInfoExtractor** (`mediainfo_extractor.py`)
   - Uses PyMediaInfo library
   - Extracts detailed track information (video, audio, subtitle)
   - Provides codec, bitrate, frame rate, resolution data

2. **FilenameExtractor** (`filename_extractor.py`)
   - Parses metadata from filename patterns
   - Detects year, resolution, source, codecs, edition info
   - Uses regex patterns to extract structured data

3. **MetadataExtractor** (`metadata_extractor.py`)
   - Reads embedded metadata using Mutagen
   - Extracts tags, container format info

4. **FileInfoExtractor** (`fileinfo_extractor.py`)
   - Basic file information (size, dates, permissions)
   - MIME type detection via python-magic

5. **TMDBExtractor** (`tmdb_extractor.py`)
   - The Movie Database API integration
   - Fetches title, year, ratings, overview, genres, poster
   - Supports movie and TV show data

6. **DefaultExtractor** (`default_extractor.py`)
   - Fallback extractor providing minimal data

#### Extractor Coordinator (`extractor.py`)
- `MediaExtractor` class orchestrates all extractors
- Provides unified `get()` interface for data retrieval
- Caching support via decorators

### Formatter System (`renamer/formatters/`)

Transforms raw extracted data into formatted display strings:

#### Specialized Formatters
1. **MediaFormatter** (`media_formatter.py`)
   - Main formatter coordinating all format operations
   - Mode-aware (technical vs catalog)
   - Applies color coding and styling

2. **CatalogFormatter** (`catalog_formatter.py`)
   - Formats catalog mode display
   - Renders TMDB data, ratings, genres, overview
   - Terminal image display for posters (rich-pixels)

3. **TrackFormatter** (`track_formatter.py`)
   - Video/audio/subtitle track formatting
   - Color-coded track information

4. **ProposedNameFormatter** (`proposed_name_formatter.py`)
   - Generates intelligent rename suggestions
   - Pattern: `Title (Year) [Resolution Source Edition].ext`
   - Sanitizes filenames (removes invalid characters)

5. **Utility Formatters**
   - `SizeFormatter`: Human-readable file sizes
   - `DateFormatter`: Timestamp formatting
   - `DurationFormatter`: Duration in HH:MM:SS
   - `ResolutionFormatter`: Resolution display
   - `TextFormatter`: Text styling utilities
   - `ExtensionFormatter`: File extension handling
   - `SpecialInfoFormatter`: Edition/source formatting
   - `HelperFormatter`: General formatting helpers

### Settings & Caching

#### Settings System (`renamer/settings.py`)
- JSON configuration stored in `~/.config/renamer/config.json`
- Configurable options:
  - `mode`: "technical" or "catalog"
  - `cache_ttl_extractors`: 21600s (6 hours)
  - `cache_ttl_tmdb`: 21600s (6 hours)
  - `cache_ttl_posters`: 2592000s (30 days)
- Automatic save/load with defaults

#### Cache System (`renamer/cache.py`)
- File-based cache with TTL support
- Location: `~/.cache/renamer/`
- Subdirectory organization (tmdb/, posters/, extractors/, general/)
- Supports JSON and pickle serialization
- In-memory cache for performance
- Image caching for TMDB posters
- Automatic expiration and cleanup

#### Unified Cache Subsystem (`renamer/cache/`)

**NEW in v0.7.0**: Complete cache subsystem rewrite with modular architecture.

**Directory Structure**:
```
renamer/cache/
├── __init__.py          # Module exports and convenience functions
├── core.py              # Core Cache class (thread-safe with RLock)
├── types.py             # Type definitions (CacheEntry, CacheStats)
├── strategies.py        # Cache key generation strategies
├── managers.py          # CacheManager for operations
└── decorators.py        # Enhanced cache decorators
```

**Cache Key Strategies**:
- `FilepathMethodStrategy`: For extractor methods (`extractor_{hash}_{method}`)
- `APIRequestStrategy`: For API responses (`api_{service}_{hash}`)
- `SimpleKeyStrategy`: For simple prefix+id patterns
- `CustomStrategy`: User-defined key generation

**Cache Decorators**:
- `@cached(strategy, ttl)`: Generic caching with configurable strategy
- `@cached_method(ttl)`: Method caching (backward compatible)
- `@cached_api(service, ttl)`: API response caching
- `@cached_property(ttl)`: Cached property decorator

**Cache Manager Operations**:
- `clear_all()`: Remove all cache entries
- `clear_by_prefix(prefix)`: Clear specific cache type (tmdb_, extractor_, poster_)
- `clear_expired()`: Remove expired entries
- `get_stats()`: Comprehensive statistics
- `clear_file_cache(file_path)`: Clear cache for specific file
- `compact_cache()`: Remove empty directories

**Command Palette Integration**:
- Access cache commands via Ctrl+P
- 7 commands: View Stats, Clear All, Clear Extractors, Clear TMDB, Clear Posters, Clear Expired, Compact
- Integrated using `CacheCommandProvider`

**Thread Safety**:
- All operations protected by `threading.RLock`
- Safe for concurrent extractor access

### Error Handling & Logging

**Exception Handling** (v0.7.0):
- No bare `except:` clauses (all use specific exception types)
- Language code conversions catch `(LookupError, ValueError, AttributeError)`
- Network errors catch `(requests.RequestException, ValueError)`
- All exceptions logged with context

**Logging Strategy**:
- **Warning level**: Network failures, API errors, MediaInfo parse failures (user-facing issues)
- **Debug level**: Language code conversions, metadata reads, MIME detection (technical details)
- **Error level**: Formatter application failures (logged via `FormatterApplier`)

**Logger Usage**:
```python
import logging
logger = logging.getLogger(__name__)

# Examples
logger.warning(f"TMDB API request failed for {url}: {e}")
logger.debug(f"Invalid language code '{lang_code}': {e}")
logger.error(f"Error applying {formatter.__name__}: {e}")
```

**Files with Logging**:
- `renamer/extractors/filename_extractor.py` - Language code conversion errors
- `renamer/extractors/mediainfo_extractor.py` - MediaInfo parse and language errors
- `renamer/extractors/metadata_extractor.py` - Mutagen and MIME detection errors
- `renamer/extractors/tmdb_extractor.py` - API request and poster download errors
- `renamer/formatters/formatter.py` - Formatter application errors
- `renamer/cache/core.py` - Cache operation errors

### UI Screens (`renamer/screens.py`)

Additional UI screens for user interaction:

1. **OpenScreen**: Directory selection dialog with validation
2. **HelpScreen**: Comprehensive help with key bindings
3. **RenameConfirmScreen**: File rename confirmation with error handling
4. **SettingsScreen**: Settings configuration interface

### Development Tools

#### Version Management (`renamer/bump.py`)
- `bump-version` command
- Auto-increments patch version in `pyproject.toml`

#### Release Automation (`renamer/release.py`)
- `release` command
- Runs: version bump → dependency sync → package build

## Key Features

### Current Features (v0.5.10)
- Recursive directory scanning for video files
- Tree view with expand/collapse navigation
- Dual-mode display (technical/catalog)
- Detailed metadata extraction from multiple sources
- Intelligent file renaming with preview
- TMDB integration with poster display
- Settings configuration UI
- Persistent caching with TTL
- Loading indicators and error handling
- Confirmation dialogs for file operations
- Color-coded information display
- Keyboard and mouse navigation

### Keyboard Commands
- `q`: Quit application
- `o`: Open directory
- `s`: Scan/rescan directory
- `f`: Refresh metadata for selected file
- `r`: Rename file with proposed name
- `p`: Toggle tree expansion
- `m`: Toggle mode (technical/catalog)
- `h`: Show help screen
- `ctrl+s`: Open settings
- `ctrl+p`: Open command palette

### Command Palette (v0.7.0)
**Access**: Press `ctrl+p` to open the command palette

**Available Commands**:
- **System Commands** (built-in from Textual):
  - Toggle theme
  - Show key bindings
  - Other system operations

- **Cache Commands** (from `CacheCommandProvider`):
  - Cache: View Statistics
  - Cache: Clear All
  - Cache: Clear Extractors
  - Cache: Clear TMDB
  - Cache: Clear Posters
  - Cache: Clear Expired
  - Cache: Compact

**Implementation**:
- Command palette extends built-in Textual commands
- Uses `COMMANDS = App.COMMANDS | {CacheCommandProvider}` pattern
- Future: Will add app operation commands (open, scan, rename, etc.)

## Technology Stack

### Core Dependencies
- **textual** (≥6.11.0): TUI framework
- **pymediainfo** (≥6.0.0): Media track analysis
- **mutagen** (≥1.47.0): Embedded metadata
- **python-magic** (≥0.4.27): MIME detection
- **langcodes** (≥3.5.1): Language code handling
- **requests** (≥2.31.0): HTTP for TMDB API
- **rich-pixels** (≥1.0.0): Terminal image display
- **pytest** (≥7.0.0): Testing framework

### System Requirements
- Python 3.11 or higher
- UV package manager (recommended)
- MediaInfo library (system dependency for pymediainfo)

## Development Workflow

### Setup
```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and sync
cd /path/to/renamer
uv sync

# Run from source
uv run python renamer/main.py [directory]
```

### Development Commands
```bash
uv run renamer              # Run installed version
uv run pytest               # Run tests
uv run bump-version         # Increment version
uv run release              # Build release (bump + sync + build)
uv build                    # Build wheel/tarball
uv tool install .           # Install as global tool
```

### Debugging
```bash
# Enable formatter logging
FORMATTER_LOG=1 uv run renamer /path/to/directory
# Creates formatter.log with detailed call traces
```

### Testing
- Test files in `renamer/test/`
- Sample filenames in `test/filenames.txt` and `test/test_filenames.txt`
- Test cases in `test/test_cases.json`
- Run with: `uv run pytest`

## Code Style & Standards

### Python Standards
- Type hints encouraged
- PEP 8 style guidelines
- Descriptive variable/function names
- Docstrings for classes and functions
- Pathlib for file operations
- Proper exception handling

### Architecture Patterns
- Extractor pattern: Each extractor focuses on one data source
- Formatter pattern: Formatters handle display logic, extractors handle data
- Separation of concerns: Data extraction → formatting → display
- Dependency injection: Extractors and formatters are modular
- Configuration management: Settings class for all config

### Best Practices
- Avoid over-engineering (keep solutions simple)
- Only add features when explicitly requested
- Validate at system boundaries only (user input, external APIs)
- Don't add unnecessary error handling for internal code
- Trust framework guarantees
- Delete unused code completely (no backwards-compat hacks)

## File Operations

### Directory Scanning
- Recursive search for supported video formats
- File tree representation with hierarchical structure
- Efficient tree updates on file operations

### File Renaming
1. Select file in tree
2. Press `r` to initiate rename
3. Review proposed name (shows current vs proposed)
4. Confirm with `y` or cancel with `n`
5. Tree updates in-place without full reload

### Metadata Caching
- First extraction cached for 6 hours
- TMDB data cached for 6 hours
- Posters cached for 30 days
- Force refresh with `f` command
- Cache invalidated on file rename

## API Integration

### TMDB API
- API key stored in `renamer/secrets.py`
- Search endpoint for movie lookup by title/year
- Image base URL for poster downloads
- Handles rate limiting and errors gracefully
- Falls back to filename data if API unavailable

## Project Files

### Documentation
- `README.md`: User-facing documentation
- `AI_AGENT.md`: AI agent instructions (legacy)
- `DEVELOP.md`: Developer guide
- `INSTALL.md`: Installation instructions
- `ToDo.md`: Task tracking
- `CLAUDE.md`: This file (AI assistant reference)

### Configuration
- `pyproject.toml`: Project metadata, dependencies, build config
- `uv.lock`: Locked dependencies

### Build Artifacts
- `dist/`: Built wheels and tarballs
- `build/`: Build intermediates
- `renamer.egg-info/`: Package metadata

## Known Issues & Limitations

### Current Limitations
- TMDB API requires internet connection
- Poster display requires terminal with image support
- Some special characters in filenames need sanitization
- Large directories may have initial scan delay

### Future Enhancements (See ToDo.md)
- Metadata editing capabilities
- Batch rename operations
- Advanced search and filtering
- Undo/redo functionality
- Plugin system for custom extractors/formatters
- Full genre name expansion (currently shows codes)
- Improved poster quality/display optimization

## Contributing Guidelines

### Making Changes
1. Read existing code and understand architecture
2. Check `ToDo.md` for pending tasks
3. Implement features incrementally
4. Test with real media files
5. Ensure backward compatibility
6. Update documentation
7. Update tests as needed
8. Run `uv run release` before committing

### Commit Standards
- Clear, descriptive commit messages
- Focus on "why" not "what"
- One logical change per commit
- Reference related issues/tasks

### Code Review Checklist
- [ ] Follows PEP 8 style
- [ ] Type hints added where appropriate
- [ ] No unnecessary complexity
- [ ] Tests pass (`uv run pytest`)
- [ ] Documentation updated
- [ ] No security vulnerabilities (XSS, injection, etc.)
- [ ] Efficient resource usage (no memory leaks)

## Security Considerations

- Input sanitization for filenames (see `ProposedNameFormatter`)
- No shell command injection risks
- Safe file operations (pathlib, proper error handling)
- TMDB API key should not be committed (stored in `secrets.py`)
- Cache directory permissions should be user-only

## Performance Notes

- In-memory cache reduces repeated extraction overhead
- File cache persists across sessions
- Tree updates optimized for rename operations
- TMDB requests throttled to respect API limits
- Large directory scans use async/await patterns

## Special Notes for AI Assistants

### When Adding Features
1. **Always read relevant files first** - Never modify code you haven't read
2. **Check ToDo.md** - See if feature is already planned
3. **Understand existing patterns** - Follow established architecture
4. **Test with real files** - Use actual media files for testing
5. **Update documentation** - Keep docs in sync with code

### When Debugging
1. **Enable formatter logging** - Use `FORMATTER_LOG=1` for detailed traces
2. **Check cache state** - Clear cache if stale data suspected
3. **Verify file permissions** - Ensure read/write access
4. **Test with sample filenames** - Use test fixtures first

### When Refactoring
1. **Maintain backward compatibility** - Unless explicitly breaking change
2. **Update tests** - Reflect refactored code
3. **Check all formatters** - Formatting is centralized
4. **Verify extractor chain** - Ensure data flow intact

### Common Pitfalls to Avoid
- Don't create new files unless absolutely necessary (edit existing)
- Don't add features beyond what's requested
- Don't over-engineer solutions
- Don't skip testing with real files
- Don't forget to update version number for releases
- Don't commit secrets or API keys
- Don't use deprecated Textual APIs

## Project History

### Evolution
- Started as simple file renamer
- Added metadata extraction (MediaInfo, Mutagen)
- Expanded to TUI with Textual framework
- Added filename parsing intelligence
- Integrated TMDB for catalog mode
- Added settings and caching system
- Implemented poster display with rich-pixels
- Added dual-mode interface (technical/catalog)

### Version Milestones
- 0.2.x: Initial TUI with basic metadata
- 0.3.x: Enhanced extractors and formatters
- 0.4.x: Added TMDB integration
- 0.5.x: Settings, caching, catalog mode, poster display

## Resources

### External Documentation
- [Textual Documentation](https://textual.textualize.io/)
- [PyMediaInfo Documentation](https://pymediainfo.readthedocs.io/)
- [Mutagen Documentation](https://mutagen.readthedocs.io/)
- [TMDB API Documentation](https://developers.themoviedb.org/3)
- [UV Documentation](https://docs.astral.sh/uv/)

### Internal Documentation
- Main README: User guide and quick start
- DEVELOP.md: Developer setup and debugging
- INSTALL.md: Installation methods
- AI_AGENT.md: Legacy AI instructions (historical)
- ToDo.md: Current task list

---

**Last Updated**: 2025-12-31
**For AI Assistant**: Claude (Anthropic)
**Project Maintainer**: sha
**Repository**: `/home/sha/bin/renamer`
