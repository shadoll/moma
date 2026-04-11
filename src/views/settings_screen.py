from textual.screen import Screen
from textual.widgets import Input, Button, Static
from textual.containers import Vertical, Horizontal, Center


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
        from ..formatters.text_formatter import TextFormatter

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
                    yield Button("ASCII", id="poster_pseudo", variant="primary" if settings.get("poster") == "pseudo" else "default")
                    yield Button("Viu", id="poster_viu", variant="primary" if settings.get("poster") == "viu" else "default")
                    yield Button("RichPixels", id="poster_richpixels", variant="primary" if settings.get("poster") == "richpixels" else "default")

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
            poster_mode = event.button.id.split("_", 1)[1]  # Use split with maxsplit=1 to handle "richpixels"
            self.app.settings.set("poster", poster_mode)  # type: ignore
            # Update button variants
            no_btn = self.query_one("#poster_no", Button)
            pseudo_btn = self.query_one("#poster_pseudo", Button)
            viu_btn = self.query_one("#poster_viu", Button)
            richpixels_btn = self.query_one("#poster_richpixels", Button)
            no_btn.variant = "primary" if poster_mode == "no" else "default"
            pseudo_btn.variant = "primary" if poster_mode == "pseudo" else "default"
            viu_btn.variant = "primary" if poster_mode == "viu" else "default"
            richpixels_btn.variant = "primary" if poster_mode == "richpixels" else "default"
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
