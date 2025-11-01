import typer

from typing import Optional


def create_typer_app(
    name: Optional[str] = None,
    help: Optional[str] = None,
) -> typer.Typer:
    typer_app = typer.Typer(
        name=name,
        help=help,
        add_completion=False,
        context_settings={
            "help_option_names": ["-h", "--help"]
        }
    )

    return typer_app
