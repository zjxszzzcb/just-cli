from pathlib import Path
from typing import Optional

import just.utils.echo_utils as echo


def extract_7z(archive_path: str, output_dir: Optional[str] = None) -> bool:
    """
    Extract a 7z archive.

    Args:
        archive_path: Path to the 7z archive
        output_dir: Directory to extract to. If None, extracts to current directory

    Returns:
        True if successful, False otherwise
    """
    try:
        import py7zr
    except ImportError:
        echo.error("py7zr package is required for .7z files. Install with: pip install py7zr")
        return False

    try:
        archive_path = Path(archive_path)
        if not archive_path.exists():
            echo.error(f"Archive not found: {archive_path}")
            return False

        if output_dir is None:
            output_dir = Path.cwd()
        else:
            output_dir = Path(output_dir)

        output_dir.mkdir(parents=True, exist_ok=True)

        with py7zr.SevenZipFile(archive_path, mode='r') as archive:
            archive.extractall(path=output_dir)

        echo.info(f"Extracted {archive_path} to {output_dir}")
        return True
    except Exception as e:
        echo.error(f"Failed to extract 7z archive: {e}")
        return False


def create_7z(source_paths: list[str], output_path: str, base_dir: Optional[str] = None) -> bool:
    """
    Create a 7z archive.

    Args:
        source_paths: List of files/directories to add
        output_path: Path for the output .7z archive
        base_dir: Base directory for relative paths

    Returns:
        True if successful, False otherwise
    """
    try:
        import py7zr
    except ImportError:
        echo.error("py7zr package is required for .7z files. Install with: pip install py7zr")
        return False

    try:
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        if base_dir:
            base_dir = Path(base_dir)

        with py7zr.SevenZipFile(output, mode='w') as archive:
            for source_path in source_paths:
                source = Path(source_path)
                if not source.exists():
                    echo.warning(f"Path not found, skipping: {source}")
                    continue
                arcname = source.relative_to(base_dir) if base_dir else source.name
                if source.is_file():
                    archive.write(source, arcname)
                elif source.is_dir():
                    archive.writeall(source, arcname)

        echo.info(f"Created archive: {output}")
        return True
    except Exception as e:
        echo.error(f"Failed to create 7z archive: {e}")
        return False
