# AGENTS.md - `src/just/utils`

## OVERVIEW
Low-level utilities for archive handling, file I/O, downloads, and CLI interactions.

## STRUCTURE
```
utils/
├── archive/              # Archive format detection & extraction
│   ├── format_detect.py  # Magic bytes + extension detection
│   ├── extractor.py      # Unified extract() interface
│   ├── zip_handler.py    # ZIP extraction
│   ├── tar_handler.py    # TAR/GZ/BZ2/XZ/ZSTD handling
│   ├── sevenzip_handler.py
│   └── compression_handler.py
├── progress.py           # Rich-based progress bars
├── download_utils.py    # HTTP downloads with resume support
├── shell_utils.py       # Shell command helpers
├── file_utils.py        # File operations
├── typer_utils.py       # Typer CLI utilities
├── echo_utils.py       # Console output helpers
├── env_utils.py        # Environment variable helpers
├── user_interaction.py # User input handling
└── format_utils.py     # Formatting utilities
```

## WHERE TO LOOK
| Task | File | Notes |
|------|------|-------|
| Detect archive format | `archive/format_detect.py` | Magic bytes: ZIP, GZIP, BZIP2, XZ, ZSTD, 7Z, RAR |
| Extract any archive | `archive/extractor.py` | Auto-detects format, delegates to handlers |
| Add new archive format | `archive/` | Add handler, register in `extractor.py` |
| Progress bar | `progress.py` | Uses Rich, auto-fallback support |
| Download with resume | `download_utils.py` | httpx-based, supports headers |

## CONVENTIONS
- **Archive handlers**: Return `bool` (True=success)
- **Magic bytes first**: Format detection uses bytes before extension
- **Compression detection**: Opens compressed stream to check for `ustar` header (tar vs single-file)
- **Progress bars**: Use `progress_bar()` factory function for compatibility

## ANTI-PATTERNS
- **No RAR default**: RAR requires `rarfile` package (not bundled), shows error if detected
- **No exception swallowing**: Archive extraction returns False on failure, logs error explicitly
