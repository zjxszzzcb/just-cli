from just import create_typer_app, just_cli


install_cli = create_typer_app(name="install", help="Install various toolkits.")
just_cli.add_typer(install_cli)

__all__ = ["install_cli"]
