from textual.screen import Screen
from textual.widgets import Input, Button, Static
from textual.containers import Vertical, Horizontal, Center
from textual.markup import escape
from pathlib import Path
import logging


class RenameConfirmScreen(Screen):
    CSS = """
    #confirm_content {
        text-align: center;
    }
    # Button {
    #     background: $surface;
    #     border: solid $surface;
    }
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
        from ..formatters.text_formatter import TextFormatter

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
            from ..formatters.text_formatter import TextFormatter
            display = self.query_one("#new_name_display", Static)
            display.update(f"{TextFormatter.green(escape(self.new_name))}")

    def on_button_pressed(self, event):
        if event.button.id == "rename":
            # Check if new name is the same as old name
            if self.new_name == self.old_path.name:
                self.app.notify("Proposed name is the same as current name; no rename needed.", severity="information", timeout=3)
                self.app.pop_screen()
                return

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
