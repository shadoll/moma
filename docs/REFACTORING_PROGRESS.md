# moma - Refactoring Roadmap

**Version**: 0.8.11
**Last Updated**: 2026-04-11

> **📋 For completed work, see [CHANGELOG.md](CHANGELOG.md)**

This document tracks the future refactoring plan for moma v0.8.x+.

---

## Completed Phases

✅ **Phase 1**: Critical Bug Fixes (5/5) - [See CHANGELOG.md](CHANGELOG.md)
✅ **Phase 2**: Architecture Foundation (5/5) - [See CHANGELOG.md](CHANGELOG.md)
✅ **Phase 3**: Code Quality (5/5) - [See CHANGELOG.md](CHANGELOG.md)

---

## Pending Phases

### Phase 3.6: Cleanup and Preparation (0/2)

**Goal**: Clean up remaining issues before major refactoring.

**Status**: NOT STARTED
**Priority**: HIGH (Must complete before Phase 4)

#### 3.6.1 Refactor ProposedNameFormatter to Use Decorator Pattern
**Status**: NOT STARTED

**Current Issue**: `ProposedNameFormatter` stores extracted values in `__init__` as instance variables, creating unnecessary coupling.

**Goal**: Convert to functional/decorator pattern similar to other formatters.

**Current Code**:
```python
class ProposedNameFormatter:
    def __init__(self, extractor):
        self.__order = extractor.get('order')
        self.__title = extractor.get('title')
        # ... more instance variables

    def rename_line(self) -> str:
        return f"{self.__order}{self.__title}..."
```

**Target Design**:
```python
class ProposedNameFormatter:
    @staticmethod
    def format_proposed_name(extractor) -> str:
        """Generate proposed filename from extractor data"""
        # Direct formatting without storing state
        order = format_order(extractor.get('order'))
        title = format_title(extractor.get('title'))
        return f"{order}{title}..."

    @staticmethod
    def format_proposed_name_with_color(file_path, extractor) -> str:
        """Format proposed name with color highlighting"""
        proposed = ProposedNameFormatter.format_proposed_name(extractor)
        # Color logic here
```

**Benefits**:
- Stateless, pure functions
- Easier to test
- Consistent with other formatters
- Can use `@cached()` decorator if needed
- No coupling to extractor instance

**Files to Modify**:
- `src/formatters/proposed_name_formatter.py`
- Update all usages in `app.py`, `screens.py`, etc.

---

#### 3.6.2 Clean Up Decorators Directory
**Status**: NOT STARTED

**Current Issue**: `src/decorators/` directory contains legacy `caching.py` file that's no longer used. All cache decorators were moved to `src/cache/decorators.py` in Phase 1.

**Current Structure**:
```
src/decorators/
├── caching.py          # ⚠️ LEGACY - Remove
└── __init__.py         # Import from src.cache
```

**Actions**:
1. **Verify no direct imports** of `src.decorators.caching`
2. **Remove `caching.py`** - All functionality now in `src/cache/decorators.py`
3. **Keep `__init__.py`** for backward compatibility (imports from `src.cache`)
4. **Update any direct imports** to use `from src.cache import cached_method`

**Verification**:
```bash
# Check for direct imports of old caching module
grep -r "from src.decorators.caching" src/
grep -r "import src.decorators.caching" src/

# Should only find imports from __init__.py that re-export from src.cache
```

**Benefits**:
- Removes dead code
- Clarifies that all caching is in `src/cache/`
- Maintains backward compatibility via `__init__.py`

---

### Phase 4: Refactor to New Architecture (0/4)

**Goal**: Migrate existing code to use the new architecture from Phase 2.

**Status**: NOT STARTED

#### 4.1 Refactor Extractors to Use Protocol
- Update all extractors to explicitly implement `DataExtractor` Protocol
- Ensure consistent method signatures
- Add missing Protocol methods where needed
- Update type hints to match Protocol

**Files to Update**:
- `filename_extractor.py`
- `mediainfo_extractor.py`
- `metadata_extractor.py`
- `fileinfo_extractor.py`
- `tmdb_extractor.py`

#### 4.2 Refactor Formatters to Use Base Classes
- Update all formatters to inherit from appropriate base classes
- Move to `DataFormatter`, `TextFormatter`, or `MarkupFormatter`
- Ensure consistent interface
- Add missing abstract methods

**Files to Update**:
- `media_formatter.py`
- `catalog_formatter.py`
- `track_formatter.py`
- `proposed_name_formatter.py`
- All specialized formatters

#### 4.3 Integrate MomaApp with Services
- Refactor `app.py` to use service layer
- Replace direct extractor calls with `MetadataService`
- Replace direct file operations with `RenameService`
- Replace direct tree building with `FileTreeService`
- Remove business logic from UI layer

**Expected Benefits**:
- Cleaner separation of concerns
- Easier testing
- Better error handling
- More maintainable code

#### 4.4 Update Imports and Dependencies
- Update all imports to use new architecture
- Remove deprecated patterns
- Verify no circular dependencies
- Update tests to match new structure

---

### Phase 5: Test Coverage (4/6 - 66% Complete)

**Goal**: Achieve comprehensive test coverage for all components.

**Status**: IN PROGRESS

#### ✅ 5.1 Service Layer Tests (COMPLETED)
- 30+ tests for FileTreeService, MetadataService, RenameService
- Integration tests for service workflows

#### ✅ 5.2 Utility Module Tests (COMPLETED)
- 70+ tests for PatternExtractor, LanguageCodeExtractor, FrameClassMatcher
- Integration tests for utility interactions

#### ✅ 5.3 Formatter Tests (COMPLETED)
- 40+ tests for all formatter classes
- FormatterApplier testing

#### ✅ 5.4 Dataset Organization (COMPLETED)
- Consolidated test data into `datasets/`
- 46 filename test cases
- 25 frame class test cases
- Sample file generator

#### ⏳ 5.5 Screen Tests (PENDING)
**Status**: NOT STARTED

**Scope**:
- Test OpenScreen functionality
- Test HelpScreen display
- Test RenameConfirmScreen workflow
- Test SettingsScreen interactions
- Mock user input
- Verify screen transitions

#### ⏳ 5.6 App Integration Tests (PENDING)
**Status**: NOT STARTED

**Scope**:
- End-to-end workflow testing
- Directory scanning → metadata display → rename
- Mode switching (technical/catalog)
- Cache integration
- Error handling flows
- Command palette integration

**Target Coverage**: >90%

---

### Phase 6: Documentation and Release (0/7)

**Goal**: Finalize documentation and prepare for release.

**Status**: NOT STARTED

#### 6.1 Update Technical Documentation
- ✅ AGENTS.md created
- [ ] API documentation generation
- [ ] Architecture diagrams
- [ ] Component interaction flows

#### 6.2 Update User Documentation
- ✅ README.md streamlined
- [ ] User guide with screenshots
- [ ] Common workflows documentation
- [ ] Troubleshooting guide
- [ ] FAQ section

#### 6.3 Update Developer Documentation
- ✅ DEVELOP.md streamlined
- [ ] Contributing guidelines
- [ ] Code review checklist
- [ ] PR template
- [ ] Issue templates

#### 6.4 Create CHANGELOG
- ✅ CHANGELOG.md created
- [ ] Detailed version history
- [ ] Migration guides for breaking changes
- [ ] Deprecation notices

#### 6.5 Version Bump to 0.7.0
- [ ] Update version in `pyproject.toml`
- [ ] Update version in all documentation
- [ ] Tag release in git
- [ ] Create GitHub release

#### 6.6 Build and Test Distribution
- [ ] Build wheel and tarball
- [ ] Test installation from distribution
- [ ] Verify all commands work
- [ ] Test on clean environment
- [ ] Cross-platform testing

#### 6.7 Prepare for PyPI Release (Optional)
- [ ] Create PyPI account
- [ ] Configure package metadata
- [ ] Test upload to TestPyPI
- [ ] Upload to PyPI
- [ ] Verify installation from PyPI

---

## Testing Status

### Current Metrics
- **Total Tests**: 560
- **Pass Rate**: 100% (559 passed, 1 skipped)
- **Coverage**: ~70% (estimated)
- **Target**: >90%

### Manual Testing Checklist
- [ ] Test with large directories (1000+ files)
- [ ] Test with various video formats
- [ ] Test TMDB integration with real API
- [ ] Test poster download and display
- [ ] Test cache expiration and cleanup
- [ ] Test concurrent file operations
- [ ] Test error recovery
- [ ] Test resource cleanup (no leaks)
- [ ] Performance regression testing

---

## Known Limitations

### Current Issues
- TMDB API requires internet connection
- Poster display requires image-capable terminal
- Some special characters need sanitization
- Large directories may have slow initial scan

### Planned Fixes
- Add offline mode with cached data
- Graceful degradation for terminal without image support
- Improve filename sanitization
- Optimize directory scanning with progress indication

---

## Breaking Changes to Consider

### Potential Breaking Changes in 0.7.0
- Cache key format (already changed in 0.6.0)
- Service layer API (internal, shouldn't affect users)
- Configuration file schema (may need migration)

### Migration Strategy
- Provide migration scripts where needed
- Document all breaking changes in CHANGELOG
- Maintain backward compatibility where possible
- Deprecation warnings before removal

---

## Performance Goals

### Current Performance
- ~2 seconds for 100 files (initial scan)
- ~50ms per file (metadata extraction with cache)
- ~200ms per file (TMDB lookup)

### Target Performance
- <1 second for 100 files
- <30ms per file (cached)
- <100ms per file (TMDB with cache)
- Background loading for large directories

---

## Architecture Improvements

### Already Implemented (Phase 2)
- ✅ Protocol-based extractors
- ✅ Service layer
- ✅ Utility modules
- ✅ Unified cache subsystem
- ✅ Thread pool for concurrent operations

### Future Improvements
- [ ] Plugin system for custom extractors/formatters
- [ ] Event-driven architecture for UI updates
- [ ] Dependency injection container
- [ ] Configuration validation schema
- [ ] API versioning

---

## Success Criteria

### Phase 4 Complete When:
- [ ] All extractors implement Protocol
- [ ] All formatters use base classes
- [ ] MomaApp uses services exclusively
- [ ] No direct business logic in UI
- [ ] All tests passing
- [ ] No performance regression

### Phase 5 Complete When:
- [ ] >90% code coverage
- [ ] All screens tested
- [ ] Integration tests complete
- [ ] Manual testing checklist done
- [ ] Performance goals met

### Phase 6 Complete When:
- [ ] All documentation updated
- [ ] Version bumped to 0.7.0
- [ ] Distribution built and tested
- [ ] Release notes published
- [ ] Migration guide available

---

## Next Steps

1. **Start Phase 4**: Refactor to new architecture
   - Begin with extractor Protocol implementation
   - Update one extractor at a time
   - Run tests after each change
   - Document any issues encountered

2. **Complete Phase 5**: Finish test coverage
   - Add screen tests
   - Add integration tests
   - Run coverage analysis
   - Fix any gaps

3. **Execute Phase 6**: Documentation and release
   - Update all docs
   - Build distribution
   - Test thoroughly
   - Release v0.7.0

---

**See Also**:
- [CHANGELOG.md](CHANGELOG.md) - Completed work
- [ToDo.md](ToDo.md) - Future feature requests
- [AGENTS.md](AGENTS.md) - Technical documentation

**Last Updated**: 2026-04-11
