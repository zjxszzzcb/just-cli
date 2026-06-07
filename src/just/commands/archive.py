import typer
from pathlib import Path
from typing import Optional

from just import Annotated, just_cli, capture_exception
from just.utils import echo
from just.utils.archive import archive as archive_create, detect_format_by_extension, ArchiveFormat


@just_cli.command(name="archive")
@capture_exception
def archive_command(
    source: Annotated[str, typer.Argument(
        help="Path to the file or directory to archive"
    )],
    output: Annotated[str, typer.Option(
        "-o", "--output",
        help="Output archive file path (format detected from extension)"
    )],
) -> None:
    """
    Create archives and compressed files.

    Supports: ZIP, TAR (with gz/bz2/xz/zst compression), GZIP, BZIP2, XZ, ZSTD, 7Z

    Format is automatically determined by the output file extension.
    Single-file formats (gz, bz2, xz, zst) only accept a single file source.

    Optional dependencies:
    - 7Z support: pip install py7zr
    - ZSTD support: pip install zstandard

    Examples:
        just archive mydir -o backup.zip          # Create ZIP archive
        just archive mydir -o backup.tar.gz       # Create tar.gz archive
        just archive myfile.txt -o myfile.txt.gz  # Compress single file with gzip
        just archive mydir -o backup.7z           # Create 7z archive
    """
    source_path = Path(source)

    if not source_path.exists():
        echo.error(f"Source not found: {source}")
        raise typer.Exit(1)

    fmt = detect_format_by_extension(output)
    if fmt is None or fmt == ArchiveFormat.UNKNOWN:
        echo.error(f"Unknown archive format for output: {output}")
        echo.info("Supported: .zip, .tar, .tar.gz, .tgz, .tar.bz2, .tbz, "
                  ".tar.xz, .txz, .tar.zst, .tzst, .gz, .bz2, .xz, .zst, .7z")
        raise typer.Exit(1)

    if fmt == ArchiveFormat.RAR:
        echo.error("RAR format is not supported for archiving")
        raise typer.Exit(1)

    if not archive_create([str(source_path)], output, base_dir=str(source_path.parent)):
        raise Exception("Failed to create archive")
