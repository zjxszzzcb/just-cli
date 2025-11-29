import gzip
import bz2
import lzma
from pathlib import Path
from typing import Optional

import just.utils.echo_utils as echo


def extract_gzip(archive_path: str, output_dir: Optional[str] = None) -> bool:
    """
    Extract a gzip compressed file.
    
    Args:
        archive_path: Path to the gzip file
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
            output_dir = archive_path.parent
        else:
            output_dir = Path(output_dir)
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_name = archive_path.stem
        if not output_name:
            output_name = archive_path.name.replace('.gz', '')
        
        output_file = output_dir / output_name
        
        with gzip.open(archive_path, 'rb') as gz_file:
            with open(output_file, 'wb') as out_file:
                out_file.write(gz_file.read())
        
        echo.info(f"Extracted {archive_path} to {output_file}")
        return True
    except Exception as e:
        echo.error(f"Failed to extract gzip file: {e}")
        return False


def extract_bzip2(archive_path: str, output_dir: Optional[str] = None) -> bool:
    """
    Extract a bzip2 compressed file.
    
    Args:
        archive_path: Path to the bzip2 file
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
            output_dir = archive_path.parent
        else:
            output_dir = Path(output_dir)
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_name = archive_path.stem
        if not output_name:
            output_name = archive_path.name.replace('.bz2', '')
        
        output_file = output_dir / output_name
        
        with bz2.open(archive_path, 'rb') as bz_file:
            with open(output_file, 'wb') as out_file:
                out_file.write(bz_file.read())
        
        echo.info(f"Extracted {archive_path} to {output_file}")
        return True
    except Exception as e:
        echo.error(f"Failed to extract bzip2 file: {e}")
        return False


def extract_xz(archive_path: str, output_dir: Optional[str] = None) -> bool:
    """
    Extract an xz/lzma compressed file.
    
    Args:
        archive_path: Path to the xz file
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
            output_dir = archive_path.parent
        else:
            output_dir = Path(output_dir)
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_name = archive_path.stem
        if not output_name:
            output_name = archive_path.name.replace('.xz', '')
        
        output_file = output_dir / output_name
        
        with lzma.open(archive_path, 'rb') as xz_file:
            with open(output_file, 'wb') as out_file:
                out_file.write(xz_file.read())
        
        echo.info(f"Extracted {archive_path} to {output_file}")
        return True
    except Exception as e:
        echo.error(f"Failed to extract xz file: {e}")
        return False


def extract_zstd(archive_path: str, output_dir: Optional[str] = None) -> bool:
    """
    Extract a zstd compressed file.
    
    Args:
        archive_path: Path to the zstd file
        output_dir: Directory to extract to. If None, extracts to current directory
        
    Returns:
        True if successful, False otherwise
    """
    try:
        import zstandard as zstd
    except ImportError:
        echo.error("zstandard package is required for .zst files. Install with: pip install zstandard")
        return False
    
    try:
        archive_path = Path(archive_path)
        if not archive_path.exists():
            echo.error(f"Archive not found: {archive_path}")
            return False
        
        if output_dir is None:
            output_dir = archive_path.parent
        else:
            output_dir = Path(output_dir)
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_name = archive_path.stem
        if not output_name:
            output_name = archive_path.name.replace('.zst', '')
        
        output_file = output_dir / output_name
        
        with open(archive_path, 'rb') as compressed:
            dctx = zstd.ZstdDecompressor()
            with open(output_file, 'wb') as out_file:
                out_file.write(dctx.decompress(compressed.read()))
        
        echo.info(f"Extracted {archive_path} to {output_file}")
        return True
    except Exception as e:
        echo.error(f"Failed to extract zstd file: {e}")
        return False
