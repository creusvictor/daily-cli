# 🎉 daily-cli-tool v1.0.0 - Initial Release

Minimalist CLI for engineers to log daily work and prepare for standups.

## ✨ Features

### Core Commands
- **`daily did "text"`** - Log completed work
- **`daily plan "text"`** - Plan work for today
- **`daily block "text"`** - Log blockers
- **`daily meeting "text"`** - Log meetings
- **`daily cheat`** - Generate standup cheat sheet

### Advanced Features
- **`daily search`** - Interactive search with fzf and preview
  - Browse all daily notes with fuzzy finder
  - Preview file content before opening
  - Filter by tags: `daily search -t aws,deploy`
  - Opens in `$EDITOR`

### Tag Support
- Add tags to any entry: `--tags tag1,tag2` or `-t tag1,tag2`
- Filter by tags in cheat and search
- Case-insensitive tag matching

### Weekend Logic
- `daily cheat` skips weekends by default
- On Monday, shows Friday's entries
- Configurable with `--workdays/--no-workdays`

### Storage
- Plain Markdown files in `~/.daily/dailies/`
- Git-friendly format
- Compatible with Obsidian and other Markdown editors
- Human-readable, no lock-in

## 📦 Installation

```bash
pipx install daily-cli-tool
```

## 🚀 Quick Start

```bash
# Log your work
daily did "Fixed CI/CD pipeline" --tags devops,cicd
daily plan "Review pending PRs" --tags code-review
daily block "Waiting for AWS access" --tags aws

# Prepare for standup
daily cheat

# Search past notes
daily search
daily search -t projectA
```

## 📋 Requirements

- Python 3.11+
- `fzf` (for `daily search` command)

## 🔗 Links

- **Repository**: https://github.com/creusvictor/daily-cli
- **Documentation**: https://github.com/creusvictor/daily-cli#readme
- **Issues**: https://github.com/creusvictor/daily-cli/issues

## 🙏 Feedback Welcome

This is the initial release! Please report any issues or suggest features on GitHub.
