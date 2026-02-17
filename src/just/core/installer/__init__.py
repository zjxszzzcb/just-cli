from .decorator import installer
from .simple_release import SimpleReleaseInstaller
from .binary import BinaryInstaller
from .bash_script import BashScriptInstaller


__all__ = [
    "installer",
    "SimpleReleaseInstaller",
    "BinaryInstaller",
    "BashScriptInstaller"
]