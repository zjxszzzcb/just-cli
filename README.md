# 🛠️ JUST CLI

## The simple stuff should be simple.

Sick of Googling *"how to install X on XXX"* for the 47th time, only to end up copying and pasting similar commands from various official docs?

Tired of copy-pasting giant commands and tapping arrow keys forever just to change one little thing?

Just want an all-in-one toolkit for everyday simple tasks, instead of endlessly searching and testing Deep Research results one by one?

## 📦 Installation

```shell
pip install just-cli
```

## 🚀 The Good Stuff

### 1. The Toolkit

#### Download Files
```bash
# Download with resume support and custom headers
just download https://example.com/file.zip
just download https://example.com/file.zip -H "Authorization: Bearer token" -o myfile.zip
```

#### Extract Archives
```bash
# Automatic format detection - ZIP, TAR, GZ, BZ2, XZ, ZSTD, 7Z
just extract archive.tar.gz
just extract data.7z -o out/
```

#### Edit Files
```bash
# Beautiful TUI editor
just edit README.md
```

#### View Files
```bash
# Preview markdown with syntax highlighting
just view README.md
```

#### Linux Commands (for Windows users)
```bash
just ls
just cat
just mkdir
just cp
just mv
just rm
```

### 2. The Extension System

This is where the magic happens. You can turn *any* complex shell command into a beautiful, typed `just` command.

Imagine you have a command you use all the time, like checking a Docker container's IP:
```bash
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' f523e75ca4ef
```
*Gross.*

Now, wave your wand:
```bash
just ext add docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' f523e75ca4ef
> just docker ip f523e75ca4ef[container_id:str#The container ID]
```

Now you have a new command:
```bash
just docker ip my-container
```

It even generates help messages!
```bash
just docker ip --help
```

## 🤝 Contributing

Found a bug? Want to add a new installer?
Fork it, fix it, ship it. We love PRs.
Just keep it cool, keep it simple, and don't break the "just works" vibe.

## 📄 License

MIT. Go wild.

