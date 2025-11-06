"""JUST CLI Initialization Command"""

import typer
from typing_extensions import Annotated

from just import just_cli, capture_exception, echo
from just.core.system_probe import probe_and_initialize_config
from just.utils.config_utils import ensure_config_dir, save_system_config, is_initialized


@just_cli.command(name="init")
@capture_exception
def init_just(
    force: Annotated[bool, typer.Option(
        "--force", "-f",
        help="Force re-initialization even if already initialized"
    )] = False
):
    """
    Initialize JUST CLI environment by probing system information.

    This command detects system information, available package managers,
    and essential tools, then stores this information in ~/.just/system_info.json
    for use by other JUST commands.
    """
    # Check if already initialized
    if is_initialized() and not force:
        echo.warning("JUST CLI is already initialized.")
        echo.info("Use --force to re-initialize.")
        return

    echo.info("Initializing JUST CLI environment...")

    # Ensure config directory exists
    ensure_config_dir()

    # Probe system information
    echo.info("Probing system information...")
    config = probe_and_initialize_config()

    # Save configuration
    echo.info("Saving configuration...")
    save_system_config(config)

    # Display summary
    echo.green("JUST CLI initialized successfully!")
    echo.info(f"Platform: {config.system.platform} ({config.system.distro} {config.system.distro_version})")
    echo.info(f"Architecture: {config.system.arch}")
    echo.info(f"Shell: {config.system.shell_name}")
    echo.info(f"Package managers detected: {len(config.pms)}")
    echo.info(f"Tools detected: {sum(1 for tool in config.tools.values() if tool.installed)}/{len(config.tools)}")