import os

from inspect import cleandoc
from pathlib import Path
from typing import Any, List, Optional, Tuple, Type


def search_exist_script(just_commands: List[str]) -> Tuple[bool, str]:
    commands_dir = Path(__file__).parent.parent / 'commands'
    extensions_dir = Path(__file__).parent.parent / 'extensions'
    # search in core commands
    if just_commands[0] == 'just':
        just_commands.pop(0)
    if not just_commands:
        raise ValueError

    if (p := Path(os.path.join(commands_dir, *just_commands)+'.py')).exists():
        return True, p.as_posix()
    else:
        p = Path(os.path.join(extensions_dir, *just_commands)+'.py')
        return p.exists(), p.as_posix()


# name, type, value, help
ParamDeclaration = List[Tuple[str, Type, Any, str]]


def create_typer_script(
    custom_command: str,
    just_commands: List[str],
    arguments: List[str],
    options: List[str]
):
    exist, expect_script_path = search_exist_script(just_commands)

    if just_commands[0] == 'just':
        just_commands.pop(0)
    if not just_commands:
        raise ValueError

    route_command = 'just'
    for i in range(len(just_commands)):
        exist, expect_script_path = search_exist_script(just_commands[:i+1])
        if exist:
            raise FileExistsError

        expect_script_dir = expect_script_path.replace('.py', '')
        if os.path.exists(expect_script_dir):
            continue

        os.makedirs(expect_script_dir)
        with open(os.path.join(expect_script_dir, '__init__.py')) as f:
            if i == 0:
                f.write(
                    cleandoc(f"""
                    from just import just_cli, create_typer_app
                    
                    
                    {just_commands[0]}_cli = create_typer_app(name="{just_commands[0]}")
                    # Add the install CLI to the just CLI
                    just_cli.add_typer({just_commands[0]}_cli)
                    
                    __all__ = ["{just_commands[0]}_cli"]
                    """)
                )
            else:
                f.write(
                    cleandoc(f"""
                    from just import create_typer_app
                    
                    from . import {just_commands[i-1]}_cli


                    {just_commands[i]}_cli = create_typer_app(name="{just_commands[i]}")
                    # Add the install CLI to the just CLI
                    {just_commands[i-1]}_cli.add_typer({just_commands[i]}_cli)

                    __all__ = ["{just_commands[i]}_cli"]
                    """)
                )







TYPER_SCRIPT_TEMPLATE = r'''
{import_statements}


CUSTOM_COMMAND = r"""
{custom_command}
"""


@{just_sub_command}_cli.command(name="{just_sub_command}")
def main({arguments_declarations}):
    {command_replacements}


{register_statement}
'''