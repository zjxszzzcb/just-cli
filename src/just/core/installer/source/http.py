import ast
import httpx
import os
import sys
import importlib.util
from pathlib import Path
from urllib.parse import urljoin
from typing import Callable, Optional

from just.core.installer.package_info import PackageInfo

from .base import JustInstallerSource


class JustInstallerHttpSource(JustInstallerSource):

    def contains(self, package_info: PackageInfo) -> bool:
        """Check if the installer script exists for the given package."""
        try:
            script_url = self._get_script_url(package_info)
            response = httpx.head(script_url)
            return response.status_code == 200
        except Exception:
            return False

    def get_installer_script(self, package_info: PackageInfo) -> str:
        """Get the installer script content for the given package."""
        script_url = self._get_script_url(package_info)
        response = httpx.get(script_url)
        response.raise_for_status()
        return response.text

    def get_installer(self, package_info: PackageInfo) -> Optional[Callable]:
        """Get the installer function for the given package by downloading and caching it."""
        try:
            # Download the script
            script_url = self._get_script_url(package_info)
            response = httpx.get(script_url)
            response.raise_for_status()

            # Create cache directory
            cache_dir = Path.home() / ".just" / "cache" / "installers"
            cache_dir.mkdir(parents=True, exist_ok=True)

            # Create package-specific directory
            package_cache_dir = cache_dir / package_info.name
            package_cache_dir.mkdir(exist_ok=True)

            # Save script to cache
            cache_path = package_cache_dir / "installer.py"
            with open(cache_path, 'w', encoding='utf-8') as f:
                f.write(response.text)

            # Find the installer function name using AST
            installer_func_name = self._find_installer_function_name(str(cache_path))

            if installer_func_name:
                # Reuse existing module loading logic
                spec = importlib.util.spec_from_file_location(f"installer_{package_info.name}", str(cache_path))
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

    def _get_script_url(self, package_info: PackageInfo) -> str:
        """Get the URL to the installer script for the given package."""
        # Construct the script URL: {source_url}/{package_name}/installer.py
        return urljoin(self.url.rstrip('/') + '/', f"{package_info.name}/installer.py")
