import ast
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
            # Find the installer function name using AST
            installer_func_name = self._find_installer_function_name(script_path)

            if installer_func_name:
                # Reuse existing module loading logic
                spec = importlib.util.spec_from_file_location(f"installer_{package_info.name}", script_path)
                module = importlib.util.module_from_spec(spec)
                sys.modules[f"installer_{package_info.name}"] = module
                spec.loader.exec_module(module)

                # Return the installer function if it exists
                if hasattr(module, installer_func_name):
                    return getattr(module, installer_func_name)

            return None
        except Exception:
            return None

    def _find_installer_function_name(self, script_path: str) -> Optional[str]:
        """Find the installer function name using AST parsing."""
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                source = f.read()

            tree = ast.parse(source)

            # Look for functions in the module
            for node in ast.iter_child_nodes(tree):
                if isinstance(node, ast.FunctionDef):
                    # 1. Check for @installer decorator
                    for decorator in node.decorator_list:
                        if isinstance(decorator, ast.Name) and decorator.id == 'installer':
                            return node.name

                    # 2. Check for function named 'installer'
                    if node.name == 'installer':
                        return 'installer'

                    # 3. Check for function named 'main' (backward compatibility)
                    if node.name == 'main':
                        return 'main'

            return None
        except Exception:
            return None

    def _get_script_path(self, package_info: PackageInfo) -> str:
        """Get the path to the installer script for the given package."""
        # Construct the script path: {source_url}/{package_name}/installer.py
        return os.path.join(self.url, package_info.name, "installer.py")