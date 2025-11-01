# 🛠️ JUST CLI

**The simple stuff should be simple.**

Sick of Googling *"how to install X on XXX"* for the 47th time? Exhausted from remembering whether it's `systemctl` or `launchctl` or `net start`? Is it `apt-get update` or `brew upgrade` or `winget update`? Should you use `ifconfig`, `ipconfig`, or `ip addr`? 


Want to install something? `just install xxx`. Need to edit a file? `just edit xxx`. Expose your local service to the internet? `just tunnel xxx`. **That's it.** Go grab a coffee while your colleagues are still Googling and copy-pasting commands.

## ✨ Features

- 🚀 **Modular Architecture** - Built on Typer with dynamic command loading
- 🎨 **Beautiful Output** - Rich library powered colorful terminal experience
- 📝 **Built-in TUI Editor** - Textual-based file editor included
- 🔌 **Extensible** - Add new commands effortlessly
- ⚡ **Zero Friction** - Install with uv and go
- 🌍 **Cross-platform** - Write once, run everywhere

## 📦 Installation

### Using uv (Recommended)

```bash
uv sync
```

### Using pip

```bash
pip install -e .
```

## 🚀 Quick Start

After installation, you can use the `just` command:

```bash
just --help
```

## 📖 Available Commands

### File Editing

Edit any file with built-in TUI or system default editor:

```bash
just edit <file_path>
```

Quick access to configuration:

```bash
just edit config
```

### Cloudflare Tunnel

Spin up a Cloudflare tunnel in seconds:

```bash
just tunnel <url>
```

### Tool Installation

Install tools without remembering platform-specific package managers:

```bash
just install cloudflare
```

No more `winget` vs `apt` vs `brew` confusion. Just install.

## 🏗️ Project Structure

```
just-cli/
├── src/just/
│   ├── cli.py              # CLI entry point and core logic
│   ├── commands/           # Command modules directory
│   │   ├── edit.py         # File editing command
│   │   ├── tunnel.py       # Cloudflare tunnel command
│   │   └── install/        # Installation related commands
│   ├── config/             # Configuration management
│   ├── tui/                # TUI components
│   │   └── editor.py       # Text editor
│   └── utils/              # Utility functions
├── scripts/                # System scripts
│   └── system/
│       ├── linux/
│       └── windows/
└── pyproject.toml          # Project configuration
```

## 🔧 Development Guide

### Adding New Commands

JustTools is designed for extensibility. Adding a new command is simple:

#### Simple Command

1. Create a Python file in `src/just/commands/`
2. Register your command with the `@just_cli.command()` decorator
3. Done. The CLI auto-discovers and loads it.

Example:

```python
from just import just_cli, capture_exception, echo

@just_cli.command(name="mycommand", help="My custom command.")
@capture_exception
def my_command(arg: str):
    echo.success(f"Running with: {arg}")
```

#### Multiple Subcommands

For commands with multiple subcommands (like `just install cloudflare`), follow this pattern:

1. Create a directory under `src/just/commands/` (e.g., `mygroup/`)
2. Create `entry.py` to define the subcommand group:

```python
from just import create_typer_app, just_cli

mygroup_cli = create_typer_app(name="mygroup", help="My command group.")
just_cli.add_typer(mygroup_cli)
```

3. Create individual command files (e.g., `foo.py`):

```python
from just import capture_exception, echo
from .entry import mygroup_cli

@mygroup_cli.command(name="foo", help="Foo subcommand.")
@capture_exception
def foo_command():
    echo.success("Running foo!")
```

4. Usage: `just mygroup foo`


### Philosophy

The goal is simple: **abstract away platform differences**. Whether you're installing a package, deploying a service, or running a script, the command should be the same. `just install`, `just deploy`, `just run`. That's it.

### Environment Configuration

Uses `.env` for configuration management:

- `JUST_EDIT_USE_TOOL`: Editor preference (`textual` or `edit`)

## 📋 Dependencies

- Python >= 3.11

## 📝 License

MIT

## 👤 Author

**zzzcb**
- Email: zjxs.zzzcb@gmail.com

## 🤝 Contributing

Contributions are welcome! Whether it's a new command, bug fix, or platform support, PRs are appreciated.

**Principle**: Keep commands simple and cross-platform. If a command only works on one OS, handle it gracefully with clear error messages.

---

**Made with frustration and coffee ☕** by developers who refuse to memorize platform-specific commands anymore.
