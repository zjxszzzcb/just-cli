import typer

from typing import List, Optional

from just import config
from just.core.system_probe import get_arch, get_platform, get_distro_name_version
from just.core.config import get_basic_installer_dir

from .package_info import PackageInfo
from .source import fetch_installer_source


def install_package(package_name: str, additional_args: Optional[List[str]] = None):
    arch = get_arch()
    platform = get_platform()
    distro, distro_version = get_distro_name_version(platform)
    package_info = PackageInfo(
        name=package_name,
        platform=platform,
        arch=arch,
        distro=distro,
        distro_version=distro_version,
    )

    installer_sources = config.JUST_INSTALLER_SOURCES
    installer_sources.insert(0, str(get_basic_installer_dir()))

    for source in installer_sources:
        source_instance = fetch_installer_source(source)
        installer = source_instance.get_installer(package_info)
        if installer:
            break
    else:
        raise Exception(f"No installer script found for {package_name}")

    app = typer.Typer()
    
    # Check if already installed
    check_cmd = getattr(installer, "_check_command", None)
    if check_cmd:
        from just.utils import execute_command, echo
        exit_code, _ = execute_command(check_cmd, capture_output=True)
        if exit_code == 0:
            echo.success(f"{package_name} is already installed.")
            return

    app.command()(installer)
    app(additional_args)
