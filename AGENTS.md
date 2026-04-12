# moma Engineering Guide

**Version**: 0.8.11
**Last Updated**: 2026-04-11
**Python**: 3.11+
**Status**: Active Development

This is the comprehensive technical reference for the moma project. It contains all architectural information, implementation details, development workflows, and AI assistant instructions.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Core Components](#core-components)
4. [Development Setup](#development-setup)
5. [Testing Strategy](#testing-strategy)
6. [Code Standards](#code-standards)
7. [AI Assistant Instructions](#ai-assistant-instructions)
8. [Release Process](#release-process)

---

## Project Overview

### Purpose

moma is a sophisticated Terminal User Interface (TUI) application for managing, viewing metadata, and renaming media files. Built with Python and the Textual framework.

**Dual-Mode Operation**:
- **Technical Mode**: Detailed technical metadata (video tracks, audio streams, codecs, bitrates)
- **Catalog Mode**: Media library catalog view with TMDB integration (posters, ratings, descriptions)

### Current Version

- **Version**: 0.8.11 (in development)
- **Python**: 3.11+
- **License**: Not specified
- **Repository**: `/Users/sha/Developer/sha.dev/moma`

### Technology Stack

#### Core Dependencies
- **textual** (≥6.11.0): TUI framework
- **pymediainfo** (≥6.0.0): Media track analysis
- **mutagen** (≥1.47.0): Embedded metadata
- **python-magic** (≥0.4.27): MIME detection
- **langcodes** (≥3.5.1): Language code handling
- **requests** (≥2.31.0): HTTP for TMDB API
- **rich-pixels** (≥1.0.0): Terminal image display
- **pytest** (≥7.0.0): Testing framework

#### Dev Dependencies
- **mypy** (≥1.0.0): Type checking

#### System Requirements
- Python 3.11 or higher
- UV package manager (recommended)
- MediaInfo library (system dependency)

---

## Architecture

### Architectural Layers

```
┌─────────────────────────────────────────┐
│         TUI Layer (Textual)             │
│  app.py, views/                         │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         Service Layer                    │
│  FileTreeService, MetadataService,      │
│  RenameService                          │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         Extractor Layer                  │
│  MediaExtractor coordinates:            │
│  - FilenameExtractor                    │
│  - MediaInfoExtractor                   │
│  - MetadataExtractor                    │
│  - FileInfoExtractor                    │
│  - TMDBExtractor                        │
│  - DefaultExtractor                     │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         Formatter Layer                  │
│  FormatterApplier coordinates:         │
│  - DataFormatters (size, duration)      │
│  - TextFormatters (case, style)         │
│  - MarkupFormatters (colors, bold)      │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│      Utility & Cache Layer              │
│  - PatternExtractor                     │
│  - LanguageCodeExtractor                │
│  - FrameClassMatcher                    │
│  - Unified Cache Subsystem              │
└─────────────────────────────────────────┘
```

### Design Patterns

1. **Protocol-Based Architecture**: `DataExtractor` Protocol defines extractor interface
2. **Coordinator Pattern**: `MediaExtractor` coordinates multiple extractors with priority system
3. **Strategy Pattern**: Cache key strategies for different data types
4. **Decorator Pattern**: `@cached_method()` for method-level caching
5. **Service Layer**: Business logic separated from UI
6. **Dependency Injection**: Services receive extractors/formatters as dependencies

---

## Core Components

### 1. Main Application (`src/app.py`)

**Class**: `MomaApp(App)`

**Responsibilities**:
- TUI layout management (split view: file tree + details panel)
- Keyboard/mouse navigation
- Command palette integration (Ctrl+P)
- File operation coordination
- Efficient tree updates

**Key Features**:
- Two command providers: `AppCommandProvider`, `CacheCommandProvider`
- Dual-mode support (technical/catalog)
- Real-time metadata display

### 2. Service Layer (`src/services/`)

#### FileTreeService (`file_tree_service.py`)
- Directory scanning and validation
- Recursive tree building with filtering
- Media file detection (based on `MEDIA_TYPES`)
- Permission error handling
- Tree node searching by path
- Directory statistics

#### MetadataService (`metadata_service.py`)
- **Thread pool management** (ThreadPoolExecutor, configurable workers)
- **Thread-safe operations** with Lock
- Concurrent metadata extraction
- **Active extraction tracking** and cancellation
- Cache integration via decorators
- Synchronous and asynchronous modes
- Formatter coordination
- Error handling with callbacks
- Context manager support

#### RenameService (`rename_service.py`)
- Proposed name generation from metadata
- Filename validation and sanitization
- Invalid character removal (cross-platform)
- Reserved name checking (Windows compatibility)
- File conflict detection
- Atomic rename operations
- Dry-run mode
- Callback-based rename with success/error handlers
- Markup tag stripping

### 3. Extractor System (`src/extractors/`)

#### Base Protocol (`base.py`)
```python
class DataExtractor(Protocol):
    """Defines standard interface for all extractors"""
    def extract_title(self) -> Optional[str]: ...
    def extract_year(self) -> Optional[str]: ...
    # ... 21 methods total
```

#### MediaExtractor (`extractor.py`)
**Coordinator class** managing priority-based extraction:

**Priority Order Examples**:
- Title: TMDB → Metadata → Filename → Default
- Year: Filename → Default
- Technical info: MediaInfo → Default
- File info: FileInfo → Default

**Usage**:
```python
extractor = MediaExtractor(Path("movie.mkv"))
title = extractor.get("title")  # Tries sources in priority order
year = extractor.get("year", source="Filename")  # Force specific source
```

#### Specialized Extractors

1. **FilenameExtractor** (`filename_extractor.py`)
   - Parses metadata from filename patterns
   - Detects year, resolution, source, codecs, edition
   - Uses regex patterns and utility classes
   - Handles Cyrillic normalization
   - Extracts language codes with counts (e.g., "2xUKR_ENG")

2. **MediaInfoExtractor** (`mediainfo_extractor.py`)
   - Uses PyMediaInfo library
   - Extracts detailed track information
   - Provides codec, bitrate, frame rate, resolution
   - Frame class matching with tolerances

3. **MetadataExtractor** (`metadata_extractor.py`)
   - Uses Mutagen library for embedded tags
   - Extracts title, artist, duration
   - Falls back to MIME type detection
   - Handles multiple container formats

4. **FileInfoExtractor** (`fileinfo_extractor.py`)
   - Basic file system information
   - Size, modification time, paths
   - Extension extraction
   - Fast, no external dependencies

5. **TMDBExtractor** (`tmdb_extractor.py`)
   - The Movie Database API integration
   - Fetches title, year, ratings, overview, genres
   - Downloads and caches posters
   - Supports movies and TV shows
   - Rate limiting and error handling

6. **DefaultExtractor** (`default_extractor.py`)
   - Fallback extractor providing default values
   - Returns None or empty collections
   - Safe final fallback in extractor chain

### 4. Formatter System (`src/formatters/`)

#### Base Classes (`base.py`)
- `Formatter`: Base ABC with abstract `format()` method
- `DataFormatter`: For data transformations (sizes, durations, dates)
- `TextFormatter`: For text transformations (case changes)
- `MarkupFormatter`: For visual styling (colors, bold, links)
- `CompositeFormatter`: For chaining multiple formatters

#### FormatterApplier
Formatters are applied via decorator modules (`*_decorators.py`) using the base classes in `base.py`.

**Order**: Data → Text → Markup

**Global Ordering**:
1. Data formatters (size, duration, date, track info)
2. Text formatters (uppercase, lowercase, camelcase)
3. Markup formatters (bold, colors, dim, underline)

#### Specialized Formatters
- **CatalogFormatter** (`catalog_formatter.py`): TMDB data, ratings, genres, poster display
- **TrackFormatter** (`track_formatter.py`): Video/audio/subtitle track formatting with colors
- **SizeFormatter** (`size_formatter.py`): Human-readable file sizes
- **DurationFormatter** (`duration_formatter.py`): Duration in HH:MM:SS
- **DateFormatter** (`date_formatter.py`): Timestamp formatting
- **ResolutionFormatter** (`resolution_formatter.py`): Resolution display
- **ExtensionFormatter** (`extension_formatter.py`): File extension handling
- **SpecialInfoFormatter** (`special_info_formatter.py`): Edition/source formatting
- **TextFormatter** (`text_formatter.py`): Text styling utilities
- **Decorator modules** (`*_decorators.py`): Reusable display decorators per formatter type

### 5. Utility Modules (`src/utils/`)

#### PatternExtractor (`pattern_utils.py`)
**Centralized regex pattern matching**:
- Movie database ID extraction (TMDB, IMDB, Trakt, TVDB)
- Year extraction and validation
- Quality indicator detection
- Source indicator detection
- Bracketed content manipulation
- Position finding for year/quality/source

**Example**:
```python
extractor = PatternExtractor()
db_info = extractor.extract_movie_db_ids("[tmdbid-12345]")
# Returns: {'type': 'tmdb', 'id': '12345'}
```

#### LanguageCodeExtractor (`language_utils.py`)
**Language code processing**:
- Extract from brackets: `[UKR_ENG]` → `['ukr', 'eng']`
- Extract standalone codes from filename
- Handle count patterns: `[2xUKR_ENG]`
- Convert to ISO 639-3 codes
- Skip quality indicators and file extensions
- Format as language counts: `"2ukr,eng"`

**Example**:
```python
extractor = LanguageCodeExtractor()
langs = extractor.extract_from_brackets("[2xUKR_ENG]")
# Returns: ['ukr', 'ukr', 'eng']
```

#### FrameClassMatcher (`frame_utils.py`)
**Resolution/frame class matching**:
- Multi-step matching algorithm
- Height and width tolerance
- Aspect ratio calculation
- Scan type detection (progressive/interlaced)
- Standard resolution checking
- Nominal height/typical widths lookup

**Matching Strategy**:
1. Exact height + width match
2. Height match with aspect ratio validation
3. Closest height match
4. Non-standard quality indicator detection

### 6. Constants (`src/constants/`)

**Modular organization** (8 files):

1. **media_constants.py**: `MEDIA_TYPES` - Supported video formats
2. **source_constants.py**: `SOURCE_DICT` - Video source types
3. **frame_constants.py**: `FRAME_CLASSES`, `NON_STANDARD_QUALITY_INDICATORS`
4. **moviedb_constants.py**: `MOVIE_DB_DICT` - Database identifiers
5. **edition_constants.py**: `SPECIAL_EDITIONS` - Edition types
6. **lang_constants.py**: `SKIP_WORDS` - Words to skip in language detection
7. **year_constants.py**: `is_valid_year()`, dynamic year validation
8. **cyrillic_constants.py**: `CYRILLIC_TO_ENGLISH` - Character mappings

**Backward Compatibility**: All constants exported via `__init__.py`

### 7. Cache Subsystem (`src/cache/`)

**Unified, modular architecture**:

```
src/cache/
├── __init__.py          # Exports and convenience functions
├── core.py              # Core Cache class (thread-safe with RLock)
├── types.py             # CacheEntry, CacheStats TypedDicts
├── strategies.py        # Cache key generation strategies
├── managers.py          # CacheManager for operations
└── decorators.py        # Enhanced cache decorators
```

#### Cache Key Strategies
- `FilepathMethodStrategy`: For extractor methods
- `APIRequestStrategy`: For API responses
- `SimpleKeyStrategy`: For simple prefix+id patterns
- `CustomStrategy`: User-defined key generation

#### Cache Decorators
```python
@cached_method(ttl=3600)  # Method caching
def extract_title(self):
    ...

@cached_api(service="tmdb", ttl=21600)  # API caching
def fetch_movie_data(self, movie_id):
    ...
```

#### Cache Manager Operations
- `clear_all()`: Remove all cache entries
- `clear_by_prefix(prefix)`: Clear specific cache type
- `clear_expired()`: Remove expired entries
- `get_stats()`: Comprehensive statistics
- `clear_file_cache(file_path)`: Clear cache for specific file
- `compact_cache()`: Remove empty directories

#### Command Palette Integration
Access via Ctrl+P:
- Cache: View Statistics
- Cache: Clear All
- Cache: Clear Extractors / TMDB / Posters
- Cache: Clear Expired / Compact

#### Thread Safety
- All operations protected by `threading.RLock`
- Safe for concurrent extractor access
- Memory cache synchronized with file cache

### 8. UI Screens (`src/views/`)

1. **OpenScreen** (`open_screen.py`): Directory selection dialog with validation
2. **HelpScreen** (`help_screen.py`): Comprehensive help with key bindings
3. **RenameConfirmScreen** (`rename_confirm_screen.py`): File rename confirmation with error handling
4. **ConvertConfirmScreen** (`convert_confirm_screen.py`): AVI/MPG/MPEG/MP4/WebM → MKV conversion confirmation
5. **DeleteConfirmScreen** (`delete_confirm_screen.py`): File deletion confirmation
6. **SettingsScreen** (`settings_screen.py`): Settings configuration interface

### 9. Settings System (`src/settings.py`)

**Configuration**: `~/.config/moma/config.json`

**Options**:
```json
{
  "mode": "technical",        // "technical" or "catalog"
  "poster": "no",            // "no", "pseudo" (ASCII art), "viu", "richpixels"
  "hevc_crf": 23,            // HEVC quality: 18=lossless, 23=high, 28=balanced
  "hevc_preset": "fast",    // HEVC speed: ultrafast, veryfast, faster, fast, medium, slow
  "cache_ttl_extractors": 21600,   // 6 hours in seconds
  "cache_ttl_tmdb": 21600,         // 6 hours in seconds
  "cache_ttl_posters": 2592000     // 30 days in seconds
}
```

Automatic save/load with defaults.

---

## Development Setup

### Installation

```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and sync
cd /Users/sha/Developer/sha.dev/moma
uv sync

# Install dev dependencies
uv sync --extra dev

# Run from source
uv run python src/main.py [directory]
```

### Development Commands

```bash
# Run installed version
uv run moma [directory]

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src

# Type checking
uv run mypy src/extractors/default_extractor.py

# Version management
uv run bump-version        # Increment patch version
uv run release             # Bump + sync + build

# Build distribution
uv build                   # Create wheel and tarball

# Install as global tool
uv tool install .
```

### Debugging

```bash
# Enable formatter logging
FORMATTER_LOG=1 uv run moma /path/to/directory
# Creates formatter.log with detailed call traces
```

---

## Testing Strategy

### Test Organization

```
src/test/
├── datasets/                    # Test data
│   ├── filenames/
│   │   ├── filename_patterns.json  # 46 test cases
│   │   └── sample_files/           # Legacy reference
│   ├── mediainfo/
│   │   └── frame_class_tests.json  # 25 test cases
│   └── sample_mediafiles/          # Generated (in .gitignore)
├── conftest.py                  # Fixtures and dataset loaders
├── test_cache_subsystem.py      # 18 cache tests
├── test_services.py             # 30+ service tests
├── test_utils.py                # 70+ utility tests
├── test_formatters.py           # 40+ formatter tests
├── test_filename_detection.py   # Comprehensive filename parsing
├── test_filename_extractor.py   # 368 extractor tests
├── test_mediainfo_*.py          # MediaInfo tests
├── test_fileinfo_extractor.py   # File info tests
└── test_metadata_extractor.py   # Metadata tests
```

### Test Statistics

- **Total Tests**: 560 (1 skipped)
- **Service Layer**: 30+ tests
- **Utilities**: 70+ tests
- **Formatters**: 40+ tests
- **Extractors**: 400+ tests
- **Cache**: 18 tests

### Sample File Generation

```bash
# Generate 46 test files from filename_patterns.json
uv run python src/test/fill_sample_mediafiles.py
```

### Test Fixtures

```python
# Load test datasets
patterns = load_filename_patterns()
frame_tests = load_frame_class_tests()
dataset = load_dataset("custom_name")
file_path = get_test_file_path("movie.mkv")
```

### Running Tests

```bash
# All tests
uv run pytest

# Specific test file
uv run pytest src/test/test_services.py

# With verbose output
uv run pytest -xvs

# With coverage
uv run pytest --cov=src --cov-report=html
```

---

## Code Standards

### Python Standards

- **Version**: Python 3.11+
- **Style**: PEP 8 guidelines
- **Type Hints**: Encouraged for all public APIs
- **Docstrings**: Google-style format
- **Pathlib**: For all file operations
- **Exception Handling**: Specific exceptions (no bare `except:`)

### Docstring Format

```python
def example_function(param1: int, param2: str) -> bool:
    """Brief description of function.

    Longer description if needed, explaining behavior,
    edge cases, or important details.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When param1 is negative

    Example:
        >>> example_function(5, "test")
        True
    """
    pass
```

### Type Hints

```python
from typing import Optional

# Function type hints
def extract_title(self) -> Optional[str]:
    ...

# Union types (Python 3.10+)
def extract_movie_db(self) -> list[str] | None:
    ...

# Generic types
def extract_tracks(self) -> list[dict]:
    ...
```

### Logging Strategy

**Levels**:
- **Debug**: Language code conversions, metadata reads, MIME detection
- **Warning**: Network failures, API errors, MediaInfo parse failures
- **Error**: Formatter application failures

**Usage**:
```python
import logging
logger = logging.getLogger(__name__)

logger.debug(f"Converted {lang_code} to {iso3_code}")
logger.warning(f"TMDB API request failed: {e}")
logger.error(f"Error applying {formatter.__name__}: {e}")
```

### Error Handling

**Guidelines**:
- Catch specific exceptions: `(LookupError, ValueError, AttributeError)`
- Log all caught exceptions with context
- Network errors: `(requests.RequestException, ValueError)`
- Always close file handles (use context managers)

**Example**:
```python
try:
    lang_obj = langcodes.Language.get(lang_code.lower())
    return lang_obj.to_alpha3()
except (LookupError, ValueError, AttributeError) as e:
    logger.debug(f"Invalid language code '{lang_code}': {e}")
    return None
```

### Architecture Patterns

1. **Extractor Pattern**: Each extractor focuses on one data source
2. **Formatter Pattern**: Formatters handle display logic, extractors handle data
3. **Separation of Concerns**: Data extraction → formatting → display
4. **Dependency Injection**: Extractors and formatters are modular
5. **Configuration Management**: Settings class for all config

### Best Practices

- **Simplicity**: Avoid over-engineering, keep solutions simple
- **Minimal Changes**: Only modify what's explicitly requested
- **Validation**: Only at system boundaries (user input, external APIs)
- **Trust Internal Code**: Don't add unnecessary error handling
- **Delete Unused Code**: No backwards-compatibility hacks
- **No Premature Abstraction**: Three similar lines > premature abstraction

---

## AI Assistant Instructions

### Core Principles

1. **Read Before Modify**: Always read files before suggesting modifications
2. **Follow Existing Patterns**: Understand established architecture before changes
3. **Test Everything**: Run `uv run pytest` after all changes
4. **Simplicity First**: Avoid over-engineering solutions
5. **Document Changes**: Update relevant documentation

### Documentation Update Protocol

**After every change to functionality, architecture, or deployment — always:**

1. **Update CHANGELOG.md** — add an entry under `[Unreleased]` describing what changed and why
2. **Update AGENTS.md** — if architecture, file structure, key bindings, settings, screens, or any documented component changed
3. **Update README.md** — if user-facing behaviour, commands, or config changed
4. **Check `docs/ToDo.md`** — if the completed work matches a task there, mark it ✅ done
5. **Propose these updates to the user** before finishing — don't silently skip doc updates

**When a feature request is deferred or postponed:**

1. **Propose adding it to `docs/ToDo.md`** under the appropriate priority section
2. **If it's large or complex** (multi-step, affects multiple components, or needs design decisions): propose creating a standalone spec file in `docs/` (e.g. `docs/feature-mkv-editor.md`) and add a reference link in `docs/ToDo.md`
3. **Always confirm with the user** before creating new doc files

**When adding a new feature:**

1. Read existing code and understand architecture
2. Check `docs/ToDo.md` and `docs/REFACTORING_PROGRESS.md` for related pending tasks
3. Implement features incrementally
4. Test with real media files
5. Ensure backward compatibility
6. Apply Documentation Update Protocol above
7. Update tests as needed
8. Run `uv run release` before committing

### When Debugging

1. Enable formatter logging: `FORMATTER_LOG=1`
2. Check cache state (clear if stale data suspected)
3. Verify file permissions
4. Test with sample filenames first
5. Check logs in `formatter.log`

### When Refactoring

1. Maintain backward compatibility unless explicitly breaking
2. Update tests to reflect refactored code
3. Check all formatters (formatting is centralized)
4. Verify extractor chain (ensure data flow intact)
5. Run full test suite
6. Apply Documentation Update Protocol above

### Common Pitfalls to Avoid

- ❌ Don't create new files unless absolutely necessary
- ❌ Don't add features beyond what's requested
- ❌ Don't skip testing with real files
- ❌ Don't forget to update version number for releases
- ❌ Don't commit secrets or API keys
- ❌ Don't use deprecated Textual APIs
- ❌ Don't use bare `except:` clauses
- ❌ Don't use command-line tools when specialized tools exist

### Tool Usage

- **Read files**: Use `Read` tool, not `cat`
- **Edit files**: Use `Edit` tool, not `sed`
- **Write files**: Use `Write` tool, not `echo >>`
- **Search files**: Use `Glob` tool, not `find`
- **Search content**: Use `Grep` tool, not `grep`
- **Run commands**: Use `Bash` tool for terminal operations only

### Git Workflow

**Commit Standards**:
- Clear, descriptive messages
- Focus on "why" not "what"
- One logical change per commit

**Commit Message Format**:
```
type: Brief description (imperative mood)

Longer explanation if needed.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**Safety Protocol**:
- ❌ NEVER update git config
- ❌ NEVER run destructive commands without explicit request
- ❌ NEVER skip hooks (--no-verify, --no-gpg-sign)
- ❌ NEVER force push to main/master
- ❌ Avoid `git commit --amend` unless conditions met

### Creating Pull Requests

1. Run `git status`, `git diff`, `git log` to understand changes
2. Analyze ALL commits that will be included
3. Draft comprehensive PR summary
4. Create PR using:
   ```bash
   gh pr create --title "Title" --body "$(cat <<'EOF'
   ## Summary
   - Bullet points of changes

   ## Test plan
   - Testing checklist

   🤖 Generated with [Claude Code](https://claude.com/claude-code)
   EOF
   )"
   ```

---

## Release Process

### Version Management

**Version Scheme**: SemVer (MAJOR.MINOR.PATCH)

**Commands**:
```bash
# Bump patch version (0.6.0 → 0.6.1)
uv run bump-version

# Full release process
uv run release  # Bump + sync + build
```

### Release Checklist

- [ ] All tests passing: `uv run pytest`
- [ ] Type checking passes: `uv run mypy src/`
- [ ] Documentation updated (CHANGELOG.md, README.md)
- [ ] Version bumped in `pyproject.toml`
- [ ] Dependencies synced: `uv sync`
- [ ] Build successful: `uv build`
- [ ] Install test: `uv tool install .`
- [ ] Manual testing with real media files

### Build Artifacts

```
dist/
├── moma-0.8.11-py3-none-any.whl    # Wheel distribution
└── moma-0.8.11.tar.gz              # Source distribution
```

---

## API Integration

### TMDB API

**Configuration**:
- API key stored in `src/secrets.py`
- Base URL: `https://api.themoviedb.org/3/`
- Image base URL for poster downloads

**Endpoints Used**:
- Search: `/search/movie`
- Movie details: `/movie/{id}`

**Rate Limiting**: Handled gracefully with error fallback

**Caching**:
- API responses cached for 6 hours
- Posters cached for 30 days
- Cache location: `~/.cache/moma/tmdb/`, `~/.cache/moma/posters/`

---

## File Operations

### Directory Scanning

- Recursive search for supported video formats
- File tree representation with hierarchical structure
- Efficient tree updates on file operations
- Permission error handling

### File Renaming

**Process**:
1. Select file in tree
2. Press `r` to initiate rename
3. Review proposed name (current vs proposed)
4. Confirm with `y` or cancel with `n`
5. Tree updates in-place without full reload

**Proposed Name Format**:
```
Title (Year) [Resolution Source Edition].ext
```

**Sanitization**:
- Invalid characters removed (cross-platform)
- Reserved names checked (Windows compatibility)
- Markup tags stripped
- Length validation

### Metadata Caching

- First extraction cached for 6 hours
- TMDB data cached for 6 hours
- Posters cached for 30 days
- Force refresh with `f` command
- Cache invalidated on file rename

---

## Keyboard Commands

| Key | Action |
|-----|--------|
| `q` | Quit application |
| `o` | Open directory |
| `s` | Scan current node's directory |
| `Ctrl+S` | Scan entire directory tree |
| `f` | Refresh metadata for selected file |
| `r` | Rename file with proposed name |
| `c` | Convert to MKV |
| `d` | Delete selected file |
| `t` | Toggle tree expansion |
| `m` | Toggle mode (technical/catalog) |
| `p` | Settings |
| `h` | Show help screen |
| `Ctrl+P` | Open command palette |

---

## Known Issues & Limitations

### Current Limitations

- TMDB API requires internet connection
- Poster display requires terminal with image support
- Some special characters in filenames need sanitization
- Large directories may have initial scan delay

### Performance Notes

- In-memory cache reduces repeated extraction overhead
- File cache persists across sessions
- Tree updates optimized for rename operations
- TMDB requests throttled to respect API limits
- Large directory scans use async/await patterns

---

## Security Considerations

- Input sanitization for filenames (see `ProposedFilenameView`)
- No shell command injection risks
- Safe file operations (pathlib, proper error handling)
- TMDB API key should not be committed (stored in `secrets.py`)
- Cache directory permissions should be user-only

---

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
- Phase 1-3 refactoring (2025-12-31 to 2026-01-01)

### Version Milestones

- **0.2.x**: Initial TUI with basic metadata
- **0.3.x**: Enhanced extractors and formatters
- **0.4.x**: Added TMDB integration
- **0.5.x**: Settings, caching, catalog mode, poster display
- **0.6.0**: Cache subsystem, service layer, protocols
- **0.7.0-dev**: Complete refactoring (in progress)

---

## Resources

### External Documentation

- [Textual Documentation](https://textual.textualize.io/)
- [PyMediaInfo Documentation](https://pymediainfo.readthedocs.io/)
- [Mutagen Documentation](https://mutagen.readthedocs.io/)
- [TMDB API Documentation](https://developers.themoviedb.org/3)
- [UV Documentation](https://docs.astral.sh/uv/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [Mypy Documentation](https://mypy.readthedocs.io/)

### Internal Documentation

- **README.md**: User guide and quick start
- **INSTALL.md**: Installation methods
- **DEVELOP.md**: Developer setup and debugging
- **CHANGELOG.md**: Version history and changes
- **docs/REFACTORING_PROGRESS.md**: Future refactoring plans
- **docs/ToDo.md**: Current task list

---

**Last Updated**: 2026-04-11
**Maintainer**: sha
**For**: AI Assistants and Developers
**Repository**: `/Users/sha/Developer/sha.dev/moma`
