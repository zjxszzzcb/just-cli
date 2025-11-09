import functools
import importlib
import os
import traceback

from pathlib import Path
from typer.core import TyperGroup
from typing import Any, Callable, List, TypeVar, Optional

from just.core.config import load_env_config, get_command_dir, get_extension_dir
from just.utils import echo
from just.utils.typer_utils import create_typer_app


just_cli = create_typer_app()

T = TypeVar('T')


def capture_exception(func: Callable[..., T]) -> Callable[..., Optional[T]]:
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Optional[T]:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            echo.error(str(e))
            exit(1)

    return wrapper


class SortedGroup(TyperGroup):
    def list_commands(self, ctx):
        return sorted(super().list_commands(ctx))
    
    
def run_just_cli(*args, **kwargs):
    load_env_config()
    just_cli(*args, **kwargs)


def traverse_script_dir(directory: str) -> List[str]:
    script_modules = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if not file.startswith('_') and file.endswith(".py"):
                script_modules.append(
                    "just." +
                    '.'.join(Path(root).relative_to(Path(__file__).parent).parts) +
                    f".{str(Path(file).stem)}"
                )
    return script_modules



def main():
    # Dynamically import all script modules to register their commands
    script_modules = []
    script_modules.extend(traverse_script_dir(get_command_dir().as_posix()))
    script_modules.extend(traverse_script_dir(get_extension_dir().as_posix()))
    script_modules.sort()
    missing_packages = []
    for module_name in script_modules:
        try:
            # echo.debug("Importing", module_name)
            importlib.import_module(module_name)
        except ImportError as e:
            traceback.print_exc()
            package_name = e.name
            if package_name not in missing_packages:
                missing_packages.append(package_name)
                # Handle the case where the module cannot be found
                echo.warning(
                    f"`{package_name}` is not installed, some sub commands are disabled, "
                    f"refer to README.md for instructions."
                )
            continue
    # Run the CLI application
    run_just_cli()
