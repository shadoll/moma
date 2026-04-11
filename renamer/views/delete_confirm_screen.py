from textual.screen import Screen
from textual.widgets import Button, Static
from textual.containers import Vertical, Horizontal, Center
from textual.markup import escape
from pathlib import Path
import logging


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
        from ..formatters.text_formatter import TextFormatter

        title_text = f"{TextFormatter.bold(TextFormatter.red('DELETE FILE'))}"

        # Build file details
        file_size = self.file_path.stat().st_size if self.file_path.exists() else 0
        from ..formatters.size_formatter import SizeFormatter
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
