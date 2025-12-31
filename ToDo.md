Project: Media File Renamer and Metadata Viewer (Python TUI with Textual)

**Current Version**: 0.5.10

## TODO Steps:
1. ✅ Set up Python project structure with UV package manager
2. ✅ Install dependencies: textual, mutagen, pymediainfo, python-magic, pathlib for file handling
3. ✅ Implement recursive directory scanning for video files (*.mkv, *.avi, *.mov, *.mp4, *.wmv, *.flv, *.webm, etc.)
4. ✅ Detect real media container type using mutagen and python-magic
5. ✅ Create Textual TUI application with split layout (left: file tree, right: file details)
6. ✅ Implement file tree display with navigation (keyboard arrows, mouse support)
7. ✅ Add bottom command bar with 'quit', 'open directory', 'scan' commands
8. ✅ Display file details on right side: file size, extension from filename, extension from metadata, file date
9. ✅ Add functionality to select files in the tree and update right panel
10. ✅ Implement detailed metadata display including video/audio/subtitle tracks with colors
11. ✅ Add custom tree styling with file icons and colored guides
12. ✅ Add scrollable details panel
13. ✅ Handle markup escaping for file names with brackets
14. ✅ Implement file renaming functionality with confirmation dialog
15. ✅ Add proposed name generation based on metadata extraction
16. ✅ Add help screen with key bindings and usage information
17. ✅ Add tree expansion/collapse toggle functionality
18. ✅ Add file refresh functionality to reload metadata for selected file
19. ✅ Optimize tree updates to avoid full reloads after renaming
20. ✅ Add loading indicators for metadata extraction
21. ✅ Add error handling for file operations and metadata extraction
22. 🔄 Implement blue highlighting for changed parts in proposed filename display (show differences between current and proposed names)
23. 🔄 Implement build script to exclude dev commands (bump-version, release) from distributed package
24. 📋 Implement metadata editing capabilities (future enhancement)
25. 📋 Add batch rename operations (future enhancement)
27. 📋 Add advanced search and filtering capabilities (future enhancement)
28. 📋 Implement undo/redo functionality for file operations (future enhancement)

---

## Media Catalog Mode Implementation Plan

**New big app evolution step: Add media catalog mode with settings, caching, and enhanced TMDB display.**

### Phase 1: Settings Management Foundation
1. ✅ Create settings module (`renamer/settings.py`) for JSON config in `~/.config/renamer/config.json` with schema: mode, cache TTLs
2. ✅ Integrate settings into app startup (load/save on launch/exit)
3. ✅ Add settings window to UI with fields for mode and TTLs
4. ✅ Add "Open Settings" command to command panel
5. ✅ Order setting menu item in the action bar by right side, close to the sysytem menu item ^p palette

### Phase 2: Mode Toggle and UI Switching
5. ✅ Add "Toggle Mode" command to switch between "technical" and "catalog" modes
6. ✅ Modify right pane for mode-aware display (technical vs catalog info)
7. ✅ Persist and restore mode state from settings

### Phase 3: Caching System
8. ✅ Create caching module (`renamer/cache.py`) for file-based cache with TTL support
9. ✅ Integrate caching into extractors (check cache first, store results)
10. ✅ Add refresh command to force re-extraction and cache update
11. ✅ Handle cache cleanup on file rename (invalidate old filename)

### Phase 4: Media Catalog Display
12. ✅ Update TMDB extractor for catalog data: title, year, duration, rates, overview, genres codes, poster_path
13. ✅ Create catalog formatter (`formatters/catalog_formatter.py`) for beautiful display
14. ✅ Integrate catalog display into right pane

### Phase 5: Poster Handling and Display
15. ✅ Add poster caching (images in cache dir with 1-month TTL)
16. ✅ Implement terminal image display (using rich-pixels library)

### Phase 6: Polish and Documentation
17. ✅ Create comprehensive CLAUDE.md for AI assistants
18. ✅ Update all markdown documentation files
19. ✅ Ensure version consistency across all files

### Additional TODOs from Plan
- 📋 Retrieve full movie details from TMDB (currently basic data only)
- 📋 Expand genres to full names instead of codes (currently shows genre IDs)
- 📋 Optimize poster quality and display (improve image rendering)
- 📋 Add TV show support (currently movie-focused)
- 📋 Implement blue highlighting for filename differences
- 📋 Build script to exclude dev commands from distribution

---

## Recently Completed (v0.5.x)

### Version 0.5.10
- Complete media catalog mode implementation
- TMDB integration with poster display
- Settings system with persistent JSON storage
- Advanced caching with TTL support
- Dual-mode display (technical/catalog)
- Settings UI screen

### Version 0.4.x
- Enhanced extractor system
- TMDB extractor foundation
- Improved formatter architecture

### Version 0.3.x
- Expanded metadata extraction
- Multiple formatter types
- Special edition detection

### Version 0.2.x
- Initial TUI implementation
- Basic metadata extraction
- File tree navigation
- Rename functionality

---

## Development Priorities

### High Priority
1. 🔄 Blue highlighting for filename differences (UX improvement)
2. 🔄 Build script for clean distribution packages
3. 📋 Genre ID to name expansion (TMDB lookup)

### Medium Priority
1. 📋 Batch rename operations
2. 📋 Advanced search/filtering
3. 📋 TV show support

### Low Priority (Future)
1. 📋 Metadata editing
2. 📋 Plugin system
3. 📋 Undo/redo functionality
4. 📋 Configuration profiles

---

**Legend:**
- ✅ Completed
- 🔄 In Progress / Partially Complete
- 📋 Planned / Future Enhancement

**Last Updated**: 2025-12-31