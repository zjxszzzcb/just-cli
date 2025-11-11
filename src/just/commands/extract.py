import typer
from pathlib import Path
from typing import Optional

from just import Annotated, just_cli, capture_exception
from just.utils import echo
from just.utils.archive import extract as archive_extract, detect_archive_format, ArchiveFormat


def get_default_output_dir(archive_path: str) -> str:
    """
    Get default output directory from archive filename.
    
    Simply removes all extensions by taking everything before the first dot.
    
    Args:
        archive_path: Path to the archive file
        
    Returns:
        Directory name without extensions
    """
    return archive_path.split(".")[0]


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
    Extract archive and compressed files with automatic format detection.
    
    Supports: ZIP, TAR (with gz/bz2/xz/zst compression), GZIP, BZIP2, XZ, ZSTD, 7Z
    
    Automatically detects format using magic bytes (file signatures) for reliable
    identification, even with incorrect file extensions. Extracts to a directory
    named after the archive by default.
    
    Optional dependencies:
    - 7Z support: pip install py7zr
    - ZSTD support: pip install zstandard
    
    Examples:
        just extract archive.zip          # Extracts to ./archive/
        just extract archive.tar.gz       # Extracts to ./archive/
        just extract file.gz              # Extracts to ./file
        just extract data.7z -o out/      # Extracts to ./out/
    """
    archive_path = Path(archive)
    
    if not archive_path.exists():
        echo.error(f"Archive not found: {archive}")
        raise typer.Exit(1)
    
    fmt = detect_archive_format(str(archive_path))
    
    if fmt == ArchiveFormat.UNKNOWN:
        echo.error(f"Unknown or unsupported archive format: {archive}")
        raise typer.Exit(1)
    
    if fmt == ArchiveFormat.RAR:
        echo.error("RAR format detected but not supported")
        echo.info("RAR is a proprietary format. Install rarfile: pip install rarfile")
        raise typer.Exit(1)
    
    if output is None:
        output = get_default_output_dir(str(archive_path))
    
    if not archive_extract(str(archive_path), output):
        raise Exception("Failed to extract archive")
