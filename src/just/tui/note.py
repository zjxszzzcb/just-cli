"""JUST CLI Note TUI Application"""

from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import (
    Header,
    Footer,
    Static,
    ListView,
    ListItem,
    Label,
    MarkdownViewer,
)

from just.utils.note_utils import list_notes, read_note


class NoteListItem(ListItem):
    """Custom list item for displaying a note"""

    def __init__(self, note_path: Path) -> None:
        super().__init__()
        self.note_path = note_path

    def compose(self) -> ComposeResult:
        yield Label(self.note_path.stem)


class NoteApp(App):
    """A TUI note management application"""

    CSS = """
    Horizontal {
        height: 1fr;
    }

    #note-list-container {
        width: 30%;
        dock: left;
        border-right: solid $primary;
    }

    #preview-container {
        width: 70%;
    }

    #note-list {
        height: 1fr;
    }

    #empty-message {
        text-align: center;
        padding: 2;
        color: $text-muted;
    }

    #markdown-preview {
        height: 1fr;
    }

    NoteListItem {
        padding: 1;
    }

    NoteListItem:hover {
        background: $primary-darken-2;
    }

    NoteListItem:focus {
        background: $primary-darken-1;
    }
    """

    BINDINGS = [
        ("n", "new_note", "New"),
        ("d", "delete_note", "Delete"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._current_note: Path | None = None

    def compose(self) -> ComposeResult:
        """Create the UI layout with sidebar and preview"""
        yield Header()
        with Horizontal():
            with Vertical(id="note-list-container"):
                yield ListView(id="note-list")
                yield Static(
                    "No notes yet. Press 'n' to create one.", id="empty-message"
                )
            with Vertical(id="preview-container"):
                yield MarkdownViewer(id="markdown-preview")
        yield Footer()

    def on_mount(self) -> None:
        """Load notes when app starts"""
        self._load_notes()

    def _load_notes(self) -> None:
        """Load notes into the list view"""
        notes = list_notes()
        list_view = self.query_one("#note-list", ListView)
        empty_msg = self.query_one("#empty-message", Static)

        if notes:
            list_view.clear()
            for note_path in notes:
                list_view.append(NoteListItem(note_path))
            empty_msg.display = False
            list_view.display = True
        else:
            list_view.display = False
            empty_msg.display = True

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        selected_item = event.item
        if isinstance(selected_item, NoteListItem):
            self._current_note = selected_item.note_path
            content = read_note(selected_item.note_path.stem)
            markdown_viewer = self.query_one("#markdown-preview", MarkdownViewer)
            markdown_viewer.document.update(content)

    def action_new_note(self) -> None:
        """Create a new note (placeholder - Task 6)"""
        # TODO: Implement in Task 6
        pass

    def action_delete_note(self) -> None:
        """Delete selected note (placeholder - Task 7)"""
        # TODO: Implement in Task 7
        pass
