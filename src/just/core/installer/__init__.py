# Decorator
from .decorator import installer

# Installers (from installers/ subpackage)
from .installers import (
    ArchiveInstaller,
    BashScriptInstaller,
    BinaryInstaller,
    PowerShellInstaller,
    ScriptInstaller,
)


__all__ = [
    # Decorator
    "installer",
    # Installers
    "ArchiveInstaller",
    "BashScriptInstaller",
    "BinaryInstaller",
    "PowerShellInstaller",
    "ScriptInstaller",
]
