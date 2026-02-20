"""daily CLI - Command line interface."""

import os
import subprocess
import sys
import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from daily.core import (
    format_daily_file_for_display,
    generate_cheat_data,
    insert_bullet,
    list_daily_files,
)

console = Console()

app = typer.Typer(
    name="daily",
    help="CLI for daily work logging.",
    no_args_is_help=True,
)


def parse_tags(tags: str | None) -> list[str] | None:
    """Parse comma-separated tags string.

    Args:
        tags: Comma-separated tags string, or None.

    Returns:
        List of tags, or None if no tags.
    """
    if not tags:
        return None
    return [tag.strip() for tag in tags.split(",") if tag.strip()]


def validate_text(text: str) -> str:
    """Validate that text is not empty.

    Args:
        text: Text to validate.

    Returns:
        Validated text (stripped).

    Raises:
        typer.BadParameter: If text is empty.
    """
    text = text.strip()
    if not text:
        raise typer.BadParameter("Text cannot be empty")
    return text


@app.command()
def did(
    text: str = typer.Argument(..., help="Completed work description"),
    tags: str = typer.Option(None, "--tags", "-t", help="Comma-separated tags"),
) -> None:
    """Log completed work (Yesterday section)."""
    text = validate_text(text)
    tag_list = parse_tags(tags)

    insert_bullet("did", text, tags=tag_list)

    if tag_list:
        typer.echo(f"✓ Added to Done: {text} #tags: {','.join(tag_list)}")
    else:
        typer.echo(f"✓ Added to Done: {text}")


@app.command()
def plan(
    text: str = typer.Argument(..., help="Planned work description"),
    tags: str = typer.Option(None, "--tags", "-t", help="Comma-separated tags"),
) -> None:
    """Plan work (Today section)."""
    text = validate_text(text)
    tag_list = parse_tags(tags)

    insert_bullet("plan", text, tags=tag_list)

    if tag_list:
        typer.echo(f"✓ Added to To Do: {text} #tags: {','.join(tag_list)}")
    else:
        typer.echo(f"✓ Added to To Do: {text}")


@app.command()
def block(
    text: str = typer.Argument(..., help="Blocker description"),
    tags: str = typer.Option(None, "--tags", "-t", help="Comma-separated tags"),
) -> None:
    """Log blocker (Blockers section)."""
    text = validate_text(text)
    tag_list = parse_tags(tags)

    insert_bullet("block", text, tags=tag_list)

    if tag_list:
        typer.echo(f"✓ Added to Blockers: {text} #tags: {','.join(tag_list)}")
    else:
        typer.echo(f"✓ Added to Blockers: {text}")


@app.command()
def meeting(
    text: str = typer.Argument(..., help="Meeting description"),
    tags: str = typer.Option(None, "--tags", "-t", help="Comma-separated tags"),
) -> None:
    """Log meeting (Meetings section)."""
    text = validate_text(text)
    tag_list = parse_tags(tags)

    insert_bullet("meeting", text, tags=tag_list)

    if tag_list:
        typer.echo(f"✓ Added to Meetings: {text} #tags: {','.join(tag_list)}")
    else:
        typer.echo(f"✓ Added to Meetings: {text}")


@app.command()
def cheat(
    tags: str = typer.Option(None, "--tags", "-t", help="Filter by tags"),
    plain: bool = typer.Option(
        False, "--plain", "-p", help="Plain text output (no colors)"
    ),
    today: bool = typer.Option(
        False, "--today", help="Show today's file instead of yesterday's"
    ),
    workdays: bool | None = typer.Option(
        None,
        "--workdays/--no-workdays",
        help="Skip weekends when looking for yesterday's file (default: from config)",
    ),
) -> None:
    """Show cheat sheet for daily standup (reads yesterday's entries by default)."""
    from daily.config import get_skip_weekends
    from daily.core import get_previous_workday

    tag_list = parse_tags(tags)

    # Determine skip_weekends behavior
    skip_weekends = workdays if workdays is not None else get_skip_weekends()

    # By default, read yesterday's file (what you logged yesterday for today's standup)
    if today:
        target_date = None  # Today
    else:
        target_date = get_previous_workday(skip_weekends=skip_weekends)

    try:
        data = generate_cheat_data(filter_tags=tag_list, date=target_date)

        if plain:
            _print_cheat_plain(data)
        else:
            _print_cheat_rich(data, target_date)
    except FileNotFoundError:
        if today:
            console.print(
                "[red]No entries for today.[/red] Use 'daily did' to get started."
            )
        else:
            console.print(
                "[red]No entries from yesterday.[/red] Use 'daily cheat --today' to see today's file."
            )
        raise typer.Exit(1)


def _format_bullet_with_tags(bullet: str) -> str:
    """Format bullet with styled tags for rich output."""
    import re

    match = re.search(r"#tags:\s*(.+)$", bullet)
    if not match:
        return bullet

    text = bullet[: match.start()].strip()
    tags = [t.strip() for t in match.group(1).split(",")]
    styled_tags = " ".join(f"[cyan]#{t}[/cyan]" for t in tags)
    return f"{text}  {styled_tags}"


def _print_cheat_plain(data: list[dict]) -> None:
    """Print cheat sheet in plain text."""
    for section in data:
        typer.echo(section["title"])
        if section["bullets"]:
            for bullet in section["bullets"]:
                typer.echo(f"- {bullet}")
        else:
            typer.echo("(no entries)")
        typer.echo()


def _print_cheat_rich(data: list[dict], date=None) -> None:
    """Print cheat sheet with rich formatting."""
    from datetime import datetime

    # Section styles
    styles = {
        "did": ("bold green", "✅"),
        "meeting": ("bold blue", "🗓"),
        "plan": ("bold yellow", "▶️"),
        "block": ("bold red", "🚧"),
    }

    # Show which date we're reading
    if date is None:
        date = datetime.now()
    date_str = date.strftime("%A, %B %d")
    console.print(f"\n[dim]── {date_str} ──[/dim]")

    for section in data:
        style, icon = styles.get(section["key"], ("bold", "•"))

        # Section header
        console.print(f"{icon} [bold]{section['title']}[/bold]", style=style)

        if section["bullets"]:
            for bullet in section["bullets"]:
                formatted = _format_bullet_with_tags(bullet)
                console.print(f"   • {formatted}")
        else:
            console.print("   [dim](no entries)[/dim]")

        console.print()


@app.command()
def search(
    tags: str = typer.Option(None, "--tags", "-t", help="Filter by tags"),
) -> None:
    """Search and open daily files interactively with fzf."""
    tag_list = parse_tags(tags)

    try:
        daily_files = list_daily_files(filter_tags=tag_list)
    except Exception as e:
        console.print(f"[red]Error listing daily files: {e}[/red]")
        raise typer.Exit(1)

    if not daily_files:
        if tag_list:
            console.print(
                f"[yellow]No daily files found with tags: {', '.join(tag_list)}[/yellow]"
            )
        else:
            console.print("[yellow]No daily files found.[/yellow]")
        raise typer.Exit(0)

    # Prepare items for fzf (display string -> file path mapping)
    display_items = []
    file_mapping = {}

    for file_path, file_date in daily_files:
        display = format_daily_file_for_display(file_path, file_date)
        display_items.append(display)
        file_mapping[display] = file_path

    # Use fzf for interactive selection
    try:
        from iterfzf import iterfzf

        # fzf will replace {} with the selected item, but we need the file path
        # We'll use a workaround: pass --preview option directly with file path extraction
        # Since display format is "YYYY-MM-DD (...) - X entries", we extract the date
        # and construct the file path

        dailies_dir = str(daily_files[0][0].parent)  # Get dailies directory

        # Preview command: extract date from line and cat the corresponding file
        # Format: "2026-01-26 (Monday) - 3 entries" -> extract "2026-01-26"
        preview_cmd = f"cat {dailies_dir}/{{1}}-daily.md 2>/dev/null || echo 'Preview not available'"

        selected = iterfzf(
            display_items,
            multi=False,
            preview=preview_cmd,
            __extra__=["--preview-window=right:50%:wrap"],
            prompt="Select daily file > ",
            query="" if not tag_list else " ".join(tag_list),
            ansi=True,
        )

        if not selected:
            # User cancelled (pressed ESC)
            raise typer.Exit(0)

        # Get the file path from selection
        selected_file = file_mapping[selected]

        # Open in $EDITOR
        editor = os.environ.get("EDITOR", "vim")

        try:
            subprocess.run([editor, str(selected_file)], check=True)
        except subprocess.CalledProcessError:
            console.print(f"[red]Failed to open {selected_file} with {editor}[/red]")
            raise typer.Exit(1)
        except FileNotFoundError:
            console.print(
                f"[red]Editor '{editor}' not found. Set $EDITOR environment variable.[/red]"
            )
            raise typer.Exit(1)

    except ImportError:
        console.print(
            "[red]fzf integration requires 'iterfzf' package and 'fzf' binary.[/red]"
        )
        console.print(
            "Install with: pip install iterfzf && brew install fzf  (or apt-get install fzf)"
        )
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error during search: {e}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
