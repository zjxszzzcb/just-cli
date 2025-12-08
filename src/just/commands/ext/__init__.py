from just import create_typer_app, just_cli

# Create and register the ext_cli
ext_cli = create_typer_app(name="ext", help="Manage just extensions.")
just_cli.add_typer(ext_cli)

__all__ = ["ext_cli"]

# Import commands after ext_cli is created to avoid circular imports
def _load_commands():
    """Lazy load all extension commands"""
    from . import add, edit, list
    from .add import add_extension
    from .edit import edit_extension
    from .list import list_extensions

    # Register commands
    ext_cli.command(name="add", context_settings={"allow_extra_args": True, "ignore_unknown_options": True})(add_extension)
    ext_cli.command(name="edit")(edit_extension)
    ext_cli.command(name="list")(list_extensions)

_load_commands()