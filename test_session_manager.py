"""
Tests for session management functionality
"""

import pytest
from pathlib import Path
import tempfile
import shutil
import json
from datetime import datetime

from models import Session
from session_manager import save_session, load_session, list_sessions


class TestSaveSession:
    """Tests for save_session function"""

    def setup_method(self):
        """Create a temporary directory for test files"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def teardown_method(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir)

    def test_save_new_session_generates_id(self):
        """Test that saving a new session generates an ID"""
        session = Session(
            topic_name="Test Topic", messages=[], created_at=datetime.now().isoformat()
        )

        session_id = save_session(session, self.temp_path)

        assert session_id.startswith("session_")
        assert session.session_id == session_id
        assert (self.temp_path / f"{session_id}.json").exists()

    def test_save_existing_session_keeps_id(self):
        """Test that saving an existing session keeps its ID"""
        session = Session(
            topic_name="Test Topic",
            messages=[],
            created_at=datetime.now().isoformat(),
            session_id="session_existing",
        )

        session_id = save_session(session, self.temp_path)

        assert session_id == "session_existing"
        assert (self.temp_path / "session_existing.json").exists()

    def test_save_session_with_messages(self):
        """Test saving a session with messages"""
        messages = [
            {"role": "tutor", "content": "Hello", "timestamp": "2024-01-01 12:00:00"},
            {"role": "student", "content": "Hi", "timestamp": "2024-01-01 12:01:00"},
        ]

        session = Session(
            topic_name="Math",
            messages=messages,
            created_at=datetime.now().isoformat(),
            session_id="session_test",
        )

        save_session(session, self.temp_path)

        # Read the file and verify content
        with open(self.temp_path / "session_test.json", "r") as f:
            data = json.load(f)

        assert data["topic_name"] == "Math"
        assert len(data["messages"]) == 2
        assert data["messages"][0]["role"] == "tutor"

    def test_save_session_overwrites_existing(self):
        """Test that saving overwrites existing session file"""
        session = Session(
            topic_name="Original",
            messages=[],
            created_at=datetime.now().isoformat(),
            session_id="session_overwrite",
        )

        # Save first version
        save_session(session, self.temp_path)

        # Modify and save again
        session.topic_name = "Modified"
        save_session(session, self.temp_path)

        # Load and verify
        with open(self.temp_path / "session_overwrite.json", "r") as f:
            data = json.load(f)

        assert data["topic_name"] == "Modified"


class TestLoadSession:
    """Tests for load_session function"""

    def setup_method(self):
        """Create a temporary directory for test files"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def teardown_method(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir)

    def test_load_existing_session(self):
        """Test loading an existing session"""
        # Create a session file
        session_data = {
            "topic_name": "Science",
            "messages": [{"role": "tutor", "content": "Welcome"}],
            "created_at": "2024-01-01T12:00:00",
            "status": "active",
            "session_id": "session_123",
        }

        with open(self.temp_path / "session_123.json", "w") as f:
            json.dump(session_data, f)

        session = load_session("session_123", self.temp_path)

        assert session is not None
        assert session.topic_name == "Science"
        assert session.session_id == "session_123"
        assert len(session.messages) == 1

    def test_load_nonexistent_session(self):
        """Test loading a session that doesn't exist"""
        session = load_session("nonexistent", self.temp_path)

        assert session is None

    def test_load_corrupted_session(self):
        """Test loading a corrupted session file"""
        # Create a corrupted JSON file
        with open(self.temp_path / "session_corrupted.json", "w") as f:
            f.write("{ invalid json }")

        session = load_session("session_corrupted", self.temp_path)

        assert session is None

    def test_load_session_with_defaults(self):
        """Test loading a session with default values"""
        session_data = {
            "topic_name": "History",
            "messages": [],
            "created_at": "2024-01-01T12:00:00",
        }

        with open(self.temp_path / "session_defaults.json", "w") as f:
            json.dump(session_data, f)

        session = load_session("session_defaults", self.temp_path)

        assert session is not None
        assert session.status == "active"
        assert session.session_id == ""


class TestListSessions:
    """Tests for list_sessions function"""

    def setup_method(self):
        """Create a temporary directory for test files"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def teardown_method(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir)

    def test_list_multiple_sessions(self):
        """Test listing multiple sessions"""
        # Create several session files
        for i in range(3):
            session_data = {
                "topic_name": f"Topic {i}",
                "messages": [{"role": "tutor", "content": f"Message {i}"}],
                "created_at": f"2024-01-0{i+1}T12:00:00",
                "status": "active",
                "session_id": f"session_test{i}",
            }

            with open(self.temp_path / f"session_test{i}.json", "w") as f:
                json.dump(session_data, f)

        sessions = list_sessions(self.temp_path)

        assert len(sessions) == 3
        assert all("session_id" in s for s in sessions)
        assert all("topic_name" in s for s in sessions)
        assert all("message_count" in s for s in sessions)

    def test_list_sessions_sorted_by_date(self):
        """Test that sessions are sorted by created_at (newest first)"""
        dates = ["2024-01-01T12:00:00", "2024-01-03T12:00:00", "2024-01-02T12:00:00"]

        for i, date in enumerate(dates):
            session_data = {
                "topic_name": f"Topic {i}",
                "messages": [],
                "created_at": date,
                "status": "active",
                "session_id": f"session_{i}",
            }

            with open(self.temp_path / f"session_{i}.json", "w") as f:
                json.dump(session_data, f)

        sessions = list_sessions(self.temp_path)

        assert len(sessions) == 3
        # Should be sorted newest first
        assert sessions[0]["created_at"] == "2024-01-03T12:00:00"
        assert sessions[1]["created_at"] == "2024-01-02T12:00:00"
        assert sessions[2]["created_at"] == "2024-01-01T12:00:00"

    def test_list_sessions_empty_directory(self):
        """Test listing sessions from empty directory"""
        sessions = list_sessions(self.temp_path)

        assert len(sessions) == 0
        assert isinstance(sessions, list)

    def test_list_sessions_ignores_non_session_files(self):
        """Test that only session_*.json files are listed"""
        # Create a valid session file
        session_data = {
            "topic_name": "Valid",
            "messages": [],
            "created_at": "2024-01-01T12:00:00",
            "status": "active",
            "session_id": "session_valid",
        }

        with open(self.temp_path / "session_valid.json", "w") as f:
            json.dump(session_data, f)

        # Create a non-session file
        with open(self.temp_path / "other_file.json", "w") as f:
            json.dump({"data": "not a session"}, f)

        sessions = list_sessions(self.temp_path)

        assert len(sessions) == 1
        assert sessions[0]["session_id"] == "session_valid"

    def test_list_sessions_includes_message_count(self):
        """Test that message_count is correctly calculated"""
        session_data = {
            "topic_name": "Test",
            "messages": [
                {"role": "tutor", "content": "1"},
                {"role": "student", "content": "2"},
                {"role": "tutor", "content": "3"},
            ],
            "created_at": "2024-01-01T12:00:00",
            "status": "active",
            "session_id": "session_count",
        }

        with open(self.temp_path / "session_count.json", "w") as f:
            json.dump(session_data, f)

        sessions = list_sessions(self.temp_path)

        assert len(sessions) == 1
        assert sessions[0]["message_count"] == 3

    def test_list_sessions_handles_corrupted_file(self):
        """Test that corrupted files are skipped gracefully"""
        # Create a valid session
        session_data = {
            "topic_name": "Valid",
            "messages": [],
            "created_at": "2024-01-01T12:00:00",
            "status": "active",
            "session_id": "session_valid",
        }

        with open(self.temp_path / "session_valid.json", "w") as f:
            json.dump(session_data, f)

        # Create a corrupted file
        with open(self.temp_path / "session_corrupted.json", "w") as f:
            f.write("{ invalid }")

        sessions = list_sessions(self.temp_path)

        # Should only include the valid session
        assert len(sessions) == 1
        assert sessions[0]["session_id"] == "session_valid"
