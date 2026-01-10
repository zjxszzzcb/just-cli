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
    is_varargs: bool = False  # True for [...] syntax - captures all remaining args


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
        
        True when:
        - repl_identifier is the flag itself (e.g., "-o/--output")
        - AND no separate user-facing flags are defined (short_flag/long_flag match the identifier)
        
        False when:
        - User-facing flags are different from the identifier (Option Alias case)
        - e.g., --text[-m/--messages] means replace --text with value from -m/--messages
        """
        # If the repl_identifier doesn't start with '-', it's definitely a replacement option
        if not self.repl_identifier.startswith('-'):
            return False
        
        # If user-facing flags are specified and different from identifier, it's a replacement option
        # Option Alias syntax: --original[-u/--user] means replace --original with value from -u/--user
        if self.short_flag or self.long_flag:
            # Check if the flags are different from the identifier (alias case)
            identifier_flags = set()
            if '/' in self.repl_identifier:
                parts = self.repl_identifier.split('/')
                identifier_flags = set(p.strip() for p in parts)
            else:
                identifier_flags = {self.repl_identifier}
            
            user_flags = set()
            if self.short_flag:
                user_flags.add(self.short_flag)
            if self.long_flag:
                user_flags.add(self.long_flag)
            
            # If user flags are different from identifier flags, it's a replacement option (alias)
            if user_flags != identifier_flags:
                return False
        
        # Default: if identifier starts with '-', it's an append option
        return True

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
    
    Supports:
        var:type="default with spaces"#help  - quoted defaults
        ...                                   - varargs (all remaining args)
        ...#help                              - varargs with help text
    
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
    variable_name = annotation
    is_varargs = False
    
    # Check for varargs syntax: [...] or [...#help]
    if annotation.startswith('...'):
        is_varargs = True
        variable_name = 'args'
        variable_type = 'list'
        # Extract help message if present
        if '#' in annotation:
            help_msg = annotation.split('#', 1)[1]
    else:
        # Parse normal annotation using regex to handle quoted values
        # Format: var[:type][=default][#help]
        pattern = r'^([^:=#]+)(?::([^=#]+))?(?:=("(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'|[^#]*))?(?:#(.*))?$'
        match = re.match(pattern, annotation)
        
        if match:
            variable_name = match.group(1) or ""
            variable_type = match.group(2) or 'str'
            raw_default = match.group(3)
            help_msg = match.group(4) or ""
            
            # Process default value - strip quotes if present
            if raw_default is not None:
                raw_default = raw_default.strip()
                if (raw_default.startswith('"') and raw_default.endswith('"')) or \
                   (raw_default.startswith("'") and raw_default.endswith("'")):
                    default_value = raw_default[1:-1].replace('\\"', '"').replace("\\'", "'")
                else:
                    default_value = raw_default if raw_default else None
        
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
    # Handle flag alias syntax like -m/--messages
    # This enables Option Alias: --text[-m/--messages:str] where user sees -m/--messages
    raw_variable_name = variable_name
    if variable_name.startswith('-') or ('/' in variable_name and '-' in variable_name):
        # This looks like a flag alias syntax (e.g., -m/--messages)
        # Extract user-facing flags from the annotation and override passed-in flags
        alias_short, alias_long = parse_flag_syntax(raw_variable_name)
        if alias_short or alias_long:
            # Override with the user-facing flags from annotation
            short_flag = alias_short
            long_flag = alias_long
        
        # Extract variable name from long flag if available, otherwise from short flag
        if alias_long:
            # Use long flag name: --messages -> messages
            variable_name = alias_long.lstrip('-').replace('-', '_')
        elif alias_short:
            # Use short flag name: -m -> m
            variable_name = alias_short.lstrip('-')
        else:
            # Fallback: just sanitize as usual
            variable_name = variable_name.lstrip('-').replace('/', '_').replace('-', '_')
    else:
        variable_name = variable_name.lstrip('-').replace('-', '_')
    
    # Handle list type for varargs
    actual_type = list if variable_type == 'list' else TYPES.get(variable_type, str)
    
    return Argument(
        repl_identifier=identifier,
        variable_name=variable_name,
        variable_type=actual_type,
        default_value=default_value,
        help_msg=help_msg,
        short_flag=short_flag,
        long_flag=long_flag,
        is_varargs=is_varargs
    )

