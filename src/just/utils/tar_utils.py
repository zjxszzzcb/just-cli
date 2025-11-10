import tarfile
from pathlib import Path
from typing import Optional

import just.utils.echo_utils as echo


def detect_tar_compression(archive_path: str) -> Optional[str]:
    """
    Detect the compression type of a tar archive based on file extension.
    
    Args:
        archive_path: Path to the tar archive
        
    Returns:
        Compression mode string or None if uncompressed
    """
    path = Path(archive_path)
    suffixes = ''.join(path.suffixes).lower()
    
    if '.tar.gz' in suffixes or '.tgz' in suffixes:
        return 'gz'
    elif '.tar.xz' in suffixes or '.txz' in suffixes:
        return 'xz'
    elif '.tar.bz2' in suffixes or '.tbz' in suffixes or '.tbz2' in suffixes:
        return 'bz2'
    elif '.tar.zst' in suffixes or '.tzst' in suffixes:
        return 'zst'
    elif '.tar' in suffixes:
        return None
    else:
        return None


def extract_tar(archive_path: str, output_dir: Optional[str] = None) -> bool:
    """
    Extract a tar archive (with various compression formats) to the specified directory.
    
    Supports: .tar, .tar.gz, .tgz, .tar.xz, .tar.bz2, .tar.zst
    
    Args:
        archive_path: Path to the tar archive
        output_dir: Directory to extract to. If None, extracts to current directory
        
    Returns:
        True if successful, False otherwise
    """
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
        
        compression = detect_tar_compression(str(archive_path))
        
        if compression == 'zst':
            try:
                import zstandard as zstd
                
                with open(archive_path, 'rb') as compressed:
                    dctx = zstd.ZstdDecompressor()
                    with dctx.stream_reader(compressed) as reader:
                        with tarfile.open(fileobj=reader, mode='r|') as tar_ref:
                            tar_ref.extractall(output_dir)
            except ImportError:
                echo.error("zstandard package is required for .tar.zst files. Install with: pip install zstandard")
                return False
        else:
            mode = f'r:{compression}' if compression else 'r'
            with tarfile.open(archive_path, mode) as tar_ref:
                tar_ref.extractall(output_dir)
        
        echo.info(f"Extracted {archive_path} to {output_dir}")
        return True
    except Exception as e:
        echo.error(f"Failed to extract tar archive: {e}")
        return False


def create_tar(
    archive_path: str,
    source_paths: list[str],
    compression: Optional[str] = None,
    base_dir: Optional[str] = None
) -> bool:
    """
    Create a tar archive from the specified files/directories.
    
    Args:
        archive_path: Path for the output tar archive
        source_paths: List of files/directories to add to the archive
        compression: Compression type ('gz', 'xz', 'bz2', 'zst', or None for no compression)
        base_dir: Base directory for relative paths. If None, uses absolute paths
        
    Returns:
        True if successful, False otherwise
    """
    try:
        archive_path = Path(archive_path)
        archive_path.parent.mkdir(parents=True, exist_ok=True)
        
        if base_dir:
            base_dir = Path(base_dir)
        
        if compression is None:
            compression = detect_tar_compression(str(archive_path))
        
        if compression == 'zst':
            try:
                import zstandard as zstd
                
                with open(archive_path, 'wb') as compressed:
                    cctx = zstd.ZstdCompressor()
                    with cctx.stream_writer(compressed) as writer:
                        with tarfile.open(fileobj=writer, mode='w|') as tar_ref:
                            for source_path in source_paths:
                                source = Path(source_path)
                                if not source.exists():
                                    echo.warning(f"Path not found, skipping: {source}")
                                    continue
                                arcname = source.relative_to(base_dir) if base_dir else source.name
                                tar_ref.add(source, arcname=arcname)
            except ImportError:
                echo.error("zstandard package is required for .tar.zst files. Install with: pip install zstandard")
                return False
        else:
            mode = f'w:{compression}' if compression else 'w'
            with tarfile.open(archive_path, mode) as tar_ref:
                for source_path in source_paths:
                    source = Path(source_path)
                    if not source.exists():
                        echo.warning(f"Path not found, skipping: {source}")
                        continue
                    arcname = source.relative_to(base_dir) if base_dir else source.name
                    tar_ref.add(source, arcname=arcname)
        
        echo.info(f"Created archive: {archive_path}")
        return True
    except Exception as e:
        echo.error(f"Failed to create tar archive: {e}")
        return False
