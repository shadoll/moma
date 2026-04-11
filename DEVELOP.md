# Developer Guide

**Version**: 0.7.0-dev
**Last Updated**: 2026-01-01

> **📘 For complete development documentation, see [ENGINEERING_GUIDE.md](ENGINEERING_GUIDE.md)**

Quick reference for developers working on the moma project.

---

## Quick Setup

```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and setup
cd /Users/sha/Developer/sha.dev/moma
uv sync --extra dev
```

---

## Essential Commands

```bash
# Run from source
uv run moma [directory]

# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=src

# Type check
uv run mypy src/

# Version bump
uv run bump-version

# Full release
uv run release

# Build distribution
uv build
```

---

## Debugging

```bash
# Enable detailed logging
FORMATTER_LOG=1 uv run moma /path/to/directory

# Check logs
cat formatter.log

# Clear cache
rm -rf ~/.cache/moma/
```

---

## Testing

```bash
# All tests
uv run pytest

# Specific file
uv run pytest src/test/test_services.py

# Verbose
uv run pytest -xvs

# Generate sample files
uv run python src/test/fill_sample_mediafiles.py
```

See [ENGINEERING_GUIDE.md - Testing Strategy](ENGINEERING_GUIDE.md#testing-strategy)

---

## Release Process

```bash
# 1. Bump version
uv run bump-version

# 2. Run full release
uv run release

# 3. Test installation
uv tool install .

# 4. Manual testing
uv run moma /path/to/test/media
```

See [ENGINEERING_GUIDE.md - Release Process](ENGINEERING_GUIDE.md#release-process)

---

## Documentation

- **[ENGINEERING_GUIDE.md](ENGINEERING_GUIDE.md)** - Complete technical reference
- **[README.md](README.md)** - User guide
- **[INSTALL.md](INSTALL.md)** - Installation instructions
- **[CHANGELOG.md](CHANGELOG.md)** - Version history
- **[REFACTORING_PROGRESS.md](REFACTORING_PROGRESS.md)** - Future plans
- **[ToDo.md](ToDo.md)** - Current tasks

---

**For complete documentation, see [ENGINEERING_GUIDE.md](ENGINEERING_GUIDE.md)**
