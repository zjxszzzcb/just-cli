import typer


def create_typer_app(*args, **kwargs) -> typer.Typer:
    if args or kwargs:
        return typer.Typer(*args, **kwargs)

    typer_app = typer.Typer(
        add_completion=False,
        context_settings={
            "help_option_names": ["-h", "--help"]
        }
    )

    return typer_app
