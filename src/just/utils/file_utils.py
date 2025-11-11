import os
import shutil

from typing import List, Optional, Union
from pathlib import Path


def search_file(source_root: str, file_path: str) -> Optional[str]:
    if os.path.exists(file_path):
        return str(Path(file_path).resolve())
    elif os.path.exists(os.path.join(source_root, file_path)):
        return str(Path(os.path.join(source_root, file_path)).resolve())
    # search `file_path` from `source_root`
    p_root = Path(source_root)
    try:
        found_iterator = p_root.rglob(file_path)
        first_match = next(found_iterator)
        return str(first_match.resolve())
    except StopIteration:
        return None


def read_file_by_lines(file_path: str, encoding: str = "utf-8") -> List[str]:
    with open(file_path, "r", encoding=encoding) as f:
        return f.readlines()


def join_lines_with_number(
    lines: List[str],
    start_index: int = 1,
    sep: str = "\n",
    number_sep: str = "→"
) -> str:
    """Add sequentially numbered prefixes to text lines and join into a single string.

    Processes a list of text lines by adding formatted line numbers as prefixes and
    concatenates them into a single string. The line number formatting automatically
    adjusts to the total line count for proper right-alignment.

    Args:
        lines: List of text lines to be processed. Each string represents one line.
        start_index: Starting value for line numbering sequence. Default is 1.
        sep: Separator string inserted between processed lines. Default is newline.
        number_sep: Separator between line number and line content. Default is "→".

    Returns:
        Single string containing all input lines with numbered prefixes, separated
        by the specified separator.

    Raises:
        ValueError: If start_index is negative or lines contains non-string elements.

    Examples:
        Basic usage:
        >>> text_lines = ["First line", "Second line", "Third line"]
        >>> numbered_text = join_lines_with_number(text_lines)
        >>> print(numbered_text)
        1→First line
        2→Second line
        3→Third line
    """
    lines_count = len(lines)
    width = len(str(lines_count))
    return sep.join([f"{i:>{width}}{number_sep}{line}" for i, line in enumerate(lines, start_index)])


def read_file_text(file_path: str, encoding: str = "utf-8", with_line_numbers: bool = False) -> str:
    if with_line_numbers:
        file_text_lines = read_file_by_lines(file_path, encoding)
        return join_lines_with_number(file_text_lines, sep='')
    with open(file_path, "r", encoding=encoding) as f:
        return f.read()


def read_file_bytes(file_path: str) -> bytes:
    with open(file_path, "rb") as f:
        return f.read()


def write_file(file_path: str, content: Union[str, bytes], encoding: str = "utf-8"):
    if isinstance(content, str):
        with open(file_path, "w", encoding=encoding) as f:
            f.write(content)
    else:
        with open(file_path, "wb") as f:
            f.write(content)


def mkdir(*dirs):
    """Create one or more directories, including parent directories if needed.
    
    Args:
        *dirs: directory paths.
    
    Raises:
        OSError: If directory creation fails.
    
    Examples:
        Create a single directory:
        >>> mkdir("/path/to/new/directory")
        
        Create multiple directories:
        >>> mkdir(["/path/to/dir1", "/path/to/dir2"])
    """
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)


def mv(src: str, dst: str):
    """Move or rename a file or directory.
    
    Args:
        src: Source file or directory path.
        dst: Destination file or directory path.
    
    Raises:
        FileNotFoundError: If source does not exist.
        OSError: If move operation fails.
    
    Examples:
        Move a file:
        >>> mv("/path/to/file.txt", "/new/path/file.txt")
        
        Rename a directory:
        >>> mv("/path/to/old_name", "/path/to/new_name")
    """
    shutil.move(src, dst)


def rm(*targets: str):
    """Remove one or more files or directories.
    
    Args:
        *targets: Variable number of file or directory paths to remove.
    
    Raises:
        OSError: If removal fails.
    
    Examples:
        Remove a single file:
        >>> rm("/path/to/file.txt")
        
        Remove multiple files and directories:
        >>> rm("/path/to/file1.txt", "/path/to/dir1", "/path/to/file2.txt")
    """
    for target in targets:
        target_path = Path(target)
        if target_path.is_file():
            target_path.unlink()
        elif target_path.is_dir():
            shutil.rmtree(target_path)
        elif target_path.exists():
            target_path.unlink()


def symlink(src: str, dst: str):
    """Create a symbolic link pointing to src named dst.
    
    Automatically detects whether the source is a file or directory
    and creates the appropriate type of symlink.
    
    Args:
        src: Source file or directory path (link target).
        dst: Destination symlink path (link name).
    
    Raises:
        FileNotFoundError: If source does not exist.
        FileExistsError: If destination already exists.
        OSError: If symlink creation fails.
    
    Examples:
        Create a symlink to a file:
        >>> symlink("/path/to/file.txt", "/path/to/link.txt")
        
        Create a symlink to a directory:
        >>> symlink("/path/to/directory", "/path/to/link_dir")
    """
    src_path = Path(src)
    target_is_directory = src_path.is_dir()
    os.symlink(src, dst, target_is_directory=target_is_directory)


if __name__ == "__main__":
    print(read_file_text(__file__, with_line_numbers=True))