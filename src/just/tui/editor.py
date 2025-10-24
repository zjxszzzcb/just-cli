import os

from textual.app import App
from textual.widgets import TextArea as TextArea, Footer, Header
from textual.containers import Vertical


class EditArea(TextArea):
    BINDINGS = [
        ("ctrl+a", "select_all", "Select All"),
        ("tab", "indent", "Indent"),
        ("shift+tab", "unindent", "Unindent"),
    ]

    def action_indent(self):
        """Indent current line or selected lines"""
        selection = self.selection
        if selection.start[0] == selection.end[0]:
            cursor = self.cursor_location
            line_idx = cursor[0]
            line = self.document.get_line(line_idx)
            self.replace(f"    {line}", (line_idx, 0), (line_idx, len(line)))
            self.move_cursor((cursor[0], cursor[1] + 4))
        else:
            start_row = min(selection.start[0], selection.end[0])
            end_row = max(selection.start[0], selection.end[0])
            
            for row in range(end_row, start_row - 1, -1):
                line = self.document.get_line(row)
                self.replace(f"    {line}", (row, 0), (row, len(line)))

    def action_unindent(self):
        """Unindent current line or selected lines"""
        selection = self.selection
        if selection.start[0] == selection.end[0]:
            cursor = self.cursor_location
            line_idx = cursor[0]
            line = self.document.get_line(line_idx)
            if line.startswith("    "):
                self.replace(line[4:], (line_idx, 0), (line_idx, len(line)))
                self.move_cursor((cursor[0], max(0, cursor[1] - 4)))
            elif line.startswith("\t"):
                self.replace(line[1:], (line_idx, 0), (line_idx, len(line)))
                self.move_cursor((cursor[0], max(0, cursor[1] - 1)))
        else:
            start_row = min(selection.start[0], selection.end[0])
            end_row = max(selection.start[0], selection.end[0])
            
            for row in range(end_row, start_row - 1, -1):
                line = self.document.get_line(row)
                if line.startswith("    "):
                    self.replace(line[4:], (row, 0), (row, len(line)))
                elif line.startswith("\t"):
                    self.replace(line[1:], (row, 0), (row, len(line)))


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
        self.is_modified = False
        self.original_content = ""

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
            self.original_content = content
            self.text_area.load_text(content)
            self.title = f"Editing: {self.file_path}"
        else:
            self.text_area.text = ""
            self.title = f"New file: {self.file_path}"

    def on_text_area_changed(self, _event):
        """Track if content has been modified"""
        self.is_modified = self.text_area.text != self.original_content
        if self.is_modified:
            self.title = f"*Editing: {self.file_path}"
        else:
            self.title = f"Editing: {self.file_path}"

    def action_save(self):
        """Save the current content to file"""
        content = self.text_area.text
        with open(self.file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        self.original_content = content
        self.is_modified = False
        self.title = f"Saved: {self.file_path}"
