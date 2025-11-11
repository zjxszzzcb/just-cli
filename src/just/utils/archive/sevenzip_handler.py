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
