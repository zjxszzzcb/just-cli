from just import just_cli, capture_exception
from just.tui import WorkspaceApp
from just.utils.note_utils import get_notes_dir


@just_cli.command(name="note")
@capture_exception
def note_command():
    """Edit notes in ~/.just/notes directory."""
    notes_dir = get_notes_dir()
    notes_dir.mkdir(parents=True, exist_ok=True)
    WorkspaceApp(str(notes_dir)).run()
