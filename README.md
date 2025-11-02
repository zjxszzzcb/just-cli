# 🛠️ JUST CLI

### The simple stuff should be simple.

Sick of Googling *"how to install X on XXX"* for the 47th time, only to end up copying and pasting similar commands from various official docs?

Tired of copy-pasting giant commands and tapping arrow keys forever just to change one little thing?

Just want an all-in-one toolkit for everyday simple tasks, instead of endlessly searching and testing Deep Research results one by one?

### Stop wasting life on terminal chores!

JUST CLI saves your terminal life from wasted seconds:

- Install something? `just install xxx`
- Edit files? `just edit xxx` (works just like a simple notepad)
- Expose service? `just tunnel xxx` (create a cloudflared tunnel)

Besides, with the powerful **Extension System**, you can instantly convert ANY complex shell command into a simple, reusable `just` command - and share it with others.

**That's it.** Now you can focus on what really matters - building great stuff.


## 📦 Installation

```shell
pip install git+https://github.com/zjxszzzcb/just-cli.git
```


## 🚀 Quick Start

After installation, you can use the `just` command:

```bash
just -h
```

### Core Commands

JUST CLI comes with several built-in core commands for common development tasks:

#### Installation Management
Install tools without remembering platform-specific package managers:

```bash
# Install Cloudflare tunnel client
just install cloudflare
```

Currently supported installations:
- `cloudflare` - Cloudflare tunnel client (cloudflared)
- `edit` - Microsoft Editor

#### File Editing
Edit any file with built-in TUI or system default editor:

```bash
# Edit any file
just edit <file_path>
```

#### File Viewing
View files with appropriate viewers:

```bash
# View any file (opens in editor)
just view <file_path>

# View markdown files with built-in viewer
just view README.md
```

#### Cloudflare Tunnel
Spin up a Cloudflare tunnel in seconds:

```bash
# Expose a local service via Cloudflare tunnel
just tunnel <url>
```

Example:
```bash
# Expose local server running on port 8080
just tunnel http://localhost:8080
```

## 🏗️ Project Structure

```
just-cli/
├── src/just/
│   ├── cli.py              # CLI entry point and core logic
│   ├── commands/           # Command modules directory
│   ├── config/             # Configuration management
│   ├── core/               # Core functionality
│   │   └── extension/      # Extension system core
│   ├── extensions/         # User-generated extension commands
│   ├── tui/                # TUI components
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

#### DNSLog Service Interaction
Transform complex curl commands into simple, reusable DNSLog commands for security testing:

##### 1. Generate a new DNSLog domain

```bash
just ext add curl 'https://dnslog.org/new_gen' \
  -H 'accept: */*' \
  -H 'accept-language: en-US,en;q=0.9,zh;q=0.8' \
  -H 'content-type: application/x-www-form-urlencoded' \
  -H 'origin: https://dnslog.org' \
  -H 'priority: u=1, i' \
  -H 'referer: https://dnslog.org/' \
  -H 'sec-ch-ua: "Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36' \
  --data-raw 'domain=log.dnslog.pp.ua.'
> just dnslog new --domain log.dnslog.pp.ua[domain:str=log.dnslog.pp.ua#DNSLog domain to generate]
```

Usage: `just dnslog new --domain mydomain.dnslog.org`


##### 2. Check DNSLog records

```bash
just ext add curl 'https://dnslog.org/rwvkku2gl89l' \
  -H 'accept: */*' \
  -H 'accept-language: en-US,en;q=0.9,zh;q=0.8' \
  -H 'content-type: application/x-www-form-urlencoded' \
  -H 'origin: https://dnslog.org' \
  -H 'priority: u=1, i' \
  -H 'referer: https://dnslog.org/' \
  -H 'sec-ch-ua: "Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36' \
  --data-raw 'domain=log.dnslog.pp.ua.'
> just dnslog check a9kkdqbwbnzp[identifier:str#subdomain prefix] --domain log.dnslog.pp.ua[domain:str=log.dnslog.pp.ua#DNSLog domain to check]
```

Usage: `just dnslog check abc123 --domain mydomain.dnslog.org`

This registers `check` as a subcommand of `dnslog`. The `check` command accepts a positional parameter `identifier` of type `str` (described as "subdomain prefix" in help text) and an option parameter `domain` of type `str` with a default value of `log.dnslog.pp.ua`.

This creates a powerful penetration testing toolkit that can quickly interact with DNSLog services to monitor DNS queries during security testing, eliminating the need to remember complex curl commands with numerous headers.

### How It Works

1. **Command Parsing**: The system parses your declaration to identify arguments, options, types, defaults, and help text
2. **Code Generation**: It generates a complete Typer command script with proper type annotations
3. **Directory Structure**: Automatically creates the necessary directory structure and `__init__.py` files
4. **Integration**: Seamlessly integrates the new command into the existing command hierarchy
5. **Execution**: When called, the command substitutes parameters and executes the original shell command

## Environment Configuration

Uses `.env` for configuration management:

- `JUST_EDIT_USE_TOOL`: Editor preference (`textual` or `edit`)

## 📝 License

MIT

## 👤 Author

**zzzcb**
- Email: zjxs.zzzcb@gmail.com

## 🤝 Contributing

Contributions are welcome! Whether it's a new command, bug fix, or platform support, PRs are appreciated.

**Principle**: Keep commands simple and cross-platform. If a command only works on one OS, handle it gracefully with clear error messages.

---
