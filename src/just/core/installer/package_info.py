from dataclasses import dataclass

from just.core.system_probe import Arch, Platform


@dataclass()
class PackageInfo:
    name: str
    platform: Platform
    arch:  Arch
    distro: str
    distro_version: str
