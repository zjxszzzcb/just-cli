# PROJECT KNOWLEDGE BASE

**Generated:** 2026-02-17T10:14:56Z
**Commit:** 68feb62
**Branch:** dev-installer

## OVERVIEW
Python CLI toolkit (just-cli) - all-in-one developer toolbox with download, extract, edit, view, tunnel, and extension system. Built with typer, textual, rich.

## STRUCTURE
```
./
├── src/just/           # Main package
│   ├── cli.py          # Entry point
│   ├── commands/       # CLI commands (download, extract, edit, view, tunnel, linux)
│   ├── core/           # Core: config, installer, extension, system_probe
│   ├── installers/    # Per-tool installers (docker, cloudflare, nvm, etc.)
│   ├── tui/           # Textual UI components (editor, markdown, extension)
│   └── utils/         # Utilities: archive, download, shell, progress
├── tests/              # Custom test framework (describe/it/expect API)
├── docs/               # Documentation
└── pyproject.toml      # Hatchling build config
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Add CLI command | `src/just/commands/` | Add `.py` file, auto-loaded |
| Add installer | `src/just/installers/` | Per-tool installer modules |
| Extension system | `src/just/core/extension/` | Parser, generator, validator |
| Archive handling | `src/just/utils/archive/` | Format detection, extractors |
| TUI components | `src/just/tui/` | Editor, markdown viewer |
| Config | `src/just/core/config/` | JustConfig, env handling |

## CONVENTIONS
- **Build**: hatchling + pyproject.toml (src-layout)
- **CLI**: typer app, commands auto-loaded from `commands/` dir
- **Entry**: `just = "just.cli:main"` in pyproject.toml
- **Testing**: Custom framework in `tests/testing.py` (describe/it/expect), NOT pytest
- **No linter configured**: No ruff/mypy/flake8 in CI
- **Download in installers**: Use `just.download_with_resume()` instead of curl/wget for consistency and resume support

## ANTI-PATTERNS (THIS PROJECT)
- NO anti-pattern comments found (no DO NOT/NEVER/ALWAYS/DEPRECATED markers)
- CI has NO test validation before publish (only runs on tag push)
- No dependency caching in GitHub Actions

## UNIQUE STYLES
- **Custom test framework**: Uses `describe()`/`it()`/`expect()` (like Jest), NOT pytest
- **Dynamic command loading**: Commands loaded from `~/.just/extensions/` at runtime
- **String-replacement extensions**: `[name:type#help]` syntax for CLI generation

## COMMANDS
```bash
# Install
pip install just-cli

# Run tests
cd tests && python run_tests.py

# Build
python -m build
```

## NOTES
- Python >= 3.10 required
- No pre-commit hooks configured
- No type checking (mypy) in CI
- Only publishes on git tag push (`v*`)
