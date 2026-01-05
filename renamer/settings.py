import json
import os
import threading
from pathlib import Path
from typing import Dict, Any, Optional


class Settings:
    """Manages application settings stored in a JSON file (Singleton)."""

    DEFAULTS = {
        "mode": "technical",  # "technical" or "catalog"
        "poster": "no",  # "no", "pseudo" (ASCII art), "viu", "richpixels"
        "hevc_crf": 23,  # HEVC quality: 18=visually lossless, 23=high quality, 28=balanced
        "hevc_preset": "fast",  # HEVC speed: ultrafast, veryfast, faster, fast, medium, slow
        "cache_ttl_extractors": 21600,  # 6 hours in seconds
        "cache_ttl_tmdb": 21600,  # 6 hours in seconds
        "cache_ttl_posters": 2592000,  # 30 days in seconds
    }

    _instance: Optional['Settings'] = None
    _lock = threading.Lock()

    def __new__(cls, config_dir: Path | None = None):
        """Create or return singleton instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, config_dir: Path | None = None):
        """Initialize settings (only once)."""
        # Only initialize once
        if self._initialized:
            return

        if config_dir is None:
            config_dir = Path.home() / ".config" / "renamer"
        self.config_dir = config_dir
        self.config_file = self.config_dir / "config.json"
        self._settings = self.DEFAULTS.copy()
        self._initialized = True
        self.load()

    def load(self) -> None:
        """Load settings from file, using defaults if file doesn't exist."""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    data = json.load(f)
                    # Validate and merge with defaults
                    for key, default_value in self.DEFAULTS.items():
                        if key in data:
                            # Basic type checking
                            if isinstance(data[key], type(default_value)):
                                self._settings[key] = data[key]
                            else:
                                print(f"Warning: Invalid type for {key}, using default")
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load settings: {e}, using defaults")
        else:
            # Create config directory and file with defaults
            self.save()

    def save(self) -> None:
        """Save current settings to file."""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, "w") as f:
                json.dump(self._settings, f, indent=2)
        except IOError as e:
            print(f"Error: Could not save settings: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value."""
        return self._settings.get(key, self.DEFAULTS.get(key, default))

    def set(self, key: str, value: Any) -> None:
        """Set a setting value and save."""
        if key in self.DEFAULTS:
            # Basic type checking
            if isinstance(value, type(self.DEFAULTS[key])):
                self._settings[key] = value
                self.save()
            else:
                raise ValueError(f"Invalid type for setting {key}")
        else:
            raise KeyError(f"Unknown setting: {key}")

    def get_all(self) -> Dict[str, Any]:
        """Get all current settings."""
        return self._settings.copy()
