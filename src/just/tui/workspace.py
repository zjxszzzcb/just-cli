"""VSCode-style workspace editor with file tree and tabs"""

from pathlib import Path
from typing import Dict

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import (
    DirectoryTree,
    Footer,
    Header,
    TabbedContent,
    TabPane,
    TextArea,
    Static,
)


class CodeEditor(TextArea):
    """Enhanced code editor with file path tracking"""

    def __init__(self, file_path: Path, **kwargs):
        # Detect language from file extension
        language = self._detect_language(file_path)
        super().__init__(language=language, **kwargs)
        self.file_path = file_path
        self._original_content = ""
        self._modified = False

    @staticmethod
    def _detect_language(file_path: Path) -> str | None:
        """Detect language from file extension"""
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
            ".h": "c",
            ".hpp": "cpp",
        }
        return ext_map.get(file_path.suffix.lower())

    def load_file(self) -> bool:
        """Load file content into editor"""
        try:
            if self.file_path.exists():
                content = self.file_path.read_text(encoding="utf-8")
                self.text = content
                self._original_content = content
                self._modified = False
                return True
        except Exception:
            pass
        return False

    def save_file(self) -> bool:
        """Save editor content to file"""
        try:
            self.file_path.write_text(self.text, encoding="utf-8")
            self._original_content = self.text
            self._modified = False
            return True
        except Exception:
            pass
        return False

    @property
    def is_modified(self) -> bool:
        return self.text != self._original_content


class FileTree(DirectoryTree):
    """Custom DirectoryTree for workspace"""

    pass


class WorkspaceApp(App):
    """VSCode-style workspace editor"""

    CSS = """
    /* Layout */
    Horizontal {
        height: 1fr;
    }

    /* Sidebar */
    #sidebar {
        width: 28;
        dock: left;
        background: $panel;
        border-right: tall $primary;
    }

    #sidebar-header {
        height: 1;
        padding: 0 1;
        background: $primary;
        color: $text;
        text-style: bold;
    }

    /* File tree */
    FileTree {
        height: 1fr;
        background: transparent;
    }

    /* Tabbed content */
    TabbedContent {
        height: 1fr;
    }

    ContentSwitcher {
        height: 1fr;
    }

    /* Tabs */
    Tabs {
        height: 1;
    }

    Tab {
        padding: 0 2;
    }

    /* Editor */
    CodeEditor {
        height: 1fr;
    }

    /* Empty state */
    #empty-state {
        text-align: center;
        padding: 4;
        color: $text-muted;
    }
    """

    BINDINGS = [
        Binding("ctrl+s", "save_current", "Save", show=True),
        Binding("ctrl+w", "close_tab", "Close Tab", show=True),
        Binding("ctrl+n", "new_file", "New", show=False),
        Binding("q", "quit", "Quit", show=True),
    ]

    def __init__(self, path: str = "."):
        super().__init__()
        self.workspace_path = Path(path).resolve()
        self._open_files: Dict[str, CodeEditor] = {}

    def compose(self) -> ComposeResult:
        yield Header()

        with Horizontal():
            # Sidebar with file tree
            with Vertical(id="sidebar"):
                yield Static("EXPLORER", id="sidebar-header")
                yield FileTree(self.workspace_path, id="file-tree")

            # Main content area with tabs
            with TabbedContent(id="tabs", initial=None):
                yield Static(
                    "Open a file from the sidebar or press Ctrl+N to create a new file.",
                    id="empty-state",
                )

        yield Footer()

    def on_mount(self) -> None:
        """Set title on mount"""
        self.title = f"Workspace: {self.workspace_path.name}"

    def on_directory_tree_file_selected(
        self, event: DirectoryTree.FileSelected
    ) -> None:
        """Handle file selection from directory tree"""
        file_path = event.path
        self._open_file(file_path)

    def _open_file(self, file_path: Path) -> None:
        """Open a file in a new tab or focus existing tab"""
        file_id = str(file_path)

        # Check if already open
        if file_id in self._open_files:
            tabs = self.query_one(TabbedContent)
            tabs.active = file_id
            return

        # Create editor
        try:
            editor = CodeEditor(file_path, id=f"editor-{len(self._open_files)}")
            if not editor.load_file():
                self.notify(f"Cannot read file: {file_path.name}", severity="error")
                return
        except Exception as e:
            self.notify(f"Error opening file: {e}", severity="error")
            return

        # Get tabbed content
        tabs = self.query_one(TabbedContent)

        # Create tab pane
        tab_title = file_path.name
        if editor.is_modified:
            tab_title = f"*{tab_title}"

        pane = TabPane(tab_title, id=file_id)
        pane._content = editor

        # Add tab
        tabs.add_pane(pane)
        tabs.active = file_id

        # Track open file
        self._open_files[file_id] = editor

    def action_save_current(self) -> None:
        """Save the currently active file"""
        tabs = self.query_one(TabbedContent)
        active_id = tabs.active

        if active_id and active_id in self._open_files:
            editor = self._open_files[active_id]
            if editor.save_file():
                self.notify(f"Saved: {editor.file_path.name}", severity="information")
            else:
                self.notify(
                    f"Failed to save: {editor.file_path.name}", severity="error"
                )

    def action_close_tab(self) -> None:
        """Close the currently active tab"""
        tabs = self.query_one(TabbedContent)
        active_id = tabs.active

        if active_id and active_id in self._open_files:
            editor = self._open_files[active_id]

            # Check for unsaved changes
            if editor.is_modified:
                # TODO: Add confirmation dialog
                pass

            # Remove tab
            tabs.remove_pane(active_id)
            del self._open_files[active_id]

    def action_new_file(self) -> None:
        """Create a new untitled file"""
        # TODO: Implement new file creation
        self.notify("New file feature coming soon!", severity="information")

    def get_editor(self, file_path: Path) -> CodeEditor | None:
        """Get editor for a file path"""
        return self._open_files.get(str(file_path))
