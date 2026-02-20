"""Tests for search functionality."""

import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from daily.core import (
    format_daily_file_for_display,
    insert_bullet,
    list_daily_files,
)
from daily.markdown import create_daily_template


@pytest.fixture
def temp_dailies_dir(monkeypatch):
    """Create temporary dailies directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        dailies_path = Path(tmpdir) / "dailies"
        dailies_path.mkdir()

        # Patch get_dailies_dir to return our temp directory
        monkeypatch.setattr("daily.core.get_dailies_dir", lambda: dailies_path)
        monkeypatch.setattr("daily.config.get_dailies_dir", lambda: dailies_path)

        yield dailies_path


def test_list_daily_files_empty(temp_dailies_dir):
    """Test listing when no files exist."""
    result = list_daily_files()
    assert result == []


def test_list_daily_files_single(temp_dailies_dir):
    """Test listing with a single file."""
    date = datetime(2026, 1, 27)
    insert_bullet("did", "Test entry", date=date)

    result = list_daily_files()
    assert len(result) == 1
    assert result[0][1] == date


def test_list_daily_files_multiple_sorted(temp_dailies_dir):
    """Test that files are sorted by date (newest first)."""
    date1 = datetime(2026, 1, 25)
    date2 = datetime(2026, 1, 27)
    date3 = datetime(2026, 1, 26)

    insert_bullet("did", "Entry 1", date=date1)
    insert_bullet("did", "Entry 2", date=date2)
    insert_bullet("did", "Entry 3", date=date3)

    result = list_daily_files()
    assert len(result) == 3
    # Should be sorted newest first
    assert result[0][1] == date2
    assert result[1][1] == date3
    assert result[2][1] == date1


def test_list_daily_files_with_tag_filter(temp_dailies_dir):
    """Test filtering files by tags."""
    date1 = datetime(2026, 1, 25)
    date2 = datetime(2026, 1, 26)
    date3 = datetime(2026, 1, 27)

    insert_bullet("did", "Work on projectA", tags=["projectA"], date=date1)
    insert_bullet("did", "Fix bug", tags=["bugfix", "projectB"], date=date2)
    insert_bullet("did", "Review code", date=date3)

    # Filter by projectA - should return only date1
    result = list_daily_files(filter_tags=["projectA"])
    assert len(result) == 1
    assert result[0][1] == date1

    # Filter by projectB - should return only date2
    result = list_daily_files(filter_tags=["projectB"])
    assert len(result) == 1
    assert result[0][1] == date2

    # Filter by multiple tags - should return files with ANY of the tags
    result = list_daily_files(filter_tags=["projectA", "bugfix"])
    assert len(result) == 2


def test_list_daily_files_tag_case_insensitive(temp_dailies_dir):
    """Test that tag filtering is case insensitive."""
    date = datetime(2026, 1, 27)
    insert_bullet("did", "Test entry", tags=["ProjectA"], date=date)

    result = list_daily_files(filter_tags=["projecta"])
    assert len(result) == 1


def test_format_daily_file_for_display(temp_dailies_dir):
    """Test formatting file for display."""
    date = datetime(2026, 1, 27)  # Tuesday
    insert_bullet("did", "Entry 1", date=date)
    insert_bullet("plan", "Entry 2", date=date)

    result = list_daily_files()
    file_path, file_date = result[0]

    display = format_daily_file_for_display(file_path, file_date)

    # Should contain date and day name (no tags in this case)
    assert "2026-01-27" in display
    assert "Tuesday" in display
    assert "tags:" not in display  # No tags were added
    assert "entries" not in display  # Entry count removed


def test_format_daily_file_for_display_single_entry(temp_dailies_dir):
    """Test formatting with single entry (no entry count shown)."""
    date = datetime(2026, 1, 27)
    insert_bullet("did", "Single entry", date=date)

    result = list_daily_files()
    file_path, file_date = result[0]

    display = format_daily_file_for_display(file_path, file_date)

    assert "2026-01-27" in display
    assert "Tuesday" in display
    assert "entry" not in display  # No entry count
    assert "entries" not in display  # No entry count


def test_format_daily_file_for_display_no_entries(temp_dailies_dir):
    """Test formatting when file has no bullets."""
    date = datetime(2026, 1, 27)
    file_path = temp_dailies_dir / "2026-01-27-daily.md"
    file_path.write_text(create_daily_template(date))

    display = format_daily_file_for_display(file_path, date)

    assert "2026-01-27" in display
    assert "Tuesday" in display
    assert "entries" not in display  # No entry count
    assert "tags:" not in display  # No tags when no entries


def test_format_daily_file_for_display_with_tags(temp_dailies_dir):
    """Test formatting includes tags when present."""
    date = datetime(2026, 1, 27)
    insert_bullet("did", "Deploy project", tags=["aws", "deploy"], date=date)
    insert_bullet("plan", "Review code", tags=["review"], date=date)

    result = list_daily_files()
    file_path, file_date = result[0]

    display = format_daily_file_for_display(file_path, file_date)

    # Should contain date, day name, and tags (no entry count)
    assert "2026-01-27" in display
    assert "Tuesday" in display
    assert "entries" not in display  # No entry count
    assert "tags:" in display
    assert "aws" in display
    assert "deploy" in display
    assert "review" in display
