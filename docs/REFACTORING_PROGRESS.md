# moma - Refactoring Roadmap

**Version**: 0.8.11
**Last Updated**: 2026-04-12

> **📋 For completed work detail, see [CHANGELOG.md](../CHANGELOG.md)**

---

## Completed (Summary)

| Phase | Description | Version |
|-------|-------------|---------|
| ✅ Phase 1 | Critical Bug Fixes — cache key fix, resource leaks, thread safety, logging | 0.7.0 |
| ✅ Phase 2 | Architecture Foundation — `DataExtractor` Protocol, service layer, utility modules, command palette (Ctrl+P) | 0.7.0 |
| ✅ Phase 3 | Code Quality — constants split into 8 modules, type hints, docstrings, dynamic year validation | 0.7.0 |
| ✅ Phase 3.6 | Cleanup — `ProposedFilenameView` moved to decorator pattern; `src/decorators/` dir removed | 0.7.0 |
| ✅ Phase 5 (4/6) | Tests — service, utility, formatter, cache, dataset tests; 560 total, 100% pass rate | 0.7.0 |
| ✅ Phase 6 (partial) | Docs — AGENTS.md, CHANGELOG.md, README.md, DEVELOP.md created/updated | 0.7.0 |

---

## Pending

### Phase 4: Refactor to New Architecture

**Status**: NOT STARTED  
**Goal**: Migrate existing code to fully use the architecture established in Phase 2.

#### 4.1 Refactor Extractors to Use Protocol
- Update all extractors to explicitly implement `DataExtractor` Protocol
- Ensure consistent method signatures and fill missing Protocol methods
- Update type hints throughout

**Files**: `filename_extractor.py`, `mediainfo_extractor.py`, `metadata_extractor.py`, `fileinfo_extractor.py`, `tmdb_extractor.py`

#### 4.2 Refactor Formatters to Use Base Classes
- Update all formatters to inherit from `DataFormatter`, `TextFormatter`, or `MarkupFormatter`
- Ensure consistent interface across formatter hierarchy

**Files**: `catalog_formatter.py`, `track_formatter.py`, and all specialized formatters in `src/formatters/`

#### 4.3 Integrate MomaApp with Services
- Refactor `app.py` to use service layer exclusively
- Replace direct extractor calls with `MetadataService`
- Replace direct file operations with `RenameService`
- Replace direct tree building with `FileTreeService`
- Remove all business logic from UI layer

#### 4.4 Update Imports and Dependencies
- Clean up imports after Phase 4.1–4.3
- Remove deprecated patterns, verify no circular dependencies
- Update tests to match new structure

---

### Phase 5: Test Coverage (4/6 — IN PROGRESS)

#### ⏳ 5.5 Screen Tests
- Test all 6 screens: OpenScreen, HelpScreen, RenameConfirmScreen, ConvertConfirmScreen, DeleteConfirmScreen, SettingsScreen
- Mock user input, verify screen transitions and error handling

#### ⏳ 5.6 App Integration Tests
- End-to-end: directory scan → metadata display → rename
- Mode switching, cache integration, error handling, command palette flows

**Target**: >90% coverage

---

### Phase 6: Documentation and Release (partially done)

#### ✅ Done
- AGENTS.md — comprehensive technical reference
- CHANGELOG.md — version history
- README.md — streamlined user guide
- DEVELOP.md — developer setup

#### Remaining
- [ ] API documentation generation
- [ ] Architecture diagrams and component interaction flows
- [ ] Contributing guidelines, PR/issue templates
- [ ] Build and test distribution (`uv build`, clean install test)
- [ ] PyPI release (optional)

---

### Manual Testing Checklist

- [ ] Large directories (1000+ files)
- [ ] Various video formats
- [ ] TMDB integration with real API key
- [ ] Poster download and display (pseudo/viu/richpixels modes)
- [ ] Cache expiration and cleanup
- [ ] Concurrent file operations
- [ ] Error recovery (missing files, permission errors, network failures)

---

**See Also**:
- [../CHANGELOG.md](../CHANGELOG.md) — Completed work with full details
- [ToDo.md](ToDo.md) — Feature requests and future ideas
- [../AGENTS.md](../AGENTS.md) — Architecture and technical documentation

**Last Updated**: 2026-04-12
