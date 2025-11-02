import os
import re

from dataclasses import dataclass
from inspect import cleandoc
from pathlib import Path
from typing import Any, List, Tuple, Type


TYPES = {
    'str': str,
    'int': int,
    'float': float,
    'bool': bool
}


@dataclass()
class Argument:
    repl_identifier: str
    variable_name: str
    variable_type: Type
    default_value: Any
    help_msg: str

    @property
    def name(self):
        return self.variable_name

    @property
    def type(self):
        return self.variable_type

    @property
    def default(self):
        return self.default_value

    @property
    def help(self):
        return self.help_msg


def search_exist_script(just_commands: List[str]) -> Tuple[bool, str]:
    commands_dir = Path(__file__).parent.parent / 'core'
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


def parse_just_commands(just_commands: List[str]):
    commands = []
    arguments = []
    options = {}

    option_flag = ""
    for command in just_commands:
        if command.startswith('-'):
            option_flag = command.replace('-', '')

        try:
            annotation = re.findall(r'\[(.+?)]',  command)[-1]
        except IndexError:
            annotation = ""

        identifier = command.replace(f'[{annotation}]', '')

        if option_flag and not annotation:
            annotation = option_flag

        if not annotation:
            commands.append(command)
            continue

        if '#' in annotation:
            annotation, help_msg = annotation.split('#', maxsplit=1)
        else:
            help_msg = ""

        if '=' in annotation:
            annotation, default_value = annotation.split('=', maxsplit=1)
        else:
            default_value = None

        if ':' in annotation:
            variable_name, variable_type = annotation.split(':', maxsplit=1)
        else:
            variable_name = annotation
            variable_type = 'str'

        arg = Argument(
            repl_identifier=identifier,
            variable_name=variable_name,
            variable_type=TYPES[variable_type],
            default_value=default_value,
            help_msg=help_msg
        )

        if option_flag:
            options[option_flag] = arg
        else:
            arguments.append(arg)

    return commands, arguments, options


def create_typer_script(
    custom_command: str,
    just_commands: List[str],
):
    just_commands, arguments, options = parse_just_commands(just_commands)
    exist, final_expect_script_path = search_exist_script(just_commands)
    if exist:
        raise FileExistsError(f"{final_expect_script_path} already exists")

    if just_commands[0] == 'just':
        just_commands.pop(0)
    if not just_commands:
        raise ValueError

    for i in range(len(just_commands)-1):
        exist, expect_script_path = search_exist_script(just_commands[:i+1])
        if exist:
            raise FileExistsError

        expect_script_dir = expect_script_path.replace('.py', '')
        if os.path.exists(expect_script_dir):
            continue

        # Create the sub command package and entry cli app
        os.makedirs(expect_script_dir)
        with open(os.path.join(expect_script_dir, '__init__.py'), 'w', encoding='utf-8') as f:
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
                    
                    from .. import {just_commands[i-1]}_cli


                    {just_commands[i]}_cli = create_typer_app(name="{just_commands[i]}")
                    # Add the install CLI to the just CLI
                    {just_commands[i-1]}_cli.add_typer({just_commands[i]}_cli)

                    __all__ = ["{just_commands[i]}_cli"]
                    """)
                )

    just_parent_command = f"{just_commands[-2]}" if len(just_commands)>1 else "just"
    just_sub_command = just_commands[-1]

    arguments_declarations = ['\n']
    for arg in arguments:
        default_assignment = f" = {arg.default_value}" if arg.default_value else ""
        arguments_declarations.append(
            f"    {arg.name}: Annotated[{arg.type.__name__}, typer.Argument(\n"
            f"        help={repr(arg.help)},\n"
            f"        show_default=False\n"
            f"    )]{default_assignment}"
        )
    # TODO: options
    arguments_declarations.append('\n')

    command_replacements = []
    for arg in arguments:
        command_replacements.append(
            f"    command = command.replace({repr(arg.repl_identifier)}, {arg.name})"
        )
    command_replacements[0] = command_replacements[0].lstrip()

    with open(final_expect_script_path, 'w', encoding='utf-8') as f:
        f.write(
            TYPER_SCRIPT_TEMPLATE.format(
                custom_command=custom_command,
                just_parent_command=just_parent_command,
                just_sub_command=just_sub_command,
                arguments_declarations="".join(arguments_declarations),
                command_replacements="\n".join(command_replacements),
            )
        )


TYPER_SCRIPT_TEMPLATE = r'''import shlex
import subprocess
import typer

from typing_extensions import Annotated

from just import create_typer_app
from . import {just_parent_command}_cli


{just_sub_command}_cli = create_typer_app()
# Add the install CLI to the just CLI
{just_parent_command}_cli.add_typer({just_sub_command}_cli)


@{just_sub_command}_cli.command(name="{just_sub_command}")
def main({arguments_declarations}):
    command = r"""
    {custom_command}
    """.strip()
    {command_replacements}
    subprocess.run(shlex.split(command), shell=True)
'''