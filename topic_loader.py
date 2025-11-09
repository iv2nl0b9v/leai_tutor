"""
Topic loading and parsing functionality
"""

from pathlib import Path
from typing import Dict
import re

from models import Topic


def parse_markdown_topic(filepath: Path) -> Topic:
    """Parse a markdown file into a Topic object"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract title (first H1)
    title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    name = title_match.group(1) if title_match else filepath.stem

    # Split by H2 headers
    sections = re.split(r"\n##\s+", content)

    objectives = ""
    materials = ""
    examples = []

    for section in sections[1:]:  # Skip the part before first H2
        lines = section.split("\n", 1)
        header = lines[0].strip()
        body = lines[1].strip() if len(lines) > 1 else ""

        if "learning objective" in header.lower():
            objectives = body
        elif "material" in header.lower():
            materials = body
        elif "example problem" in header.lower():
            # Extract list items
            examples = [
                line.strip("- ").strip()
                for line in body.split("\n")
                if line.strip().startswith("-")
            ]

    return Topic(
        name=name,
        objectives=objectives,
        materials=materials,
        examples=examples,
        filename=filepath.name,
    )


def load_all_topics(topics_dir: Path) -> Dict[str, Topic]:
    """Load all topics from the topics directory"""
    topics = {}
    if not topics_dir.exists():
        topics_dir.mkdir(exist_ok=True)
        return topics

    for md_file in topics_dir.glob("*.md"):
        try:
            topic = parse_markdown_topic(md_file)
            topics[topic.name] = topic
        except Exception as e:
            print(f"Error loading topic {md_file}: {e}")

    return topics
