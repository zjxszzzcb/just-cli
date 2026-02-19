from .decorator import installer
from .simple_release import SimpleReleaseInstaller
from .binary import BinaryInstaller
from .script_installer import ScriptInstaller, BashScriptInstaller, PowerShellInstaller


__all__ = [
    "installer",
    "SimpleReleaseInstaller",
    "BinaryInstaller",
    "BashScriptInstaller",
    "ScriptInstaller",
    "PowerShellInstaller",
]
