# Installation Guide for Renamer

Renamer is a terminal-based media file renamer and metadata viewer built with Python and Textual.

## Prerequisites

- Python 3.11 or higher
- UV package manager (recommended) or pip

## Installation Methods

### Method 1: UV Tool Install (Recommended)

This is the easiest way to install and use Renamer globally on your system.

#### Install UV (if not already installed)
```bash
# On Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.sh | iex"
```

#### Install Renamer
```bash
# One-command install from remote wheel
uv tool install https://git.shadoll.dev/sha/renamer/raw/branch/main/dist/renamer-0.2.4-py3-none-any.whl

# Or from local wheel (if downloaded)
uv tool install dist/renamer-0.2.4-py3-none-any.whl

# Or from PyPI (when published)
uv tool install renamer
```

#### Usage
```bash
renamer                    # Scan current directory
renamer /path/to/directory # Scan specific directory
```

### Method 2: pip Install from Wheel

If you have the wheel file, you can install it with pip.

```bash
# Install the wheel
pip install dist/renamer-0.2.0-py3-none-any.whl

# Or install globally (may require sudo)
sudo pip install dist/renamer-0.2.0-py3-none-any.whl
```

### Method 3: Development Installation

For development or if you want to run from source:

#### Clone and Setup
```bash
git clone <repository-url>
cd renamer

# Install dependencies
uv sync

# Run directly
uv run python main.py
uv run python main.py /path/to/directory
```

#### Install in Development Mode
```bash
uv sync
uv tool install --editable .
```

### Method 4: Direct Python Execution

If you prefer not to install globally:

```bash
# Ensure you have Python 3.11+
python3 --version

# Install dependencies
pip install textual mutagen pymediainfo python-magic langcodes

# Run the application
python3 main.py
python3 main.py /path/to/directory
```

## System Requirements

### Linux
- Python 3.11+
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
- Python 3.11+ (via Homebrew or official installer)
- MediaInfo (automatically handled by pymediainfo)

### Windows
- Python 3.11+ (official installer)
- MediaInfo (automatically handled by pymediainfo)

## Verification

After installation, verify it works:

```bash
renamer --help
# or
python3 main.py --help
```

You should see the help text for the Renamer application.

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
uv tool uninstall renamer
```

### pip Uninstall
```bash
pip uninstall renamer
```

### Development Uninstall
```bash
uv tool uninstall renamer
# Remove the cloned directory if desired
```</content>
<parameter name="filePath">/home/sha/bin/renamer/INSTALL.md