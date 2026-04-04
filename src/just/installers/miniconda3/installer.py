import just
from pathlib import Path


@just.installer(check="conda --version")
def install_miniconda3():
    """
    Install Miniconda3 - minimal conda installer (Linux only).
    """
    install_dir = Path.home() / "miniconda3"

    if just.system.platform == "linux":
        # Linux installation
        if just.system.arch == "x86_64":
            installer_url = "https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
        elif just.system.arch == "aarch64":
            installer_url = "https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh"
        else:
            raise NotImplementedError(f"Miniconda3 installer not available for {just.system.arch}")

        installer_path = install_dir / "miniconda.sh"
        just.download_with_resume(installer_url, output_file=str(installer_path))

        try:
            just.execute_commands(f"bash {installer_path} -b -u -p {install_dir}")
            just.execute_commands(f"{install_dir}/bin/conda init --all")
        finally:
            # Clean up installer script even on failure
            if installer_path.exists():
                installer_path.unlink()
    else:
        raise NotImplementedError(f"Miniconda3 installer is not supported on {just.system.platform}.")

