import re
from dataclasses import dataclass
from typing import Any, List, Dict, Type, Tuple


TYPES = {
    'str': str,
    'int': int,
    'float': float,
    'bool': bool
}


@dataclass()
class Argument:
    """Represents a command argument or option."""
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


def parse_command_structure(just_commands: List[str]) -> Tuple[List[str], List[Argument], Dict[str, Argument]]:
    """
    Parse command structure from a list of command parts.

    This function takes a list of command parts and parses them into:
    - Commands (command names)
    - Arguments (positional parameters)
    - Options (flag parameters)

    Args:
        just_commands: List of command parts to parse

    Returns:
        Tuple of (commands, arguments, options)
    """
    commands = []
    arguments = []
    options = {}

    option_flag = ""
    for command in just_commands:
        if command.startswith('-'):
            option_flag = command.replace('-', '')

        try:
            annotation = re.findall(r'\[(.+?)]', command)[-1]
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