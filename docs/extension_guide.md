# Extension System Guide

The `just` extension system allows you to create custom CLI commands by wrapping existing shell commands with a clean, typed interface.

## Quick Start

```bash
# Create an extension
just ext add echo MESSAGE
> just echo MESSAGE[msg:str#Message to display]

# Use the extension
just echo --help
just echo "Hello World"
```

## Core Concepts

Extensions work by **template replacement** - you define placeholders in your command that get replaced with user input at runtime.

---

## Syntax Patterns

There are **3 core patterns** for defining extension parameters:

### 1. Positional Arguments (Replace Placeholder)

```
PLACEHOLDER[var:type=default#help]
```

The placeholder in the original command is replaced with the user's input.

| Component | Description | Example |
|-----------|-------------|---------|
| `PLACEHOLDER` | Text to replace in command | `MESSAGE` |
| `var` | Python variable name | `msg` |
| `type` | Type hint (str, int, float, bool) | `str` |
| `default` | Default value (makes arg optional) | `"Hello"` |
| `help` | Help text shown in --help | `Message to display` |

**Examples:**

```bash
# Basic argument
just ext add echo MESSAGE
> just echo MESSAGE[msg]

# With type
just ext add echo MESSAGE
> just echo MESSAGE[msg:str]

# With default (makes it optional)
just ext add echo MESSAGE
> just echo MESSAGE[msg:str=Hello]

# With quoted default (for spaces)
just ext add echo MESSAGE
> just echo MESSAGE[msg:str="Hello World"]

# With help text
just ext add echo MESSAGE
> just echo MESSAGE[msg:str#Message to display]

# Full syntax with quoted default
just ext add echo MESSAGE
> just echo MESSAGE[msg:str="Hello World"#Message to display]
```

---

### 2. Options (Replace Placeholder)

```
--flag PLACEHOLDER[var:type]
```

A named option where the placeholder value is replaced.

**Examples:**

```bash
# Named option
just ext add curl -X METHOD URL
> just curl --method METHOD[method:str=GET] URL[url:str]

# Usage:
just curl --method POST https://api.example.com
# Executes: curl -X POST https://api.example.com
```

---

### 3. Option Aliases (Append to Command)

```
-s/--source[target:type]
```

This pattern is different - it **appends** the original flag to the command instead of replacing a placeholder. The user sees the new flag name, but the original flag is added to the command.

**Key difference:**
- User runs: `just cmd --target value`
- Executes: `original_cmd --source value`

**Examples:**

```bash
# Create alias: user uses --output-dir, command gets --output
just ext add rsync SRC DEST
> just rsync SRC[src:str] DEST[dest:str] -o/--output[output_dir:str]

# Usage:
just rsync /local /remote --output-dir /logs
# Executes: rsync /local /remote --output /logs
```

**Self-referential flags:**

If no annotation is provided, the flag uses its own name:

```bash
just ext add docker run IMAGE
> just docker run IMAGE[image] -d/--detach

# Usage:
just docker run nginx --detach
# Executes: docker run nginx --detach
```

---

## Type Reference

| Type | Description | Example |
|------|-------------|---------|
| `str` | String (default) | `"hello"` |
| `int` | Integer | `42` |
| `float` | Floating point | `3.14` |
| `bool` | Boolean flag | `true/false` |

---

## Extension Management

```bash
# List all extensions
just ext list

# Remove an extension
just ext remove <command>
just ext remove -y <command>  # Skip confirmation

# Edit an extension (opens in editor)
just ext edit <command>
```

---

## Generated Script Structure

When you create an extension, a Python script is generated:

```python
import subprocess
from typing_extensions import Annotated
import typer

from just import just_cli, create_typer_app

myext_cli = create_typer_app()
just_cli.add_typer(myext_cli)

@myext_cli.command(name="myext")
def main(
    msg: Annotated[str, typer.Argument(help='Message')]
):
    command = r"""echo MESSAGE""".strip()
    command = command.replace('MESSAGE', str(msg))
    subprocess.run(command, shell=True)
```

Extensions are stored in `~/.just/extensions/`.

---

## Best Practices

1. **Use descriptive variable names** - They appear in `--help`
2. **Add help text** - Use `#` to document parameters
3. **Set defaults for optional args** - Use `=value` syntax
4. **Use option aliases for complex flags** - Simplify long flag names
