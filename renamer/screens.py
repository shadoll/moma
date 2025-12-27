from textual.screen import Screen
from textual.widgets import Input, Button, Static
from textual.containers import Vertical, Horizontal, Center, Container
from rich.markup import escape
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
        self.app.scan_dir = path
        self.app.scan_files()
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
• p: Expand/Collapse - Toggle expansion of selected directory
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
    Button {
        background: $surface;
        border: solid $surface;
    }
    Button:focus {
        background: $primary;
        color: $text-primary;
        border: solid $primary;
    }
    #buttons {
        align: center middle;
    }
    """

    def __init__(self, old_path: Path, new_name: str):
        super().__init__()
        self.old_path = old_path
        self.new_name = new_name
        self.new_path = old_path.parent / new_name

    def compose(self):
        from .formatters.text_formatter import TextFormatter
        
        confirm_text = f"""
{TextFormatter.bold(TextFormatter.red("RENAME CONFIRMATION"))}

Current name: {TextFormatter.cyan(escape(self.old_path.name))}
New name:     {TextFormatter.green(escape(self.new_name))}

{TextFormatter.yellow("This action cannot be undone!")}

Do you want to proceed with renaming?
        """.strip()

        with Center():
            with Vertical():
                yield Static(confirm_text, id="confirm_content", markup=True)
                with Horizontal(id="buttons"):
                    yield Button("Rename (y)", id="rename")
                    yield Button("Cancel (n)", id="cancel")

    def on_mount(self):
        self.set_focus(self.query_one("#rename"))

    def on_button_pressed(self, event):
        if event.button.id == "rename":
            try:
                self.old_path.rename(self.new_path)
                # Update the tree node
                self.app.update_renamed_file(self.old_path, self.new_path)
                self.app.pop_screen()
            except Exception as e:
                # Show error
                content = self.query_one("#confirm_content", Static)
                content.update(f"Error renaming file: {str(e)}")
        elif event.button.id == "cancel":
            self.app.pop_screen()

    def on_key(self, event):
        if event.key == "left":
            self.set_focus(self.query_one("#rename"))
        elif event.key == "right":
            self.set_focus(self.query_one("#cancel"))
        elif event.key == "y":
            # Trigger rename
            try:
                self.old_path.rename(self.new_path)
                # Update the tree node
                self.app.update_renamed_file(self.old_path, self.new_path)
                self.app.pop_screen()
            except Exception as e:
                # Show error
                content = self.query_one("#confirm_content", Static)
                content.update(f"Error renaming file: {str(e)}")
        elif event.key == "n":
            # Cancel
            self.app.pop_screen()