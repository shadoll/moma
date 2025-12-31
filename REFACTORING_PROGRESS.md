# Renamer v0.7.0 Refactoring Progress

**Started**: 2025-12-31
**Target Version**: 0.7.0 (from 0.6.0)
**Goal**: Stable version with critical bugs fixed and deep architectural refactoring

---

## Phase 1: Critical Bug Fixes ✅ COMPLETED (3/5)

### ✅ 1.1 Fix Cache Key Generation Bug
**Status**: COMPLETED
**File**: `renamer/cache.py`
**Changes**:
- Complete rewrite of `_get_cache_file()` method (lines 20-75 → 47-86)
- Fixed critical variable scoping bug at line 51 (subkey used before assignment)
- Simplified cache key logic to single consistent pathway
- Removed complex pkl/json branching that caused errors
- Added `_sanitize_key_component()` for filesystem safety

**Testing**: Needs verification

---

### ✅ 1.2 Add Thread Safety to Cache
**Status**: COMPLETED
**File**: `renamer/cache.py`
**Changes**:
- Added `threading.RLock` for thread-safe operations (line 29)
- Wrapped all cache operations with `with self._lock:` context manager
- Added thread-safe `clear_expired()` method (lines 342-380)
- Memory cache now properly synchronized

**Testing**: Needs verification with concurrent access

---

### ✅ 1.3 Fix Resource Leaks in Tests
**Status**: COMPLETED
**Files**:
- `renamer/test/test_mediainfo_frame_class.py` (lines 14-17)
- `renamer/test/test_mediainfo_extractor.py` (lines 60-72)

**Changes**:
- Replaced bare `open()` with context managers
- Fixed test_mediainfo_frame_class.py: Now uses `Path(__file__).parent` and `with open()`
- Fixed test_mediainfo_extractor.py: Converted to fixture-based approach instead of parametrize with open file
- Both files now properly close file handles

**Testing**: Run `uv run pytest` to verify no resource leaks

---

### 🔄 1.4 Replace Bare Except Clauses
**Status**: PENDING
**Files to fix**:
- `renamer/extractors/filename_extractor.py` (lines 327, 384, 458, 515)
- `renamer/extractors/mediainfo_extractor.py` (line 168)

**Plan**:
- Replace `except:` with specific exception types
- Add logging for caught exceptions
- Test error scenarios

**Testing**: Need to verify with invalid inputs

---

### 🔄 1.5 Add Logging to Error Handlers
**Status**: PENDING (Partially done in cache.py)
**Completed**:
- ✅ Cache module now has comprehensive logging
- ✅ All cache errors logged with context

**Still needed**:
- Add logging to extractor error handlers
- Add logging to formatter error handlers
- Configure logging levels

**Testing**: Check log output during errors

---

## Phase 2: Architecture Foundation (PENDING)

### 2.1 Create Base Classes and Protocols
**Status**: NOT STARTED
**Files to create**:
- `renamer/extractors/base.py` - DataExtractor Protocol
- `renamer/formatters/base.py` - Formatter ABC

---

### 2.2 Create Service Layer
**Status**: NOT STARTED
**Files to create**:
- `renamer/services/__init__.py`
- `renamer/services/file_tree_service.py`
- `renamer/services/metadata_service.py`
- `renamer/services/rename_service.py`

---

### 2.3 Add Thread Pool to MetadataService
**Status**: NOT STARTED
**Dependencies**: Requires 2.2 to be completed

---

### 2.4 Extract Utility Modules
**Status**: NOT STARTED
**Files to create**:
- `renamer/utils/__init__.py`
- `renamer/utils/language_utils.py`
- `renamer/utils/pattern_utils.py`
- `renamer/utils/frame_utils.py`

---

## Phase 3: Code Quality (PENDING)

### 3.1 Refactor Long Methods
**Status**: NOT STARTED
**Target methods**:
- `extract_title()` (85 lines) → split into 4 helpers
- `extract_audio_langs()` (130 lines) → split into 3 helpers
- `extract_frame_class()` (55 lines) → split into 2 helpers
- `update_renamed_file()` (39 lines) → split into 2 helpers

---

### 3.2 Eliminate Code Duplication
**Status**: NOT STARTED
**Target duplications**:
- Movie DB pattern extraction (44 lines duplicated)
- Language code detection (150+ lines duplicated)
- Frame class matching (duplicated logic)
- Year extraction (duplicated logic)

---

### 3.3 Extract Magic Numbers to Constants
**Status**: NOT STARTED
**New constants needed in `renamer/constants.py`**:
- `CURRENT_YEAR`, `YEAR_FUTURE_BUFFER`, `MIN_VALID_YEAR`
- `MAX_VIDEO_TRACKS`, `MAX_AUDIO_TRACKS`, `MAX_SUBTITLE_TRACKS`
- `FRAME_HEIGHT_TOLERANCE_LARGE`, `FRAME_HEIGHT_TOLERANCE_SMALL`
- `DEFAULT_CACHE_TTL`

---

### 3.4 Add Missing Type Hints
**Status**: NOT STARTED
**Files needing type hints**:
- `renamer/extractors/default_extractor.py` (13 methods)
- Various cache methods (replace `Any` with specific types)

---

### 3.5 Add Comprehensive Docstrings
**Status**: NOT STARTED
**All modules need docstring review**

---

## Phase 4: Refactor to New Architecture (PENDING)

- Refactor all extractors to use protocol
- Refactor all formatters to use base class
- Refactor RenamerApp to use services
- Update all imports and dependencies

---

## Phase 5: Test Coverage (PENDING)

### New Test Files Needed:
- `renamer/test/test_cache.py`
- `renamer/test/test_formatters.py`
- `renamer/test/test_screens.py`
- `renamer/test/test_services.py`
- `renamer/test/test_app.py`
- `renamer/test/test_utils.py`

---

## Phase 6: Documentation and Release (PENDING)

- Update CLAUDE.md
- Update DEVELOP.md
- Update AI_AGENT.md
- Update README.md
- Bump version to 0.7.0
- Create CHANGELOG.md
- Build and test distribution

---

## Testing Status

### Manual Tests Needed
- [ ] Test cache with concurrent file selections
- [ ] Test cache expiration
- [ ] Test cache invalidation on rename
- [ ] Test resource cleanup (no file handle leaks)
- [ ] Test with real media files
- [ ] Performance test (ensure no regression)

### Automated Tests
- [ ] Run `uv run pytest` - verify all tests pass
- [ ] Run with coverage: `uv run pytest --cov=renamer`
- [ ] Check for resource warnings

---

## Current Status Summary

**Completed**: 3 critical bug fixes
**In Progress**: None (waiting for testing)
**Blocked**: None
**Next Steps**: Test current changes, then continue with Phase 1.4 and 1.5

---

## Breaking Changes Introduced

### Cache System
- **Cache key format changed**: Old cache files will be invalid
- **Migration**: Users should clear cache: `rm -rf ~/.cache/renamer/`
- **Impact**: No data loss, just cache miss on first run

### Thread Safety
- **Cache now thread-safe**: Multiple concurrent accesses properly handled
- **Impact**: Positive - prevents race conditions

---

## Notes

### Cache Rewrite Details
The cache system was completely rewritten for:
1. **Bug Fix**: Fixed critical variable scoping issue
2. **Thread Safety**: Added RLock for concurrent access
3. **Simplification**: Single code path instead of branching logic
4. **Logging**: Comprehensive logging for debugging
5. **Security**: Added key sanitization to prevent filesystem escaping
6. **Maintenance**: Added `clear_expired()` utility method

### Test Fixes Details
- Used proper `Path(__file__).parent` for relative paths
- Converted parametrize with open file to fixture-based approach
- All file operations now use context managers

---

**Last Updated**: 2025-12-31 (after Phase 1.1-1.3)
