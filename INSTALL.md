# Installation Guide for moma

moma is a terminal-based media file renamer and metadata viewer built with Python and Textual.

## Prerequisites

- Python 3.12 or higher
- UV package manager (recommended) or pip

## Installation Methods

### Method 1: UV Tool Install (Recommended)

This is the easiest way to install and use moma globally on your system.

#### Install UV (if not already installed)
```bash
# On Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.sh | iex"
```

#### Install moma
```bash
# Always-latest (recommended, no version to update)
uv tool install https://github.com/shadoll/moma/releases/latest/download/moma-latest.tar.gz

# Specific version
uv tool install https://github.com/shadoll/moma/releases/download/v0.9.9/moma-0.9.9-py3-none-any.whl

# From PyPI (when published)
uv tool install moma
```

#### Reinstall / Upgrade moma
```bash
# Reinstall (same URL — force overwrite)
uv tool install --force https://github.com/shadoll/moma/releases/latest/download/moma-latest.tar.gz

# Upgrade to a newer specific version
uv tool install --force https://github.com/shadoll/moma/releases/download/v0.9.9/moma-0.9.9-py3-none-any.whl
```

#### Usage
```bash
moma                    # Scan current directory
moma /path/to/directory # Scan specific directory
```

### Method 2: pip Install from Wheel

```bash
# Always-latest (recommended, no version to update)
pip install https://github.com/shadoll/moma/releases/latest/download/moma-latest.tar.gz

# Specific version
pip install https://github.com/shadoll/moma/releases/download/v0.9.9/moma-0.9.9-py3-none-any.whl
```

### Method 3: Development Installation

For development or if you want to run from source:

#### Clone and Setup
```bash
git clone git@github.com:shadoll/moma.git
cd moma

# Install dependencies
uv sync

# Run directly
uv run python src/main.py
uv run python src/main.py /path/to/directory
```

#### Install in Development Mode
```bash
uv sync
uv tool install --editable .
```

### Method 4: Direct Python Execution

If you prefer not to install globally:

```bash
# Ensure you have Python 3.12+
python3 --version

# Install dependencies
pip install textual mutagen pymediainfo python-magic langcodes

# Run the application
python3 src/main.py
python3 src/main.py /path/to/directory
```

## System Requirements

### Linux
- Python 3.12+
- MediaInfo library (for detailed media analysis)
  ```bash
  # Ubuntu/Debian
  sudo apt install libmediainfo-dev

  # Fedora/CentOS
  sudo dnf install libmediainfo-devel

  # Arch Linux
  sudo pacman -S libmediainfo
  ```

### macOS
- Python 3.12+ (via Homebrew or official installer)
- MediaInfo (automatically handled by pymediainfo)

### Windows
- Python 3.12+ (official installer)
- MediaInfo (automatically handled by pymediainfo)

## Downloading Releases

All release packages (`.whl` and `.tar.gz`) are attached to each [GitHub Release](https://github.com/shadoll/moma/releases). Releases are built automatically by CI when a version tag (`v*.*.*`) is pushed.

---

## Verification

After installation, verify it works:

```bash
moma --help
```

You should see the help text for the moma application.

## Troubleshooting

### Common Issues

1. **"Command not found"**
   - Ensure UV bin directory is in your PATH
   - Try `uv tool install` again

2. **Import errors**
   - Ensure all dependencies are installed
   - Try `uv sync` or `pip install -r requirements.txt`

3. **Permission errors**
   - Use `sudo` for system-wide pip installs
   - Or use UV tool install which handles permissions

4. **MediaInfo not found**
   - Install system MediaInfo library
   - Or use basic mode (limited functionality)

### Getting Help

If you encounter issues:
1. Check the [README.md](README.md) for usage instructions
2. Verify your Python version: `python3 --version`
3. Check UV installation: `uv --version`

## Uninstallation

### UV Tool Uninstall
```bash
uv tool uninstall moma
```

### pip Uninstall
```bash
pip uninstall moma
```

### Development Uninstall
```bash
uv tool uninstall moma
# Remove the cloned directory if desired
```</content>
<parameter name="filePath">/Users/sha/Developer/sha.dev/moma/INSTALL.md