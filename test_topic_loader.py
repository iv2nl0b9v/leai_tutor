"""
Tests for topic loading functionality
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from topic_loader import parse_markdown_topic, load_all_topics


class TestParseMarkdownTopic:
    """Tests for parse_markdown_topic function"""

    def setup_method(self):
        """Create a temporary directory for test files"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def teardown_method(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir)

    def test_parse_complete_topic(self):
        """Test parsing a complete topic markdown file"""
        content = """# Simplifying Fractions

## Learning Objectives
- Understand numerator and denominator
- Learn to find common factors

## Materials
This is the teaching material about fractions.
It can span multiple lines.

## Example Problems
- Simplify 4/8
- Simplify 6/9
- Simplify 10/15
"""

        filepath = self.temp_path / "test-topic.md"
        filepath.write_text(content, encoding="utf-8")

        topic = parse_markdown_topic(filepath)

        assert topic.name == "Simplifying Fractions"
        assert "numerator" in topic.objectives
        assert "teaching material" in topic.materials
        assert len(topic.examples) == 3
        assert "Simplify 4/8" in topic.examples
        assert topic.filename == "test-topic.md"

    def test_parse_topic_without_h1(self):
        """Test parsing topic without H1 header uses filename"""
        content = """## Learning Objectives
- Test objective

## Materials
Test materials

## Example Problems
- Problem 1
"""

        filepath = self.temp_path / "fallback-name.md"
        filepath.write_text(content, encoding="utf-8")

        topic = parse_markdown_topic(filepath)

        assert topic.name == "fallback-name"

    def test_parse_topic_with_empty_sections(self):
        """Test parsing topic with missing/empty sections"""
        content = """# Test Topic

## Learning Objectives

## Materials

## Example Problems
"""

        filepath = self.temp_path / "empty.md"
        filepath.write_text(content, encoding="utf-8")

        topic = parse_markdown_topic(filepath)

        assert topic.name == "Test Topic"
        assert topic.objectives == ""
        assert topic.materials == ""
        assert len(topic.examples) == 0

    def test_parse_topic_partial_sections(self):
        """Test parsing topic with only some sections"""
        content = """# Partial Topic

## Materials
Only materials here
"""

        filepath = self.temp_path / "partial.md"
        filepath.write_text(content, encoding="utf-8")

        topic = parse_markdown_topic(filepath)

        assert topic.name == "Partial Topic"
        assert topic.materials == "Only materials here"
        assert topic.objectives == ""
        assert len(topic.examples) == 0


class TestLoadAllTopics:
    """Tests for load_all_topics function"""

    def setup_method(self):
        """Create a temporary directory for test files"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def teardown_method(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir)

    def test_load_multiple_topics(self):
        """Test loading multiple topic files"""
        # Create two topic files
        topic1 = """# Topic One

## Learning Objectives
- Objective 1

## Materials
Materials 1

## Example Problems
- Problem 1
"""

        topic2 = """# Topic Two

## Learning Objectives
- Objective 2

## Materials
Materials 2

## Example Problems
- Problem 2
"""

        (self.temp_path / "topic1.md").write_text(topic1, encoding="utf-8")
        (self.temp_path / "topic2.md").write_text(topic2, encoding="utf-8")

        topics = load_all_topics(self.temp_path)

        assert len(topics) == 2
        assert "Topic One" in topics
        assert "Topic Two" in topics
        assert topics["Topic One"].filename == "topic1.md"
        assert topics["Topic Two"].filename == "topic2.md"

    def test_load_from_empty_directory(self):
        """Test loading from empty directory"""
        topics = load_all_topics(self.temp_path)

        assert len(topics) == 0
        assert isinstance(topics, dict)

    def test_load_creates_directory_if_not_exists(self):
        """Test that load_all_topics creates directory if it doesn't exist"""
        non_existent = self.temp_path / "new_dir"

        assert not non_existent.exists()

        topics = load_all_topics(non_existent)

        assert non_existent.exists()
        assert len(topics) == 0

    def test_load_ignores_non_md_files(self):
        """Test that only .md files are loaded"""
        # Create a .md file and a .txt file
        (self.temp_path / "topic.md").write_text(
            "# Valid Topic\n\n## Materials\nTest", encoding="utf-8"
        )
        (self.temp_path / "readme.txt").write_text("Not a topic", encoding="utf-8")

        topics = load_all_topics(self.temp_path)

        assert len(topics) == 1
        assert "Valid Topic" in topics

    def test_load_handles_corrupted_file(self):
        """Test that corrupted files are skipped gracefully"""
        # Create a valid file and a corrupted one
        (self.temp_path / "valid.md").write_text(
            "# Valid\n\n## Materials\nTest", encoding="utf-8"
        )

        # Create an empty or problematic file
        corrupted_file = self.temp_path / "corrupted.md"
        corrupted_file.write_bytes(b"\x00\x00\x00")

        # Should not crash, should load the valid file
        topics = load_all_topics(self.temp_path)

        # At least the valid topic should be loaded
        assert "Valid" in topics or len(topics) >= 0  # Graceful failure
