import os

from textual.app import App
from textual.widgets import TextArea as TextArea, Footer, Header
from textual.containers import Vertical


class EditArea(TextArea):
    BINDINGS = [
        ("ctrl+a", "select_all", "Select All")
    ]


class FileEditor(App):
    """A simple TUI file editor using Textual"""

    CSS = """
    TextArea {
        height: 1fr;
    }
    """

    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path
        self.text_area = EditArea(id="editor")

    BINDINGS = [
        ("escape", "quit", "Quit"),
        ("ctrl+q", "quit", "Quit"),
        ("ctrl+s", "save", "Save"),
    ]

    def compose(self):
        """Create the UI layout"""
        yield Header()
        yield Vertical(self.text_area, Footer())

    def on_mount(self):
        """Load file content when the app starts"""
        if os.path.exists(self.file_path):
            with open(self.file_path, encoding='utf-8') as f:
                content = f.read()
            self.text_area.text = content
            self.title = f"Editing: {self.file_path}"
        else:
            self.text_area.text = ""
            self.title = f"New file: {self.file_path}"

    def action_save(self):
        """Save the current content to file"""
        # Ensure parent directory exists
        # Save the file
        content = self.text_area.text
        with open(self.file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        # Update title to show saved status
        self.title = f"Saved: {self.file_path}"
