import zipfile
from pathlib import Path
from typing import Optional

import just.utils.echo_utils as echo


def extract_zip(archive_path: str, output_dir: Optional[str] = None) -> bool:
    """
    Extract a zip archive.
    
    Args:
        archive_path: Path to the zip archive
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
        
        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            zip_ref.extractall(output_dir)
            
        echo.info(f"Extracted {archive_path} to {output_dir}")
        return True
    except Exception as e:
        echo.error(f"Failed to extract zip archive: {e}")
        return False


def create_zip(archive_path: str, source_paths: list[str], base_dir: Optional[str] = None) -> bool:
    """
    Create a zip archive.
    
    Args:
        archive_path: Path for the output zip archive
        source_paths: List of files/directories to add
        base_dir: Base directory for relative paths
        
    Returns:
        True if successful, False otherwise
    """
    try:
        archive_path = Path(archive_path)
        archive_path.parent.mkdir(parents=True, exist_ok=True)
        
        if base_dir:
            base_dir = Path(base_dir)
        
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
            for source_path in source_paths:
                source = Path(source_path)
                if not source.exists():
                    echo.warning(f"Path not found, skipping: {source}")
                    continue
                    
                if source.is_file():
                    arcname = source.relative_to(base_dir) if base_dir else source.name
                    zip_ref.write(source, arcname)
                elif source.is_dir():
                    for file_path in source.rglob('*'):
                        if file_path.is_file():
                            arcname = file_path.relative_to(base_dir) if base_dir else file_path.relative_to(source.parent)
                            zip_ref.write(file_path, arcname)
                            
        echo.info(f"Created archive: {archive_path}")
        return True
    except Exception as e:
        echo.error(f"Failed to create zip archive: {e}")
        return False
