# Developer Guide

**Version**: 0.8.11
**Last Updated**: 2026-04-11

> **📘 For complete development documentation, see [AGENTS.md](AGENTS.md)**

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

See [AGENTS.md - Testing Strategy](AGENTS.md#testing-strategy)

---

## Release Process

```bash
# 1. Bump version (increments patch in pyproject.toml)
uv run bump-version

# 2. Run full release (bump + sync + build)
uv run release

# 3. Test installation locally
uv tool install .

# 4. Manual testing
uv run moma /path/to/test/media

# 5. Tag and push — CI builds and publishes to GitHub Releases automatically
git tag v$(grep '^version' pyproject.toml | grep -o '[0-9.]*')
git push origin main --tags
```

### CI / GitHub Actions

Two workflows live in `.github/workflows/`:

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `ci.yml` | Push to `main`, PRs | Run tests + mypy on Python 3.12 |
| `release.yml` | Push of `v*.*.*` tag | Run tests, build wheel + tarball, publish as GitHub Release |

**To publish a release**: bump version → commit → `git tag vX.Y.Z` → `git push --tags`. CI handles the rest.

See [AGENTS.md - Release Process](AGENTS.md#release-process)

---

## Documentation

- **[AGENTS.md](AGENTS.md)** - Complete technical reference
- **[README.md](README.md)** - User guide
- **[INSTALL.md](INSTALL.md)** - Installation instructions
- **[CHANGELOG.md](CHANGELOG.md)** - Version history
- **[docs/REFACTORING_PROGRESS.md](docs/REFACTORING_PROGRESS.md)** - Future plans
- **[docs/ToDo.md](docs/ToDo.md)** - Current tasks

---

**For complete documentation, see [AGENTS.md](AGENTS.md)**
