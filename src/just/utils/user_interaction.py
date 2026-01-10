from prompt_toolkit import prompt as pt_prompt
from prompt_toolkit.styles import Style


_prompt_style = Style.from_dict({
    'prompt': '#00aa00 bold',
})


def confirm_action(message: str) -> bool:
    """Prompt user for confirmation"""
    response = pt_prompt(
        f"{message} (y/N): ",
        style=_prompt_style
    ).strip().lower()
    return response in ['y', 'yes']


def get_input(message: str, default: str = "") -> str:
    """Get user input with arrow key support and better styling"""
    return pt_prompt(
        message,
        default=default,
        style=_prompt_style
    )