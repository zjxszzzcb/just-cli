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

        # For options, the identifier should be the placeholder in the command template
        # For arguments, it's the placeholder
        if option_flag and not annotation:
            # This is a flag option, identifier is the flag itself
            identifier = option_flag
        else:
            # For annotated parameters, the identifier is the part before the annotation
            # Extract the identifier (placeholder in the original command)
            # For annotated parameters like "f523e75ca4ef[container_id:str#help]",
            # the identifier is "f523e75ca4ef"
            identifier = command.split('[')[0]

        if option_flag and not annotation:
            # For flags like -v[verbose:bool#help], we need to extract the annotation correctly
            flag_start = command.find('[')
            flag_end = command.find(']')
            if flag_start != -1 and flag_end != -1:
                flag_annotation = command[flag_start+1:flag_end]
                if flag_annotation:
                    annotation = flag_annotation
                    identifier = command[:flag_start]  # The flag itself is the identifier
                else:
                    annotation = option_flag
                    identifier = option_flag
            else:
                annotation = option_flag
                identifier = option_flag

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

        # Convert default value to appropriate type
        if default_value is not None:
            if variable_type == 'int':
                try:
                    default_value = int(default_value)
                except ValueError:
                    pass  # Keep as string if conversion fails
            elif variable_type == 'float':
                try:
                    default_value = float(default_value)
                except ValueError:
                    pass  # Keep as string if conversion fails
            elif variable_type == 'bool':
                default_value = default_value.lower() in ('true', '1', 'yes', 'on')

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
    all_params = []

    # Track variable names to avoid duplicates
    used_names = set()

    # Add arguments
    for arg in arguments:
        # Ensure unique variable names
        var_name = arg.name
        counter = 1
        while var_name in used_names:
            var_name = f"{arg.name}_{counter}"
            counter += 1
        used_names.add(var_name)

        default_assignment = ""
        if arg.default_value is not None:
            # Handle string default values properly
            if isinstance(arg.default_value, str):
                default_assignment = f" = '{arg.default_value}'"
            else:
                default_assignment = f" = {arg.default_value}"
        all_params.append(
            f"    {var_name}: Annotated[{arg.type.__name__}, typer.Argument(\n"
            f"        help={repr(arg.help)},\n"
            f"        show_default=False\n"
            f"    )]{default_assignment}"
        )

    # Add options processing
    for flag, opt in options.items():
        # Ensure unique variable names
        var_name = opt.name
        counter = 1
        while var_name in used_names:
            var_name = f"{opt.name}_{counter}"
            counter += 1
        used_names.add(var_name)

        default_assignment = ""
        if opt.default_value is not None:
            # Handle string default values properly
            if isinstance(opt.default_value, str):
                default_assignment = f" = '{opt.default_value}'"
            else:
                default_assignment = f" = {opt.default_value}"
        # Determine if it's a boolean flag option
        elif opt.type.__name__ == 'bool':
            # Boolean flag without explicit default - treat as False default
            default_assignment = " = False"

        all_params.append(
            f"    {var_name}: Annotated[{opt.type.__name__}, typer.Option(\n"
            f"        {repr(f'--{flag}')},\n"
            f"        help={repr(opt.help)},\n"
            f"        show_default=False\n"
            f"    )]{default_assignment}"
        )

    # Join all parameters with commas
    for i, param in enumerate(all_params):
        if i < len(all_params) - 1:
            arguments_declarations.append(param + ",\n")
        else:
            arguments_declarations.append(param + "\n")

    arguments_declarations.append('\n')

    command_replacements = []
    # Create mapping of original names to new names
    name_mapping = {}

    # Map arguments
    arg_counter = 1
    for arg in arguments:
        var_name = arg.name
        while var_name in name_mapping.values():
            var_name = f"{arg.name}_{arg_counter}"
            arg_counter += 1
        name_mapping[arg.name] = var_name

    # Map options
    opt_counter = 1
    for flag, opt in options.items():
        var_name = opt.name
        while var_name in name_mapping.values():
            var_name = f"{opt.name}_{opt_counter}"
            opt_counter += 1
        name_mapping[opt.name] = var_name

    # Generate replacements for arguments
    for arg in arguments:
        var_name = name_mapping[arg.name]
        command_replacements.append(
            f"    command = command.replace({repr(arg.repl_identifier)}, str({var_name}))"
        )

    # Generate replacements for options
    for flag, opt in options.items():
        var_name = name_mapping[opt.name]
        # For boolean flags, only add the flag if True
        if opt.type.__name__ == 'bool':
            command_replacements.append(
                f"    if {var_name}:"
            )
            # For boolean flags, we typically just want to include the flag itself, not its value
            command_replacements.append(
                f"        command = command.replace({repr(opt.repl_identifier)}, '{opt.repl_identifier}')"
            )
        else:
            command_replacements.append(
                f"    command = command.replace({repr(opt.repl_identifier)}, str({var_name}))"
            )

    if command_replacements:
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