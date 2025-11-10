import shutil
import typer
from pathlib import Path
from typing import Optional

from just import Annotated, just_cli, capture_exception, system
from just.utils import echo, execute_command
from just.utils.zip_utils import extract_zip
from just.utils.tar_utils import extract_tar


def detect_archive_type(archive_path: str) -> Optional[str]:
    """
    Detect archive type based on file extension.
    
    Returns:
        'zip', 'tar', or None if unknown
    """
    path = Path(archive_path)
    suffixes = ''.join(path.suffixes).lower()
    
    if '.zip' in suffixes:
        return 'zip'
    elif any(ext in suffixes for ext in ['.tar', '.tgz', '.tar.gz', '.tar.xz', '.tar.bz2', '.tar.zst', '.txz', '.tbz', '.tbz2', '.tzst']):
        return 'tar'
    
    return None


def get_default_output_dir(archive_path: str) -> str:
    """
    Get default output directory from archive filename (removes all extensions).
    
    Args:
        archive_path: Path to the archive file
        
    Returns:
        Directory name without extensions
    """
    path = Path(archive_path)
    name = path.name
    
    if name.endswith('.tar.gz'):
        name = name[:-7]
    elif name.endswith('.tar.xz'):
        name = name[:-7]
    elif name.endswith('.tar.bz2'):
        name = name[:-8]
    elif name.endswith('.tar.zst'):
        name = name[:-8]
    elif name.endswith('.tgz'):
        name = name[:-4]
    elif name.endswith('.txz'):
        name = name[:-4]
    elif name.endswith('.tbz') or name.endswith('.tbz2'):
        name = name[:-4] if name.endswith('.tbz') else name[:-5]
    elif name.endswith('.tzst'):
        name = name[:-5]
    else:
        name = path.stem
    
    return str(path.parent / name)


def extract_with_system_tool(archive_path: str, output_dir: Optional[str] = None) -> bool:
    """
    Try to extract using system tools (unzip, tar).
    
    Returns:
        True if successful, False if system tool not available or failed
    """
    archive_type = detect_archive_type(archive_path)
    
    if archive_type == 'zip':
        if shutil.which('unzip'):
            echo.info("Using system unzip tool...")
            if output_dir:
                cmd = f'unzip -q "{archive_path}" -d "{output_dir}"'
            else:
                cmd = f'unzip -q "{archive_path}"'
            
            exit_code, _ = execute_command(cmd, capture_output=True, verbose=False)
            if exit_code == 0:
                echo.info(f"Extracted {archive_path}" + (f" to {output_dir}" if output_dir else ""))
                return True
                
    elif archive_type == 'tar':
        if shutil.which('tar'):
            echo.info("Using system tar tool...")
            if output_dir:
                Path(output_dir).mkdir(parents=True, exist_ok=True)
                cmd = f'tar -xf "{archive_path}" -C "{output_dir}"'
            else:
                cmd = f'tar -xf "{archive_path}"'
            
            exit_code, _ = execute_command(cmd, capture_output=True, verbose=False)
            if exit_code == 0:
                echo.info(f"Extracted {archive_path}" + (f" to {output_dir}" if output_dir else ""))
                return True
    
    return False


def extract_with_python(archive_path: str, output_dir: Optional[str] = None) -> bool:
    """
    Extract using Python built-in libraries.
    
    Returns:
        True if successful, False otherwise
    """
    archive_type = detect_archive_type(archive_path)
    
    if archive_type == 'zip':
        echo.info("Using Python zipfile library...")
        return extract_zip(archive_path, output_dir)
    elif archive_type == 'tar':
        echo.info("Using Python tarfile library...")
        return extract_tar(archive_path, output_dir)
    else:
        echo.error(f"Unsupported archive format: {archive_path}")
        return False


@just_cli.command(name="extract")
@capture_exception
def extract_command(
    archive: Annotated[str, typer.Argument(
        help="Path to the archive file to extract"
    )],
    output: Annotated[Optional[str], typer.Option(
        "-o", "--output",
        help="Output directory for extracted files (default: archive name without extension)"
    )] = None
) -> None:
    """
    Extract archive files (zip, tar, tar.gz, tgz, tar.xz, tar.zst).
    
    By default, extracts to a directory with the same name as the archive (without extension).
    Automatically detects archive format and uses system tools (unzip, tar) when available,
    falling back to Python implementation if needed.
    
    Examples:
        just extract archive.zip          # Extracts to ./archive/
        just extract archive.tar.gz       # Extracts to ./archive/
        just extract archive.tar.zst -o extracted/
    """
    archive_path = Path(archive)
    
    if not archive_path.exists():
        echo.error(f"Archive not found: {archive}")
        raise typer.Exit(1)
    
    archive_type = detect_archive_type(str(archive_path))
    if not archive_type:
        echo.error(f"Unknown archive format: {archive}")
        raise typer.Exit(1)
    
    if output is None:
        output = get_default_output_dir(str(archive_path))
    
    if extract_with_system_tool(str(archive_path), output):
        return
    
    echo.warning("System tool not available or failed, using Python implementation...")
    
    if not extract_with_python(str(archive_path), output):
        raise Exception("Failed to extract archive")
