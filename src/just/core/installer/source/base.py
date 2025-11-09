from abc import ABC, abstractmethod
from typing import Callable, Optional

from just.core.installer.package_info import PackageInfo


class JustInstallerSource(ABC):

    def __init__(self, url: str):
        self.url = url

    @abstractmethod
    def contains(self, package_info: PackageInfo) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_installer_script(self, package_info: PackageInfo) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_installer(self, package_info: PackageInfo) -> Optional[Callable]:
        raise NotImplementedError
