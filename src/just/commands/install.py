import typer
from typing import List, Optional
from typing_extensions import Annotated

from rich.console import Console
from rich.table import Table

from just import just_cli, echo
from just.core.installer.install_package import install_package, list_available_installers
from just.utils.typer_utils import show_help


@just_cli.command(name="install", context_settings={"ignore_unknown_options": True})
def install(
    args: Annotated[Optional[List[str]], typer.Argument(
        help="The arguments to install the package"
    )] = None,
    list_flag: Annotated[bool, typer.Option(
        "--list", "-l",
        help="List all available tools that can be installed"
    )] = False,
    help_flag: Annotated[bool, typer.Option(
        "--help", "-h",
        help="Show this help message and exit"
    )] = False
):
    # Handle --list option
    if list_flag:
        _show_available_installers()
        return
    
    if not args:
        show_help(just_cli, "install")
        return

    package_name = args.pop(0)
    if help_flag:
        args.append("--help")

    try:
        install_package(package_name, args)
    except Exception as e:
        echo.fail(f"Error installing {package_name}: {e}")
        raise typer.Exit(1)


def _show_available_installers():
    """Display all available installers in a formatted table."""
    installers = list_available_installers()
    
    if not installers:
        echo.warning("No installers found.")
        return
    
    console = Console()
    
    table = Table(
        title="Available Tools",
        title_style="bold cyan",
        header_style="bold green",
        border_style="dim",
        show_lines=False
    )
    
    table.add_column("Tool", style="cyan", no_wrap=True)
    table.add_column("Description", style="white")
    
    for installer in installers:
        table.add_row(installer['name'], installer['description'])
    
    console.print()
    console.print(table)
    console.print()
    console.print(f"[dim]Total: {len(installers)} tools available[/dim]")
    console.print(f"[dim]Usage: just install <tool-name>[/dim]")


if __name__ == "__main__":
    just_cli()