"""Markdown file manipulation for daily."""

import re
from datetime import datetime

from daily.config import SECTIONS, TAG_FORMAT


def create_daily_template(date: datetime) -> str:
    """Generate daily file template.

    Args:
        date: Date for the daily note.

    Returns:
        String with the complete Markdown template.
    """
    date_str = date.strftime("%Y-%m-%d")
    return f"""---
type: daily
date: {date_str}
---

## ✅ Done

## ▶️ To Do

## 🚧 Blockers

## 🗓 Meetings

## 🧠 Quick Notes
"""


def find_section(content: str, section_title: str) -> int:
    """Find the line index where a section begins.

    Args:
        content: Markdown file content.
        section_title: Section title to find (e.g., "## ✅ Yesterday").

    Returns:
        Line index where the section is, or -1 if not found.
    """
    lines = content.split("\n")

    # First try exact match
    for i, line in enumerate(lines):
        if line.strip() == section_title:
            return i

    # If no exact match, try fuzzy matching with emoji and first keyword
    # Extract emoji and first keyword from section_title
    # E.g., "## 🧠 Quick Notes" -> look for lines starting with "## 🧠 Quick"
    if section_title.startswith("## ") and len(section_title) > 3:
        # Get everything up to the first space after the emoji
        parts = section_title.split()
        if len(parts) >= 3:  # ["##", "emoji", "first_word", ...]
            fuzzy_pattern = f"{parts[0]} {parts[1]} {parts[2]}"
            for i, line in enumerate(lines):
                if line.strip().startswith(fuzzy_pattern):
                    return i

    return -1


def find_next_section(content: str, after_line: int) -> int:
    """Find the index of the next section after a given line.

    Args:
        content: Markdown file content.
        after_line: Line index to start searching from.

    Returns:
        Index of the next section, or total lines if none found.
    """
    lines = content.split("\n")

    for i in range(after_line + 1, len(lines)):
        # Match any line starting with ## (h2 header) to be more tolerant to typos
        if lines[i].strip().startswith("##"):
            return i

    return len(lines)


def insert_at_section(content: str, section_title: str, bullet: str) -> str:
    """Insert a bullet in a specific section.

    The bullet is inserted at the end of the section, just before the next
    section or at the end of the file.

    Args:
        content: Markdown file content.
        section_title: Section title where to insert.
        bullet: Bullet text to insert (without the "- " prefix).

    Returns:
        New content with the bullet inserted.

    Raises:
        ValueError: If the section doesn't exist in the content.
    """
    section_line = find_section(content, section_title)
    if section_line == -1:
        raise ValueError(f"Section '{section_title}' not found")

    lines = content.split("\n")
    next_section = find_next_section(content, section_line)

    # Find insertion position (last non-empty line of the section)
    insert_pos = section_line + 1

    # Find the last line with content before the next section
    for i in range(next_section - 1, section_line, -1):
        if lines[i].strip():
            insert_pos = i + 1
            break

    # Insert the bullet
    bullet_line = f"- {bullet}"
    lines.insert(insert_pos, bullet_line)

    return "\n".join(lines)


def parse_tags(bullet: str) -> list[str]:
    """Extract tags from a bullet.

    Tags have the format "#tags: tag1,tag2,tag3" at the end of the bullet.

    Args:
        bullet: Bullet text.

    Returns:
        List of tags found, or empty list if none.
    """
    match = re.search(r"#tags:\s*(.+)$", bullet)
    if not match:
        return []

    tags_str = match.group(1)
    return [tag.strip() for tag in tags_str.split(",") if tag.strip()]


def format_bullet_with_tags(text: str, tags: list[str] | None = None) -> str:
    """Format text with optional tags.

    Args:
        text: Bullet text.
        tags: List of tags to add (optional).

    Returns:
        Text formatted with tags if provided.
    """
    if not tags:
        return text

    tags_str = ",".join(tags)
    return f"{text} {TAG_FORMAT.format(tags=tags_str)}"


def extract_bullets_from_section(content: str, section_title: str) -> list[str]:
    """Extract all bullets from a section.

    Args:
        content: Markdown file content.
        section_title: Section title.

    Returns:
        List of bullets (without the "- " prefix).
    """
    section_line = find_section(content, section_title)
    if section_line == -1:
        return []

    lines = content.split("\n")
    next_section = find_next_section(content, section_line)

    bullets = []
    for i in range(section_line + 1, next_section):
        line = lines[i].strip()
        if line.startswith("- "):
            bullets.append(line[2:])  # Remove "- " prefix

    return bullets


def filter_bullets_by_tags(bullets: list[str], tags: list[str]) -> list[str]:
    """Filter bullets that contain at least one of the specified tags.

    Args:
        bullets: List of bullets.
        tags: List of tags to search for.

    Returns:
        List of bullets that contain at least one tag.
    """
    if not tags:
        return bullets

    filtered = []
    tags_set = set(tag.lower() for tag in tags)

    for bullet in bullets:
        bullet_tags = set(tag.lower() for tag in parse_tags(bullet))
        if bullet_tags & tags_set:  # Non-empty intersection
            filtered.append(bullet)

    return filtered
