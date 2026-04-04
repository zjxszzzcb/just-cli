"""
Clash/Mihomo Installer

Installs Mihomo (Clash Meta) proxy client and sets it up as a systemd user service.
"""

import os
from pathlib import Path

import just

from just.utils.file_utils import write_file, mkdir
from just.utils.shell_utils import execute_command


@just.installer
def install_clash(
    subscription_url: just.Annotated[str, just.Argument(help="Clash subscription URL")],
    version: just.Annotated[str, just.Option("-v", "--version", help="Mihomo version")] = "v1.18.10"
):
    """
    Install Clash/Mihomo proxy client as a systemd user service.

    Downloads the Mihomo binary, configures it with your subscription,
    and sets it up as a user service (no root required).
    """
    # Platform validation
    if just.system.platform != 'linux':
        raise NotImplementedError(f"Clash installer is only supported on Linux, current platform: {just.system.platform}")

    # Architecture mapping and validation
    arch_map = {
        'x86_64': 'amd64',
        'aarch64': 'arm64',
        'armv7l': 'armv7'
    }

    if just.system.arch not in arch_map:
        raise NotImplementedError(f"Unsupported architecture: {just.system.arch}")

    go_arch = arch_map[just.system.arch]

    # Setup paths
    home = Path.home()
    cache_dir = home / ".cache" / "just" / "installed"
    config_dir = home / ".config" / "clash"
    systemd_dir = home / ".config" / "systemd" / "user"

    binary_path = cache_dir / "clash"
    config_path = config_dir / "config.yaml"
    geoip_path = config_dir / "Country.mmdb"
    service_path = systemd_dir / "clash.service"

    # Step 1: Download Mihomo binary
    just.echo.info(f"Downloading Mihomo {version} for {just.system.arch} ({go_arch})")
    mkdir(str(cache_dir))

    # Mihomo release files include version in filename: mihomo-linux-amd64-v1.18.10.gz
    gz_filename = f"mihomo-linux-{go_arch}-{version}.gz"
    gz_path = cache_dir / gz_filename
    binary_url = f"https://github.com/MetaCubeX/mihomo/releases/download/{version}/{gz_filename}"

    # Download compressed binary
    just.download_with_resume(url=binary_url, output_file=str(gz_path))

    # Extract .gz file
    just.echo.info("Extracting binary")
    just.extract(str(gz_path), str(cache_dir))

    # Extracted file has version in name, rename to 'clash'
    extracted_name = f"mihomo-linux-{go_arch}-{version}"
    extracted_path = cache_dir / extracted_name

    if extracted_path.exists():
        # Remove existing binary if present
        if binary_path.exists():
            binary_path.unlink()
        extracted_path.rename(binary_path)
    elif not binary_path.exists():
        raise RuntimeError(f"Extracted file not found: {extracted_path}")

    # Remove .gz file
    gz_path.unlink()

    # Make executable
    just.echo.info("Making binary executable")
    binary_path.chmod(0o755)

    # Step 2: Create config directory
    just.echo.info("Creating config directory")
    mkdir(str(config_dir))

    # Step 3: Download subscription configuration (with retry)
    just.echo.info("Downloading subscription configuration")
    max_retries = 3
    config_downloaded = False

    for attempt in range(1, max_retries + 1):
        try:
            just.download_with_resume(url=subscription_url, output_file=str(config_path))
            config_downloaded = True
            break
        except Exception as e:
            if attempt < max_retries:
                just.echo.warning(f"Download failed (attempt {attempt}/{max_retries}): {e}")
                just.echo.info("Retrying...")
            else:
                just.echo.error(f"Failed to download subscription after {max_retries} attempts: {e}")
                just.echo.error("Please download the configuration manually and save it to:")
                just.echo.error(f"  {config_path}")
                raise

    if not config_downloaded:
        raise RuntimeError("Failed to download subscription configuration")

    # Step 4: Download GeoIP database
    just.echo.info("Downloading GeoIP database")
    geoip_url = "https://github.com/MetaCubeX/meta-rules-dat/releases/download/latest/country.mmdb"
    just.download_with_resume(url=geoip_url, output_file=str(geoip_path))

    # Step 5: Create systemd user service
    just.echo.info("Creating systemd user service")

    # Verify systemd is available
    exit_code, _ = execute_command("systemctl --user --version", capture_output=True)
    if exit_code != 0:
        raise RuntimeError("systemd user service manager is not available")

    # Create systemd directory
    mkdir(str(systemd_dir))

    # Generate service file
    service_content = f"""[Unit]
Description=Clash Service
After=network.target

[Service]
Type=simple
ExecStart={binary_path} -d {config_dir}
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=default.target
"""

    write_file(str(service_path), service_content)

    # Step 6: Enable and start service
    just.echo.info("Reloading systemd daemon")
    execute_command("systemctl --user daemon-reload", capture_output=True)

    just.echo.info("Enabling clash service")
    execute_command("systemctl --user enable clash", capture_output=True)

    just.echo.info("Starting clash service")
    exit_code, output = execute_command("systemctl --user start clash", capture_output=True)

    if exit_code != 0:
        just.echo.warning(f"Service started with exit code {exit_code}: {output}")

    # Verification
    just.echo.info("Verifying service status")
    exit_code, status = execute_command("systemctl --user status clash --no-pager", capture_output=True)

    if exit_code == 0:
        just.echo.success("Clash service is running!")
    else:
        just.echo.warning(f"Service status check returned code {exit_code}")

    just.echo.success("\n========================================")
    just.echo.success("Clash installation completed!")
    just.echo.success("========================================")
    just.echo.info(f"\nBinary: {binary_path}")
    just.echo.info(f"Config: {config_path}")
    just.echo.info(f"Service: {service_path}")
    just.echo.info("\nManage service with:")
    just.echo.info("  systemctl --user status clash")
    just.echo.info("  systemctl --user stop clash")
    just.echo.info("  systemctl --user restart clash")
    just.echo.info("\nView logs:")
    just.echo.info("  journalctl --user -u clash -f")
    just.echo.info("\nTest proxy (default port 7890):")
    just.echo.info("  curl -x http://127.0.0.1:7890 https://api.ipify.org")
