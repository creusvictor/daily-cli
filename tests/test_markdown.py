"""Tests for the markdown module."""

from datetime import datetime

import pytest

from daily.markdown import (
    create_daily_template,
    extract_bullets_from_section,
    filter_bullets_by_tags,
    find_section,
    format_bullet_with_tags,
    insert_at_section,
    parse_tags,
)


class TestCreateDailyTemplate:
    """Tests for create_daily_template."""

    def test_create_daily_template_has_frontmatter(self):
        """Verifies template has YAML frontmatter."""
        date = datetime(2026, 1, 26)
        template = create_daily_template(date)

        assert template.startswith("---\n")
        assert "type: daily" in template
        assert "date: 2026-01-26" in template

    def test_create_daily_template_has_all_sections(self):
        """Verifies template has all sections."""
        date = datetime(2026, 1, 26)
        template = create_daily_template(date)

        assert "## ✅ Done" in template
        assert "## ▶️ To Do" in template
        assert "## 🚧 Blockers" in template
        assert "## 🗓 Meetings" in template
        assert "## 🧠 Quick Notes" in template

    def test_create_daily_template_date_format(self):
        """Verifies date format in template."""
        date = datetime(2026, 12, 31)
        template = create_daily_template(date)

        assert "date: 2026-12-31" in template


class TestFindSection:
    """Tests for find_section."""

    def test_find_section_exists(self):
        """Finds an existing section."""
        content = "## ✅ Yesterday\n\n## ▶️ Today\n"
        result = find_section(content, "## ✅ Yesterday")
        assert result == 0

    def test_find_section_middle(self):
        """Finds a section in the middle."""
        content = "---\nfrontmatter\n---\n\n## ✅ Yesterday\n\n## ▶️ Today\n"
        result = find_section(content, "## ▶️ Today")
        assert result == 6

    def test_find_section_not_found(self):
        """Returns -1 if section doesn't exist."""
        content = "## ✅ Yesterday\n"
        result = find_section(content, "## Does not exist")
        assert result == -1

    def test_find_section_with_whitespace(self):
        """Handles whitespace correctly."""
        content = "  ## ✅ Yesterday  \n"
        result = find_section(content, "## ✅ Yesterday")
        assert result == 0


class TestInsertAtSection:
    """Tests for insert_at_section."""

    def test_insert_in_empty_section(self):
        """Inserts in an empty section."""
        content = "## ✅ Done\n\n## ▶️ To Do\n"
        result = insert_at_section(content, "## ✅ Done", "Completed task")

        assert "- Completed task" in result
        lines = result.split("\n")
        done_idx = lines.index("## ✅ Done")
        todo_idx = lines.index("## ▶️ To Do")
        bullet_idx = lines.index("- Completed task")
        assert done_idx < bullet_idx < todo_idx

    def test_insert_preserves_existing_bullets(self):
        """Doesn't overwrite existing bullets."""
        content = "## ✅ Yesterday\n- Task 1\n\n## ▶️ Today\n"
        result = insert_at_section(content, "## ✅ Yesterday", "Task 2")

        assert "- Task 1" in result
        assert "- Task 2" in result

    def test_insert_section_not_found(self):
        """Raises error if section doesn't exist."""
        content = "## ✅ Yesterday\n"
        with pytest.raises(ValueError, match="not found"):
            insert_at_section(content, "## Does not exist", "Task")

    def test_insert_multiple_bullets(self):
        """Inserts multiple bullets correctly."""
        content = "## ✅ Yesterday\n\n## ▶️ Today\n"
        result = insert_at_section(content, "## ✅ Yesterday", "Task 1")
        result = insert_at_section(result, "## ✅ Yesterday", "Task 2")

        assert "- Task 1" in result
        assert "- Task 2" in result


class TestParseTags:
    """Tests for parse_tags."""

    def test_parse_tags_single(self):
        """Parses a single tag."""
        bullet = "Completed task #tags: cicd"
        result = parse_tags(bullet)
        assert result == ["cicd"]

    def test_parse_tags_multiple(self):
        """Parses multiple tags."""
        bullet = "Deploy project #tags: cicd,infra,aws"
        result = parse_tags(bullet)
        assert result == ["cicd", "infra", "aws"]

    def test_parse_tags_with_spaces(self):
        """Handles spaces in tags."""
        bullet = "Task #tags: cicd, infra, aws"
        result = parse_tags(bullet)
        assert result == ["cicd", "infra", "aws"]

    def test_parse_tags_no_tags(self):
        """Returns empty list if no tags."""
        bullet = "Task without tags"
        result = parse_tags(bullet)
        assert result == []

    def test_parse_tags_empty_tags(self):
        """Handles empty tags."""
        bullet = "Task #tags: "
        result = parse_tags(bullet)
        assert result == []


class TestFormatBulletWithTags:
    """Tests for format_bullet_with_tags."""

    def test_format_with_tags(self):
        """Formats text with tags."""
        result = format_bullet_with_tags("Task", ["cicd", "infra"])
        assert result == "Task #tags: cicd,infra"

    def test_format_without_tags(self):
        """Returns text unchanged if no tags."""
        result = format_bullet_with_tags("Task", None)
        assert result == "Task"

    def test_format_empty_tags(self):
        """Returns text unchanged if tag list is empty."""
        result = format_bullet_with_tags("Task", [])
        assert result == "Task"

    def test_format_single_tag(self):
        """Formats with a single tag."""
        result = format_bullet_with_tags("Task", ["cicd"])
        assert result == "Task #tags: cicd"


class TestExtractBulletsFromSection:
    """Tests for extract_bullets_from_section."""

    def test_extract_bullets_basic(self):
        """Extracts bullets from a section."""
        content = "## ✅ Yesterday\n- Task 1\n- Task 2\n\n## ▶️ Today\n"
        result = extract_bullets_from_section(content, "## ✅ Yesterday")
        assert result == ["Task 1", "Task 2"]

    def test_extract_bullets_empty_section(self):
        """Returns empty list for section without bullets."""
        content = "## ✅ Yesterday\n\n## ▶️ Today\n"
        result = extract_bullets_from_section(content, "## ✅ Yesterday")
        assert result == []

    def test_extract_bullets_section_not_found(self):
        """Returns empty list if section doesn't exist."""
        content = "## ✅ Yesterday\n- Task\n"
        result = extract_bullets_from_section(content, "## Does not exist")
        assert result == []

    def test_extract_bullets_with_tags(self):
        """Extracts bullets including tags."""
        content = "## ✅ Yesterday\n- Task #tags: cicd\n\n## ▶️ Today\n"
        result = extract_bullets_from_section(content, "## ✅ Yesterday")
        assert result == ["Task #tags: cicd"]


class TestFilterBulletsByTags:
    """Tests for filter_bullets_by_tags."""

    def test_filter_by_single_tag(self):
        """Filters by a single tag."""
        bullets = [
            "Task 1 #tags: cicd",
            "Task 2 #tags: infra",
            "Task 3 #tags: cicd,aws",
        ]
        result = filter_bullets_by_tags(bullets, ["cicd"])
        assert result == ["Task 1 #tags: cicd", "Task 3 #tags: cicd,aws"]

    def test_filter_by_multiple_tags(self):
        """Filters by multiple tags (OR)."""
        bullets = [
            "Task 1 #tags: cicd",
            "Task 2 #tags: infra",
            "Task 3 #tags: aws",
        ]
        result = filter_bullets_by_tags(bullets, ["cicd", "aws"])
        assert result == ["Task 1 #tags: cicd", "Task 3 #tags: aws"]

    def test_filter_no_match(self):
        """Returns empty list if no matches."""
        bullets = ["Task 1 #tags: cicd"]
        result = filter_bullets_by_tags(bullets, ["infra"])
        assert result == []

    def test_filter_empty_tags(self):
        """Returns all bullets if no tags specified."""
        bullets = ["Task 1", "Task 2"]
        result = filter_bullets_by_tags(bullets, [])
        assert result == bullets

    def test_filter_case_insensitive(self):
        """Filtering is case-insensitive."""
        bullets = ["Task #tags: CICD"]
        result = filter_bullets_by_tags(bullets, ["cicd"])
        assert result == ["Task #tags: CICD"]
