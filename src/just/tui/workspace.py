"""Minimal workspace editor with file tree and editor"""

from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import DirectoryTree, TextArea


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
                self.notify(f"Failed to save", severity="error")
