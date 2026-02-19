"""JUST CLI Note TUI Application"""

from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import (
    Header,
    Footer,
    Static,
    ListView,
    ListItem,
    Label,
    MarkdownViewer,
    Input,
    Button,
)

from just.tui.editor import EditArea
from just.utils.note_utils import delete_note, list_notes, read_note


class NewNoteScreen(ModalScreen):
    """Modal dialog for creating a new note"""

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label("Enter note title:", id="prompt")
            yield Input(placeholder="Note title", id="title-input")
            with Horizontal(id="buttons"):
                yield Button("Create", variant="primary", id="create")
                yield Button("Cancel", variant="default", id="cancel")

    def on_mount(self) -> None:
        self.query_one("#title-input", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "title-input" and event.value.strip():
            self.dismiss(event.value.strip())

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "create":
            title = self.query_one("#title-input", Input).value.strip()
            if title:
                self.dismiss(title)
        elif event.button.id == "cancel":
            self.dismiss(None)


class DeleteConfirmScreen(ModalScreen[bool]):
    """Modal dialog for confirming note deletion"""

    def compose(self) -> ComposeResult:
        with Vertical(id="confirm-dialog"):
            yield Label("Delete this note?", id="confirm-prompt")
            with Horizontal(id="confirm-buttons"):
                yield Button("Delete", variant="error", id="confirm-delete")
                yield Button("Cancel", variant="default", id="cancel-delete")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm-delete":
            self.dismiss(True)
        else:
            self.dismiss(False)


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
    /* Main layout */
    Horizontal {
        height: 1fr;
    }

    /* Sidebar - note list */
    #note-list-container {
        width: 28;
        dock: left;
        background: $surface-darken-1;
        border-right: wide $primary;
    }

    /* Preview area */
    #preview-container {
        width: 1fr;
        background: $surface;
        padding: 1 2;
    }

    /* Note list */
    #note-list {
        height: 1fr;
        background: transparent;
    }

    #empty-message {
        text-align: center;
        padding: 2;
        color: $text-muted;
        text-style: italic;
    }

    /* Markdown preview */
    #markdown-preview {
        height: 1fr;
        background: transparent;
        padding: 0;
    }

    /* Editor */
    #editor {
        height: 1fr;
        background: $surface;
    }

    .hidden {
        display: none;
    }

    /* Note list items - compact style */
    NoteListItem {
        height: 1;
        padding: 0 1;
        background: transparent;
    }

    NoteListItem:hover {
        background: $primary-darken-3;
    }

    NoteListItem.-active {
        background: $primary-darken-2;
    }

    NoteListItem:focus {
        background: $primary-darken-1;
        text-style: bold;
    }

    NoteListItem Label {
        width: 1fr;
        height: 1;
        content-align: left middle;
        overflow: hidden;
    }

    /* Header styling */
    Header {
        background: $primary;
        color: $text-primary;
    }

    /* New Note Dialog */
    #dialog {
        align: center middle;
        width: 50;
        height: 11;
        background: $surface;
        border: wide $primary;
        padding: 1;
    }

    #prompt {
        padding: 1;
        text-align: center;
        text-style: bold;
        color: $text;
    }

    #title-input {
        margin: 0 2;
        border: wide $primary;
    }

    #buttons {
        align: center middle;
        height: 3;
        padding: 1;
    }

    #buttons Button {
        margin: 0 1;
        min-width: 12;
    }

    /* Delete Confirm Dialog */
    #confirm-dialog {
        align: center middle;
        width: 42;
        height: 9;
        background: $surface;
        border: wide $error;
        padding: 1;
    }

    #confirm-prompt {
        padding: 1;
        text-align: center;
        text-style: bold;
        color: $error;
    }

    #confirm-buttons {
        align: center middle;
        height: 3;
        padding: 1;
    }

    #confirm-buttons Button {
        margin: 0 1;
        min-width: 10;
    }
    """

    BINDINGS = [
        ("n", "new_note", "New"),
        ("d", "delete_note", "Delete"),
        ("q", "quit", "Quit"),
        Binding("enter", "edit_note", "Edit", show=False),
        Binding("ctrl+s", "save_note", "Save", show=False),
        Binding("escape", "cancel_edit", "Cancel", show=False),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._current_note: Path | None = None
        self._is_editing: bool = False

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
                yield EditArea(id="editor", classes="hidden")
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
        """Create a new note"""
        self.push_screen(NewNoteScreen(), self._on_new_note_title)

    def _on_new_note_title(self, title: str | None) -> None:
        """Handle new note title input"""
        if not title:
            return

        from just.utils.note_utils import create_note

        note_path = create_note(title, f"# {title}\n\n")
        self._load_notes()

        list_view = self.query_one("#note-list", ListView)
        for i, item in enumerate(list_view.children):
            if isinstance(item, NoteListItem) and item.note_path == note_path:
                list_view.index = i
                break

        self._current_note = note_path
        markdown_viewer = self.query_one("#markdown-preview", MarkdownViewer)
        markdown_viewer.document.update(f"# {title}\n\n")
        self.action_edit_note()

    def action_delete_note(self) -> None:
        if self._current_note is None:
            return
        note_to_delete = self._current_note
        self.push_screen(
            DeleteConfirmScreen(),
            lambda confirmed: self._on_delete_confirmed(confirmed, note_to_delete),
        )

    def _on_delete_confirmed(self, confirmed: bool | None, note_path: Path) -> None:
        if not confirmed:
            return

        delete_note(note_path.stem)
        self._current_note = None
        self._load_notes()

        markdown_viewer = self.query_one("#markdown-preview", MarkdownViewer)
        markdown_viewer.document.update("")

        list_view = self.query_one("#note-list", ListView)
        if not list_view.children:
            empty_msg = self.query_one("#empty-message", Static)
            empty_msg.display = True
            list_view.display = False

    def action_edit_note(self) -> None:
        """Enter edit mode for the selected note"""
        if self._current_note is None:
            return

        content = read_note(self._current_note.stem)
        editor = self.query_one("#editor", EditArea)
        editor.load_text(content)

        self._is_editing = True
        markdown_viewer = self.query_one("#markdown-preview", MarkdownViewer)
        markdown_viewer.display = False
        editor.display = True
        editor.focus()

    def action_save_note(self) -> None:
        """Save the current note content"""
        if not self._is_editing or self._current_note is None:
            return

        editor = self.query_one("#editor", EditArea)
        content = editor.text
        self._current_note.write_text(content, encoding="utf-8")

        markdown_viewer = self.query_one("#markdown-preview", MarkdownViewer)
        markdown_viewer.document.update(content)

        self._is_editing = False
        editor.display = False
        markdown_viewer.display = True

    def action_cancel_edit(self) -> None:
        """Cancel editing and return to preview mode"""
        if not self._is_editing:
            return

        self._is_editing = False
        editor = self.query_one("#editor", EditArea)
        markdown_viewer = self.query_one("#markdown-preview", MarkdownViewer)
        editor.display = False
        markdown_viewer.display = True
