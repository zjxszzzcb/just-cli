import inspect
import re
import typer
from rich.markdown import Markdown
from rich.console import Console


def docstring(doc: str) -> str:
    # Remove line continuations (backslash + newline) and any following whitespace
    doc = re.sub(r'\\\n\s*', '', doc)
    # Normalize remaining indentation using docstring()
    return inspect.cleandoc(doc)


def markdown(text: str):
    text = docstring(text)
    console = Console()
    # md = Markdown(text)
    # console.print(md)
    console.print(text)


def echo(text: str):
    typer.echo(text)


def red(text: str):
    typer.secho(text, fg=typer.colors.RED)


def green(text: str):
    typer.secho(text, fg=typer.colors.GREEN)


def yellow(text: str):
    typer.secho(text, fg=typer.colors.YELLOW)


def blue(text: str):
    typer.secho(text, fg=typer.colors.BLUE)


def cyan(text: str):
    typer.secho(text, fg=typer.colors.CYAN)


def error(text: str):
    red(f"[ERROR] {text}")
    