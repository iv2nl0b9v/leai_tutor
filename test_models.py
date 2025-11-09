"""
Tests for data models
"""

import pytest
from models import Topic, Message, Session


class TestTopic:
    """Tests for Topic dataclass"""

    def test_topic_creation(self):
        """Test creating a Topic instance"""
        topic = Topic(
            name="Test Topic",
            objectives="Learn testing",
            materials="Testing materials",
            examples=["Example 1", "Example 2"],
            filename="test.md",
        )

        assert topic.name == "Test Topic"
        assert topic.objectives == "Learn testing"
        assert topic.materials == "Testing materials"
        assert len(topic.examples) == 2
        assert topic.filename == "test.md"

    def test_topic_with_empty_examples(self):
        """Test Topic with no examples"""
        topic = Topic(
            name="Test",
            objectives="Obj",
            materials="Mat",
            examples=[],
            filename="test.md",
        )

        assert len(topic.examples) == 0


class TestMessage:
    """Tests for Message dataclass"""

    def test_message_creation(self):
        """Test creating a Message instance"""
        msg = Message(
            role="student",
            content="Hello!",
            canvas_image=None,
            timestamp="2024-01-01 12:00:00",
        )

        assert msg.role == "student"
        assert msg.content == "Hello!"
        assert msg.canvas_image is None
        assert msg.timestamp == "2024-01-01 12:00:00"

    def test_message_with_defaults(self):
        """Test Message with default values"""
        msg = Message(role="tutor", content="Hi there!")

        assert msg.role == "tutor"
        assert msg.content == "Hi there!"
        assert msg.canvas_image is None
        assert msg.timestamp == ""

    def test_message_with_canvas_image(self):
        """Test Message with canvas image"""
        msg = Message(
            role="student", content="My answer", canvas_image="base64encodedstring"
        )

        assert msg.canvas_image == "base64encodedstring"


class TestSession:
    """Tests for Session dataclass"""

    def test_session_creation(self):
        """Test creating a Session instance"""
        session = Session(
            topic_name="Math",
            messages=[],
            created_at="2024-01-01T12:00:00",
            status="active",
            session_id="session_123",
        )

        assert session.topic_name == "Math"
        assert len(session.messages) == 0
        assert session.created_at == "2024-01-01T12:00:00"
        assert session.status == "active"
        assert session.session_id == "session_123"

    def test_session_with_defaults(self):
        """Test Session with default values"""
        session = Session(
            topic_name="Science",
            messages=[{"role": "tutor", "content": "Hello"}],
            created_at="2024-01-01T12:00:00",
        )

        assert session.status == "active"
        assert session.session_id == ""
        assert len(session.messages) == 1

    def test_session_with_messages(self):
        """Test Session with multiple messages"""
        messages = [
            {"role": "tutor", "content": "Welcome"},
            {"role": "student", "content": "Hi"},
        ]
        session = Session(
            topic_name="English", messages=messages, created_at="2024-01-01T12:00:00"
        )

        assert len(session.messages) == 2
        assert session.messages[0]["role"] == "tutor"
        assert session.messages[1]["role"] == "student"
