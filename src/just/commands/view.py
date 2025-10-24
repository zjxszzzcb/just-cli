from pathlib import Path

from just import just_cli
from just.tui.markdown import MarkdownApp

from .edit import edit_file


def view_markdown_by_textual(file_path: str):
    """View markdown file."""
    app = MarkdownApp()
    app.path = Path(file_path)
    app.run()


@just_cli.command(name="view", help="Read Text file.")
def view_file(file_path: str):
    ext = "".join(Path(file_path).suffixes)
    if ext == '.md':
        view_markdown_by_textual(file_path)
    else:
        edit_file(file_path)
