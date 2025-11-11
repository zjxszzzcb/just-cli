import os
import sys
import importlib.util
from pathlib import Path
from typing import Callable, Optional

from just.core.installer.package_info import PackageInfo

from .base import JustInstallerSource


class JustInstallerLocalSource(JustInstallerSource):

    def contains(self, package_info: PackageInfo) -> bool:
        """Check if the installer script exists for the given package."""
        script_path = self._get_script_path(package_info)
        return os.path.exists(script_path)

    def get_installer_script(self, package_info: PackageInfo) -> str:
        """Get the installer script content for the given package."""
        script_path = self._get_script_path(package_info)
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"Installer script not found: {script_path}")

        with open(script_path, 'r', encoding='utf-8') as f:
            return f.read()

    def get_installer(self, package_info: PackageInfo) -> Optional[Callable]:
        """Get the installer function for the given package."""
        script_path = self._get_script_path(package_info)
        if not os.path.exists(script_path):
            return None

        try:
            # Load the module
            spec = importlib.util.spec_from_file_location(f"installer_{package_info.name}", script_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[f"installer_{package_info.name}"] = module
            spec.loader.exec_module(module)

            # Find function with _is_just_installer attribute (set by @installer decorator)
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if callable(attr) and getattr(attr, '_is_just_installer', False):
                    return attr

            return None
        except Exception:
            return None

    def _get_script_path(self, package_info: PackageInfo) -> str:
        """Get the path to the installer script for the given package."""
        # Construct the script path: {source_url}/{package_name}/installer.py
        return os.path.join(self.url, package_info.name, "installer.py")