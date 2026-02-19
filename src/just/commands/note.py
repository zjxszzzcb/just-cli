from just import just_cli, capture_exception
from just.tui import NoteApp


@just_cli.command(name="note")
@capture_exception
def note_command():
    """
    Manage notes with TUI interface.
    """
    NoteApp().run()
