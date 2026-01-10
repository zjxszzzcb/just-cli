import typer

from rich.console import Console

from just.utils.format_utils import docstring


def to_string(*args, sep: str = ' ', end: str = '\n'):
    return sep.join(map(str, args)) + end


def echo(*args, sep: str = ' ', end: str = '\n'):
    typer.echo(to_string(*args, sep=sep, end=end), nl=False)


def red(*args, sep: str = ' ', end: str = '\n'):
    typer.secho(to_string(*args, sep=sep, end=end), fg=typer.colors.RED, nl=False)


def green(*args, sep: str = ' ', end: str = '\n'):
    typer.secho(to_string(*args, sep=sep, end=end), fg=typer.colors.GREEN, nl=False)


def yellow(*args, sep: str = ' ', end: str = '\n'):
    typer.secho(to_string(*args, sep=sep, end=end), fg=typer.colors.YELLOW, nl=False)


def blue(*args, sep: str = ' ', end: str = '\n'):
    typer.secho(to_string(*args, sep=sep, end=end), fg=typer.colors.BLUE, nl=False)


def cyan(*args, sep: str = ' ', end: str = '\n'):
    typer.secho(to_string(*args, sep=sep, end=end), fg=typer.colors.CYAN, nl=False)


def debug(*args, sep: str = ' ', end: str = '\n'):
    blue(f"[DEBUG] {to_string(*args, sep=sep, end=end)}", end='')


def info(*args, sep: str = ' ', end: str = '\n'):
    echo(f"[INFO] {to_string(*args, sep=sep, end=end)}", end='')


def warning(*args, sep: str = ' ', end: str = '\n'):
    yellow(f"[WARNING] {to_string(*args, sep=sep, end=end)}", end='')


def error(*args, sep: str = ' ', end: str = '\n'):
    red(f"[ERROR] {to_string(*args, sep=sep, end=end)}", end='')


def critical(*args, sep: str = ' ', end: str = '\n'):
    typer.secho(f"[CRITICAL] {to_string(*args, sep=sep, end=end)}", fg=typer.colors.BRIGHT_RED, bold=True, nl=False)


def success(*args, sep: str = ' ', end: str = '\n'):
    green(f"[SUCCESS] {to_string(*args, sep=sep, end=end)}", end='')

    
def fail(*args, sep: str = ' ', end: str = '\n'):
    typer.secho(f"[FAIL] {to_string(*args, sep=sep, end=end)}", fg=typer.colors.BRIGHT_RED, bold=True, nl=False)


def markdown(*args, sep: str = ' ', end: str = '\n'):
    text = docstring(to_string(*args, sep=sep, end=end))
    console = Console()
    # md = Markdown(text)
    # console.print(md)
    console.print(text, end="")
