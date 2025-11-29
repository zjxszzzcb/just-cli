import shlex
import shutil
import subprocess

from typing import Optional, Tuple, List, Union

import just.utils.echo_utils as echo


def execute_command(
    command: str,
    capture_output: bool = False,
    verbose: Optional[bool] = None
) -> Tuple[int, str]:
    """
    Execute a command in the terminal.

    Args:
        command: The command to execute.
        capture_output: Whether to capture the output of the command. Defaults to False.
        verbose: Whether to print the command being executed and its output.

    Returns:
        A tuple containing the exit code of the command and the output of the command.
    """
    if verbose is None and not capture_output:
        verbose = True
    else:
        verbose = False

    terminal_width = min(shutil.get_terminal_size().columns, 70)
    exit_code, output = 0, ""

    try:
        command = command.strip()
        if verbose:
            echo.debug(" Command Execution Start ".center(terminal_width, '='))
            echo.debug(f"> {command}")
        if not capture_output:
            res = subprocess.run(shlex.split(command))
        else:
            res = subprocess.run(shlex.split(command), capture_output=True, text=True)
            output = res.stdout
        exit_code = res.returncode
    except Exception as e:
        echo.error(e)
        exit_code = 1
        output = str(e)
    except KeyboardInterrupt:
        pass
    if verbose:
        echo.debug(" Command Execution End ".center(terminal_width, '='))
    return exit_code, output


def execute_commands(
    commands: Union[str, List[str]],
    capture_output: bool = False,
    verbose: Optional[bool] = None
) -> List[str]:
    if isinstance(commands, str):
        commands = [line for line in commands.splitlines()]

    outputs = []
    for line in commands:
        outputs.append(execute_command(line, capture_output, verbose))

    return outputs


def split_command(command: str):
    return shlex.split(command)
