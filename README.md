# 🛠️ JUST CLI

**The simple stuff should be simple.**

Sick of Googling *"how to install X on XXX"* for the 47th time, only to end up copying and pasting similar commands from various official docs?

Tired of copy-pasting giant commands and tapping arrow keys forever just to change one little thing?

Just want an all-in-one toolkit for everyday simple tasks, instead of endlessly searching and testing Deep Research results one by one?

**Stop wasting life on terminal chores !!!**

JUST CLI saves your terminal life from wasted seconds:

- Install something? `just install xxx`
- Edit files? `just edit xxx` (works just like a simple notepad)
- Expose service? `just tunnel xxx`

Besides, with the powerful **Extension System**, you can instantly convert ANY complex shell command into a simple, reusable `just` command - and share it with others.

**That's it.** Now you can focus on what really matters - building great stuff.


## ✨ Features

- 🚀 **Modular Architecture** - Built on Typer with dynamic command loading
- 🎨 **Beautiful Output** - Rich library powered colorful terminal experience
- 📝 **Built-in TUI Editor** - Textual-based file editor included
- 🔌 **Extensible** - Add new commands effortlessly
- ⚡ **Zero Friction** - Install with uv and go
- 🌍 **Cross-platform** - Write once, run everywhere
- 🧠 **Smart Extension System** - Convert any shell command into typed, reusable JUST commands with `just ext add`

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

### Extension System Quick Start

Transform any shell command into a reusable JUST command:

```bash
# Add a new extension command
just ext add docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' f523e75ca4ef
> just docker ip f523e75ca4ef[container_id:str#Docker container ID or name]

# Use your new command
just docker ip my_container
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

### Extension Management

Manage your custom commands with the extension system:

```bash
# Add a new extension command
just ext add <shell_command>

# List all available extensions
just ext --help
```

## 🏗️ Project Structure

```
just-cli/
├── src/just/
│   ├── cli.py              # CLI entry point and core logic
│   ├── commands/           # Command modules directory
│   │   ├── edit.py         # File editing command
│   │   ├── tunnel.py       # Cloudflare tunnel command
│   │   ├── install/        # Installation related commands
│   │   └── extension/      # Extension management commands
│   │       └── add.py      # Add new extensions
│   ├── config/             # Configuration management
│   ├── core/               # Core functionality
│   │   └── extension/      # Extension system core
│   │       ├── parser.py   # Command parsing logic
│   │       ├── generator.py# Script generation logic
│   │       └── utils.py    # Helper functions
│   ├── extensions/         # User-generated extension commands
│   ├── tui/                # TUI components
│   │   ├── editor.py       # Text editor
│   │   └── extension.py    # Extension configuration TUI
│   └── utils/              # Utility functions
├── scripts/                # System scripts
│   └── system/
│       ├── linux/
│       └── windows/
└── pyproject.toml          # Project configuration
```

## 🧠 Extension System

The heart of JUST CLI's power lies in its Extension System. This innovative feature allows you to transform any shell command into a typed, reusable JUST command with minimal effort.

### Core Concept

The Extension System works by:
1. Taking a custom shell command template with placeholders
2. Converting it to a properly typed Typer command
3. Automatically generating the necessary Python code and directory structure
4. Integrating it seamlessly into the existing command hierarchy

### Usage Pattern

```bash
just ext add <any_shell_command>
> just subcmd_1 subcmd_2 <argValue>[varName:varType=defaultValue#help] -optAlias <optValue>[optName:optType=defaultValue#help]
```

### Declaration Syntax

The declaration syntax allows you to define typed parameters with defaults and help text:

- **Positional Arguments**: `param_name:type=default#help text`
- **Options**: `-alias param_name:type=default#help text`
- **Supported Types**: `str`, `int`, `float`, `bool`
- **Defaults**: Optional values assigned with `=`
- **Help Text**: Optional descriptions after `#`

### Examples

#### Simple Docker Command
Convert a complex Docker inspect command into a simple, reusable command:

```bash
just ext add docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' f523e75ca4ef
> just docker ip f523e75ca4ef[container_id:str#Docker container ID or name]
```

Usage: `just docker ip my_container`

#### HTTP API Interaction
Transform a curl command into a typed command with options:

```bash
just ext add curl --data-raw 'domain=<DOMAIN>' <URL>
> just dnslog new <URL>[url:str] --domain <DOMAIN>[domain:str=default_domain#Subdomain for DNS logging]
```

Usage: `just dnslog new https://api.dnslog.com --domain mysubdomain`

#### Command with Numeric Parameters
Create a compression command with typed parameters:

```bash
just ext add gzip -<LEVEL> <FILE>
> just compress <FILE>[file_path:str] -l LEVEL[int=6#Compression level 1-9]
```

Usage: `just compress document.txt -l 9`

### How It Works

1. **Command Parsing**: The system parses your declaration to identify arguments, options, types, defaults, and help text
2. **Code Generation**: It generates a complete Typer command script with proper type annotations
3. **Directory Structure**: Automatically creates the necessary directory structure and `__init__.py` files
4. **Integration**: Seamlessly integrates the new command into the existing command hierarchy
5. **Execution**: When called, the command substitutes parameters and executes the original shell command

### Benefits

- **Type Safety**: All parameters are strongly typed with automatic conversion
- **Help Integration**: Generated commands automatically integrate with `just --help`
- **Default Values**: Support for default parameter values
- **Cross-Platform**: Extensions work on all supported platforms
- **Reusable**: Once created, extensions can be used just like built-in commands
- **No Coding Required**: Create powerful commands without writing any Python code

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
2. Create `__init__.py` to define the subcommand group:

```python
from just import create_typer_app, just_cli

mygroup_cli = create_typer_app(name="mygroup", help="My command group.")
just_cli.add_typer(mygroup_cli)
```

3. Create individual command files (e.g., `foo.py`):

```python
from just import capture_exception, echo
from . import mygroup_cli

@mygroup_cli.command(name="foo", help="Foo subcommand.")
@capture_exception
def foo_command():
    echo.success("Running foo!")
```

4. Usage: `just mygroup foo`

### Adding New Extensions

With the Extension System, you don't need to write Python code to add new commands. Simply use:

```bash
just ext add <your_shell_command>
```

And follow the interactive prompts to define your command structure. The system will automatically generate the Python code and integrate it into the CLI.

For advanced users who want to create extensions programmatically, you can use the extension generation APIs in `src/just/core/extension/`.


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
