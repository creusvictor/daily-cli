# daily

Minimalist CLI for engineers to log daily work. Perfect for daily standups.

[![PyPI version](https://badge.fury.io/py/daily-cli-tool.svg)](https://pypi.org/project/daily-cli-tool/)
[![Python versions](https://img.shields.io/pypi/pyversions/daily-cli-tool.svg)](https://pypi.org/project/daily-cli-tool/)

## Features

- **Fast capture**: Log work in under 10 seconds
- **Markdown-based**: Human-readable files, Git-friendly
- **Tag support**: Filter entries by project or topic
- **Cheat sheet**: Quick summary for daily standups
- **Interactive search**: Browse and edit past notes with fzf
- **No database**: Plain files in `~/.daily/dailies/`

## Installation

### Using pipx (recommended)

```bash
pipx install daily-cli-tool
```

That's it! The `daily` command is now available globally.

### From source (for development)

```bash
# Clone the repository
git clone https://github.com/creusvictor/daily-cli.git
cd daily-cli

# Install with pipx
pipx install .

# Or install with uv
uv sync
```

### Using uv (for development)

```bash
# Clone the repository
git clone https://github.com/user/daily-cli.git
cd daily-cli

# Install
uv sync

# Run
uv run daily --help
```

### Using pip

```bash
pip install daily-cli
```

### From source

```bash
git clone https://github.com/user/daily-cli.git
cd daily-cli
pip install -e .
```

## Quick Start

```bash
# Log completed work
daily did "Fixed CI/CD pipeline" --tags cicd,infra

# Plan today's work
daily plan "Review pending PRs" --tags code-review

# Log a blocker
daily block "Waiting for AWS access" --tags aws

# Log a meeting
daily meeting "Sprint planning" --tags team

# Show cheat sheet for standup
daily cheat
```

## Commands

| Command | Description | Section |
|---------|-------------|---------|
| `daily did "text"` | Log completed work | Done |
| `daily plan "text"` | Plan work for today | To Do |
| `daily block "text"` | Log a blocker | Blockers |
| `daily meeting "text"` | Log a meeting | Meetings |
| `daily cheat` | Show standup cheat sheet | - |
| `daily search` | Search and open daily files | - |

All commands support `--tags` or `-t` for tagging:

```bash
daily did "Deploy to production" --tags deploy,aws
daily did "Code review" -t review
```

## Cheat Sheet

The `daily cheat` command generates a clean summary for standups:

```
DONE
- Fixed CI/CD pipeline
- Deployed new feature

MEETINGS
- Sprint planning
- 1:1 with manager

TO DO
- Review pending PRs
- Write documentation

BLOCKERS
- Waiting for AWS access
```

### Options

```bash
# Filter by tags
daily cheat --tags aws

# Show today's file instead of yesterday's
daily cheat --today

# Plain text output (no colors)
daily cheat --plain
```

### Weekend Logic

By default, `daily cheat` skips weekends when looking for "yesterday's" file:

- On **Monday**, it shows **Friday's** entries
- On **Saturday** or **Sunday**, it shows **Friday's** entries

This matches typical standup workflows where you report on the last workday.

```bash
# Override: always skip weekends
daily cheat --workdays

# Override: use literal yesterday (even if weekend)
daily cheat --no-workdays
```

Configure the default in `~/.daily/config.toml`:

```toml
# Set to false to always use literal yesterday
skip_weekends = true
```

## Search

The `daily search` command provides an interactive fuzzy finder (fzf) to browse and edit your daily notes:

```bash
# Search all daily files
daily search

# Filter by tags (only show files with these tags)
daily search --tags aws,deploy
daily search -t projectA
```

**Features**:
- **Interactive selection**: Use arrow keys or fuzzy search to find notes
- **Preview panel**: See the content of each note before opening
- **Opens in $EDITOR**: Selected file opens in your preferred editor (vim, nano, etc.)
- **Tag filtering**: Only show files containing specific tags
- **Sorted by date**: Newest files appear first
- **Tag display**: Each file shows all tags used (e.g., `2026-02-20 (Friday) - tags: aws,deploy`)

**Requirements**: This command requires `fzf` to be installed:

```bash
# Ubuntu/Debian
sudo apt-get install fzf

# macOS
brew install fzf

# Arch Linux
sudo pacman -S fzf
```

## File Structure

Daily notes are stored in `~/.daily/dailies/` with format `YYYY-MM-DD-daily.md`:

```markdown
---
type: daily
date: 2026-01-27
---

## ✅ Done
- Fixed CI/CD pipeline #tags: cicd,infra

## ▶️ To Do
- Review pending PRs

## 🚧 Blockers
- Waiting for AWS access #tags: aws

## 🗓 Meetings
- Sprint planning #tags: team

## 🧠 Quick Notes
```

## Configuration

Create `~/.daily/config.toml` to customize behavior:

```toml
# Directory where daily notes are stored
dailies_dir = "~/.daily/dailies"

# Skip weekends in daily cheat (Monday shows Friday)
skip_weekends = true
```

### Custom directory

Set `DAILY_DIR` environment variable (takes priority over config file):

```bash
export DAILY_DIR=/path/to/my/dailies
```

Priority: Environment variable > Config file > Default (`~/.daily/dailies`)

## Development

```bash
# Install dev dependencies
uv sync

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=daily

# Format code
uv run black daily tests

# Lint
uv run ruff check daily tests

# Type check
uv run mypy daily
```

## FAQ

**Q: Where are my notes stored?**
A: In `~/.daily/dailies/` by default. Each day creates a new file like `2026-01-27-daily.md`.

**Q: Can I edit files manually?**
A: Yes! Files are plain Markdown. Manual edits are preserved.

**Q: Does it work with Obsidian?**
A: Yes! Point Obsidian to your dailies directory for a nice viewing experience.

**Q: Can I use it with Git?**
A: Absolutely. The files are designed to be Git-friendly.

**Q: What if I forget to log something?**
A: You can edit the Markdown file directly, or use the API with a specific date.

**Q: Why does `daily cheat` show Friday's entries on Monday?**
A: By default, weekends are skipped so Monday's standup shows Friday's work. Use `--no-workdays` to show literal yesterday, or set `skip_weekends = false` in config.

## License

MIT
