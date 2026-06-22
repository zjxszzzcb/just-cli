from pathlib import Path
from typing import Optional

import just.utils.echo_utils as echo
from .format_detect import ArchiveFormat, detect_format_by_extension
from .zip_handler import create_zip
from .tar_handler import create_tar
from .compression_handler import create_gzip, create_bzip2, create_xz, create_zstd
from .sevenzip_handler import create_7z

# Single-file compression formats (source must be a file, not a directory)
_SINGLE_FILE_FORMATS = {
    ArchiveFormat.GZIP,
    ArchiveFormat.BZIP2,
    ArchiveFormat.XZ,
    ArchiveFormat.ZSTD,
}

# Maps ArchiveFormat to tar compression mode
_TAR_COMPRESSION_MAP = {
    ArchiveFormat.TAR: None,
    ArchiveFormat.TAR_GZ: 'gz',
    ArchiveFormat.TAR_BZ2: 'bz2',
    ArchiveFormat.TAR_XZ: 'xz',
    ArchiveFormat.TAR_ZST: 'zst',
}


def archive(
    source_paths: list[str],
    output_path: str,
    base_dir: Optional[str] = None,
) -> bool:
    """
    Universal archive creation interface.

    Detects format from the output file extension and routes to the
    appropriate handler.

    Supported formats:
    - ZIP (.zip)
    - TAR (.tar, .tar.gz, .tgz, .tar.bz2, .tbz, .tar.xz, .txz, .tar.zst, .tzst)
    - GZIP (.gz), BZIP2 (.bz2), XZ (.xz), ZSTD (.zst)  -- single file only
    - 7Z (.7z) -- requires py7zr package

    Args:
        source_paths: List of files/directories to archive
        output_path: Path for the output archive
        base_dir: Base directory for relative paths inside the archive

    Returns:
        True if successful, False otherwise
    """
    fmt = detect_format_by_extension(output_path)
    if fmt is None or fmt == ArchiveFormat.UNKNOWN:
        echo.error(f"Unknown archive format for output: {output_path}")
        return False

    if fmt == ArchiveFormat.RAR:
        echo.error("RAR format is not supported for archiving")
        return False

    # Single-file compression: only one file source allowed
    if fmt in _SINGLE_FILE_FORMATS:
        if len(source_paths) != 1:
            echo.error(f"Format .{fmt.value} only supports compressing a single file")
            return False
        source = Path(source_paths[0])
        if source.is_dir():
            echo.error(f"Format .{fmt.value} only supports single files, not directories. "
                       "Use .tar.{ext} for directory compression.")
            return False
        if not source.is_file():
            echo.error(f"Source not found: {source}")
            return False

        create_fn = {
            ArchiveFormat.GZIP: create_gzip,
            ArchiveFormat.BZIP2: create_bzip2,
            ArchiveFormat.XZ: create_xz,
            ArchiveFormat.ZSTD: create_zstd,
        }[fmt]
        return create_fn(source_paths[0], output_path)

    # TAR family
    if fmt in _TAR_COMPRESSION_MAP:
        compression = _TAR_COMPRESSION_MAP[fmt]
        return create_tar(output_path, source_paths, compression=compression, base_dir=base_dir)

    if fmt == ArchiveFormat.ZIP:
        return create_zip(output_path, source_paths, base_dir=base_dir)

    if fmt == ArchiveFormat.SEVEN_ZIP:
        return create_7z(source_paths, output_path, base_dir=base_dir)

    echo.error(f"Unsupported archive format: {fmt}")
    return False
