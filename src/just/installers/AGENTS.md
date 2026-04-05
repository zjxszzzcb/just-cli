# INSTALLER KNOWLEDGE BASE

**Generated:** 2026-04-05
**Scope:** Per-tool installation modules

## OVERVIEW
15 specialized installer modules with complexity levels from simple script execution to multi-step systemd service configuration.

## STRUCTURE
```
./installers/
├── clash/          # Complex: 184 lines, systemd service, subscription config
├── gh/             # Medium: 49 lines, platform-specific package managers
├── nvm/            # Simple: 29 lines, versioned script download
├── uv/             # Simple: 30 lines, BashScriptInstaller wrapper
├── cloudflare/     # Simple: 16 lines, BinaryInstaller with PM fallback
├── docker/         # Simple: 16 lines, single script download
└── [9 others]      # Simple: minimal pattern variations
```

## WHERE TO LOOK
| Pattern | Example | Notes |
|---------|---------|-------|
| Simple script download | docker, nvm, uv | Download official script and execute |
| Package manager priority | cloudflare, gh, opencode | Try winget/brew/apt first, fallback to manual |
| BinaryInstaller class | cloudflare | Single binary: download, chmod +x, symlink to PATH |
| BashScriptInstaller | uv | Wrap curl-pipe-sh patterns |
| Complex multi-step | clash | systemd user service, subscription retry, GeoIP download |

## CONVENTIONS
- **Decorator**: `@just.installer(check="command --version")` for auto-detection
- **Platform detection**: `just.system.platform` (linux/windows/darwin)
- **Architecture mapping**: `just.system.arch` (x86_64/aarch64/armv7l)
- **Package managers**: `just.system.pms.winget/brew/apt.is_available()`
- **Installer helpers**: Use `BinaryInstaller()`, `ArchiveInstaller()`, `BashScriptInstaller()` from `just.core.installer`
- **Download**: Use `just.download_with_resume()` for all downloads (not curl/wget)
- **Execute**: Use `just.execute_commands()` for shell commands

## ANTI-PATTERNS
- Direct `curl`/`wget` calls in installers - use `just.download_with_resume()` instead
- Reinventing binary installation logic - use `BinaryInstaller` helper class
- Manual chmod + PATH management - let `BinaryInstaller` handle it
- Missing platform/arch validation - always check before download
- No fallback strategy - prefer package managers over manual downloads
- Silent failures - use explicit `raise NotImplementedError` with helpful messages

## INSTALLER PATTERNS BY COMPLEXITY

**Simple (16-30 lines)**:
- Download single script/binary and execute
- No state management beyond file placement
- Example: docker, cloudflare, nvm, uv

**Medium (30-100 lines)**:
- Platform-specific package manager detection
- Multiple installation methods with fallback
- Example: gh

**Complex (>100 lines)**:
- Multi-step orchestration with retry logic
- Service configuration and lifecycle management
- User-facing feedback and verification steps
- Example: clash (systemd user service, subscription URL, GeoIP database)

## MOST COMPLEX REFERENCE
**clash/installer.py** (184 lines) demonstrates:
- Platform/arch validation with mapping
- Retry logic for subscription download
- systemd user service file generation
- Service lifecycle (enable/start/status)
- User feedback and verification
- Architecture: `mihomo-linux-{arch}-{version}.gz` naming pattern
