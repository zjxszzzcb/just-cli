# INSTALLER FRAMEWORK KNOWLEDGE BASE

**Generated:** 2026-04-05
**Scope:** Core installer framework and source system

## OVERVIEW
Modular installer framework with pluggable source system (HTTP/local), automated install discovery, and pre-built installer classes (BinaryInstaller, ArchiveInstaller, BashScriptInstaller).

## STRUCTURE
```
installer/
├── install_package.py          # Factory: install_package() orchestrates source discovery
├── installers/                  # Installer implementation classes
│   ├── binary_release.py       # BinaryInstaller, ArchiveInstaller
│   └── remote_script.py        # BashScriptInstaller, PowerShellInstaller
├── source/                     # Pluggable source system
│   ├── base.py                 # JustInstallerSource abstract base
│   ├── http.py                 # HTTP source for remote installers
│   └── local.py                # Local file system source
├── package_info.py             # Platform/arch/distro metadata container
├── utils.py                    # Path operations, symlink management
└── decorator.py                # @just.installer decorator
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Add new installer class | `installers/` | Extend BinaryInstaller/ArchiveInstaller pattern |
| Add new source type | `source/` | Implement JustInstallerSource ABC |
| Modify install discovery | `install_package.py` | Source iteration logic (lines 28-35) |
| Change PATH check logic | `utils.py` | check_path_included() function |
| Decorator behavior | `decorator.py` | Function wrapping and check command storage |

## CONVENTIONS
- **Source priority**: Built-in installers (`get_basic_installer_dir()`) checked before remote sources
- **Auto-detection**: `_check_command` attribute used to verify installation (lines 42-58)
- **BinaryInstaller**: Downloads directly to `~/.just/bin/`, chmod +x, no cache cleanup
- **ArchiveInstaller**: Downloads to cache, extracts to `~/.just/releases/`, symlinks to `~/.just/bin/`, cleanup after install
- **Executables**: ArchiveInstaller auto-detects from `bin/` dir or root, checks executable permissions (Unix) or extensions (Windows)
- **Verification**: Post-installation check runs `--version` command and shows first line of output

## ANTI-PATTERNS (THIS MODULE)
- NO manual symlink creation - use `create_symlink_or_wrapper()` from utils
- NO hardcoded paths - always use `get_bin_dir()`, `get_cache_dir()`, `get_releases_dir()`
- NO reinventing executable detection - reuse `_auto_detect_executables()` pattern
- NO bypassing source system - all installers must go through `install_package()` factory

## ARCHITECTURE NOTES

**Source System Flow**:
1. `install_package()` creates `PackageInfo` with platform/arch/distro
2. Iterates through sources (built-in first, then remote)
3. Each source's `get_installer()` returns callable or None
4. First found installer is executed with `typer.Typer()`
5. Verification runs after installation

**BinaryInstaller** (`~/.just/bin/<alias>`):
- Direct download to bin directory
- Single file: download, chmod, PATH check
- No cache, no extraction

**ArchiveInstaller** (`~/.just/releases/<name>/`):
- Multi-file: download to cache, extract, symlink executables
- Auto-detects executables from bin/ or root
- Cleanup removes cached archive after successful install

**PackageInfo**:
- Immutable container for platform detection results
- Used by sources to filter compatible installers
- Fields: name, platform, arch, distro, distro_version
