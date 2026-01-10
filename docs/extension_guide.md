# Just Extension System Guide

The `just` extension system allows you to create custom CLI commands by wrapping existing shell commands with a clean, typed interface.

## Quick Start

```bash
# Create an extension that wraps 'echo' with a message parameter
just ext add echo MESSAGE
> just echo MESSAGE[msg]

# Use the extension
just echo "Hello World"
```

---

## Core Concepts

Extensions work by **template replacement** - you define placeholders in your original shell command that get replaced with user input at runtime.

**Flow:**
1. `just ext add <name> <PLACEHOLDERS>` - starts the creation process
2. Enter the extension syntax with annotations
3. A Python script is generated that wraps the original command
4. Run `just <name> [args]` to execute the wrapped command

---

## The 5 Syntax Patterns

### Pattern 1: Command Alias

Create a simple alias for a command without parameters.

```bash
# Create
just ext add greet
> just greet

# Enter the command template (no placeholders)
echo "Hello World"

# Use
just greet  # Outputs: Hello World
```

This pattern wraps a static command with no variable parts.

---

### Pattern 2: Positional Argument (Replace Placeholder)

```
PLACEHOLDER[var:type=default#help]
```

The placeholder in the original command is replaced with the user's input.

| Component | Required | Description | Example |
|-----------|----------|-------------|---------|
| `PLACEHOLDER` | Yes | Text to replace in command | `MESSAGE` |
| `var` | Yes | Python variable name | `msg` |
| `type` | No | Type hint (str, int, float, bool) | `str` |
| `default` | No | Default value (makes arg optional) | `"Hello"` |
| `help` | No | Help text shown in --help | `Message to display` |

**Examples:**

```bash
# Basic argument
just ext add echo MESSAGE
> just echo MESSAGE[msg]

# With type
> just echo MESSAGE[msg:str]

# With default (makes it optional)
> just echo MESSAGE[msg:str=Hello]

# With quoted default (for spaces)
> just echo MESSAGE[msg:str="Hello World"]

# With help text
> just echo MESSAGE[msg:str#Message to display]

# Full syntax
> just echo MESSAGE[msg:str="Hello World"#Message to display]
```

**Generated behavior:**
```python
command = "echo MESSAGE"
command = command.replace("MESSAGE", str(msg))
```

---

### Pattern 3: Option with Placeholder Replacement

```
--flag PLACEHOLDER[var:type=default#help]
-s/--short-long PLACEHOLDER[var:type=default#help]
```

A named option where the placeholder value is replaced in the command.

**Examples:**

```bash
# Named option with placeholder
just ext add echo MESSAGE TEXT
> just echo -m/--messages MESSAGE[msg] TEXT[text=Hi]

# Usage:
just echo -m "Hello"        # Outputs: Hello Hi
just echo -m "Hello" "Hey"  # Outputs: Hello Hey
```

**Key points:**
- The flag `-m/--messages` becomes the CLI option name
- `MESSAGE` is the placeholder that gets replaced
- User provides value via `-m <value>` or `--messages <value>`

---

### Pattern 4: Varargs (Capture All Unknown Arguments)

```
PLACEHOLDER[...]
PLACEHOLDER[...#help]
```

Captures **all unknown arguments**, including unknown options like `-m` or `--foo`.

**Examples:**

```bash
# Basic varargs
just ext add passthrough ARGS
> just passthrough ARGS[...]

# Usage - all unknown args are captured:
just passthrough hello world          # → echo hello world
just passthrough -m hello --verbose   # → echo -m hello --verbose
just passthrough a b c -x -y          # → echo a b c -x -y
```

**With help text:**
```bash
> just passthrough ARGS[...#Files to process]
```

**Key points:**
- Similar to `argparse.parse_known_args()` behavior
- All extra arguments are captured into `ctx.args`
- Very useful for wrapper commands that need to pass through arbitrary flags

---

### Pattern 5: Option Alias (Append Original Flag)

```
--original-flag[-u/--user-facing:type=default#help]
```

The user sees and uses `-u/--user-facing`, but the **original flag** `--original-flag` is appended to the command.

**Examples:**

```bash
# Create alias: user uses -m/--msg, command gets --text
just ext add echo
> just echo --text[-m/--msg:str#Text to display]

# Usage:
just echo -m "Hello"        # Executes: echo --text Hello
just echo --msg "World"     # Executes: echo --text World
```

**Key points:**
- The original flag (`--text`) goes in front of the brackets
- User-facing flags (`-m/--msg`) go inside the brackets
- When user provides `-m value`, the command gets `--text value` appended

**Another example:**
```bash
# Simplify rsync's verbose output option
just ext add backup SRC DEST
> just backup SRC[src] DEST[dest] --verbose[-v:bool]

# Usage:
just backup /local /remote -v  # → rsync /local /remote --verbose
```

---

## Type Reference

| Type | Description | Default Conversion | Example Values |
|------|-------------|-------------------|----------------|
| `str` | String (default) | As-is | `"hello"`, `path/to/file` |
| `int` | Integer | `int()` | `42`, `-1` |
| `float` | Floating point | `float()` | `3.14`, `-0.5` |
| `bool` | Boolean flag | `true/false/yes/no` | `true`, `false` |

---

## Parameter Ordering

Python requires that parameters with default values come **after** parameters without defaults. The extension system automatically reorders parameters to satisfy this requirement.

For example, if you define:
```
TEXT[text=Hello] MESSAGE[msg]
```

The generated function will have `msg` first (no default), then `text` (has default):
```python
def main(msg: str, text: str = "Hello"):
```

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

## Extension Storage

Extensions are stored as Python scripts in `~/.just/extensions/`.

**Structure:**
```
~/.just/extensions/
├── mycommand.py           # Top-level extension
├── docker/
│   ├── __init__.py        # Subcommand group
│   ├── build.py           # docker build extension
│   └── ip.py              # docker ip extension
```

---

## Generated Script Example

When you create an extension like:
```bash
just ext add greet NAME
> just greet NAME[name:str="World"#Your name]
```

This generates:
```python
import subprocess
from typing_extensions import Annotated
import typer

from just import just_cli, create_typer_app


greet_cli = create_typer_app()
just_cli.add_typer(greet_cli)


@greet_cli.command(name="greet")
def main(
    name: Annotated[str, typer.Argument(
        help='Your name',
        show_default=False
    )] = 'World'
):
    command = r"""
    echo Hello NAME
    """.strip()
    command = command.replace('NAME', str(name))

    subprocess.run(command, shell=True)
```

---

## Best Practices

1. **Use descriptive variable names** - They appear in `--help` output
2. **Add help text** - Use `#` to document parameters clearly
3. **Set defaults for optional args** - Use `=value` syntax
4. **Use option aliases for complex flags** - Simplify long flag names for users
5. **Use varargs for passthrough commands** - When you need to forward arbitrary arguments
