# Decorator
from .decorator import installer

# Installers
from .binary import BinaryInstaller
from .script_installer import BashScriptInstaller, PowerShellInstaller, ScriptInstaller
from .simple_release import SimpleReleaseInstaller


__all__ = [
    # Decorator
    "installer",
    # Installers
    "BinaryInstaller",
    "BashScriptInstaller",
    "PowerShellInstaller",
    "ScriptInstaller",
    "SimpleReleaseInstaller",
]
