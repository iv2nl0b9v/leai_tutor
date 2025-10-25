"""
Data models for Leia's AI Tutor
"""
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict


@dataclass
class Topic:
    """Represents a learning topic loaded from markdown"""
    name: str
    objectives: str
    materials: str
    examples: List[str]
    filename: str


@dataclass
class Message:
    """Represents a message in the conversation"""
    role: str  # "student" or "tutor"
    content: str
    canvas_image: Optional[str] = None  # Base64 encoded image
    timestamp: str = ""


@dataclass
class Session:
    """Represents a tutoring session"""
    topic_name: str
    messages: List[Dict]  # List of message dicts
    created_at: str
    status: str = "active"  # "active" or "completed"
    session_id: str = ""

