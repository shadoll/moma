from textual.screen import Screen
from textual.widgets import Static, Button
from textual.containers import Vertical


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
