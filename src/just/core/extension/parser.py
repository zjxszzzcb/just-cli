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
    short_flag: str = ""   # Short option flag (e.g., "-n")
    long_flag: str = ""    # Long option flag (e.g., "--no-newline")

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

    @property
    def flags(self) -> List[str]:
        """Return all flags as a list for typer.Option()."""
        result = []
        if self.short_flag:
            result.append(self.short_flag)
        if self.long_flag:
            result.append(self.long_flag)
        return result

    @property
    def is_append_option(self) -> bool:
        """
        Check if this option should be appended to command rather than replacing placeholder.
        
        True when repl_identifier is the flag itself (e.g., "-o/--output")
        meaning no separate placeholder was provided.
        """
        # If the repl_identifier starts with '-', it's an append option
        return self.repl_identifier.startswith('-')

    @property
    def original_flag(self) -> str:
        """Return the original flag to use in the command (prefer long flag)."""
        return self.long_flag if self.long_flag else self.short_flag


def parse_flag_syntax(flag_str: str) -> Tuple[str, str]:
    """
    Parse flag syntax supporting alias format.
    
    Supports:
    - "-n" -> ("-n", "")
    - "--no-newline" -> ("", "--no-newline")
    - "-n/--no-newline" -> ("-n", "--no-newline")
    
    Returns:
        Tuple of (short_flag, long_flag)
    """
    if '/' in flag_str:
        parts = flag_str.split('/')
        short_flag = ""
        long_flag = ""
        for part in parts:
            part = part.strip()
            if part.startswith('--'):
                long_flag = part
            elif part.startswith('-'):
                short_flag = part
        return short_flag, long_flag
    elif flag_str.startswith('--'):
        return "", flag_str
    elif flag_str.startswith('-'):
        return flag_str, ""
    return "", ""


def parse_command_structure(just_commands: List[str]) -> Tuple[List[str], List[Argument], Dict[str, Argument]]:
    """
    Parse command structure from a list of command parts.

    This function takes a list of command parts and parses them into:
    - commands: The subcommand hierarchy (e.g., ['just', 'docker', 'ip'])
    - arguments: Positional parameters with annotations
    - options: Flag-based parameters with annotations

    Supported Syntax:
    - Argument: `placeholder[var:type=default#help]`
    - Option (two-token): `--flag placeholder[var:type=default#help]`
    - Inline option: `-n[var:bool#help]`
    - Alias: `-n/--no-newline[var:type#help]`
    - Self-referential flag: `-o/--output` → defaults to `[-o/--output:str]`

    Limitations:
    - Parameters are only added to the FIRST process in a pipeline
    - Pipe symbols (`|`) in quoted strings are not distinguished from shell pipes
    - For complex pipelines, create extensions for individual commands

    Args:
        just_commands: List of command parts to parse

    Returns:
        Tuple of (commands, arguments, options)
    """
    commands = []
    arguments = []
    options = {}

    # State for tracking option flags across tokens
    pending_option_flag = ""
    pending_short_flag = ""
    pending_long_flag = ""
    pending_flag_identifier = ""  # The full flag string for self-referential use
    
    for command in just_commands:
        # Check if this token starts a new flag
        is_flag_token = command.startswith('-') and not command[1:2].isdigit()
        
        # Try to extract annotation from this token
        try:
            annotation = re.findall(r'\[(.+?)]', command)[-1]
        except IndexError:
            annotation = ""
        
        if is_flag_token:
            # If there's a pending flag without annotation, process it as self-referential first
            if pending_option_flag:
                # Create self-referential option: -o/--output defaults to [-o/--output:str]
                arg = _process_annotation(
                    annotation=_make_self_referential_annotation(pending_flag_identifier),
                    identifier=pending_flag_identifier,
                    short_flag=pending_short_flag,
                    long_flag=pending_long_flag
                )
                options[pending_option_flag] = arg
            
            # Parse the new flag syntax (supports -n/--no-newline format)
            flag_part = command.split('[')[0]
            short_flag, long_flag = parse_flag_syntax(flag_part)
            
            # Use the long flag name (without --) or short flag name (without -) as key
            if long_flag:
                option_flag = long_flag.lstrip('-')
            elif short_flag:
                option_flag = short_flag.lstrip('-')
            else:
                option_flag = flag_part.lstrip('-')
            
            # Check if this flag token also has an inline annotation (e.g., -n[var:bool#help])
            if annotation:
                # Inline option - process immediately
                identifier = flag_part  # The flag itself is the placeholder
                
                # Process the annotation and create the argument
                arg = _process_annotation(
                    annotation=annotation,
                    identifier=identifier,
                    short_flag=short_flag,
                    long_flag=long_flag
                )
                options[option_flag] = arg
                
                # Reset pending state
                pending_option_flag = ""
                pending_short_flag = ""
                pending_long_flag = ""
                pending_flag_identifier = ""
            else:
                # Flag without annotation - store for later
                pending_option_flag = option_flag
                pending_short_flag = short_flag
                pending_long_flag = long_flag
                pending_flag_identifier = flag_part
            continue
        
        # Not a flag token
        if pending_option_flag:
            # Previous token was a flag, this token should be the placeholder with annotation
            if annotation:
                identifier = command.split('[')[0]  # The placeholder part
                
                # Process the annotation and create the argument
                arg = _process_annotation(
                    annotation=annotation,
                    identifier=identifier,
                    short_flag=pending_short_flag,
                    long_flag=pending_long_flag
                )
                options[pending_option_flag] = arg
            else:
                # No annotation - treat the pending flag as self-referential
                # and this token as a regular command/argument
                arg = _process_annotation(
                    annotation=_make_self_referential_annotation(pending_flag_identifier),
                    identifier=pending_flag_identifier,
                    short_flag=pending_short_flag,
                    long_flag=pending_long_flag
                )
                options[pending_option_flag] = arg
                
                # Also process the current token as regular
                if not annotation:
                    commands.append(command)
            
            # Reset pending state
            pending_option_flag = ""
            pending_short_flag = ""
            pending_long_flag = ""
            pending_flag_identifier = ""
            continue
        
        # Regular token (not a flag and no pending flag)
        if annotation:
            # This is a positional argument with annotation
            identifier = command.split('[')[0]
            arg = _process_annotation(
                annotation=annotation,
                identifier=identifier,
                short_flag="",
                long_flag=""
            )
            arguments.append(arg)
        else:
            # Regular command (subcommand name)
            commands.append(command)

    # Handle trailing pending flag (flag at end with no following token)
    if pending_option_flag:
        arg = _process_annotation(
            annotation=_make_self_referential_annotation(pending_flag_identifier),
            identifier=pending_flag_identifier,
            short_flag=pending_short_flag,
            long_flag=pending_long_flag
        )
        options[pending_option_flag] = arg

    return commands, arguments, options


def _make_self_referential_annotation(flag_str: str) -> str:
    """
    Create a self-referential annotation for a flag.
    
    Example:
        "-o/--output" -> "o_output:str"
        "-n" -> "n:str"
        "--verbose" -> "verbose:str"
    
    Args:
        flag_str: The flag string (e.g., "-o/--output")
    
    Returns:
        Annotation string for use in _process_annotation
    """
    # Create a variable name from the flag
    # Remove leading dashes and replace / with _
    var_name = flag_str.lstrip('-').replace('/', '_').replace('-', '_')
    return f"{var_name}:str"


def _process_annotation(annotation: str, identifier: str, short_flag: str, long_flag: str) -> Argument:
    """
    Process an annotation string and create an Argument.
    
    Args:
        annotation: The annotation string (e.g., "var:type=default#help")
        identifier: The placeholder/identifier to replace
        short_flag: Optional short flag (e.g., "-n")
        long_flag: Optional long flag (e.g., "--no-newline")
    
    Returns:
        Argument object
    """
    help_msg = ""
    default_value = None
    variable_type = 'str'
    
    # Extract help message
    if '#' in annotation:
        annotation, help_msg = annotation.split('#', maxsplit=1)
    
    # Extract default value
    if '=' in annotation:
        annotation, default_value = annotation.split('=', maxsplit=1)
    
    # Extract type and variable name
    if ':' in annotation:
        variable_name, variable_type = annotation.split(':', maxsplit=1)
    else:
        variable_name = annotation
    
    # Convert default value to appropriate type
    if default_value is not None:
        if variable_type == 'int':
            try:
                default_value = int(default_value)
            except ValueError:
                pass
        elif variable_type == 'float':
            try:
                default_value = float(default_value)
            except ValueError:
                pass
        elif variable_type == 'bool':
            default_value = default_value.lower() in ('true', '1', 'yes', 'on')
    
    # Sanitize variable_name to be a valid Python identifier
    # Strip leading dashes and convert hyphens to underscores
    variable_name = variable_name.lstrip('-').replace('-', '_')
    
    return Argument(
        repl_identifier=identifier,
        variable_name=variable_name,
        variable_type=TYPES[variable_type],
        default_value=default_value,
        help_msg=help_msg,
        short_flag=short_flag,
        long_flag=long_flag
    )
