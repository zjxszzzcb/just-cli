"""JUST CLI Note Utility Functions"""

from pathlib import Path
from typing import List

from just.core.config.utils import get_config_dir
from just.utils.file_utils import read_file_text, write_file


def get_notes_dir() -> Path:
    """Get JUST notes directory path"""
    return get_config_dir() / "notes"


def ensure_notes_dir_exists() -> Path:
    """Ensure JUST notes directory exists, create if not"""
    notes_dir = get_notes_dir()
    notes_dir.mkdir(parents=True, exist_ok=True)
    return notes_dir


def sanitize_filename(title: str) -> str:
    """Convert title to safe filename by replacing invalid characters with underscore

    Replaces the following characters with underscore:
    / \\ : * ? " < > |

    Args:
        title: Original title string

    Returns:
        Safe filename with .md extension

    Examples:
        >>> sanitize_filename("My Test/Note")
        'My_Test_Note.md'
        >>> sanitize_filename("Invalid:File")
        'Invalid_File.md'
    """
    if not title:
        title = "Untitled"

    # Replace invalid characters with underscore
    safe = title.strip()
    for char in '/\\:*?"<>|':
        safe = safe.replace(char, "_")

    # Add .md extension
    return f"{safe}.md"


def list_notes() -> List[Path]:
    """List all note files in alphabetical order

    Returns:
        List of Path objects representing note files, sorted alphabetically

    Examples:
        >>> notes = list_notes()
        >>> len(notes) > 0
        True
    """
    ensure_notes_dir_exists()
    notes_dir = get_notes_dir()

    if not notes_dir.exists():
        return []

    note_files = []
    for file_path in notes_dir.iterdir():
        if file_path.is_file():
            note_files.append(file_path)

    # Sort by filename (without .md extension)
    return sorted(note_files, key=lambda p: p.stem)


def get_unique_filename(title: str) -> str:
    """Get a unique filename for a note, appending _1, _2, etc. if needed

    Args:
        title: Original note title

    Returns:
        Unique filename with .md extension

    Examples:
        >>> get_unique_filename("Test Note")
        'Test_Note.md'
        >>> get_unique_filename("Test Note")  # If Test_Note.md already exists
        'Test_Note_1.md'
    """
    base_filename = sanitize_filename(title)
    notes_dir = get_notes_dir()
    note_path = notes_dir / base_filename

    if not note_path.exists():
        return base_filename

    # Extract base name without .md
    base = base_filename[:-3] if base_filename.endswith(".md") else base_filename
    counter = 1

    while True:
        new_filename = f"{base}_{counter}.md"
        new_path = notes_dir / new_filename
        if not new_path.exists():
            return new_filename
        counter += 1


def create_note(title: str, content: str = "") -> Path:
    """Create a new note file with unique filename handling

    Args:
        title: Note title (will be sanitized to filename)
        content: Note content (default: empty string)

    Returns:
        Path to created note file

    Examples:
        >>> note_path = create_note("My Note", "This is content")
        >>> note_path.exists()
        True
    """
    filename = get_unique_filename(title)
    notes_dir = get_notes_dir()

    ensure_notes_dir_exists()
    note_path = notes_dir / filename

    write_file(str(note_path), content)
    return note_path


def delete_note(filename: str) -> bool:
    """Delete a note file

    Args:
        filename: Note filename (without .md extension)

    Returns:
        True if file was deleted, False if file didn't exist

    Examples:
        >>> delete_note("My Note")
        True
    """
    notes_dir = get_notes_dir()

    ensure_notes_dir_exists()
    note_path = notes_dir / sanitize_filename(filename)

    if not note_path.exists():
        return False

    note_path.unlink()
    return True


def read_note(filename: str) -> str:
    """Read note content

    Args:
        filename: Note filename (without .md extension)

    Returns:
        Note content as string, or empty string if file doesn't exist

    Examples:
        >>> content = read_note("My Note")
        >>> isinstance(content, str)
        True
    """
    notes_dir = get_notes_dir()

    ensure_notes_dir_exists()
    note_path = notes_dir / sanitize_filename(filename)

    if not note_path.exists():
        return ""

    return read_file_text(str(note_path))


def note_exists(filename: str) -> bool:
    """Check if a note exists

    Args:
        filename: Note filename (without .md extension)

    Returns:
        True if note exists, False otherwise

    Examples:
        >>> note_exists("My Note")
        False
    """
    notes_dir = get_notes_dir()

    ensure_notes_dir_exists()
    note_path = notes_dir / sanitize_filename(filename)

    return note_path.exists()
