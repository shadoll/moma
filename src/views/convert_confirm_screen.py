from textual.screen import Screen
from textual.widgets import Button, Static
from textual.containers import Vertical, Horizontal, Center
from textual.markup import escape
from pathlib import Path


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
        from ..formatters.text_formatter import TextFormatter

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
                    yield Button("Convert Copy (y)", id="convert_copy", variant="success")
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
        app = self.app
        settings = app.settings # type: ignore

        # Get CRF and preset from settings if using HEVC
        crf = settings.get("hevc_crf", 23) if encode_hevc else 18
        preset = settings.get("hevc_preset", "fast") if encode_hevc else "medium"

        mode_str = f"HEVC CRF {crf} ({preset})" if encode_hevc else "Copy"
        app.notify(f"Starting conversion ({mode_str})...", severity="information", timeout=2)

        def do_conversion():
            from ..services.conversion_service import ConversionService
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
        if event.key == "y":
            # Copy mode
            self._do_conversion(encode_hevc=False)
        elif event.key == "e":
            # HEVC mode
            self._do_conversion(encode_hevc=True)
        elif event.key == "n" or event.key == "escape":
            self.app.pop_screen()  # type: ignore
