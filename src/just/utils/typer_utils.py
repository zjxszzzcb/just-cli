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


def show_help(app: typer.Typer, command_name: str = ""):
    click_command = typer.main.get_command(app)

    if not command_name:
        # 显示主帮助
        typer.echo(click_command.get_help(click_command.make_context("just", [])))
        return

    # 查找子命令
    if hasattr(click_command, 'commands') and command_name in getattr(click_command, 'commands'):
        sub_command = click_command.commands[command_name]
        typer.echo(sub_command.get_help(sub_command.make_context(command_name, [])))
    else:
        typer.echo(f"Command '{command_name}' not found")