# Decorator
from .decorator import installer

# Installers (from installers/ subpackage)
from .installers import (
    BashScriptInstaller,
    BinaryInstaller,
    PowerShellInstaller,
    ScriptInstaller,
    SimpleReleaseInstaller,
)


__all__ = [
    # Decorator
    "installer",
    # Installers
    "BashScriptInstaller",
    "BinaryInstaller",
    "PowerShellInstaller",
    "ScriptInstaller",
    "SimpleReleaseInstaller",
]
