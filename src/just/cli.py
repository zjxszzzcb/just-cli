import functools
import importlib
import os

from dotenv import load_dotenv, set_key
from pathlib import Path
from typer.core import TyperGroup
from typing import Any, Callable, TypeVar, Optional

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
            return None

    return wrapper


def load_env():
    load_dotenv(Path(__file__).parent / ".env")


def update_env_file(key: str, value: str):
    print("Update", str(Path(__file__).parent / ".env"), f"{key}={value}")
    set_key(str(Path(__file__).parent / ".env"), key, value)


class SortedGroup(TyperGroup):
    def list_commands(self, ctx):
        return sorted(super().list_commands(ctx))
    
    
def run_just_cli(*args, **kwargs):
    load_env()
    just_cli(*args, **kwargs)


def main():
    # Dynamically import all script modules to register their commands
    scripts_dir = os.path.join(os.path.dirname(__file__), "commands")
    script_modules = []
    for root, dirs, files in os.walk(scripts_dir):
        for file in files:
            if file.endswith(".py"):
                script_modules.append(
                    "just."+
                    '.'.join(Path(root).relative_to(Path(__file__).parent).parts)+
                    f".{str(Path(file).stem)}"
                )
    script_modules.sort()
    missing_packages = []
    for module_name in script_modules:
        try:
            importlib.import_module(module_name)
        except ImportError as e:
            package_name = e.name
            if package_name not in missing_packages:
                missing_packages.append(package_name)
                # Handle the case where the module cannot be found
                print(
                    f"[WARNING] `{package_name}` is not installed, some sub commands are disabled, "
                    f"refer to README.md for instructions."
                )
            continue
    # Run the CLI application
    run_just_cli()


if __name__ == "__main__":
    update_env_file("JUST_EDIT_USE_TOOL", "textual")