# Renamer - Future Tasks

**Version**: 0.7.0-dev
**Last Updated**: 2026-01-01

> **📋 For completed work, see [CHANGELOG.md](CHANGELOG.md)**
>
> **📋 For refactoring plans, see [REFACTORING_PROGRESS.md](REFACTORING_PROGRESS.md)**

This file tracks future feature enhancements and improvements.

---

## Priority Tasks

### High Priority

- [ ] **Phase 4: Refactor to New Architecture**
  - Refactor existing extractors to use Protocol
  - Refactor existing formatters to use base classes
  - Integrate RenamerApp with services
  - Update all imports and dependencies
  - See [REFACTORING_PROGRESS.md](REFACTORING_PROGRESS.md) for details

- [ ] **Complete Test Coverage**
  - Add UI screen tests
  - Add app integration tests
  - Increase coverage to >90%

### Medium Priority

- [ ] **Metadata Editing Capabilities**
  - Edit embedded metadata tags
  - Batch editing support
  - Validation and preview

- [ ] **Batch Rename Operations**
  - Select multiple files
  - Preview all changes
  - Bulk rename with rollback

- [ ] **Advanced Search and Filtering**
  - Filter by resolution, codec, year
  - Search by TMDB metadata
  - Save filter presets

---

## Feature Enhancements

### UI Improvements

- [ ] **Blue Highlighting for Filename Differences**
  - Show changed parts in proposed filename
  - Color-code additions, removals, changes
  - Side-by-side comparison view

- [ ] **Enhanced Poster Display**
  - Optimize image quality
  - Support for fanart/backdrops
  - Poster cache management UI

- [ ] **Dedicated Poster Window with Real Image Support**
  - Create separate panel/window for poster display in catalog mode
  - Display actual poster images (not ASCII art) using terminal graphics protocols
  - Support for Kitty graphics protocol, iTerm2 inline images, or Sixel
  - Configurable poster size with smaller font rendering
  - Side-by-side layout: metadata (60%) + poster (40%)
  - Higher resolution ASCII art as fallback (100+ chars with extended gradient)

- [ ] **Progress Indicators**
  - Show scan progress
  - Batch operation progress bars
  - Background task status

### TMDB Integration

- [ ] **Full Movie Details**
  - Cast and crew information
  - Production companies
  - Budget and revenue data
  - Release dates by region

- [ ] **Genre Name Expansion**
  - Show full genre names instead of IDs
  - Genre-based filtering
  - Multi-genre support

- [ ] **TV Show Support**
  - Episode and season metadata
  - TV show renaming patterns
  - Episode numbering detection

- [ ] **Collection/Series Support**
  - Detect movie collections
  - Group related media
  - Collection-based renaming

### Technical Improvements

- [ ] **Undo/Redo Functionality**
  - Track file operations history
  - Undo renames
  - Redo operations
  - Operation log

- [ ] **Performance Optimization**
  - Lazy loading for large directories
  - Virtual scrolling in tree view
  - Background metadata extraction
  - Smart cache invalidation

### Build and Distribution

- [ ] **Build Script Improvements**
  - Exclude dev commands from distribution
  - Automated release workflow
  - Cross-platform testing

- [ ] **Package Distribution**
  - PyPI publication
  - Homebrew formula
  - AUR package
  - Docker image

---

## Potential Future Features

### Advanced Features

- [ ] Subtitle downloading and management
- [ ] NFO file generation
- [ ] Integration with media servers (Plex, Jellyfin, Emby)
- [ ] Watch history tracking
- [ ] Duplicate detection
- [ ] Quality comparison (upgrade detection)

### Integrations

- [ ] Multiple database support (TVDB, Trakt, AniDB)
- [ ] Custom API integrations
- [ ] Local database option (offline mode)
- [ ] Webhook support for automation

### Export/Import

- [ ] Export catalog to CSV/JSON
- [ ] Import rename mappings
- [ ] Backup/restore settings
- [ ] Configuration profiles

---

## Known Issues

See [REFACTORING_PROGRESS.md](REFACTORING_PROGRESS.md) for current limitations and planned fixes.

---

## Contributing

Before working on any task:

1. Check [ENGINEERING_GUIDE.md](ENGINEERING_GUIDE.md) for architecture details
2. Review [CHANGELOG.md](CHANGELOG.md) for recent changes
3. Read [DEVELOP.md](DEVELOP.md) for development setup
4. Run tests: `uv run pytest`
5. Follow code standards in [ENGINEERING_GUIDE.md](ENGINEERING_GUIDE.md#code-standards)

---

**Last Updated**: 2026-01-01
