from textual.screen import Screen
from textual.widgets import Input, Button, Static
from textual.containers import Vertical, Horizontal, Center, Container
from textual.markup import escape
from pathlib import Path
import logging


class OpenScreen(Screen):
    def compose(self):
        yield Input(placeholder="Enter directory path", value=".", id="dir_input")
        yield Button("OK", id="ok")

    def on_button_pressed(self, event):
        if event.button.id == "ok":
            self.submit_path()

    def on_input_submitted(self, event):
        self.submit_path()

    def submit_path(self):
        path_str = self.query_one("#dir_input", Input).value
        path = Path(path_str)
        if not path.exists():
            # Show error
            self.query_one("#dir_input", Input).value = f"Path does not exist: {path_str}"
            return
        if not path.is_dir():
            self.query_one("#dir_input", Input).value = f"Not a directory: {path_str}"
            return
        self.app.scan_dir = path # type: ignore
        self.app.scan_files() # type: ignore
        self.app.pop_screen()


class HelpScreen(Screen):
    def compose(self):
        try:
            from importlib.metadata import version
            app_version = version("renamer")
        except Exception:
            app_version = "unknown"
        
        help_text = f"""
Media File Renamer v{app_version}

A powerful tool for analyzing and renaming media files with intelligent metadata extraction.

NAVIGATION:
• Use arrow keys to navigate the file tree
• Right arrow: Expand directory
• Left arrow: Collapse directory
• Enter/Space: Select file

ACTIONS:
• o: Open directory - Change the scan directory
• s: Scan - Refresh the current directory
• f: Refresh - Reload metadata for selected file
• r: Rename - Rename selected file with proposed name
• c: Convert - Convert AVI file to MKV container with metadata
• d: Delete - Delete selected file (with confirmation)
• p: Expand/Collapse - Toggle expansion of selected directory
• m: Toggle Mode - Switch between technical and catalog display modes
• ctrl+s: Settings - Open settings window
• ctrl+p: Command Palette - Access cache commands and more
• h: Help - Show this help screen
• q: Quit - Exit the application

FEATURES:
• Automatic metadata extraction from filenames
• MediaInfo integration for technical details
• Intelligent title, year, and format detection
• Support for special editions and collections
• Real-time file analysis and renaming suggestions

FILE ANALYSIS:
The app extracts various metadata including:
• Movie/series titles and years
• Video resolution and frame rates
• Audio languages and formats
• Special edition information
• Collection order numbers
• HDR and source information

Press any key to close this help screen.
        """.strip()

        with Vertical():
            yield Static(help_text, id="help_content")
            yield Button("Close", id="close")

    def on_button_pressed(self, event):
        if event.button.id == "close":
            self.app.pop_screen()

    def on_key(self, event):
        # Close on any key press
        self.app.pop_screen()


class RenameConfirmScreen(Screen):
    CSS = """
    #confirm_content {
        text-align: center;
    }
    # Button {
    #     background: $surface;
    #     border: solid $surface;
    # }
    Button:focus {
         background: $primary;
    #     color: $text-primary;
    #     border: solid $primary;
    }
    #buttons {
        align: center middle;
    }
    #new_name_input {
        width: 100%;
        margin: 1 0;
    }
    #new_name_display {
        text-align: center;
        margin-bottom: 1;
    }
    #warning_content {
        text-align: center;
        margin-bottom: 0;
    }
    """

    def __init__(self, old_path: Path, new_name: str):
        super().__init__()
        self.old_path = old_path
        self.new_name = new_name.replace("/", "-").replace("\\", "-")
        self.new_path = old_path.parent / self.new_name
        self.was_edited = False

    def compose(self):
        from .formatters.text_formatter import TextFormatter
        
        confirm_text = f"""
{TextFormatter.bold(TextFormatter.red("RENAME CONFIRMATION"))}

RAW name: {escape(self.old_path.name)}

Current name:  {TextFormatter.cyan(escape(self.old_path.name))}
Proposed name: {TextFormatter.green(escape(self.new_name))}

{TextFormatter.yellow("Edit the new name below:")}
        """.strip()

        warning_text = f"""
{TextFormatter.bold(TextFormatter.red("This action cannot be undone!"))}
Do you want to proceed with renaming?
        """.strip()

        with Center():
            with Vertical():
                yield Static(confirm_text, id="confirm_content", markup=True)
                yield Input(value=self.new_name, id="new_name_input", placeholder="New file name")
                yield Static(f"{TextFormatter.green(escape(self.new_name))}", id="new_name_display", markup=True)
                yield Static(warning_text, id="warning_content", markup=True)
                with Horizontal(id="buttons"):
                    yield Button("Rename (y)", id="rename")
                    yield Button("Cancel (n)", id="cancel")

    def on_mount(self):
        self.set_focus(self.query_one("#rename"))

    def on_input_changed(self, event):
        if event.input.id == "new_name_input":
            self.new_name = event.input.value.replace("/", "-").replace("\\", "-")
            self.new_path = self.old_path.parent / self.new_name
            self.was_edited = True
            # Update the display
            from .formatters.text_formatter import TextFormatter
            display = self.query_one("#new_name_display", Static)
            display.update(f"{TextFormatter.green(escape(self.new_name))}")

    def on_button_pressed(self, event):
        if event.button.id == "rename":
            try:
                logging.info(f"Starting rename: old_path={self.old_path}, new_path={self.new_path}")
                logging.info(f"Old file name: {self.old_path.name}")
                logging.info(f"New file name: {self.new_name}")
                logging.info(f"New path parent: {self.new_path.parent}, Old path parent: {self.old_path.parent}")
                if "/" in self.new_name or "\\" in self.new_name:
                    logging.warning(f"New name contains path separators: {self.new_name}")
                self.old_path.rename(self.new_path)
                logging.info(f"Rename successful: {self.old_path} -> {self.new_path}")
                # Update the tree node
                self.app.update_renamed_file(self.old_path, self.new_path) # type: ignore
                self.app.pop_screen()
            except Exception as e:
                logging.error(f"Rename failed: {self.old_path} -> {self.new_path}, error: {str(e)}")
                # Show error
                content = self.query_one("#confirm_content", Static)
                content.update(f"Error renaming file: {str(e)}")
        elif event.button.id == "cancel":
            self.app.pop_screen()

    def on_key(self, event):
        current = self.focused
        if current and hasattr(current, 'id'):
            if current.id == "new_name_input":
                # When input is focused, let left/right move cursor, use up/down to change focus
                if event.key == "up":
                    self.set_focus(self.query_one("#cancel"))
                elif event.key == "down":
                    self.set_focus(self.query_one("#rename"))
            elif current.id in ("rename", "cancel"):
                if event.key == "left":
                    if current.id == "rename":
                        self.set_focus(self.query_one("#new_name_input"))
                    elif current.id == "cancel":
                        self.set_focus(self.query_one("#rename"))
                elif event.key == "right":
                    if current.id == "new_name_input":
                        self.set_focus(self.query_one("#rename"))
                    elif current.id == "rename":
                        self.set_focus(self.query_one("#cancel"))
                elif event.key == "up":
                    if current.id == "rename":
                        self.set_focus(self.query_one("#new_name_input"))
                    elif current.id == "cancel":
                        self.set_focus(self.query_one("#rename"))
                elif event.key == "down":
                    if current.id == "new_name_input":
                        self.set_focus(self.query_one("#rename"))
                    elif current.id == "rename":
                        self.set_focus(self.query_one("#cancel"))
                    elif current.id == "cancel":
                        self.set_focus(self.query_one("#new_name_input"))
        
        # Hotkeys only work when not focused on input
        if not current or not hasattr(current, 'id') or current.id != "new_name_input":
            if event.key == "y":
                # Trigger rename
                try:
                    logging.info(f"Hotkey rename: old_path={self.old_path}, new_path={self.new_path}")
                    logging.info(f"Old file name: {self.old_path.name}")
                    logging.info(f"New file name: {self.new_name}")
                    logging.info(f"New path parent: {self.new_path.parent}, Old path parent: {self.old_path.parent}")
                    if "/" in self.new_name or "\\" in self.new_name:
                        logging.warning(f"New name contains path separators: {self.new_name}")
                    self.old_path.rename(self.new_path)
                    logging.info(f"Hotkey rename successful: {self.old_path} -> {self.new_path}")
                    # Update the tree node
                    self.app.update_renamed_file(self.old_path, self.new_path) # type: ignore
                    self.app.pop_screen()
                except Exception as e:
                    logging.error(f"Hotkey rename failed: {self.old_path} -> {self.new_path}, error: {str(e)}")
                    # Show error
                    content = self.query_one("#confirm_content", Static)
                    content.update(f"Error renaming file: {str(e)}")
            elif event.key == "n":
                # Cancel
                self.app.pop_screen()


class SettingsScreen(Screen):
    CSS = """
    #settings_content {
        text-align: center;
    }
    Button:focus {
         background: $primary;
    }
    #buttons {
        align: center middle;
    }
    .input_field {
        width: 100%;
        margin: 1 0;
    }
    .label {
        text-align: left;
        margin-bottom: 0;
    }
    """

    def compose(self):
        from .formatters.text_formatter import TextFormatter
        
        settings = self.app.settings  # type: ignore
        
        content = f"""
{TextFormatter.bold("SETTINGS")}

Configure application settings.
        """.strip()

        with Center():
            with Vertical():
                yield Static(content, id="settings_content", markup=True)
                
                # Mode selection
                yield Static("Display Mode:", classes="label")
                with Horizontal():
                    yield Button("Technical", id="mode_technical", variant="primary" if settings.get("mode") == "technical" else "default")
                    yield Button("Catalog", id="mode_catalog", variant="primary" if settings.get("mode") == "catalog" else "default")

                # Poster selection
                yield Static("Poster Display (Catalog Mode):", classes="label")
                with Horizontal():
                    yield Button("No", id="poster_no", variant="primary" if settings.get("poster") == "no" else "default")
                    yield Button("Pseudo", id="poster_pseudo", variant="primary" if settings.get("poster") == "pseudo" else "default")
                    yield Button("Viu", id="poster_viu", variant="primary" if settings.get("poster") == "viu" else "default")

                # HEVC quality selection
                yield Static("HEVC Encoding Quality (for conversions):", classes="label")
                with Horizontal():
                    yield Button("CRF 18 (Visually Lossless)", id="hevc_crf_18", variant="primary" if settings.get("hevc_crf") == 18 else "default")
                    yield Button("CRF 23 (High Quality)", id="hevc_crf_23", variant="primary" if settings.get("hevc_crf") == 23 else "default")
                    yield Button("CRF 28 (Balanced)", id="hevc_crf_28", variant="primary" if settings.get("hevc_crf") == 28 else "default")

                # HEVC preset selection
                yield Static("HEVC Encoding Speed (faster = lower quality/smaller file):", classes="label")
                with Horizontal():
                    yield Button("Ultrafast", id="hevc_preset_ultrafast", variant="primary" if settings.get("hevc_preset") == "ultrafast" else "default")
                    yield Button("Veryfast", id="hevc_preset_veryfast", variant="primary" if settings.get("hevc_preset") == "veryfast" else "default")
                    yield Button("Fast", id="hevc_preset_fast", variant="primary" if settings.get("hevc_preset") == "fast" else "default")
                    yield Button("Medium", id="hevc_preset_medium", variant="primary" if settings.get("hevc_preset") == "medium" else "default")

                # TTL inputs
                yield Static("Cache TTL - Extractors (hours):", classes="label")
                yield Input(value=str(settings.get("cache_ttl_extractors") // 3600), id="ttl_extractors", classes="input_field")
                
                yield Static("Cache TTL - TMDB (hours):", classes="label")
                yield Input(value=str(settings.get("cache_ttl_tmdb") // 3600), id="ttl_tmdb", classes="input_field")
                
                yield Static("Cache TTL - Posters (days):", classes="label")
                yield Input(value=str(settings.get("cache_ttl_posters") // 86400), id="ttl_posters", classes="input_field")
                
                with Horizontal(id="buttons"):
                    yield Button("Save", id="save")
                    yield Button("Cancel", id="cancel")

    def on_button_pressed(self, event):
        if event.button.id == "save":
            self.save_settings()
            self.app.pop_screen()  # type: ignore
        elif event.button.id == "cancel":
            self.app.pop_screen()  # type: ignore
        elif event.button.id.startswith("mode_"):
            # Toggle mode buttons
            mode = event.button.id.split("_")[1]
            self.app.settings.set("mode", mode)  # type: ignore
            # Update button variants
            tech_btn = self.query_one("#mode_technical", Button)
            cat_btn = self.query_one("#mode_catalog", Button)
            tech_btn.variant = "primary" if mode == "technical" else "default"
            cat_btn.variant = "primary" if mode == "catalog" else "default"
        elif event.button.id.startswith("poster_"):
            # Toggle poster buttons
            poster_mode = event.button.id.split("_")[1]
            self.app.settings.set("poster", poster_mode)  # type: ignore
            # Update button variants
            no_btn = self.query_one("#poster_no", Button)
            pseudo_btn = self.query_one("#poster_pseudo", Button)
            viu_btn = self.query_one("#poster_viu", Button)
            no_btn.variant = "primary" if poster_mode == "no" else "default"
            pseudo_btn.variant = "primary" if poster_mode == "pseudo" else "default"
            viu_btn.variant = "primary" if poster_mode == "viu" else "default"
        elif event.button.id.startswith("hevc_crf_"):
            # Toggle HEVC CRF buttons
            crf_value = int(event.button.id.split("_")[-1])
            self.app.settings.set("hevc_crf", crf_value)  # type: ignore
            # Update button variants
            crf18_btn = self.query_one("#hevc_crf_18", Button)
            crf23_btn = self.query_one("#hevc_crf_23", Button)
            crf28_btn = self.query_one("#hevc_crf_28", Button)
            crf18_btn.variant = "primary" if crf_value == 18 else "default"
            crf23_btn.variant = "primary" if crf_value == 23 else "default"
            crf28_btn.variant = "primary" if crf_value == 28 else "default"
        elif event.button.id.startswith("hevc_preset_"):
            # Toggle HEVC preset buttons
            preset_value = event.button.id.split("_")[-1]
            self.app.settings.set("hevc_preset", preset_value)  # type: ignore
            # Update button variants
            ultrafast_btn = self.query_one("#hevc_preset_ultrafast", Button)
            veryfast_btn = self.query_one("#hevc_preset_veryfast", Button)
            fast_btn = self.query_one("#hevc_preset_fast", Button)
            medium_btn = self.query_one("#hevc_preset_medium", Button)
            ultrafast_btn.variant = "primary" if preset_value == "ultrafast" else "default"
            veryfast_btn.variant = "primary" if preset_value == "veryfast" else "default"
            fast_btn.variant = "primary" if preset_value == "fast" else "default"
            medium_btn.variant = "primary" if preset_value == "medium" else "default"

    def save_settings(self):
        try:
            # Get values and convert to seconds
            ttl_extractors = int(self.query_one("#ttl_extractors", Input).value) * 3600
            ttl_tmdb = int(self.query_one("#ttl_tmdb", Input).value) * 3600
            ttl_posters = int(self.query_one("#ttl_posters", Input).value) * 86400
            
            self.app.settings.set("cache_ttl_extractors", ttl_extractors)  # type: ignore
            self.app.settings.set("cache_ttl_tmdb", ttl_tmdb)  # type: ignore
            self.app.settings.set("cache_ttl_posters", ttl_posters)  # type: ignore

            self.app.notify("Settings saved!", severity="information", timeout=2)  # type: ignore
        except ValueError:
            self.app.notify("Invalid TTL values. Please enter numbers only.", severity="error", timeout=3)  # type: ignore


class ConvertConfirmScreen(Screen):
    """Confirmation screen for AVI to MKV conversion."""

    CSS = """
    #convert_content {
        text-align: center;
    }
    Button:focus {
        background: $primary;
    }
    #buttons {
        align: center middle;
    }
    #conversion_details {
        text-align: left;
        margin: 1 2;
        padding: 1 2;
        border: solid $primary;
    }
    #warning_content {
        text-align: center;
        margin-bottom: 1;
        margin-top: 1;
    }
    """

    def __init__(
        self,
        avi_path: Path,
        mkv_path: Path,
        audio_languages: list,
        subtitle_files: list,
        extractor
    ):
        super().__init__()
        self.avi_path = avi_path
        self.mkv_path = mkv_path
        self.audio_languages = audio_languages
        self.subtitle_files = subtitle_files
        self.extractor = extractor

    def compose(self):
        from .formatters.text_formatter import TextFormatter

        title_text = f"{TextFormatter.bold(TextFormatter.yellow('MKV CONVERSION'))}"

        # Build details
        details_lines = [
            f"{TextFormatter.bold('Source:')} {TextFormatter.cyan(escape(self.avi_path.name))}",
            f"{TextFormatter.bold('Output:')} {TextFormatter.green(escape(self.mkv_path.name))}",
            "",
            f"{TextFormatter.bold('Audio Languages:')}",
        ]

        # Add audio language mapping
        for i, lang in enumerate(self.audio_languages):
            if lang:
                details_lines.append(f"  Track {i+1}: {TextFormatter.green(lang)}")
            else:
                details_lines.append(f"  Track {i+1}: {TextFormatter.grey('(no language)')}")

        # Add subtitle info
        if self.subtitle_files:
            details_lines.append("")
            details_lines.append(f"{TextFormatter.bold('Subtitles to include:')}")
            for sub_file in self.subtitle_files:
                details_lines.append(f"  • {TextFormatter.blue(escape(sub_file.name))}")
        else:
            details_lines.append("")
            details_lines.append(f"{TextFormatter.grey('No subtitle files found')}")

        details_text = "\n".join(details_lines)

        # Get HEVC CRF from settings
        settings = self.app.settings  # type: ignore
        hevc_crf = settings.get("hevc_crf", 23)

        info_text = f"""
{TextFormatter.bold('Choose conversion mode:')}

{TextFormatter.green('Copy Mode')} - Fast remux, no re-encoding (seconds to minutes)
{TextFormatter.yellow(f'HEVC Mode')} - Re-encode to H.265, CRF {hevc_crf} quality (minutes to hours)
  {TextFormatter.grey('(Change quality in Settings with Ctrl+S)')}
        """.strip()

        with Center():
            with Vertical():
                yield Static(title_text, id="convert_content", markup=True)
                yield Static(details_text, id="conversion_details", markup=True)
                yield Static(info_text, id="info_text", markup=True)
                with Horizontal(id="buttons"):
                    yield Button("Convert Copy (c)", id="convert_copy", variant="success")
                    yield Button("Convert HEVC (e)", id="convert_hevc", variant="primary")
                    yield Button("Cancel (n)", id="cancel", variant="error")

    def on_mount(self):
        self.set_focus(self.query_one("#convert_copy"))

    def on_button_pressed(self, event):
        if event.button.id == "convert_copy":
            self._do_conversion(encode_hevc=False)
            event.stop()  # Prevent key event from also triggering
        elif event.button.id == "convert_hevc":
            self._do_conversion(encode_hevc=True)
            event.stop()  # Prevent key event from also triggering
        elif event.button.id == "cancel":
            self.app.pop_screen()  # type: ignore
            event.stop()  # Prevent key event from also triggering

    def _do_conversion(self, encode_hevc: bool):
        """Start conversion with the specified encoding mode."""
        app = self.app  # type: ignore
        settings = app.settings

        # Get CRF and preset from settings if using HEVC
        crf = settings.get("hevc_crf", 23) if encode_hevc else 18
        preset = settings.get("hevc_preset", "fast") if encode_hevc else "medium"

        mode_str = f"HEVC CRF {crf} ({preset})" if encode_hevc else "Copy"
        app.notify(f"Starting conversion ({mode_str})...", severity="information", timeout=2)

        def do_conversion():
            from .services.conversion_service import ConversionService
            import threading
            import logging

            conversion_service = ConversionService()
            logging.info(f"Starting conversion of {self.avi_path} with encode_hevc={encode_hevc}, crf={crf}, preset={preset}")
            logging.info(f"CPU architecture: {conversion_service.cpu_arch}")

            success, message = conversion_service.convert_avi_to_mkv(
                self.avi_path,
                extractor=self.extractor,
                encode_hevc=encode_hevc,
                crf=crf,
                preset=preset
            )

            logging.info(f"Conversion result: success={success}, message={message}")

            # Schedule UI updates on the main thread
            mkv_path = self.avi_path.with_suffix('.mkv')

            def handle_success():
                logging.info(f"handle_success called: {mkv_path}")
                app.notify(f"✓ {message}", severity="information", timeout=5)
                logging.info(f"Adding file to tree: {mkv_path}")
                app.add_file_to_tree(mkv_path)
                logging.info("Conversion success handler completed")

            def handle_error():
                logging.info(f"handle_error called: {message}")
                app.notify(f"✗ {message}", severity="error", timeout=10)
                logging.info("Conversion error handler completed")

            if success:
                logging.info(f"Conversion successful, scheduling UI update for {mkv_path}")
                app.call_later(handle_success)
            else:
                logging.error(f"Conversion failed: {message}")
                app.call_later(handle_error)

        # Run conversion in background thread
        import threading
        threading.Thread(target=do_conversion, daemon=True).start()

        # Close the screen
        self.app.pop_screen()  # type: ignore

    def on_key(self, event):
        if event.key == "c":
            # Copy mode
            self._do_conversion(encode_hevc=False)
        elif event.key == "e":
            # HEVC mode
            self._do_conversion(encode_hevc=True)
        elif event.key == "n" or event.key == "escape":
            self.app.pop_screen()  # type: ignore


class DeleteConfirmScreen(Screen):
    """Confirmation screen for file deletion."""

    CSS = """
    #delete_content {
        text-align: center;
    }
    Button:focus {
        background: $primary;
    }
    #buttons {
        align: center middle;
    }
    #file_details {
        text-align: left;
        margin: 1 2;
        padding: 1 2;
        border: solid $error;
    }
    #warning_content {
        text-align: center;
        margin-bottom: 1;
        margin-top: 1;
    }
    """

    def __init__(self, file_path: Path):
        super().__init__()
        self.file_path = file_path

    def compose(self):
        from .formatters.text_formatter import TextFormatter

        title_text = f"{TextFormatter.bold(TextFormatter.red('DELETE FILE'))}"

        # Build file details
        file_size = self.file_path.stat().st_size if self.file_path.exists() else 0
        from .formatters.size_formatter import SizeFormatter
        size_str = SizeFormatter.format_size_full(file_size)

        details_lines = [
            f"{TextFormatter.bold('File:')} {TextFormatter.cyan(escape(self.file_path.name))}",
            f"{TextFormatter.bold('Path:')} {TextFormatter.grey(escape(str(self.file_path.parent)))}",
            f"{TextFormatter.bold('Size:')} {TextFormatter.yellow(size_str)}",
        ]

        details_text = "\n".join(details_lines)

        warning_text = f"""
{TextFormatter.bold(TextFormatter.red("WARNING: This action cannot be undone!"))}
{TextFormatter.yellow("The file will be permanently deleted from your system.")}

Are you sure you want to delete this file?
        """.strip()

        with Center():
            with Vertical():
                yield Static(title_text, id="delete_content", markup=True)
                yield Static(details_text, id="file_details", markup=True)
                yield Static(warning_text, id="warning_content", markup=True)
                with Horizontal(id="buttons"):
                    yield Button("No (n)", id="cancel", variant="primary")
                    yield Button("Yes (y)", id="delete", variant="error")

    def on_mount(self):
        # Set focus to "No" button by default (safer option)
        self.set_focus(self.query_one("#cancel"))

    def on_button_pressed(self, event):
        if event.button.id == "delete":
            # Delete the file
            app = self.app  # type: ignore

            try:
                if self.file_path.exists():
                    self.file_path.unlink()
                    app.notify(f"✓ Deleted: {self.file_path.name}", severity="information", timeout=3)
                    logging.info(f"File deleted: {self.file_path}")

                    # Remove from tree
                    app.remove_file_from_tree(self.file_path)
                else:
                    app.notify(f"✗ File not found: {self.file_path.name}", severity="error", timeout=3)

            except PermissionError:
                app.notify(f"✗ Permission denied: Cannot delete {self.file_path.name}", severity="error", timeout=5)
                logging.error(f"Permission denied deleting file: {self.file_path}")
            except Exception as e:
                app.notify(f"✗ Error deleting file: {e}", severity="error", timeout=5)
                logging.error(f"Error deleting file {self.file_path}: {e}", exc_info=True)

            self.app.pop_screen()  # type: ignore
        else:
            # Cancel
            self.app.pop_screen()  # type: ignore

    def on_key(self, event):
        if event.key == "y":
            # Simulate delete button press
            delete_button = self.query_one("#delete")
            self.on_button_pressed(type('Event', (), {'button': delete_button})())
        elif event.key == "n" or event.key == "escape":
            self.app.pop_screen()  # type: ignore