from just import create_typer_app, just_cli


install_cli = create_typer_app(name="install", help="Install various toolkits.")

# Add the install CLI to the just CLI
just_cli.add_typer(install_cli)
