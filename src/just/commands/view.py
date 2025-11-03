import typer

from pathlib import Path
from typing_extensions import Annotated

from just import just_cli
from just.tui.markdown import MarkdownApp
from just.commands.edit import edit_file


def view_markdown_by_textual(file_path: str):
    """View markdown file."""
    app = MarkdownApp()
    app.path = Path(file_path)
    app.run()


@just_cli.command(name="view")
def view_file(
    file_path: Annotated[str, typer.Argument(
        help="The file to view",
        show_default=False
    )]
):
    """
    Preview the structured text files (e.g., Markdown, JSON, XML)
    """
    ext = "".join(Path(file_path).suffixes)
    if ext == '.md':
        view_markdown_by_textual(file_path)
    # TODO: support other file types
    else:
        edit_file(file_path)
