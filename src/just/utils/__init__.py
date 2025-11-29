import just.utils.echo_utils as echo

from just.utils.archive import extract
from just.utils.format_utils import docstring
from just.utils.shell_utils import execute_command, execute_commands, split_command
from just.utils.typer_utils import create_typer_app
from just.utils.user_interaction import confirm_action
from just.utils.system_probe import SystemProbe


def __getattr__(name):
    """Lazy import for download_utils to avoid circular imports."""
    if name in ('download_with_resume', 'DownloadError', 'NetworkError', 
                'FileSystemError', 'InvalidResponseError', 'FileSizeMismatchError', 
                'DownloadCancelledError'):
        from just.utils import download_utils
        return getattr(download_utils, name)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


__all__ = [
    "SystemProbe",
    "create_typer_app",
    "docstring",
    "echo",
    "extract",
    "execute_command",
    "execute_commands",
    "split_command",
    "download_with_resume",
    "DownloadError",
    "NetworkError",
    "FileSystemError",
    "InvalidResponseError",
    "FileSizeMismatchError",
    "DownloadCancelledError",
    "confirm_action"
]
