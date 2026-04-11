from textual.screen import Screen
from textual.widgets import Input, Button
from pathlib import Path


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
