"""daily CLI - Command line interface."""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from daily.core import generate_cheat_data, insert_bullet

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
    plain: bool = typer.Option(False, "--plain", "-p", help="Plain text output (no colors)"),
    today: bool = typer.Option(False, "--today", help="Show today's file instead of yesterday's"),
) -> None:
    """Show cheat sheet for daily standup (reads yesterday's entries by default)."""
    from datetime import datetime, timedelta

    tag_list = parse_tags(tags)

    # By default, read yesterday's file (what you logged yesterday for today's standup)
    if today:
        target_date = None  # Today
    else:
        target_date = datetime.now() - timedelta(days=1)  # Yesterday

    try:
        data = generate_cheat_data(filter_tags=tag_list, date=target_date)

        if plain:
            _print_cheat_plain(data)
        else:
            _print_cheat_rich(data, target_date)
    except FileNotFoundError:
        if today:
            console.print("[red]No entries for today.[/red] Use 'daily did' to get started.")
        else:
            console.print("[red]No entries from yesterday.[/red] Use 'daily cheat --today' to see today's file.")
        raise typer.Exit(1)


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
                console.print(f"   • {bullet}")
        else:
            console.print("   [dim](no entries)[/dim]")

        console.print()


if __name__ == "__main__":
    app()
