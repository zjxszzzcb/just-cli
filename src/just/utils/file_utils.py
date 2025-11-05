import os

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


if __name__ == "__main__":
    print(read_file_text(__file__, with_line_numbers=True))