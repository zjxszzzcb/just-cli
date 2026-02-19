"""Minimal workspace editor with file tree and editor"""

from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import DirectoryTree, TextArea, Input, Button, Label


class InputDialog(ModalScreen[str]):
    def __init__(self, placeholder: str = ""):
        super().__init__()
        self._placeholder = placeholder

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label("New note name:", id="prompt")
            yield Input(placeholder=self._placeholder, id="input")
            with Horizontal(id="buttons"):
                yield Button("Create", variant="primary", id="ok")
                yield Button("Cancel", id="cancel")

    def on_mount(self) -> None:
        self.query_one(Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.value.strip():
            self.dismiss(event.value.strip())

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "ok":
            value = self.query_one(Input).value.strip()
            if value:
                self.dismiss(value)
        else:
            self.dismiss("")

    CSS = """
    #dialog {
        align: center middle;
        width: 48;
        background: $surface;
        border: tall $primary;
        padding: 1 2;
    }
    #prompt { padding: 1; text-style: bold; }
    #input { margin: 1 0; }
    #buttons { height: auto; align-horizontal: center; padding: 1; }
    Button { margin: 0 1; min-width: 10; }
    """


class ConfirmDialog(ModalScreen[bool]):
    def __init__(self, filename: str):
        super().__init__()
        self._filename = filename

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label(f"Delete {self._filename}?", id="prompt")
            with Horizontal(id="buttons"):
                yield Button("Delete", variant="error", id="ok")
                yield Button("Cancel", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "ok")

    CSS = """
    #dialog {
        align: center middle;
        width: 36;
        background: $surface;
        border: tall $error;
        padding: 1 2;
    }
    #prompt { padding: 1; text-style: bold; color: $error; }
    #buttons { height: auto; align-horizontal: center; padding: 1; }
    Button { margin: 0 1; min-width: 8; }
    """


class CodeEditor(TextArea):
    def __init__(self, file_path: Path, **kwargs):
        language = self._detect_language(file_path)
        super().__init__(language=language, **kwargs)
        self.file_path = file_path
        self._original_content = ""

    @staticmethod
    def _detect_language(file_path: Path) -> str | None:
        ext_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".json": "json",
            ".html": "html",
            ".css": "css",
            ".md": "markdown",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".toml": "toml",
            ".sh": "bash",
            ".rs": "rust",
            ".go": "go",
            ".java": "java",
            ".c": "c",
            ".cpp": "cpp",
        }
        return ext_map.get(file_path.suffix.lower())

    def load_file(self) -> bool:
        try:
            if self.file_path.exists():
                content = self.file_path.read_text(encoding="utf-8")
                self.text = content
                self._original_content = content
                return True
        except Exception:
            pass
        return False

    def save_file(self) -> bool:
        try:
            self.file_path.write_text(self.text, encoding="utf-8")
            self._original_content = self.text
            return True
        except Exception:
            pass
        return False

    @property
    def is_modified(self) -> bool:
        return self.text != self._original_content


class WorkspaceApp(App):
    CSS = """
    Horizontal {
        height: 1fr;
    }

    #sidebar {
        width: 24;
        dock: left;
        background: $panel;
        border-right: tall $primary;
    }

    DirectoryTree {
        height: 1fr;
    }

    CodeEditor {
        height: 1fr;
    }
    """

    BINDINGS = [
        Binding("ctrl+s", "save", "Save"),
        Binding("ctrl+n", "new", "New"),
        Binding("d", "delete", "Delete"),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self, path: str = "."):
        super().__init__()
        self.workspace_path = Path(path).resolve()
        self._current_file: Path | None = None

    def compose(self) -> ComposeResult:
        with Horizontal():
            with Vertical(id="sidebar"):
                yield DirectoryTree(self.workspace_path)
            yield CodeEditor(Path("/dev/null"), id="editor")

    def on_mount(self) -> None:
        self.title = str(self.workspace_path)

    def on_directory_tree_file_selected(
        self, event: DirectoryTree.FileSelected
    ) -> None:
        self._current_file = event.path
        editor = self.query_one(CodeEditor)
        editor.file_path = event.path
        editor.load_file()
        self.title = f"{event.path.name} - {self.workspace_path.name}"

    def action_save(self) -> None:
        editor = self.query_one(CodeEditor)
        if editor.file_path and editor.is_modified:
            if editor.save_file():
                self.notify(f"Saved: {editor.file_path.name}")
            else:
                self.notify("Failed to save", severity="error")

    def action_new(self) -> None:
        self.push_screen(InputDialog("untitled"), self._create_note)

    def _create_note(self, name: str) -> None:
        if not name:
            return
        if not name.endswith(".md"):
            name += ".md"
        file_path = self.workspace_path / name
        if file_path.exists():
            self.notify("File already exists", severity="error")
            return
        file_path.write_text(f"# {name[:-3]}\n\n", encoding="utf-8")
        self._refresh_tree()
        self._open_file(file_path)

    def action_delete(self) -> None:
        editor = self.query_one(CodeEditor)
        if not editor.file_path or editor.file_path.name == "null":
            self.notify("No file selected", severity="warning")
            return
        self.push_screen(ConfirmDialog(editor.file_path.name), self._confirm_delete)

    def _confirm_delete(self, confirmed: bool) -> None:
        if not confirmed:
            return
        editor = self.query_one(CodeEditor)
        if editor.file_path and editor.file_path.exists():
            editor.file_path.unlink()
            self._refresh_tree()
            editor.text = ""
            editor.file_path = Path("/dev/null")
            editor._original_content = ""
            self._current_file = None
            self.title = str(self.workspace_path)
            self.notify("Deleted")

    def _refresh_tree(self) -> None:
        tree = self.query_one(DirectoryTree)
        tree.reload()

    def _open_file(self, file_path: Path) -> None:
        self._current_file = file_path
        editor = self.query_one(CodeEditor)
        editor.file_path = file_path
        editor.load_file()
        self.title = f"{file_path.name} - {self.workspace_path.name}"
