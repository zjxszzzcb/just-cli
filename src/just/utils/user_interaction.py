import sys

from prompt_toolkit import prompt as pt_prompt
from prompt_toolkit.styles import Style


_prompt_style = Style.from_dict({
    'prompt': '#00aa00 bold',
})


def confirm_action(message: str) -> bool:
    """Prompt user for confirmation.

    Falls back to a plain ``input()`` (defaulting to "no") when stdin is not a
    TTY — prompt_toolkit crashes on non-terminal stdin, which broke scripted /
    CI usage of commands guarded by confirmation prompts.
    """
    prompt_text = f"{message} (y/N): "
    if not sys.stdin.isatty():
        try:
            response = input(prompt_text).strip().lower()
        except EOFError:
            return False
        return response in ['y', 'yes']

    response = pt_prompt(
        prompt_text,
        style=_prompt_style,
    ).strip().lower()
    return response in ['y', 'yes']


def get_input(message: str, default: str = "") -> str:
    """Get user input with arrow key support and better styling.

    Falls back to a plain ``input()`` when stdin is not a TTY.
    """
    if not sys.stdin.isatty():
        try:
            return input(message)
        except EOFError:
            return default

    return pt_prompt(
        message,
        default=default,
        style=_prompt_style,
    )