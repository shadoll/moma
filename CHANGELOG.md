# Changelog

All notable changes to the moma project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Future Plans
See [docs/REFACTORING_PROGRESS.md](docs/REFACTORING_PROGRESS.md) and [docs/ToDo.md](docs/ToDo.md) for upcoming features and improvements.

---

## [0.8.11] - 2026-04-11

### Changed
- Renamed project package from `renamer` to `moma`, CLI command is now `moma`
- Main app class renamed `RenamerApp` → `MomaApp`
- Package source directory renamed `renamer/` → `src/`
- Config path `~/.config/renamer/` → `~/.config/moma/`
- Cache path `~/.cache/renamer/` → `~/.cache/moma/`
- Migrated repository to GitHub: `git@github.com:shadoll/moma.git`

---

## [0.8.10] - 2026-04-10

### Added
- **OpenScreen**: Dedicated screen for directory input with validation
- **ConvertConfirmScreen**: Conversion confirmation for AVI/MP4/WebM → MKV
- **DeleteConfirmScreen**: File deletion confirmation screen
- **Singleton logging configuration** (`logging_config.py`)

### Fixed
- Improved scan commands and key bindings usability
- MP4 and WebM support in conversion service

---

## [0.7.10] - 2026-02-01

### Added
- **Poster rendering**: ASCII art, Viu, and RichPixels poster display options
- **HEVC encoding options**: configurable CRF and preset in settings
- **MPG/MPEG format support** in conversion service
- **Genre extraction** added to media properties panel
- **File icons** in directory tree
- **Delete file functionality** with confirmation

### Changed
- Refactored `FormatterApplier` class (removed, inlined)
- Consolidated text color decorators
- Improved scan type detection for interlaced content
- Updated bitrate calculation in `TrackFormatter`
- Replaced dots with spaces in title normalization

### Fixed
- Poster handling and rendering in catalog mode
- TMDB data retrieval improvements

---

## [0.7.0] - 2026-01-01

### Major Refactoring (Phases 1-3)

Significant refactoring focused on code quality, architecture, and maintainability.

---

### Phase 3: Code Quality (COMPLETED)

#### Added
- **Type Hints**: Complete type coverage for `DefaultExtractor` (21 methods)
- **Mypy Integration**: Added mypy>=1.0.0 as dev dependency for type checking
- **Comprehensive Docstrings**: Added module + class + method docstrings to 5 key files:
  - `default_extractor.py` - 22 docstrings
  - `extractor.py` - Enhanced with examples
  - `fileinfo_extractor.py` - Enhanced with Args/Returns
  - `metadata_extractor.py` - Enhanced with examples
  - `formatter.py` - Enhanced FormatterApplier

#### Changed
- **Constants Reorganization**: Split monolithic `constants.py` into 8 logical modules:
  - `media_constants.py` - Media types
  - `source_constants.py` - Video sources
  - `frame_constants.py` - Frame classes and quality indicators
  - `moviedb_constants.py` - Database identifiers
  - `edition_constants.py` - Special editions
  - `lang_constants.py` - Skip words for language detection
  - `year_constants.py` - Dynamic year validation
  - `cyrillic_constants.py` - Character mappings
- **Dynamic Year Validation**: Replaced hardcoded year values with `is_valid_year()` function
- **Language Extraction**: Simplified using `langcodes.Language.get()` for dynamic validation (~80 lines removed)

#### Removed
- **Code Duplication**: Eliminated ~95 lines of duplicated code:
  - ~80 lines of hardcoded language lists
  - ~15 lines of duplicated movie DB pattern matching
- **Hardcoded Values**: Removed hardcoded quality indicators, year values, Cyrillic mappings

### Phase 2: Architecture Foundation (COMPLETED)

#### Added
- **Base Classes and Protocols** (409 lines):
  - `DataExtractor` Protocol defining extractor interface (23 methods)
  - `Formatter` ABCs: `DataFormatter`, `TextFormatter`, `MarkupFormatter`, `CompositeFormatter`
- **Service Layer** (935 lines):
  - `FileTreeService`: Directory scanning and validation
  - `MetadataService`: Thread-pooled metadata extraction with cancellation support
  - `RenameService`: Filename validation, sanitization, and atomic renaming
- **Utility Modules** (953 lines):
  - `PatternExtractor`: Centralized regex pattern matching
  - `LanguageCodeExtractor`: Language code processing
  - `FrameClassMatcher`: Resolution/frame class matching
- **Command Palette Integration**:
  - `AppCommandProvider`: 11 main app commands (open, scan_local, scan, refresh, rename, convert, delete, toggle_mode, expand, settings, help)
  - `CacheCommandProvider`: 7 cache management commands
  - Access via Ctrl+P

#### Improved
- **Thread Safety**: MetadataService uses ThreadPoolExecutor with Lock for concurrent operations
- **Testability**: Services can be tested independently of UI
- **Reusability**: Clear interfaces and separation of concerns

### Phase 1: Critical Bug Fixes (COMPLETED)

#### Fixed
- **Cache Key Generation Bug**: Fixed critical variable scoping issue in cache system
- **Resource Leaks**: Fixed file handle leaks in tests (proper context managers)
- **Exception Handling**: Replaced bare `except:` clauses with specific exceptions

#### Added
- **Thread Safety**: Added `threading.RLock` to cache for concurrent access
- **Logging**: Comprehensive logging throughout extractors and formatters:
  - Debug: Language code conversions, metadata reads
  - Warning: Network failures, API errors, MediaInfo parse failures
  - Error: Formatter application failures

#### Changed
- **Unified Cache Subsystem** (500 lines):
  - Modular architecture: `core.py`, `types.py`, `strategies.py`, `managers.py`, `decorators.py`
  - 4 cache key strategies: `FilepathMethodStrategy`, `APIRequestStrategy`, `SimpleKeyStrategy`, `CustomStrategy`
  - Enhanced decorators: `@cached_method()`, `@cached_api()`, `@cached_property()`
  - Cache manager operations: `clear_all()`, `clear_by_prefix()`, `clear_expired()`, `compact_cache()`

---

### Phase 5: Test Coverage (PARTIALLY COMPLETED - 4/6)

#### Added
- **Service Tests** (30+ tests): FileTreeService, MetadataService, RenameService
- **Utility Tests** (70+ tests): PatternExtractor, LanguageCodeExtractor, FrameClassMatcher
- **Formatter Tests** (40+ tests): All formatter classes and FormatterApplier
- **Cache Tests** (18 tests): Cache subsystem functionality
- **Dataset Organization**:
  - `filename_patterns.json`: 46 comprehensive test cases
  - `frame_class_tests.json`: 25 frame class test cases
  - Sample file generator: `fill_sample_mediafiles.py`
  - Dataset loaders in `conftest.py`

#### Changed
- **Test Organization**: Consolidated test data into `src/test/datasets/`
- **Total Tests**: 560 tests (1 skipped), all passing

---

### Documentation Improvements

#### Added
- **AGENTS.md**: Comprehensive 900+ line technical reference
- **CHANGELOG.md**: This file

#### Changed
- **CLAUDE.md**: Streamlined to pointer to AGENTS.md
- **AI_AGENT.md**: Marked as deprecated, points to AGENTS.md
- **DEVELOP.md**: Streamlined with references to AGENTS.md
- **README.md**: Streamlined user guide with references

#### Removed
- Outdated version information from documentation files
- Duplicated content now in AGENTS.md

---

### Breaking Changes

#### Cache System
- **Cache key format changed**: Old cache files are invalid
- **Migration**: Users should clear cache: `rm -rf ~/.cache/moma/`
- **Impact**: No data loss, just cache miss on first run after upgrade

#### Dependencies
- **Added**: mypy>=1.0.0 as dev dependency

---

### Statistics

#### Code Quality Metrics
- **Lines Added**: ~3,497 lines
  - Phase 1: ~500 lines (cache subsystem)
  - Phase 2: ~2,297 lines (base classes + services + utilities)
  - Phase 3: ~200 lines (docstrings)
  - Phase 5: ~500 lines (new tests)
- **Lines Removed**: ~290 lines through code duplication elimination
- **Net Gain**: ~3,207 lines of quality code

#### Test Coverage
- **Total Tests**: 560 (was 518)
- **New Tests**: +42 tests (+8%)
- **Pass Rate**: 100% (559 passed, 1 skipped)

#### Architecture Improvements
- ✅ Protocols and ABCs for consistent interfaces
- ✅ Service layer with dependency injection
- ✅ Thread pool for concurrent operations
- ✅ Utility modules for shared logic
- ✅ Command palette for unified access
- ✅ Type hints and mypy integration
- ✅ Comprehensive docstrings

---

## [0.6.0] - 2025-12-31

### Added
- Initial cache subsystem implementation
- Basic service layer structure
- Protocol definitions for extractors

### Changed
- Refactored cache key generation
- Improved error handling

---

## [0.5.10] - Previous Release

### Features
- Dual display modes (technical/catalog)
- TMDB integration with poster display
- Settings configuration UI
- Persistent caching with TTL
- Intelligent file renaming
- Color-coded information display
- Keyboard and mouse navigation
- Help screen with key bindings

---

## Version History Summary

- **0.7.0-dev** (2026-01-01): Major refactoring - code quality, architecture, testing
- **0.6.0** (2025-12-31): Cache improvements, service layer foundation
- **0.5.x**: Settings, caching, catalog mode, poster display
- **0.4.x**: TMDB integration
- **0.3.x**: Enhanced extractors and formatters
- **0.2.x**: Initial TUI with basic metadata

---

## Links

- [AGENTS.md](AGENTS.md) - Complete technical documentation
- [docs/REFACTORING_PROGRESS.md](docs/REFACTORING_PROGRESS.md) - Future refactoring plans
- [docs/ToDo.md](docs/ToDo.md) - Current task list

---

**Last Updated**: 2026-04-11
