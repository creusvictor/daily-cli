"""Tests for the CLI module."""

from datetime import datetime

import pytest
from typer.testing import CliRunner

from daily.cli import app
from daily.core import get_daily_file_path, read_daily_file

runner = CliRunner()


@pytest.fixture
def temp_dailies_dir(tmp_path, monkeypatch):
    """Fixture that configures a temporary directory for dailies."""
    dailies_dir = tmp_path / "dailies"
    dailies_dir.mkdir()
    monkeypatch.setenv("DAILY_DIR", str(dailies_dir))
    return dailies_dir


class TestDidCommand:
    """Tests for the did command."""

    def test_did_command_creates_file(self, temp_dailies_dir):
        """Creates file if it doesn't exist."""
        result = runner.invoke(app, ["did", "Completed task"])

        assert result.exit_code == 0
        assert "Added to Done" in result.output

        # Verify file was created
        file_path = get_daily_file_path()
        assert file_path.exists()

    def test_did_command_inserts_bullet(self, temp_dailies_dir):
        """Inserts bullet in Done section."""
        runner.invoke(app, ["did", "Deploy completed"])

        content = read_daily_file()
        assert "- Deploy completed" in content

        # Verify it's in the correct section
        lines = content.split("\n")
        done_idx = next(i for i, l in enumerate(lines) if "## ✅ Done" in l)
        todo_idx = next(i for i, l in enumerate(lines) if "## ▶️ To Do" in l)
        bullet_idx = next(i for i, l in enumerate(lines) if "- Deploy completed" in l)

        assert done_idx < bullet_idx < todo_idx

    def test_did_command_with_tags(self, temp_dailies_dir):
        """Formats tags correctly."""
        result = runner.invoke(app, ["did", "Fix pipeline", "--tags", "cicd,aws"])

        assert result.exit_code == 0
        assert "#tags: cicd,aws" in result.output

        content = read_daily_file()
        assert "- Fix pipeline #tags: cicd,aws" in content

    def test_did_command_with_short_tags_option(self, temp_dailies_dir):
        """Accepts short -t option for tags."""
        result = runner.invoke(app, ["did", "Task", "-t", "tag1"])

        assert result.exit_code == 0
        assert "#tags: tag1" in result.output


class TestPlanCommand:
    """Tests for the plan command."""

    def test_plan_command_inserts_bullet(self, temp_dailies_dir):
        """Inserts bullet in To Do section."""
        result = runner.invoke(app, ["plan", "Review PR"])

        assert result.exit_code == 0
        assert "Added to To Do" in result.output

        content = read_daily_file()
        assert "- Review PR" in content

        # Verify it's in the correct section
        lines = content.split("\n")
        todo_idx = next(i for i, l in enumerate(lines) if "## ▶️ To Do" in l)
        blockers_idx = next(i for i, l in enumerate(lines) if "## 🚧 Blockers" in l)
        bullet_idx = next(i for i, l in enumerate(lines) if "- Review PR" in l)

        assert todo_idx < bullet_idx < blockers_idx

    def test_plan_command_with_tags(self, temp_dailies_dir):
        """Formats tags correctly."""
        result = runner.invoke(app, ["plan", "Setup CI", "--tags", "infra"])

        assert result.exit_code == 0
        content = read_daily_file()
        assert "- Setup CI #tags: infra" in content


class TestBlockCommand:
    """Tests for the block command."""

    def test_block_command_inserts_bullet(self, temp_dailies_dir):
        """Inserts bullet in Blockers section."""
        result = runner.invoke(app, ["block", "Waiting for AWS permissions"])

        assert result.exit_code == 0
        assert "Added to Blockers" in result.output

        content = read_daily_file()
        assert "- Waiting for AWS permissions" in content

        # Verify it's in the correct section
        lines = content.split("\n")
        blockers_idx = next(i for i, l in enumerate(lines) if "## 🚧 Blockers" in l)
        meetings_idx = next(i for i, l in enumerate(lines) if "## 🗓 Meetings" in l)
        bullet_idx = next(
            i for i, l in enumerate(lines) if "- Waiting for AWS permissions" in l
        )

        assert blockers_idx < bullet_idx < meetings_idx

    def test_block_command_with_tags(self, temp_dailies_dir):
        """Formats tags correctly."""
        result = runner.invoke(app, ["block", "VPN down", "--tags", "infra,urgent"])

        assert result.exit_code == 0
        content = read_daily_file()
        assert "- VPN down #tags: infra,urgent" in content


class TestMeetingCommand:
    """Tests for the meeting command."""

    def test_meeting_command_inserts_bullet(self, temp_dailies_dir):
        """Inserts bullet in Meetings section."""
        result = runner.invoke(app, ["meeting", "Daily standup"])

        assert result.exit_code == 0
        assert "Added to Meetings" in result.output

        content = read_daily_file()
        assert "- Daily standup" in content

        # Verify it's in the correct section
        lines = content.split("\n")
        meetings_idx = next(i for i, l in enumerate(lines) if "## 🗓 Meetings" in l)
        notes_idx = next(i for i, l in enumerate(lines) if "## 🧠 Quick Notes" in l)
        bullet_idx = next(i for i, l in enumerate(lines) if "- Daily standup" in l)

        assert meetings_idx < bullet_idx < notes_idx

    def test_meeting_command_with_tags(self, temp_dailies_dir):
        """Formats tags correctly."""
        result = runner.invoke(app, ["meeting", "Sprint retro", "--tags", "team"])

        assert result.exit_code == 0
        content = read_daily_file()
        assert "- Sprint retro #tags: team" in content


class TestCommandValidation:
    """Tests for input validation."""

    def test_command_with_empty_text_fails(self, temp_dailies_dir):
        """Rejects empty text."""
        result = runner.invoke(app, ["did", "   "])

        assert result.exit_code != 0
        assert "cannot be empty" in result.output

    def test_command_with_whitespace_only_fails(self, temp_dailies_dir):
        """Rejects text with only whitespace."""
        result = runner.invoke(app, ["plan", "  \t  "])

        assert result.exit_code != 0

    def test_command_strips_whitespace(self, temp_dailies_dir):
        """Strips leading and trailing whitespace."""
        result = runner.invoke(app, ["did", "  Task with spaces  "])

        assert result.exit_code == 0

        content = read_daily_file()
        assert "- Task with spaces" in content
        # Should not have extra spaces
        assert "  Task with spaces  " not in content


class TestCommandHelp:
    """Tests for command help."""

    def test_main_help(self):
        """Shows main help."""
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "daily" in result.output.lower()
        assert "did" in result.output
        assert "plan" in result.output
        assert "block" in result.output
        assert "meeting" in result.output

    def test_did_help(self):
        """Shows help for did."""
        result = runner.invoke(app, ["did", "--help"])

        assert result.exit_code == 0
        assert (
            "completed" in result.output.lower() or "yesterday" in result.output.lower()
        )
        assert "--tags" in result.output

    def test_plan_help(self):
        """Shows help for plan."""
        result = runner.invoke(app, ["plan", "--help"])

        assert result.exit_code == 0
        assert "plan" in result.output.lower() or "today" in result.output.lower()

    def test_block_help(self):
        """Shows help for block."""
        result = runner.invoke(app, ["block", "--help"])

        assert result.exit_code == 0
        assert "blocker" in result.output.lower()

    def test_meeting_help(self):
        """Shows help for meeting."""
        result = runner.invoke(app, ["meeting", "--help"])

        assert result.exit_code == 0
        assert "meeting" in result.output.lower()


class TestMultipleInsertions:
    """Tests for multiple insertions."""

    def test_multiple_bullets_same_section(self, temp_dailies_dir):
        """Inserts multiple bullets in the same section."""
        runner.invoke(app, ["did", "Task 1"])
        runner.invoke(app, ["did", "Task 2"])
        runner.invoke(app, ["did", "Task 3"])

        content = read_daily_file()
        assert "- Task 1" in content
        assert "- Task 2" in content
        assert "- Task 3" in content

    def test_bullets_different_sections(self, temp_dailies_dir):
        """Inserts bullets in different sections."""
        runner.invoke(app, ["did", "Done yesterday"])
        runner.invoke(app, ["plan", "For today"])
        runner.invoke(app, ["block", "A blocker"])
        runner.invoke(app, ["meeting", "A meeting"])

        content = read_daily_file()
        assert "- Done yesterday" in content
        assert "- For today" in content
        assert "- A blocker" in content
        assert "- A meeting" in content


class TestCheatCommand:
    """Tests for the cheat command."""

    def test_cheat_reads_yesterday_by_default(self, temp_dailies_dir):
        """Cheat reads yesterday's file by default."""
        from datetime import datetime, timedelta
        from daily.core import insert_bullet

        yesterday = datetime.now() - timedelta(days=1)
        insert_bullet("did", "Yesterday's work", date=yesterday)
        insert_bullet("did", "Today's work")  # Today's file

        result = runner.invoke(app, ["cheat"])

        assert result.exit_code == 0
        assert "Yesterday's work" in result.output
        assert "Today's work" not in result.output

    def test_cheat_today_flag(self, temp_dailies_dir):
        """--today flag reads today's file."""
        from datetime import datetime, timedelta
        from daily.core import insert_bullet

        yesterday = datetime.now() - timedelta(days=1)
        insert_bullet("did", "Yesterday's work", date=yesterday)
        insert_bullet("did", "Today's work")  # Today's file

        result = runner.invoke(app, ["cheat", "--today"])

        assert result.exit_code == 0
        assert "Today's work" in result.output
        assert "Yesterday's work" not in result.output

    def test_cheat_command_with_tags(self, temp_dailies_dir):
        """Filters correctly by tags."""
        from datetime import datetime, timedelta
        from daily.core import insert_bullet

        yesterday = datetime.now() - timedelta(days=1)
        insert_bullet("did", "Task cicd", tags=["cicd"], date=yesterday)
        insert_bullet("did", "Task infra", tags=["infra"], date=yesterday)
        insert_bullet("plan", "Plan cicd", tags=["cicd"], date=yesterday)

        result = runner.invoke(app, ["cheat", "--tags", "cicd"])

        assert result.exit_code == 0
        assert "Task cicd" in result.output
        assert "Task infra" not in result.output
        assert "Plan cicd" in result.output

    def test_cheat_format_no_markdown(self, temp_dailies_dir):
        """Plain output has no Markdown headers."""
        from datetime import datetime, timedelta
        from daily.core import insert_bullet

        yesterday = datetime.now() - timedelta(days=1)
        insert_bullet("did", "Task", date=yesterday)

        result = runner.invoke(app, ["cheat", "--plain"])

        assert result.exit_code == 0
        assert "##" not in result.output
        assert "DONE" in result.output

    def test_cheat_empty_sections(self, temp_dailies_dir):
        """Handles empty sections."""
        from datetime import datetime, timedelta
        from daily.core import insert_bullet

        yesterday = datetime.now() - timedelta(days=1)
        insert_bullet("did", "Only this", date=yesterday)

        result = runner.invoke(app, ["cheat"])

        assert result.exit_code == 0
        assert "Only this" in result.output
        assert "no entries" in result.output

    def test_cheat_no_file_yesterday(self, temp_dailies_dir):
        """Handles non-existent yesterday file."""
        result = runner.invoke(app, ["cheat"])

        assert result.exit_code == 1
        assert "No entries from yesterday" in result.output

    def test_cheat_help(self):
        """Shows help for cheat."""
        result = runner.invoke(app, ["cheat", "--help"])

        assert result.exit_code == 0
        assert "standup" in result.output.lower()
        assert "--tags" in result.output
        assert "--today" in result.output
        assert "--workdays" in result.output


class TestCheatWeekendLogic:
    """Tests for the cheat command weekend logic."""

    def test_cheat_skips_weekends_by_default(self, temp_dailies_dir, monkeypatch):
        """On Monday, cheat shows Friday's file when skip_weekends=true."""
        from datetime import datetime
        from unittest.mock import patch
        from daily.core import insert_bullet

        # Create Friday's file
        friday = datetime(2026, 1, 30)  # Friday
        insert_bullet("did", "Friday work", date=friday)

        # Mock datetime.now() to be Monday
        monday = datetime(2026, 2, 2)

        # Ensure config returns True for skip_weekends
        monkeypatch.setattr(
            "daily.config.CONFIG_FILE", temp_dailies_dir / "nonexistent.toml"
        )

        with patch("daily.core.datetime") as mock_dt:
            mock_dt.now.return_value = monday
            # timedelta still needs to work
            from datetime import timedelta

            mock_dt.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

            result = runner.invoke(app, ["cheat"])

        assert result.exit_code == 0
        assert "Friday work" in result.output

    def test_cheat_no_workdays_shows_literal_yesterday(
        self, temp_dailies_dir, monkeypatch
    ):
        """--no-workdays shows literal yesterday even on Monday."""
        from datetime import datetime
        from unittest.mock import patch
        from daily.core import insert_bullet

        # Create Sunday's file (literal yesterday from Monday)
        sunday = datetime(2026, 2, 1)  # Sunday
        insert_bullet("did", "Sunday work", date=sunday)

        # Mock datetime.now() to be Monday
        monday = datetime(2026, 2, 2)

        with patch("daily.core.datetime") as mock_dt:
            mock_dt.now.return_value = monday
            mock_dt.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

            result = runner.invoke(app, ["cheat", "--no-workdays"])

        assert result.exit_code == 0
        assert "Sunday work" in result.output

    def test_cheat_workdays_flag_overrides_config(self, temp_dailies_dir, monkeypatch):
        """--workdays flag overrides config setting."""
        from datetime import datetime
        from unittest.mock import patch
        from daily.core import insert_bullet

        # Create Friday's file
        friday = datetime(2026, 1, 30)  # Friday
        insert_bullet("did", "Friday work", date=friday)

        # Create Sunday's file
        sunday = datetime(2026, 2, 1)  # Sunday
        insert_bullet("did", "Sunday work", date=sunday)

        # Mock datetime.now() to be Monday
        monday = datetime(2026, 2, 2)

        # Set config to skip_weekends=false
        config_file = temp_dailies_dir / "config.toml"
        config_file.write_text("skip_weekends = false")
        monkeypatch.setattr("daily.config.CONFIG_FILE", config_file)

        with patch("daily.core.datetime") as mock_dt:
            mock_dt.now.return_value = monday
            mock_dt.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

            # But use --workdays flag to override
            result = runner.invoke(app, ["cheat", "--workdays"])

        assert result.exit_code == 0
        assert "Friday work" in result.output
        assert "Sunday work" not in result.output

    def test_cheat_respects_config_skip_weekends_false(
        self, temp_dailies_dir, monkeypatch
    ):
        """Respects config skip_weekends=false."""
        from datetime import datetime
        from unittest.mock import patch
        from daily.core import insert_bullet

        # Create Sunday's file
        sunday = datetime(2026, 2, 1)  # Sunday
        insert_bullet("did", "Sunday work", date=sunday)

        # Mock datetime.now() to be Monday
        monday = datetime(2026, 2, 2)

        # Set config to skip_weekends=false
        config_file = temp_dailies_dir / "config.toml"
        config_file.write_text("skip_weekends = false")
        monkeypatch.setattr("daily.config.CONFIG_FILE", config_file)

        with patch("daily.core.datetime") as mock_dt:
            mock_dt.now.return_value = monday
            mock_dt.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

            result = runner.invoke(app, ["cheat"])

        assert result.exit_code == 0
        assert "Sunday work" in result.output
