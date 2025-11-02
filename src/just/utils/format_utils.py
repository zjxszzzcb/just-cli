import inspect
import re


def docstring(doc: str) -> str:
    # Remove line continuations (backslash + newline) and any following whitespace
    doc = re.sub(r'\\\n\s*', '', doc)
    # Normalize remaining indentation using docstring()
    return inspect.cleandoc(doc)
