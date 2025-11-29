import typer
from typing import List, Optional
from typing_extensions import Annotated

from just import just_cli, echo
from just.core.installer.install_package import install_package
from just.utils.typer_utils import show_help


@just_cli.command(name="install", context_settings={"ignore_unknown_options": True})
def install(
    args: Annotated[Optional[List[str]], typer.Argument(
        help="The arguments to install the package"
    )] = None,
    help_flag: Annotated[bool, typer.Option(
        "--help", "-h",
        help="Show this help message and exit"
    )] = False
):
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


if __name__ == "__main__":
    just_cli()