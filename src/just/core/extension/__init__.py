from just import create_typer_app, just_cli


ext_cli = create_typer_app(name="ext", help="Manage just extensions.")
just_cli.add_typer(ext_cli)

__all__ = ["ext_cli"]
